"""BENCH-ALIGN protocol contracts: temporary dummy seed streams only."""
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ccc.bench import seeds
from ccc.bench import __main__ as cli
from ccc.bench.methods import run_methods, ladder, ladder_v1, ccc
from ccc.bench.enumerate import census, lookup, design_reference
from ccc.bench.observe import canonical, observe, SETS
from ccc.bench.score import symmetry
from ccc.bench.twins import continuation, pair, suite
from ccc.bench.report import strongest_baseline


class AlignmentTests(unittest.TestCase):
    def test_crn_pointwise_identical_twins_every_arm_and_noise_stratum(self):
        for eps in (0,.1):
            a,b=pair('P3',13000,eps)  # identical policies; external record differs
            for arm in ('F','K','S','N','J','REF'):
                for probe in (False,True):
                    for index in range(8):
                        self.assertEqual(canonical(continuation(a,arm,index,probe=probe)),
                                         canonical(continuation(b,arm,index,probe=probe)))
        a,b=pair('P3',13000,.1)
        tables=census(13000,.1); rows=[]
        for instance in (a,b):
            for s in SETS[:-1]:
                view=observe(instance,s)
                rows.append(dict(seed=13000,unit='seed-13000',kind='P3',member=instance.member,
                                 epsilon=.1,set=s,view_sha256=sha256(canonical(view).encode()).hexdigest(),
                                 methods=run_methods(view,design_reference(lookup(tables,view)))))
        result=symmetry(rows)
        self.assertIn('common random numbers',result['randomness'])
        self.assertTrue(all(x['kind']=='P3' and x['rate']['unit_k']==0 for x in result['violations']))
        rows[-1]['methods']['B0']['status']='injected leak'
        self.assertTrue(any(x['rate']['unit_k'] for x in symmetry(rows)['violations']))

    def test_v1_negative_separator_evidence_and_v0_preserved(self):
        for eps in (0,.1):
            for kind,start in (('P1',3),('P2',4),('P3',5)):
                for member in pair(kind,13000,eps):
                    for i,s in enumerate(SETS):
                        view=observe(member,s); exposure=ccc(view)
                        old=ladder(view,exposure); new=ladder_v1(view,exposure)
                        self.assertNotEqual(old['status'],'L3 excluded')
                        if member.member=='1' and i>=start:
                            self.assertEqual(new['status'],'L3 excluded',(kind,eps,s))
                            self.assertIs(new['predictions']['M'],False)
                            self.assertEqual(new['predictions']['E'],old['predictions']['E'])
                            self.assertEqual(new['rung'],old['rung'])
                        else:
                            self.assertEqual(new,old,(kind,eps,s,member.member))
        # A single K effect is not evidence of inertness even if J equals K.
        from ccc.bench.twins import construct
        view=observe(construct(13000,'P1','primary'),'I3')
        self.assertNotEqual(ladder_v1(view,ccc(view))['status'],'L3 excluded')
        view=observe(construct(13000,'invalid',corruption='leaked_mask'),'I5')
        self.assertEqual(ladder_v1(view,ccc(view))['status'],'invalid')

    def test_rq2_is_independent_of_ladder_correctness(self):
        from ccc.bench.report import frontier_table
        rows=[]; frontiers=[]
        for eps in (0,.1):
            frontiers.append(dict(epsilon=eps,pairs={'P2':dict(minimal_pair_separator='I4')}))
            for s in SETS:
                for member in ('0','1'):
                    target=member=='0'
                    rows.append(dict(kind='P2',seed=13000,member=member,unit='seed-13000',epsilon=eps,set=s,
                        truth=dict(M='harmful-coordination' if target else 'legitimate-cooperation'),
                        view_sha256=member if s in ('I4','I5') else 'same',
                        methods={'Bayes-given-S':dict(predictions=dict(M=target if s in ('I4','I5') else True)),
                                 'CCC-L-v0':dict(predictions=dict(M=None)),
                                 'CCC-L-v1':dict(predictions=dict(M=None))}))
        for cell in frontier_table(rows,frontiers):
            if cell['kind']=='P2':
                self.assertTrue(cell['pass_criterion'])
                self.assertEqual(cell['observed_bayes'],'I4')
        rows[0]['methods']['CCC-L-v1']['predictions']['M']=True
        rows[1]['methods']['CCC-L-v1']['predictions']['M']=False
        cell=next(x for x in frontier_table(rows,frontiers) if x['kind']=='P2' and x['epsilon']==0)
        self.assertFalse(cell['pass_criterion'])

    def test_seed_formula_skip_and_global_disjointness(self):
        dummy=sha256(b'dummy protocol for unit testing only').hexdigest()
        initial=int.from_bytes(sha256(f'{dummy}|P1|0'.encode()).digest()[:4],'big')>>1
        with tempfile.TemporaryDirectory() as td:
            excluded,_=seeds.exclusions(Path(td))
            excluded['test_collision']=[initial]
            result=seeds.draw(dummy,excluded)
            salted=int.from_bytes(sha256(f'{dummy}|P1|0|1'.encode()).digest()[:4],'big')>>1
            self.assertEqual(result['strata']['P1'][0],salted)
            self.assertEqual(result['skips_recorded'][0]['seed'],initial)
            self.assertEqual(result['self_intersection'],0)
            self.assertTrue(all(v['intersection']==0 for v in result['excluded_sets'].values()))
            path=Path(td)/'test_seeds.json'; path.write_text(json.dumps(result))
            self.assertEqual(seeds.draw(dummy,excluded),result)
        with self.assertRaisesRegex(ValueError,'FREEZE.json is absent'):
            seeds.materialize(dummy,Path('/tmp/never-created-bench-seeds.json'),Path('/tmp/absent-bench-root'))

    def test_collision_with_previously_used_label_is_salted(self):
        dummy=sha256(b'dummy collision test protocol').hexdigest()
        def collide(data):
            return sha256(f'{dummy}|P1|0'.encode() if data==f'{dummy}|P2|0'.encode() else data)
        with tempfile.TemporaryDirectory() as td:
            excluded,_=seeds.exclusions(Path(td))
            with patch.object(seeds,'sha256',side_effect=collide):
                result=seeds.draw(dummy,excluded)
            self.assertNotEqual(result['strata']['P1'][0],result['strata']['P2'][0])
            self.assertTrue(any(x['stratum']=='P2' and x['reason']=='already-used' for x in result['skips_recorded']))
            path=Path(td)/'dummy.json';path.write_text(json.dumps(result))

    def test_prospective_schedule_is_only_frozen_file_values(self):
        # Dummy seed-file validation data; no world is constructed.
        dummy=sha256(b'dummy schedule protocol').hexdigest()
        with tempfile.TemporaryDirectory() as td:
            excluded,_=seeds.exclusions(Path(td))
            data=seeds.draw(dummy,excluded)
            schedule,population=cli._schedule('prospective',dict(_seed_schedule=data['strata']))
            self.assertEqual(len(schedule),2100)
            self.assertEqual(len(population),200)
            self.assertEqual({k:sum(k in v for v in schedule.values()) for k in seeds.PAIRS},dict.fromkeys(seeds.PAIRS,200))
            self.assertEqual({k:sum(k in v for v in schedule.values()) for k in seeds.CLASSES},dict.fromkeys(seeds.CLASSES,100))

    def test_seed_census_world_sampling_and_embedded_fields(self):
        import tarfile,io
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); analysis=root/'docs/analysis/exp002_heldout_test';analysis.mkdir(parents=True)
            (analysis/'rows.json').write_text(json.dumps([dict(world_id='123456',sampling_seed=987654)]))
            archive=root/'docs/runner/archives';archive.mkdir(parents=True)
            with tarfile.open(archive/'sample.tar.gz','w:gz') as stream:
                raw=json.dumps(dict(seed=876543,parameters=json.dumps(dict(seed=765432)))).encode()
                entry=tarfile.TarInfo('run/manifest.json');entry.size=len(raw);stream.addfile(entry,io.BytesIO(raw))
            excluded,sources=seeds.exclusions(root)
            self.assertEqual(excluded['exp002_exp001_pilot_seeds'],[123456,765432,876543,987654])
            self.assertEqual(len(sources),2)

    def test_protocol_roster_counts_and_dev_baseline_tie(self):
        cases=list(suite(13000))
        self.assertEqual(set(x.kind for x in cases),set(seeds.COUNTS)-{'jira_iid'})
        self.assertEqual(sum(x.kind=='invalid-corrupted-trace' for x in cases),3)
        rows=[dict(seed=13000,set='I1',epsilon=e,truth=dict(M=m),
                   methods={name:dict(predictions=dict(M=p)) for name in ('B2+','B3b')})
              for e in (0,.1) for m,p in (('harmful-coordination',True),('legitimate-cooperation',False))]
        self.assertEqual(strongest_baseline(rows)['strongest_baseline'],'B2+')
        rows[0]['seed']=1000000
        with self.assertRaisesRegex(ValueError,'DEV only'): strongest_baseline(rows)

    def test_method_crash_is_retained_for_all_methods(self):
        failures=[]
        instance=pair('P3',13000)[0]
        with patch.object(cli,'run_methods',side_effect=RuntimeError('injected crash')):
            result=cli.safe_methods({}, {}, instance, 'I1', failures)
        self.assertEqual(len(result),13)
        self.assertTrue(all(x['status']=='failed' for x in result.values()))
        self.assertEqual(failures[0]['seed'],13000)

    def test_dev_report_has_all_rqs_tables_and_failure_cells(self):
        path=Path('docs/enh/bench/dev_run/RESULTS_dev.json')
        if not path.exists(): self.skipTest('DEV report generated by full run')
        result=json.loads(path.read_text())
        self.assertTrue(result['development'])
        self.assertEqual(set(result['rq']),{f'RQ{i}' for i in range(1,7)} | {'RQ4b'})
        self.assertTrue(all(f'T{i}' in result['tables'] for i in range(1,11)))
        self.assertEqual(result['rq']['RQ6']['status'],'descriptive')
        self.assertEqual(set(result['rq']['RQ3']['by_epsilon']),{'0','0.1'})
        self.assertTrue(all(type(r['H']) is bool for data in result['tables']['T4']['strata'].values() for r in data['rows']))
        self.assertTrue(all(v['status'] in ('pass','fail','descriptive') for v in result['rq'].values()))
        self.assertIn('not a performance claim',result['circularity_disclosure'])

    def test_amended_report_criteria_and_twin_exhibit(self):
        path=Path('docs/enh/bench/dev_run/RESULTS_dev.json')
        if not path.exists(): self.skipTest('DEV report generated by full run')
        result=json.loads(path.read_text())
        self.assertEqual(result['rq']['RQ5']['primary_method'],'CCC-L-v1')
        self.assertIn('v0_comparison',result['rq']['RQ5'])
        self.assertEqual({r['method'] for r in result['tables']['T8']},{'CCC-L-v1'})
        self.assertEqual({r['method'] for r in result['tables']['T8_v0']},{'CCC-L-v0'})
        for row in result['tables']['T5b']:
            rate=row['over_attribution']['member_rate']
            self.assertEqual(row['method'],'B2+')
            self.assertEqual(row['pass_criterion'],rate>.5 if row['kind'] in ('P2','P3') else rate<=.05)
        self.assertIn('all four class rates >0.5',result['frozen_criteria']['RQ4'])
        twin=result['twin_exhibit']
        self.assertEqual((twin['kind'],twin['epsilon'],twin['seed']),('P2',0,13000))
        self.assertEqual(set(twin['members']),{'A','B'})
        self.assertEqual(json.loads(Path('docs/enh/bench/dev_run/RESULTS.json').read_text()),result)
        for member,data in twin['members'].items():
            self.assertEqual(set(data['outcome_means']),{'F','K','S','N','J','PF','PK'})
            self.assertEqual(data['ccc_v1_2_2_status'],'supported')
            self.assertEqual(data['ccc_status'],'supported')
            self.assertEqual(data['outcomes'],{a:v['Omean'] for a,v in data['outcome_means'].items()})
            self.assertEqual(data['i4_probe']['before'],'route')
            self.assertEqual(data['i4_probe']['after'],'route' if member=='A' else 'base')
            self.assertEqual(data['I4_probe']['before'],['route'])
            self.assertEqual(data['I4_probe']['after'],['route'] if member=='A' else ['base'])
