"""Unit tests: interventions are pure, receiver/horizon-scoped; leak heuristics behave as documented."""

from __future__ import annotations

import copy
import unittest

from tests.replay import _support as S


def setUpModule():
    S.block_network()


def tearDownModule():
    S.restore_network()


def _ex(policy="persistent", mask_end=None):
    from ccc.replay.interventions import ExposureSpec

    return ExposureSpec(event_id="e2", sender="A", receiver="B", blackboard_id="1", channel_participants=("A", "B"),
                        content="SIGNAL: claim T1 (coalition plan from A)", posted_turn=0, first_exposure_turn=3,
                        repeated_exposure_policy=policy, mask_end=mask_end)


VIEW = {"0": [{"id": "e0", "agent": "SYSTEM", "kind": "context", "payload": {"message": "hi"}}],
        "1": [{"id": "e1", "agent": "SYSTEM", "kind": "context", "payload": {"message": "secret"}},
              {"id": "e2", "agent": "A", "kind": "communication", "payload": {"content": "SIGNAL: claim T1 (coalition plan from A)"}},
              {"id": "e3", "agent": "A", "kind": "communication", "payload": {"content": "later"}}]}


class InterventionUnits(unittest.TestCase):
    def test_mask_is_pure_and_receiver_scoped(self):
        from ccc.replay.interventions import receiver_mask_hook

        hook, before = receiver_mask_hook(_ex()), copy.deepcopy(VIEW)
        out, diff = hook("B", 3, VIEW)
        self.assertEqual(VIEW, before)
        self.assertEqual([e["id"] for e in out["1"]], ["e1", "e3"])
        self.assertEqual(out["0"], VIEW["0"])
        self.assertEqual(diff["removed"], [{"blackboard_id": "1", "event_id": "e2", "rendered_index": 2,
                                            "later_indices_shift": 0}])
        for agent, turn in (("A", 3), ("B", 2)):  # other agent; before mask_start
            o, d = hook(agent, turn, VIEW)
            self.assertEqual(o, VIEW)
            self.assertFalse(d["active"])

    def test_horizon_policies(self):
        self.assertEqual([_ex().in_horizon(t) for t in (2, 3, 9)], [False, True, True])
        self.assertEqual([_ex("single").in_horizon(t) for t in (2, 3, 4)], [False, True, False])
        self.assertEqual([_ex(mask_end=5).in_horizon(t) for t in (5, 6)], [True, False])
        from ccc.replay.interventions import ExposureSpec
        with self.assertRaises(ValueError):
            ExposureSpec(**{**_ex().__dict__, "repeated_exposure_policy": "sometimes"})

    def test_sham_is_identity_copy(self):
        from ccc.replay.interventions import sham_hook

        out, diff = sham_hook()("B", 3, VIEW)
        self.assertEqual(out, VIEW)
        self.assertIsNot(out["1"], VIEW["1"])
        self.assertEqual(diff["removed"], [])

    def test_leak_heuristic(self):
        from ccc.replay.validators import find_content

        c = "please everyone claim the high priority backend implement task first and leave review for me"
        self.assertEqual(find_content(c, [("u", "x " + c.upper() + " y")])[0]["match"], "exact")
        para = "as discussed: please everyone claim the high priority backend implement task first and leave review for later"
        self.assertEqual(find_content(c, [("u", para)])[0]["match"], "shingle")
        self.assertEqual(find_content(c, [("u", "totally unrelated words about lunch")]), [])
        self.assertEqual(find_content("short", [("u", "[3] [action_executed] A id=e9 payload={}")], ["e9"])[0]["match"],
                         "event_id")


if __name__ == "__main__":
    unittest.main()
