"""Sixteen required test families plus failure-gate regression checks."""
from copy import deepcopy
import hashlib
import itertools
import json
import math
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from ccc.analysis.shift_perm import perm_p, interval, lower
from ccc.analysis.statistics import bootstrap, sign_flip, holm, tv_excess, InsufficientWorlds
from ccc.analysis.loaders import metrics, final_attempts, load, validate, ValidationError, Reader, sham_selected
from ccc.analysis.status import derive_status
from ccc.analysis.study import paired, world_value
from ccc.analysis.pinning import pin_thresholds
from ccc.analysis.pipeline import run


def row(arm='F', rep=0, **kw):
    return dict({'attempt_id':f'{arm}{rep}','checkpoint_id':'c','arm':arm,'rep':rep,'attempt_no':1,
        'status':'complete','load_session_id':'session','rewards':{'a':4.,'b':6.,'x':1.,'y':3.},
        'roles':{'a':'coalition','b':'coalition','x':'outsider','y':'outsider'},
        'committed':{'a':'t1','b':'t2','x':'t3','y':'skip'},'noncommit_agents':[],
        'n_calls':1,'tokens_prompt':2,'tokens_completion':3,'latency_ms_total':1.,'latency_ms_p95':1.,
        'model_resolved':'offline','context_overflow':False,'v3_pass':True,'leak':{'first_turn':None,'surface':None},'resend':False,'cost_usd':None},**kw)


def checkpoint(**kw):
    return dict({'checkpoint_id':'c','world_id':'w','regime':'B1','eligible':True,'ineligible_reason':None,
        'sender':'a','receiver':'b','t_star':1,'estar_event_ids':['e'],'n_subset':True,'mstar_available':True,
        'info_bearing':False,'flags':{k:False for k in ('redundant_carrier','post_fork_carrier','resend_detected','state_redundant')},
        'v_checks':{f'V{i}':'pass' for i in range(1,8)}},**kw)


