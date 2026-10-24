"""Native engine smoke/fault tests; no provider or secret manifest access."""
from contextlib import ExitStack
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

from ccc import paths
from ccc.audit.gate_a import generate_dev, native_case
from ccc.fixtures.worlds import split_manifest


class NativeIntegration(unittest.TestCase):
    def setUp(self):
        self.stack=ExitStack(); self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(paths,'colosseum_root',return_value=Path(__file__).resolve().parents[2]/'starter/collusion_hackathon/colosseum'))
        self.stack.enter_context(patch.object(paths,'_local_manifest',side_effect=AssertionError('secret manifest forbidden')))
        self.stack.enter_context(patch.object(socket.socket,'connect',side_effect=AssertionError('offline test')))
    def probe(self,case,seed=12001):
        return native_case(generate_dev(case,seed,split_manifest()))
    def test_native_sham_and_isolation(self):
        r=self.probe('A1a')
        self.assertTrue(r['eligible'])
        for c in r['checks']:
            if c['name'] in ('sham_identity','branch_isolation','targeted_exposure','neutral_exact_every_prompt'):
                self.assertEqual(c['status'],'pass',c)
        self.assertNotIn('runner_error',' '.join(r['CCC']['reasons']))
    def test_hidden_copy_invalid(self):
        r=self.probe('A6a'); self.assertEqual(r['CCC']['status'],'invalid')
        self.assertTrue(any('V05' in s or 'V3' in s for s in r['CCC']['reasons']))
    def test_cost_corruption_invalid(self):
        r=self.probe('A6c-K'); self.assertEqual(r['CCC']['status'],'invalid')
        self.assertTrue(any('static_task_cost' in s for s in r['CCC']['reasons']))
    def test_route_invalid(self): self.assertEqual(self.probe('A6e')['CCC']['status'],'invalid')
    def test_tool_fault_invalid(self): self.assertEqual(self.probe('A6f')['CCC']['status'],'invalid')
    def test_post_decision_has_no_fork(self):
        r=self.probe('A4a'); self.assertFalse(r['eligible'])
        self.assertEqual(r['CCC']['status'],'inconclusive')
    def test_benign_cooperation_abstains(self): self.assertNotEqual(self.probe('A2b')['CCC']['status'],'supported')
    def test_native_n_m_provenance_and_actual_counts(self):
        from ccc.audit.decision import validated_placebo
        r=native_case(generate_dev('A1a',12001,split_manifest()),full_replicates=True)
        self.assertEqual(r['actual_arm_counts'],{'F':4,'K':4,'S':2,'N':4})
        self.assertTrue(validated_placebo(r['branch_replicates'],r['placebo_selection']))
        self.assertEqual(r['CCC']['placebo_status'],'accepted')
