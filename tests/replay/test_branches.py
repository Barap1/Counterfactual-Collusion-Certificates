"""F/S/K branch invariants on the deterministic coalition-signal fixture (real upstream objects,
scripted LLM, no network). Test IDs follow docs/spec/10_verification.md."""

from __future__ import annotations

import json
import unittest

from tests.replay import _support as S


def setUpModule():
    S.block_network()


def tearDownModule():
    S.restore_network()


class _Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from ccc.replay.fixtures import run_fixture, signal_fixture

        cls.rep = run_fixture(signal_fixture())
        cls.cp = cls.rep.audit.checkpoint
        cls.ex = cls.cp.exposure
        cls.F, cls.S, cls.K = (cls.rep.audit.branches[a] for a in ("F", "S", "K"))


class CheckpointTests(_Fixture):
    def test_V01_V02_V06_checkpoint_validation(self):
        st = {c.id: c.status for c in self.cp.validation}
        self.assertEqual(st, {"V06": "pass", "V01": "pass", "V02": "pass"}, [c.to_json() for c in self.cp.validation])
        self.assertTrue(self.cp.valid)

    def _assert_pre_exposure(self, cp, require_prior_turn):
        ex = cp.exposure
        obs = [o for o in self.rep.source.observations if o["agent"] == ex.receiver]
        seen = lambda o: ex.event_id in {i for ids in o["visible_event_ids"].values() for i in ids}
        before = [o for o in obs if o["turn_index"] < cp.boundary]
        if require_prior_turn:
            self.assertTrue(before, "receiver must have had an earlier turn for this check to bite")
        self.assertFalse(any(seen(o) for o in before))
        self.assertTrue(seen(next(o for o in obs if o["turn_index"] == cp.boundary)))
        self.assertLess(ex.posted_turn, cp.boundary)
        logs = [e["id"] for b in json.loads(cp.snapshot.dynamic)["megaboard"]["blackboards"] for e in b["logs"]]
        self.assertIn(ex.event_id, logs)  # in the checkpoint state ...
        self.assertEqual(self.rep.source.world.schedule[cp.boundary].agent, ex.receiver)  # ... receiver moves next

    def test_checkpoint_is_pre_exposure_and_earliest(self):
        self._assert_pre_exposure(self.cp, require_prior_turn=False)  # SIGNAL: receiver's first turn

    def test_pre_exposure_when_receiver_had_earlier_turns(self):
        from ccc.replay.engine import audit, candidate_exposures, make_checkpoint, scripted_factory

        ack = next(e for e in candidate_exposures(self.rep.source) if e.content.startswith("ACK from"))
        cp = make_checkpoint(self.rep.source, ack)
        self.assertTrue(cp.valid, [c.to_json() for c in cp.validation])
        self._assert_pre_exposure(cp, require_prior_turn=True)
        res = audit(cp, scripted_factory(self.rep.fixture.policy_factory))
        self.assertTrue(res.valid, {a: (b.status, b.reasons) for a, b in res.branches.items()})

    def test_manifest_fields(self):
        m = self.cp.manifest
        for k in ("snapshot_id", "static_sha256", "dynamic_sha256", "prefix_request_sha256", "scheduler_cursor",
                  "rng_records", "exposure", "code", "model_backend", "state_coverage_note", "restore_validation"):
            self.assertIn(k, m)
        self.assertEqual(m["scheduler_cursor"], self.cp.boundary)
        self.assertEqual(len(m["prefix_request_sha256"]), len(self.rep.source.ledger.before(self.cp.boundary)))

    def test_prefix_strategy_gives_identical_checkpoint(self):
        from ccc.replay.engine import make_checkpoint

        cp_b = make_checkpoint(self.rep.source, self.ex, strategy="prefix")
        self.assertTrue(cp_b.valid)
        self.assertEqual(cp_b.snapshot.snapshot_id, self.cp.snapshot.snapshot_id)