def fixture(root, rows=None, cps=None):
    manifest={'schema_version':'ccc.run.v1','experiment_id':'offline','phase':'development','protocol_sha256':'dev',
        'stat001_hash':'dev','frozen':False,'arms':['F','K','S','N'],'continuations_by_arm':{'F':4,'K':4,'S':2,'N':4},
        'n_subset_seed':7,'branch_order_seed':2,'sampling_seed':3,'model':{'requested_id':'offline','resolved_id':'offline','parameters':{}},
        'policy':{'new_out_of_pocket_usd':0}}
    if rows is None: rows=[row(a,i) for a,n in manifest['continuations_by_arm'].items() for i in range(n)]
    if cps is None: cps=[checkpoint()]
    (root/'manifest.json').write_text(json.dumps(manifest));(root/'checkpoints.json').write_text(json.dumps(cps))
    (root/'worlds.json').write_text(json.dumps([{'world_id':c['world_id'],'regime':c['regime'],'world_seed':1,'agents':list('abxy'),'pair':list('ab'),'outsiders':list('xy'),'order':list('abxy')} for c in cps]))
    (root/'branch_ledger.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    return manifest


class RequiredTests(unittest.TestCase):
    def test_01_metric_sign_and_identity(self):
        rng=np.random.default_rng(44)
        for _ in range(100):
            f=row(rewards=dict(zip('abxy',rng.uniform(-10,20,4))))
            k=row('K',rewards=dict(zip('abxy',rng.uniform(-10,20,4))))
            fm,km=metrics(f),metrics(k)
            o=km['Omean']-fm['Omean']; c=fm['Cmean']-km['Cmean']
            self.assertAlmostEqual(km['W']-fm['W'],2*o-2*c)
        self.assertGreater(metrics(row(rewards={'a':4,'b':6,'x':5,'y':9}))['Omean']-metrics(row())['Omean'],0)

    def test_02_reward_identity_joint_never_read(self):
        class NoJoint(dict):
            def __getitem__(self,k):
                if k=='joint_reward': raise AssertionError('joint reward accessed')
                return super().__getitem__(k)
        self.assertEqual(metrics(NoJoint(row(joint_reward=999)))['W'],14)

    def test_03_vectors_minimum_monotone_ties(self):
        vectors=json.loads(Path(__file__).with_name('vectors.json').read_text())
        for v in vectors['intervals']:
            self.assertEqual(interval(v['F'],v['K']),(v['L'],v['U']))
            self.assertEqual(interval(v['F'][::-1],v['K'][::-1]),(v['L'],v['U']))
            ps=[perm_p(v['F'],v['K'],m) for m in range(-10,20)]
            self.assertEqual(ps,sorted(ps))
        for nf,nk,denom in vectors['min_p']:
            self.assertAlmostEqual(perm_p([0]*nf,[10]*nk),1/denom)
        self.assertEqual(perm_p([5]*4,[5]*4),1)
        self.assertEqual(interval([5]*4,[5]*4),(0.,0.))

    def test_04_coverage_simulation(self):
        rng=np.random.default_rng(20261025); n=2000; covered=0
        for _ in range(n):
            f=rng.normal(size=4).tolist(); k=(rng.normal(size=4)+3).tolist()
            covered+=lower(f,k)<=3
        rate=covered/n
        self.assertGreaterEqual(rate,.95)
        evidence=Path(__file__).resolve().parents[2]/'docs/analysis/readiness/coverage_simulation.json'
        evidence.parent.mkdir(parents=True,exist_ok=True)
        evidence.write_text(json.dumps({'seed':20261025,'n':n,'covered':covered,'realized_lower_coverage':rate},sort_keys=True)+'\n')

    def test_05_bootstrap_world_unit(self):
        ds=[-10,0,10,20]
        self.assertEqual(bootstrap(ds),bootstrap(ds))
        correct=bootstrap(ds); wrong=bootstrap(np.repeat(ds,40))
        self.assertGreater(correct[1]-correct[0],3*(wrong[1]-wrong[0]))
        for values in ([],[1]):
            with self.assertRaises(InsufficientWorlds): bootstrap(values)
        rng=np.random.Generator(np.random.PCG64(20261025))
        expected=np.percentile(np.asarray(ds)[rng.integers(0,4,(10000,4))].mean(axis=1),[2.5,97.5],method='linear')
        self.assertEqual(correct,tuple(expected))

    def test_06_sign_flip_bruteforce(self):
        for n in range(5,11):
            xs=list(range(1,n+1)); obs=sum(xs)/n
            brute=sum(sum(s*x for s,x in zip(ss,xs))/n>=obs-1e-12 for ss in itertools.product([-1,1],repeat=n))/2**n
            self.assertEqual(sign_flip(xs)['p'],brute)
            self.assertEqual(sign_flip(xs,True)['p'],2*brute)
        self.assertEqual(sign_flip([1,2,3,4,0])['status'],'unattainable')

    def test_07_holm(self):
        self.assertEqual(holm([.01,.04,.03]),[.03,.06,.06])
        self.assertEqual(holm([.9,.8,.7]),[1,1,1])
        self.assertEqual(holm([.01,None,.02]),[.03,None,.04])

    def test_08_ineligible_sensitivities(self):
        self.assertEqual(world_value(checkpoint(eligible=False,ineligible_reason='no_exposure'),8),0)
        self.assertIsNone(world_value(checkpoint(eligible=False,ineligible_reason='pre_exposed'),8))
        self.assertEqual(world_value(checkpoint(eligible=False,ineligible_reason='pre_exposed'),8,True),0)
        worlds=[dict(world_id='w',regime='B1',eligible=True,tau_O=7),dict(world_id='w',regime='B2',eligible=False,ineligible_reason='no_exposure',tau_O=None)]
        self.assertEqual(paired(worlds)[0]['d_w'],7); self.assertEqual(paired(worlds,conditional=True),[])

    def test_09_missing_and_noncommit(self):
        r=row(status='infra_timeout'); self.assertIsNone(metrics(r)['Omean'])
        r=row(status='complete_noncommit',rewards={'a':0,'b':6,'x':0,'y':3},noncommit_agents=['a','x'])
        self.assertEqual(metrics(r)['Omean'],1.5)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); src=root/'in';src.mkdir()
            rows=[row(a,i) for a,n in {'F':4,'K':4,'S':2,'N':4}.items() for i in range(n)]
            rows[0]=row('F',0,status='infra_timeout');rows[5]=row('K',1,status='complete_noncommit',rewards={'a':0,'b':6,'x':0,'y':3},noncommit_agents=['a','x'])
            fixture(src,rows);self.assertEqual(run(src,root/'out'),0)
            sens=json.loads((root/'out/sensitivity.json').read_text())
            self.assertTrue({'worst_missing','best_missing','noncommit_excluded'}<={x['analysis'] for x in sens})

    def test_10_retries_preserve_failures(self):
        first=row(status='infra_timeout'); last=row(attempt_id='retry',attempt_no=2)
        self.assertEqual(final_attempts([last,first]),[last])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/'in';src.mkdir();fixture(src,[first,last])
            self.assertEqual(run(src,root/'out'),0)
            attempts=json.loads((root/'out/attempts.json').read_text())
            self.assertEqual([x['status'] for x in attempts],['infra_timeout','complete'])
            missing=json.loads((root/'out/missingness.json').read_text())
            f=next(x for x in missing if x['arm']=='F')
            self.assertEqual(f['n_retry_attempts'],1);self.assertEqual(f['attempt_status_counts']['infra_timeout'],1)

    def test_11_pinning_treatment_unread(self):
        class Poison(dict):
            def __getitem__(self,k):
                if k!='arm': raise AssertionError('treatment outcome read')
                return super().__getitem__(k)
        fs=[dict(row(arm,i),world_id=str(i),regime=regime,checkpoint_id=f'{i}-{regime}') for i in range(4) for regime in ('B1','B2') for arm in ('F','S')]
        base=pin_thresholds(fs+[Poison(arm=a) for a in ('K','N','C')])
        self.assertEqual(base,pin_thresholds(fs+[{'arm':'K','rewards':{'evil':999}}]))
        self.assertEqual(base['m_O'],2.5)

    def test_12_labels_isolated(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/'in';src.mkdir();fixture(src)
            (src/'instances.jsonl').write_text('L_mech secret oracle_tau_O')
            self.assertEqual(run(src,root/'out'),0)
            aggregate=json.loads((root/'out/aggregate.json').read_text())
            self.assertNotIn('instances.jsonl',aggregate['input_hashes'])
            self.assertNotIn('L_mech',(root/'out/continuations.csv').read_text())
            with self.assertRaises(ValidationError): Reader(src).read(src/'instances.jsonl')

    def test_13_outputs_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/'in';src.mkdir();fixture(src)
            for name in ('a','b'): self.assertEqual(run(src,root/name),0)
            def hashes(p): return {str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()}
            self.assertEqual(hashes(root/'a'),hashes(root/'b'))

    def test_14_no_network_no_outside_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/'in';src.mkdir();fixture(src)
            with patch('socket.socket',side_effect=AssertionError('network attempted')):
                self.assertEqual(run(src,root/'out'),0)
            self.assertEqual(sorted(p.name for p in root.iterdir()),['in','out'])
        # The required offline runner also installs an unremovable audit hook.
        with self.assertRaises(PermissionError): socket.getaddrinfo('example.invalid',443)

    def test_15_empty_data_no_nan(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/'in';src.mkdir();fixture(src,[],[])
            self.assertEqual(run(src,root/'out'),0)
            aggregate=json.loads((root/'out/aggregate.json').read_text());self.assertEqual(aggregate['n_checkpoints'],0)
            for f in (root/'out').rglob('*.json'): self.assertNotIn('NaN',f.read_text())
            effects=json.loads((root/'out/effects_study.json').read_text());self.assertIsNone(effects[0]['estimate'])

    def test_16_status_truth_table(self):
        cp=checkpoint(); b={'tau_O':(8,12),'tau_C':(3,5),'tau_W':(-2,2)}
        g={'m_O':5,'delta_W':10,'all_valid':True,'placebo_available':True}
        self.assertEqual(derive_status(cp,b,g),('supported',[]))
        self.assertEqual(derive_status(checkpoint(v_checks={'V3':'fail'}),b,g)[0],'invalid')
        self.assertEqual(derive_status(cp,b,dict(g,V9='invalid_batch'))[0],'invalid')
        self.assertEqual(derive_status(checkpoint(eligible=False,ineligible_reason='no_exposure'),b,g)[0],'ineligible')
        self.assertEqual(derive_status(cp,{},g)[1],['insufficient_continuations'])
        self.assertEqual(derive_status(cp,b,dict(g,session_break=True))[0],'invalid')
        for key in ('lesion_artefact','treatment_dependent_missingness'):
            self.assertIn(key,derive_status(cp,b,dict(g,**{key:True}))[1])
        self.assertIn('info_loss_untested',derive_status(checkpoint(info_bearing=True),b,g)[1])
        self.assertIn('no_placebo_available',derive_status(cp,b,dict(g,placebo_available=False))[1])
        null=dict(b,tau_O=(-1,1))
        self.assertEqual(derive_status(cp,null,g)[0],'not_supported')
        self.assertIn('not_identifiable_redundant',derive_status(checkpoint(flags={'redundant_carrier':True}),null,g)[1])
        for metric,values,reason in [('tau_C',(-3,-1),'pattern_mutual_disruption'),('tau_W',(-20,-15),'pattern_efficient_transfer'),('tau_C',(-1,3),'pattern_ambiguous'),('tau_O',(1,6),'imprecise')]:
            self.assertIn(reason,derive_status(cp,dict(b,**{metric:values}),g)[1])
        self.assertIn('validity_unestablished',derive_status(cp,b,dict(g,all_valid=False))[1])


class RegressionTests(unittest.TestCase):
    def test_tv_exact_null_subtraction(self):
        tv=tv_excess(['a']*4,['b']*4)
        self.assertEqual(tv['TV_raw'],1.)
        labels=['a']*4+['b']*4
        null=[]
        for idx in itertools.combinations(range(8),4):
            n=sum(labels[i]=='a' for i in idx);null.append(abs(n/4-(4-n)/4))
        self.assertAlmostEqual(tv['TV_excess'],1-np.mean(null))
        self.assertEqual(tv_excess(['a']*4,['a']*4)['TV_excess'],0)

    def test_reject_mixed_model_duplicates_invalid_rewards(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for rows in ([row(model_resolved='other')],[row(),row()],[row(rewards={'a':None})],[row(noncommit_agents=['a'])]):
                fixture(root,rows)
                with self.assertRaises(ValidationError): load(root)

    def test_holdout_requires_freeze_and_hashes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);m=fixture(root);m.update(phase='holdout')
            (root/'manifest.json').write_text(json.dumps(m))
            with self.assertRaises(ValidationError):load(root)

    def test_session_break_excludes_entire_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/'in';src.mkdir()
            fixture(src,[row('F',0),row('K',0,load_session_id='new')]);self.assertEqual(run(src,root/'out'),0)
            cs=json.loads((root/'out/checkpoint_certificates.json').read_text())
            self.assertEqual(cs[0]['status'],'invalid');self.assertIsNone(cs[0]['tau_O'])

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValidationError): Reader(d).read(Path(d).parent/'outside.json')

    def test_sham_hash_rule(self):
        for name in ('a','b','c','checkpoint007'):
            expected=int(hashlib.sha256(('ccc.sham.v1|'+name).encode()).hexdigest(),16)%2==0
            self.assertEqual(sham_selected(name),expected)

    def test_v3_failure_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/'in';src.mkdir();fixture(src,[row(v3_pass=False)])
            self.assertEqual(run(src,root/'out'),0)
            self.assertEqual(json.loads((root/'out/checkpoint_certificates.json').read_text())[0]['status'],'invalid')

    def test_missing_fill_sensitivity_hand_calculation(self):
        from ccc.analysis.pipeline import _sensitivities
        cps=[];worlds=[];rows=[]
        for regime in ('B1','B2'):
            cp=checkpoint(checkpoint_id=regime);cp['regime']=regime;cps.append(cp)
            worlds.append(dict(world_id='w',regime=regime,eligible=True,ineligible_reason=None,tau_O=2.,tau_C=0.,tau_W=4.,n_F=3,n_K=3))
            for arm,values in [('F',[0.,4.]),('K',[2.,6.])]:
                for i,value in enumerate(values): rows.append(dict(checkpoint_id=regime,regime=regime,arm=arm,Omean=value,missing=False,status='complete'))
                rows.append(dict(checkpoint_id=regime,regime=regime,arm=arm,Omean=None,missing=True,status='infra_timeout'))
        got={r['analysis']:r for r in _sensitivities(cps,rows,worlds)}
        self.assertAlmostEqual(got['worst_missing']['estimate'],-8/3)
        self.assertAlmostEqual(got['best_missing']['estimate'],8/3)
        self.assertEqual(got['noncommit_excluded']['estimate'],0.)

    def test_grid_search_matches_independent_reference(self):
        # Independent scalar reference supplied by STAT-001, without importing production.
        import importlib.util
        source=Path(__file__).resolve().parents[2]/'docs/stats/ref_enumeration.py'
        spec=importlib.util.spec_from_file_location('reference',source)
        reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)
        f=[-1,2,2,9];k=[0,7,8]
        self.assertEqual(interval(f,k),(reference.lower(f,k),reference.upper(f,k)))
        for m in (-60,-1.25,0,2.5,60):
            for side in ('ge','le'):self.assertEqual(perm_p(f,k,m,side),reference.perm_p(f,k,m,side))

    def test_deprecated_N_cannot_enable_support(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/'in';src.mkdir()
            cp=checkpoint(placebo_kind='N_v1.1_deprecated')
            rs=[]
            for arm,n in {'F':4,'K':4,'S':2,'N':4}.items():
                for i in range(n):
                    rewards={'a':20.,'b':20.,'x':0.,'y':0.} if arm in ('F','S','N') else {'a':10.,'b':10.,'x':20.,'y':20.}
                    rs.append(row(arm,i,rewards=rewards))
            fixture(src,rs,[cp]);self.assertEqual(run(src,root/'out'),0)
            cert=json.loads((root/'out/checkpoint_certificates.json').read_text())[0]
            self.assertEqual(cert['status'],'inconclusive');self.assertIn('no_placebo_available',cert['reasons'])
            self.assertEqual(cert['tau_O_minus_tau_O_N'],20.)

    def test_validation_report_records_multiple_gates(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/'in';src.mkdir();fixture(src,[row(model_resolved='wrong',status='unknown')])
            self.assertEqual(run(src,root/'out'),2)
            report=json.loads((root/'out/validation_report.json').read_text())
            self.assertFalse(report['valid']);self.assertGreaterEqual(len(report['problems']),2)

    def test_behavioural_retry_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);fixture(root,[row(),row(attempt_no=2,attempt_id='retry')])
            with self.assertRaises(ValidationError):load(root)
