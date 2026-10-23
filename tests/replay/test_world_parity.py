"""The CCC world is the real upstream system: setup and turn loop reproduce an archived upstream run.

The archived pilot (results/baselines, read-only) was produced by experiments/collusion/run.py
with a live model. Its tool events are the only state-changing outputs of the model (agents keep
no memory across turns), so feeding exactly those tool calls through the CCC world must reproduce
the archived blackboards and final rewards. No model is called.
"""

from __future__ import annotations

import json
import unittest
from collections import defaultdict

from tests.replay import _support as S


def setUpModule():
    S.block_network()


def tearDownModule():
    S.restore_network()


@unittest.skipUnless(S.pilot_run_dir(), "archived pilot not present")
class PilotParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from ccc.replay.engine import scripted_factory
        from ccc.replay.world import ColosseumWorld, WorldSpec

        run = S.pilot_run_dir()
        cls.run_config = json.loads((run / "run_config.json").read_text())
        cls.blackboards = json.loads((run / "blackboards.json").read_text())
        cls.final = json.loads((run / "final_summary.json").read_text())
        tool_events = json.loads((run / "tool_events.json").read_text())
        batch = json.loads((S.PILOT_BATCH / "config.json").read_text())
        cls.spec = WorldSpec.from_batch_config(batch, seed=cls.run_config["seed"])

        # group archived tool calls by (agent, phase, planning_round), in archived order
        queue = defaultdict(list)
        for e in tool_events:
            queue[(e["agent_name"], e["phase"], e["planning_round"])].append(
                {"name": e["tool_name"], "arguments": e["arguments"]})

        def policy_factory():
            def policy(call):
                if any(m.get("role") in ("assistant", "tool") for m in call.messages):
                    return {"content": "done"}
                return {"content": "", "tool_calls": queue.pop((call.agent, call.phase, call.planning_round), [])}
            return policy

        cls.queue = queue
        cls.world = ColosseumWorld(cls.spec, scripted_factory(policy_factory), branch_id="pilot_parity")
        cls.setup_state = cls.world.static_state()
        cls.world.run_turns()

    def test_setup_matches_archived_run_config(self):
        rc, st = self.run_config, self.setup_state
        self.assertEqual(st["colluders"], rc["colluders"])
        self.assertEqual(st["turn_order"], rc["agent_turn_order"])
        self.assertEqual(st["roles"], rc["roles"])
        self.assertEqual(st["secret_blackboard_id"], rc["secret_blackboard_id"])
        parts = {str(i): sorted(b.agents) for i, b in enumerate(self.world.protocol.megaboard.blackboards)}
        self.assertEqual(parts, rc["blackboard_participants"])
        self.assertEqual(self.world.prompt_variant, rc["prompt_variant"])

    def test_all_archived_tool_calls_consumed(self):
        self.assertEqual(dict(self.queue), {})
        self.assertEqual(self.world.errors, [])

    def test_blackboards_reproduced_exactly_except_ids_and_wallclock(self):
        mine = self.world.protocol.megaboard.blackboards
        self.assertEqual(len(mine), len(self.blackboards))
        for arch, b in zip(self.blackboards, mine):
            strip = lambda evs: [{k: v for k, v in e.items() if k not in ("id", "ts")} for e in evs]
            self.assertEqual(strip(b.logs), strip(arch["events"]), f"blackboard {arch['blackboard_id']}")

    def test_final_rewards_reproduced(self):
        fs = self.world.final_summary()
        for k in ("status", "joint_reward", "agent_rewards", "assignment", "tasks_done", "total_cost", "violations",
                  "coverage", "normalized_score"):
            self.assertEqual(fs[k], self.final[k], k)
        self.assertEqual(S.attempts, [])


class Determinism(unittest.TestCase):
    def test_two_source_runs_are_identical(self):
        from ccc.replay.engine import record_source_run, scripted_factory
        from ccc.replay.fixtures import signal_fixture

        fx = signal_fixture()
        a = record_source_run(fx.spec, scripted_factory(fx.policy_factory))
        b = record_source_run(fx.spec, scripted_factory(fx.policy_factory))
        self.assertEqual(a.world.state_hashes, b.world.state_hashes)
        self.assertEqual([r.request_sha256 for r in a.ledger.records], [r.request_sha256 for r in b.ledger.records])
        self.assertTrue(a.response_ids.isdisjoint(b.response_ids))  # every call is a new call

    def test_every_boundary_snapshot_restores(self):
        from ccc.replay.engine import NoCallClient, record_source_run, scripted_factory
        from ccc.replay.fixtures import signal_fixture
        from ccc.replay.world import ColosseumWorld

        fx = signal_fixture()
        src = record_source_run(fx.spec, scripted_factory(fx.policy_factory))
        self.assertEqual(sorted(src.world.snapshots), list(range(len(src.world.schedule) + 1)))
        for k, snap in src.world.snapshots.items():
            w = ColosseumWorld(fx.spec, lambda n, wd: NoCallClient(), branch_id=f"rt{k}")
            w.restore(snap)
            self.assertEqual(w.snapshot().dynamic, snap.dynamic, k)
            self.assertEqual(snap.dynamic_sha256, src.world.state_hashes[k], k)


if __name__ == "__main__":
    unittest.main()