class ArmTests(_Fixture):
    def test_all_arms_valid(self):
        for b in (self.F, self.S, self.K):
            self.assertEqual(b.status, "valid", (b.arm, b.reasons, [c.to_json() for c in b.checks]))
        self.assertTrue(self.rep.audit.valid)

    def test_V04_sham_identity(self):
        v04 = next(c for c in self.rep.audit.cross_checks if c.id == "V04")
        self.assertEqual(v04.status, "pass", v04.details)

    def test_factual_and_sham_identical_state(self):
        # identical delivered content + deterministic policy => identical trajectory and final state
        self.assertEqual(self.F.world.snapshot().dynamic, self.S.world.snapshot().dynamic)
        self.assertEqual([r.request_sha256 for r in self.F.records], [r.request_sha256 for r in self.S.records])
        self.assertEqual(self.F.outcomes, self.S.outcomes)
        # ...while every response is a distinct fresh call
        self.assertTrue({r.response_id for r in self.F.records}.isdisjoint({r.response_id for r in self.S.records}))
        # S really went through the intervention path
        self.assertTrue(all(o["hook"] == "sham_identity" for o in self.S.world.protocol.observations))
        self.assertTrue(all(o["hook"] == "none" for o in self.F.world.protocol.observations))

    def test_F_reproduces_source_with_deterministic_policy(self):
        self.assertEqual(self.F.world.snapshot().dynamic, self.rep.source.world.snapshots[len(self.F.world.schedule)].dynamic)

    def test_V05_knockout_changes_only_intended_exposure(self):
        v05 = next(c for c in self.rep.audit.cross_checks if c.id == "V05")
        self.assertEqual(v05.status, "pass", v05.details)
        fo, ko = self.F.observation(self.ex.receiver, self.cp.boundary), self.K.observation(self.ex.receiver, self.cp.boundary)
        self.assertIn(self.ex.content, fo["contexts"][self.ex.blackboard_id])
        self.assertNotIn(self.ex.content, ko["contexts"][self.ex.blackboard_id])
        for bb in fo["contexts"]:
            if bb != self.ex.blackboard_id:
                self.assertEqual(fo["contexts"][bb], ko["contexts"][bb])
        self.assertEqual([d["event_id"] for d in ko["diff"]["removed"]], [self.ex.event_id])
        # underlying world untouched: the event still exists for everyone else
        self.assertIn(self.ex.event_id, ko["underlying_event_ids"][self.ex.blackboard_id])

    def test_knockout_downstream_is_regenerated(self):
        rcv = self.ex.receiver
        self.assertNotEqual(self.F.outcomes["assignment"][rcv], self.K.outcomes["assignment"][rcv])
        self.assertEqual(self.rep.expectations, {"F_equals_S_outcome": True, "K_changes_receiver_assignment": True})

    def test_V07_persistent_mask_holds_for_horizon(self):
        rcv_obs = [o for o in self.K.world.protocol.observations if o["agent"] == self.ex.receiver]
        self.assertGreaterEqual(len(rcv_obs), 2, "receiver must be re-rendered at least twice in the horizon")
        for o in rcv_obs:
            self.assertNotIn(self.ex.event_id, {i for ids in o["visible_event_ids"].values() for i in ids})
            self.assertIn(self.ex.event_id, {i for ids in o["underlying_event_ids"].values() for i in ids})
        self.assertEqual(next(c for c in self.K.checks if c.id == "V07").status, "pass")

    def test_V08_tool_protocol_legal_in_every_request(self):
        for b in (self.F, self.S, self.K):
            self.assertEqual(next(c for c in b.checks if c.id == "V08").status, "pass")
            self.assertTrue(any(r.request["messages"][-1].get("role") == "tool" for r in b.records))

    def test_V09_fresh_continuation(self):
        src_ids = self.rep.source.response_ids
        for b in (self.F, self.S, self.K):
            self.assertTrue(b.records)
            self.assertEqual(min(r.turn_index for r in b.records), self.cp.boundary)
            self.assertEqual({r.cache_mode for r in b.records}, {"fresh"})
            self.assertTrue({r.response_id for r in b.records}.isdisjoint(src_ids))
            calls = sum(a.client._inner.calls for a in b.world.env.agents)
            self.assertEqual(calls, len(b.records))  # every recorded response came from a new call

    def test_zz_no_network_attempts(self):
        self.assertEqual(S.attempts, [])


class IsolationTests(_Fixture):
    def test_V03_no_shared_mutable_state(self):
        from ccc.replay.validators import check_isolation

        r = check_isolation([self.F.world, self.S.world, self.K.world, self.rep.source.world], self.cp.snapshot,
                            self.cp.snapshot.dynamic)
        self.assertEqual(r.status, "pass", r.details)

    def test_V03_mutating_one_branch_cannot_change_another_or_the_source(self):
        from ccc.replay.engine import run_branch, scripted_factory

        fx = self.rep.fixture
        snap_before = self.cp.snapshot.dynamic
        src_final = self.rep.source.world.snapshot().dynamic
        k_final = self.K.world.snapshot().dynamic
        # vandalize F in place
        mb = self.F.world.protocol.megaboard
        mb.blackboards[0].logs.append({"id": "vandal", "kind": "communication", "agent": "X", "payload": {"content": "x"}})
        mb.blackboards[1].logs[0]["payload"]["message"] = "overwritten"
        self.F.world.env.assignment[self.ex.receiver] = "vandal"
        self.assertEqual(self.cp.snapshot.dynamic, snap_before)
        self.assertTrue(self.cp.snapshot.verify())
        self.assertEqual(self.rep.source.world.snapshot().dynamic, src_final)
        self.assertEqual(self.K.world.snapshot().dynamic, k_final)
        # a new K branch from the same checkpoint is unaffected
        k2 = run_branch(self.cp, "K", scripted_factory(fx.policy_factory), replicate_id="after_vandal")
        self.assertEqual(k2.world.snapshot().dynamic, k_final)

    def test_V03_interleaved_branches_equal_sequential(self):
        from ccc.replay.engine import scripted_factory
        from ccc.replay.interventions import receiver_mask_hook
        from ccc.replay.world import ColosseumWorld

        fac = scripted_factory(self.rep.fixture.policy_factory)
        wf = ColosseumWorld(self.cp.spec, fac, branch_id="iF")
        wk = ColosseumWorld(self.cp.spec, fac, branch_id="iK")
        wf.restore(self.cp.snapshot)
        wk.restore(self.cp.snapshot)
        wk.set_view_hook(receiver_mask_hook(self.ex), "receiver_mask")
        while wf.cursor < len(wf.schedule):
            wf.run_turns(wf.cursor + 1)
            wk.run_turns(wk.cursor + 1)
        self.assertEqual(wf.snapshot().dynamic, self.F.world.snapshot().dynamic)
        self.assertEqual(wk.snapshot().dynamic, self.K.world.snapshot().dynamic)

    def test_V10_replicates_are_distinct_calls(self):
        from ccc.replay.engine import run_branch, scripted_factory

        fac = scripted_factory(self.rep.fixture.policy_factory)
        r1 = run_branch(self.cp, "F", fac, replicate_id="1")
        r2 = run_branch(self.cp, "F", fac, replicate_id="2", other_response_ids={x.response_id for x in r1.records})
        self.assertEqual((r1.status, r2.status), ("valid", "valid"))
        self.assertTrue({x.response_id for x in r1.records}.isdisjoint({x.response_id for x in r2.records}))


if __name__ == "__main__":
    unittest.main()
