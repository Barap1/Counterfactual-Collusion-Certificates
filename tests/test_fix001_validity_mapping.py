"""Independent runner-shaped regression inputs for FIX-001; no live data/calls."""
import json
from pathlib import Path
import tempfile
import unittest
from ccc.analysis.loaders import load
from ccc.analysis.pipeline import run


class ValidityMappingTests(unittest.TestCase):
    def analyze(self, style='engine', failure=None, missing=None, phase='synthetic_readiness', statuses=None):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); src = root/'input'; src.mkdir()
            def put(path, data):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(data))
            world = dict(id='FIX_B1', seed=101, regime='B1', split=phase)
            manifest = dict(schema_version='ccc.runner.manifest.v1', experiment_id='FIX-001-test',
                phase=phase, worlds=[world], arms=['F','K','S','N'], continuations_per_arm={'F':4,'K':4,'S':1,'N':4},
                model=dict(requested_id='offline', parameters={}), protocol_sha256='synthetic',
                policy=dict(new_out_of_pocket_usd=0, live_inference_enabled=False))
            put(src/'manifest.json', manifest); put(src/'WATCHDOG_EXIT.json', {})
            d = src/'worlds/FIX_B1/attempt_0001'
            put(d/'begin.json', dict(world=world, load_session='offline'))
            put(d/'checkpoint.json', dict(exposure=dict(sender='a',receiver='b')))
            # Engine IDs differ from the analysis protocol IDs; V08/V09 are
            # tool syntax / fresh sampling, not batch V8/V9 statistical gates.
            ids = ['V01','V02','V3','V09','V08','V6','V07'] if style=='engine' else [f'V{i}' for i in range(1,8)]
            branches=[]
            for arm in ('F','K'):
                for rep in range(4):
                    checks=[dict(id=cid, status='fail' if (cid==failure and arm=='F' and rep==0) else (statuses or {}).get(cid, 'pass'))
                            for cid in ids if cid!=missing]
                    o,c = (0,10) if arm=='F' else (3,9)
                    branches.append(dict(arm=arm,replicate=rep,status='valid',checks=checks,
                        outcomes=dict(status='complete',agent_rewards=dict(a=c,b=c,x=o,y=o),
                                      assignment=dict(a='a',b='b',x='x',y='y'))))
            put(d/'result.json',dict(status='complete',branches=branches,load_session='offline'))
            (d/'budget.jsonl').write_text(json.dumps(dict(event='attempt_end',model_resolved='offline'))+'\n')
            cp=load(src)[1][0]
            self.assertEqual(run(src,root/'output'),0)
            cert=json.loads((root/'output/checkpoint_certificates.json').read_text())[0]
            return cp,cert

    def test_engine_passes_establish_validity(self):
        cp,cert=self.analyze()
        self.assertTrue(cert['gates']['all_valid'])
        self.assertNotIn('validity_unestablished',cert['reasons'])
        self.assertEqual(cert['status'],'inconclusive')

    def test_canonical_passes_establish_validity(self):
        self.assertTrue(self.analyze(style='canonical')[1]['gates']['all_valid'])

    def test_zero_padded_restore_ids_normalize(self):
        cp,_=self.analyze()
        self.assertEqual([cp['v_checks'].get(k) for k in ('V1','V2')],['pass','pass'])

    def test_failures_dominate_later_passes(self):
        for cid in ('V01','V3','V09','V08','V6','V07'):
            with self.subTest(cid=cid):
                _,cert=self.analyze(failure=cid)
                self.assertFalse(cert['gates']['all_valid'])
                self.assertEqual(cert['status'],'invalid')

    def test_missing_checks_are_not_inferred_to_pass(self):
        _,cert=self.analyze(missing='V09')
        self.assertFalse(cert['gates']['all_valid'])
        self.assertIn('validity_unestablished',cert['reasons'])

    def test_legacy_runner_passes(self):
        self.assertTrue(self.analyze(phase='development',style='canonical')[1]['gates']['all_valid'])

    def test_not_applicable_is_recognized_without_inventing_a_pass(self):
        cp,cert=self.analyze(statuses={'V07':'not_applicable'})
        self.assertEqual(cp['v_checks']['V7'],'na')
        self.assertTrue(cert['gates']['all_valid'])

    def test_unknown_evidence_does_not_establish_validity(self):
        _,cert=self.analyze(statuses={'V09':'unknown'})
        self.assertFalse(cert['gates']['all_valid'])
        self.assertIn('validity_unestablished',cert['reasons'])
