"""Held-out-shaped runner readiness using only synthetic metadata."""
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from ccc.analysis.loaders import load, sham_selected, ValidationError
from ccc.analysis.pipeline import run
from ccc.analysis.statistics import holm
from tests.analysis.readiness_fixture import generate


class ReadinessTests(unittest.TestCase):
    def test_runner_end_to_end(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); src=root/'synthetic'; generate(src)
            with patch('socket.socket',side_effect=AssertionError('network')):
                self.assertEqual(run(src,root/'out'),0)
            out=root/'out'
            read=lambda n:json.loads((out/(n+'.json')).read_text())
            agg=read('aggregate'); self.assertEqual(agg['n_checkpoints'],16)
            self.assertEqual(agg['thresholds'],dict(m_O=2.5,delta_W=5.,delta_S=2.5,theta=.4,weak_detector=True))
            certs=read('checkpoint_certificates')
            self.assertTrue(any(c['status']=='inconclusive' and 'no_placebo_available' in c['reasons'] for c in certs))
            self.assertTrue(all(c['tau_O_minus_tau_O_N'] is None and c['placebo_contrast_status'].startswith('unavailable:') for c in certs))
            rows=read('continuations')
            self.assertFalse(any(r['arm']=='N' for r in rows))
            self.assertTrue(all(sham_selected(r['checkpoint_id']) for r in rows if r['arm']=='S'))
            self.assertTrue(all(r['rep']==0 for r in rows if r['arm']=='S'))
            self.assertEqual(sum(r['n_scheduled'] for r in read('missingness') if r['arm']=='N'),0)
            self.assertTrue(all(r['n_missing']==0 for r in read('missingness')))
            schedule=read('scheduled_statuses'); self.assertEqual(sum(r['kind']=='world_attempt' for r in schedule),16)
            self.assertEqual(sum(r['status']=='failed' for r in schedule),2)
            self.assertEqual(sum(r.get('error')=='frozen request cap exhausted' for r in schedule),1)
            effects=read('effects_study'); by={r['effect']:r for r in effects}
            ds=[0,1,2,3,4,5,7] # B2 no-exposure is zero in pair seven; pair eight undefined.
            rng=np.random.Generator(np.random.PCG64(20261025))
            ci=np.percentile(np.array(ds)[rng.integers(0,7,(10000,7))].mean(axis=1),[2.5,97.5])
            self.assertEqual(by['Delta_total']['estimate'],sum(ds)/7)
            self.assertEqual([by['Delta_total']['L'],by['Delta_total']['U']],list(ci))
            brute=sum(sum(s*x for s,x in zip(ss,ds))>=sum(ds) for ss in itertools.product((-1,1),repeat=7))/128
            self.assertEqual(by['Delta_total']['p_raw'],brute)
            self.assertEqual(by['Delta_conditional']['n_independent'],6)
            self.assertEqual(by['eligibility_difference']['estimate'],1/8)
            secondary=[by[f'S{i}'] for i in range(1,4)]
            self.assertEqual([r['p_holm'] for r in secondary],holm([r['p_raw'] for r in secondary]))
            v9=[r for r in read('validity_checks') if r['check']=='V9']
            self.assertTrue(all(r['status']=='pass' and r['L90']==r['U90']==0 for r in v9))
            self.assertEqual(sum(r['n_independent'] for r in v9),sum(r['arm']=='S' for r in rows))
            self.assertFalse(any(r['confirmatory'] for r in effects))
            self.assertEqual(run(src,root/'repeat'),0)
            first={str(p.relative_to(out)):p.read_bytes() for p in out.rglob('*') if p.is_file()}
            second={str(p.relative_to(root/'repeat')):p.read_bytes() for p in (root/'repeat').rglob('*') if p.is_file()}
            self.assertEqual(first,second)
            self.assertEqual(len(first),39)

    def test_active_synthetic_refused_before_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); generate(root); (root/'WATCHDOG_EXIT.json').unlink()
            with self.assertRaises(ValidationError): load(root)

    def test_synthetic_cannot_enable_live(self):
        from tests.analysis.readiness_fixture import put
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); m=generate(root); m['policy']['live_inference_enabled']=True
            put(root/'manifest.json',m)
            with self.assertRaises(ValidationError): load(root)

    def test_real_frozen_manifest_contract_without_outcomes(self):
        # Only the explicitly authorized design manifest is read; no experiment output.
        from ccc.analysis.loaders import ROOT
        from tests.analysis.readiness_fixture import put
        m=json.loads((ROOT/'docs/runner/exp002_manifest.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            put(root/'manifest.json',m)
            (root/'worlds').mkdir()
            (root/'WATCHDOG_EXIT.json').write_text('{}')
            manifest,cps,rows,events,schedule,hashes,warnings,addendum=load(root)
            self.assertEqual(len(schedule),16)
            self.assertEqual(cps,[]); self.assertEqual(rows,[])
            self.assertEqual(manifest['phase'],'holdout')
            self.assertFalse(manifest['synthetic'])
            self.assertEqual(addendum['m_O'],2.5)

    def test_whole_world_retry_does_not_pool_old_branches(self):
        from tests.analysis.readiness_fixture import put
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); src=root/'in'; generate(src)
            directory=src/'worlds/SYN01_B1/attempt_0002'
            original=src/'worlds/SYN01_B1/attempt_0001'
            begin=json.loads((original/'begin.json').read_text())['data']
            put(directory/'begin.json',dict(begin,load_session='new-session'))
            put(directory/'checkpoint.json',json.loads((original/'checkpoint.json').read_text())['data'])
            put(directory/'placebo.json',json.loads((original/'placebo.json').read_text())['data'])
            put(directory/'result.json',dict(status='failed',outcomes=None,error='synthetic failed retry'))
            self.assertEqual(run(src,root/'out'),0)
            rows=json.loads((root/'out/continuations.json').read_text())
            current=[r for r in rows if r['checkpoint_id']=='SYN01_B1']
            self.assertTrue(current)
            self.assertTrue(all(r['status']=='unrecorded_missing' for r in current))
            missing=json.loads((root/'out/missingness.json').read_text())
            self.assertEqual(next(r for r in missing if r['regime']=='B1' and r['arm']=='F')['n_missing'],4)

    def test_v9_s1_tost_uncertain_and_invalid(self):
        from ccc.analysis.pipeline import _validity
        from ccc.analysis.statistics import t_interval
        for differences,expected in [([3.,3.,3.],'invalid_batch'),([-10.,0.,10.],'sham_uncertain'),([0.,.1,-.1],'pass')]:
            cps=[dict(checkpoint_id=str(i),world_id=str(i),regime='B1',eligible=True) for i in range(3)]
            rows=[dict(checkpoint_id=str(i),arm=arm,Omean=value,missing=False) for i,d in enumerate(differences) for arm,value in [('F',0.),('S',-d)]]
            validity,_=_validity(cps,rows,[],2.5)
            v9=next(r for r in validity if r['check']=='V9')
            self.assertEqual(v9['status'],expected)
            self.assertEqual((v9['L90'],v9['U90']),t_interval(differences,.90))
            self.assertEqual((v9['L95'],v9['U95']),t_interval(differences,.95))
