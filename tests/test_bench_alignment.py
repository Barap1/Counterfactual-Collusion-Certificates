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
from ccc.bench.methods import run_methods
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
        self.assertEqual(len(result),12)
        self.assertTrue(all(x['status']=='failed' for x in result.values()))
        self.assertEqual(failures[0]['seed'],13000)

    def test_dev_report_has_all_rqs_tables_and_failure_cells(self):
        path=Path('docs/enh/bench/dev_run/RESULTS_dev.json')
        if not path.exists(): self.skipTest('DEV report generated by full run')
        result=json.loads(path.read_text())
        self.assertTrue(result['development'])
        self.assertEqual(set(result['rq']),{f'RQ{i}' for i in range(1,7)})
        self.assertTrue(all(f'T{i}' in result['tables'] for i in range(1,11)))
        self.assertEqual(result['rq']['RQ6']['status'],'descriptive')
        self.assertEqual(set(result['rq']['RQ3']['by_epsilon']),{'0','0.1'})
        self.assertTrue(all(type(r['H']) is bool for data in result['tables']['T4']['strata'].values() for r in data['rows']))
        self.assertTrue(all(v['status'] in ('pass','fail','descriptive') for v in result['rq'].values()))
        self.assertIn('not a performance claim',result['circularity_disclosure'])
