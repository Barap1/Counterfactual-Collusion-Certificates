"""GA-DIAG regressions: public replay diagnostics, never oracle-driven decisions."""
import unittest
from unittest.mock import patch

from ccc.audit.gate_a import merge_replay_carriers, generate_dev, native_case
from ccc.fixtures.worlds import split_manifest
from tests.audit import test_native


class DiagnosisIntegration(unittest.TestCase):
    setUp = test_native.NativeIntegration.setUp
    probe = test_native.NativeIntegration.probe
    def test_v07_carriers_reach_decision(self):
        result = self.probe('A5a-verbatim', 12000)
        flags = {flag for c in result['checks'] if c['id'] == 'V07'
                 for flag in c['details'].get('flags', [])}
        self.assertTrue(flags)
        self.assertLessEqual(flags, set(result['CCC']['flags']))
        self.assertEqual(result['CCC']['status'], 'inconclusive')
        self.assertIn('not_identifiable_redundant', result['CCC']['reasons'])

    def test_inactive_single_mask_matches_clean_k(self):
        from ccc.replay import engine
        original = engine.run_branch
        count = 0
        for stratum in ('crossed', 'naturalistic'):
            for seed in (12000, 12002, 12004, 12012, 12014):
                with self.subTest(stratum=stratum, seed=seed):
                    captured = []
                    def capture(cp, arm, *args, **kwargs):
                        branch = original(cp, arm, *args, **kwargs)
                        if arm == 'K':
                            captured.append((cp, branch))
                        return branch
                    offset = seed - split_manifest()['development']['world_seeds']['start']
                    base = 'A1a' if bool((offset % 2) ^ ((offset // 2) % 2)) else 'A3a'
                    world = generate_dev('A6b', seed, split_manifest(), stratum=stratum, invalid_base=base)
                    with patch.object(engine, 'run_branch', side_effect=capture):
                        result = native_case(world)
                    self.assertFalse(result['fault_exercised'])
                    self.assertEqual(len(captured), 2)
                    (cp, clean), (_, fault) = captured
                    self.assertEqual(fault.status, 'valid')
                    self.assertEqual([r.request_sha256 for r in clean.records],
                                     [r.request_sha256 for r in fault.records])
                    self.assertEqual(clean.outcomes, fault.outcomes)
                    self.assertEqual(len([o for o in fault.world.protocol.observations
                                          if o['agent'] == cp.exposure.receiver]), 1)
                    count += 1
        self.assertEqual(count, 10)
        print('GA-DIAG inactive A6b: 10/10 valid; clean K request hashes and outcomes identical; one receiver observation each')

    def test_merge_keeps_flags_and_provenance_without_mutation(self):
        found = {'post_fork_carrier': {'turn': 3}}
        checks = [{'id': 'V07', 'details': {'flags': ['resend_detected', 'unknown'],
                   'carriers': [{'flag': 'resend_detected', 'event_id': 'new-post'}]}}]
        merged = merge_replay_carriers(found, checks)
        self.assertEqual(set(merged), {'post_fork_carrier', 'resend_detected'})
        self.assertEqual(merged['resend_detected']['carriers'][0]['event_id'], 'new-post')
        self.assertEqual(found, {'post_fork_carrier': {'turn': 3}})
