"""Native replay bridge checks; reads neither secret manifests nor credentials."""

from pathlib import Path
import socket
import unittest
from unittest.mock import patch

from ccc import paths
from ccc.fixtures.jira import exact_oracle, generate_jira as _generate_jira
from ccc.fixtures.native_replay import as_replay_fixture


def generate_jira(*args, **kwargs):
    kwargs.setdefault("profile", "golden")
    return _generate_jira(*args, **kwargs)


class NativeReplayBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[2]/"starter/collusion_hackathon/colosseum"
        cls.guards=[patch.object(paths,"colosseum_root",return_value=root),
                    patch.object(paths,"_local_manifest",side_effect=AssertionError("secret manifest forbidden")),
                    patch.object(socket.socket,"connect",side_effect=AssertionError("network forbidden"))]
        for guard in cls.guards:
            guard.start()
        from ccc.replay.fixtures import run_fixture
        cls.execute=staticmethod(run_fixture)

    @classmethod
    def tearDownClass(cls):
        for guard in reversed(cls.guards):
            guard.stop()

    def test_native_valid_mechanisms_match_exact_oracle(self):
        for case in ("A1a","A1b","A2a","A2b","A2-boundary","A3a","A3b","A4b","A5a-paraphrase","A5b"):
            with self.subTest(case=case):
                world=generate_jira(case,12000)
                report=self.execute(as_replay_fixture(world))
                self.assertTrue(report.audit.valid, {a:b.reasons for a,b in report.audit.branches.items()})
                self.assertTrue(all(report.expectations.values()),report.expectations)
                for record in report.source.ledger.records:
                    text=str(record.request)
                    for marker in ("colluder", "secret coalition", "L_mech", "world_seed", case):
                        self.assertNotIn(marker,text)

    def test_native_verbatim_resend_exposes_mask_validator_limitation(self):
        # A post-fork resend is permitted under K. The current engine scans its
        # text as a leaked original. Preserve this mismatch rather than changing
        # the ground truth or treating it as successful redundant-case handling.
        world=generate_jira("A5a-verbatim",12000)
        self.assertEqual(exact_oracle(world)["L_mech"],"redundant")
        report=self.execute(as_replay_fixture(world))
        self.assertTrue(all(report.expectations.values()))
        self.assertFalse(report.audit.valid)
        self.assertEqual(report.audit.branches["K"].status,"invalid")
        self.assertIn("V07 mask_no_leak failed",report.audit.branches["K"].reasons)

    def test_native_bridge_refuses_unsupported_stress_or_stochastic_instances(self):
        from fractions import Fraction
        for world in (generate_jira("A6a",12000),generate_jira("A4a",12000),
                      generate_jira("A1a",12000,epsilon=Fraction(1,4))):
            with self.assertRaises(ValueError):
                as_replay_fixture(world)


if __name__ == "__main__":
    unittest.main()
