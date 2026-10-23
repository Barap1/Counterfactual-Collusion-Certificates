"""Mutation tests: each deliberate corruption must yield `invalid`/`failed`, never a valid score."""

from __future__ import annotations

import dataclasses
import json
import unittest

from tests.replay import _support as S


def setUpModule():
    S.block_network()


def tearDownModule():
    S.restore_network()


def _fixture():
    from ccc.replay.fixtures import run_fixture, signal_fixture

    return run_fixture(signal_fixture())


class LeakTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rep = _fixture()
        cls.cp = cls.rep.audit.checkpoint

    def test_V07_leak_through_summary_rerender_invalidates_K(self):
        from ccc.replay.engine import run_branch, scripted_factory
        from ccc.replay.interventions import leaky_summary_mask_hook

        br = run_branch(self.cp, "K", scripted_factory(self.rep.fixture.policy_factory),
                        hook=leaky_summary_mask_hook(self.cp.exposure), replicate_id="leaky")
        self.assertEqual(br.status, "invalid")
        v07 = next(c for c in br.checks if c.id == "V07")
        self.assertEqual(v07.status, "fail")
        self.assertTrue(all(h["surface"] == "messages[1].user" for h in v07.details["leaks"]))

    def test_V07_leak_through_sender_resend_invalidates_K(self):
        from ccc.replay.fixtures import run_fixture, signal_fixture

        rep = run_fixture(signal_fixture(resend_if_no_ack=True))
        K = rep.audit.branches["K"]
        self.assertEqual(rep.audit.branches["F"].status, "valid")
        self.assertEqual(K.status, "invalid", K.reasons)
        self.assertTrue(next(c for c in K.checks if c.id == "V07").details["leaks"])
        self.assertFalse(rep.audit.valid)

    def test_V07_leak_through_public_relay_invalidates_K(self):
        from ccc.replay.fixtures import run_fixture, signal_fixture

        rep = run_fixture(signal_fixture(relay_to_public=True))
        K = rep.audit.branches["K"]
        self.assertEqual(K.status, "invalid", K.reasons)
        leaks = next(c for c in K.checks if c.id == "V07").details["leaks"]
        self.assertTrue(leaks)

    def test_single_exposure_policy_scopes_the_leak_check(self):
        # Under "single" the original event is withheld only at the first exposure turn and is
        # re-rendered afterwards BY DESIGN; the declared horizon, not silence, bounds the claim.
        from ccc.replay.fixtures import run_fixture, signal_fixture

        rep = run_fixture(signal_fixture(repeated_exposure_policy="single"))
        K, ex = rep.audit.branches["K"], rep.audit.checkpoint.exposure
        self.assertEqual(K.status, "valid", K.reasons)
        later = [o for o in K.world.protocol.observations if o["agent"] == ex.receiver and o["turn_index"] > ex.mask_start]
        self.assertTrue(any(ex.event_id in {i for ids in o["visible_event_ids"].values() for i in ids} for o in later))


class CheckpointCorruption(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rep = _fixture()
        cls.cp = cls.rep.audit.checkpoint

    def _branches_blocked(self, cp):
        from ccc.replay.engine import audit, scripted_factory

        res = audit(cp, scripted_factory(self.rep.fixture.policy_factory))
        self.assertFalse(cp.valid)
        self.assertFalse(res.valid)
        for b in res.branches.values():
            self.assertEqual(b.status, "invalid")
            self.assertIsNone(b.outcomes)
            self.assertIsNone(b.world)  # nothing was even run
        return res

    def test_V06_checkpoint_after_exposure_is_flagged(self):
        from ccc.replay.engine import make_checkpoint

        sched = self.rep.source.world.schedule
        later = next(t.index for t in sched if t.agent == self.cp.exposure.receiver and t.index > self.cp.boundary)
        cp = make_checkpoint(self.rep.source, self.cp.exposure, boundary=later)
        v06 = next(c for c in cp.validation if c.id == "V06")
        self.assertEqual(v06.status, "fail")
        self.assertIn("already saw", " ".join(v06.details["problems"]))
        self._branches_blocked(cp)

    def test_V15_tampered_snapshot_bytes(self):
        from ccc.replay.engine import make_checkpoint

        bad = dataclasses.replace(self.cp.snapshot, dynamic=self.cp.snapshot.dynamic.replace(b'"assignment":[]',
                                                                                              b'"assignment":[["Mona","x"]]'))
        self.assertNotEqual(bad.dynamic, self.cp.snapshot.dynamic)
        cp = make_checkpoint(self.rep.source, self.cp.exposure, snapshot_override=bad)
        self.assertEqual(next(c for c in cp.validation if c.id == "V01").status, "fail")
        self._branches_blocked(cp)

    def test_V15_rehashed_but_altered_snapshot_caught_by_prefix_crosscheck(self):
        from ccc.replay.canonical import sha256_bytes, state_bytes
        from ccc.replay.engine import make_checkpoint

        d = json.loads(self.cp.snapshot.dynamic)
        d["megaboard"]["blackboards"][0]["logs"][0]["payload"]["message"] += " (edited)"
        data = state_bytes(d)
        bad = dataclasses.replace(self.cp.snapshot, dynamic=data, dynamic_sha256=sha256_bytes(data))
        self.assertTrue(bad.verify())  # internally consistent forgery
        cp = make_checkpoint(self.rep.source, self.cp.exposure, snapshot_override=bad)
        st = {c.id: c.status for c in cp.validation}
        self.assertEqual(st["V02"], "fail")
        self.assertEqual(st["V01"], "fail")  # next observation no longer matches the recorded one
        self._branches_blocked(cp)

    def test_V15_static_world_drift_refuses_restore(self):
        from ccc.replay.engine import scripted_factory
        from ccc.replay.world import ColosseumWorld, RestoreError

        other = dataclasses.replace(self.cp.spec, seed=self.cp.spec.seed + 1)
        w = ColosseumWorld(other, scripted_factory(self.rep.fixture.policy_factory), branch_id="drift")
        with self.assertRaises(RestoreError):
            w.restore(self.cp.snapshot)
        forged = dataclasses.replace(self.cp.snapshot, world_id=other.world_id)
        w2 = ColosseumWorld(other, scripted_factory(self.rep.fixture.policy_factory), branch_id="drift2")
        with self.assertRaises(RestoreError):  # tasks/costs/names differ -> static hash differs
            w2.restore(forged)

    def test_V02_prefix_request_mismatch_stops_reconstruction(self):
        from ccc.replay.engine import SourceRun, make_checkpoint

        src = self.rep.source
        recs = src.ledger.records
        saved = recs[2].request_sha256
        try:
            recs[2].request_sha256 = "0" * 64
            cp = make_checkpoint(SourceRun(src.spec, src.world), self.cp.exposure, strategy="prefix")
        finally:
            recs[2].request_sha256 = saved
        v02 = next(c for c in cp.validation if c.id == "V02")
        self.assertEqual(v02.status, "fail")
        self.assertIn("hash mismatch", v02.details["error"])


class BranchCorruption(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rep = _fixture()
        cls.cp = cls.rep.audit.checkpoint

    def test_V09_reused_source_responses_are_rejected(self):
        from ccc.replay.clients import ReusingClient
        from ccc.replay.engine import run_branch

        recorded = self.rep.source.ledger.at_or_after(self.cp.boundary)
        br = run_branch(self.cp, "K", lambda n, w: ReusingClient([r for r in recorded if r.agent == n]))
        self.assertEqual(br.status, "invalid")
        v09 = next(c for c in br.checks if c.id == "V09")
        self.assertEqual(v09.status, "fail")
        self.assertIn("reused from the source run", " ".join(v09.details["problems"]))

    def test_V18_failed_model_call_is_not_an_outcome(self):
        from ccc.replay.engine import run_branch

        class Boom:
            cache_mode, accepts_ccc_context = "fresh", True

            def init_context(self, s, u):
                return [{"role": "system", "content": s}, {"role": "user", "content": u}]

            def generate_response(self, input, params, ccc_context=None):  # noqa: A002
                raise TimeoutError("simulated provider timeout")

        br = run_branch(self.cp, "F", lambda n, w: Boom())
        self.assertEqual(br.status, "failed")
        self.assertIsNone(br.outcomes)
        self.assertTrue(any(r.status == "failed" for r in br.records))

    def test_impure_intervention_fails_branch(self):
        from ccc.replay.engine import run_branch, scripted_factory

        def mutating(agent, turn, view):
            for evs in view.values():
                evs.clear()
            return view, {"arm": "K"}

        br = run_branch(self.cp, "K", scripted_factory(self.rep.fixture.policy_factory), hook=mutating)
        self.assertEqual(br.status, "failed")
        self.assertIn("mutated its input", " ".join(br.reasons))

    def test_V08_validator_detects_broken_tool_pairing(self):
        from ccc.replay.validators import tool_protocol_errors

        good = next(r for r in self.rep.audit.branches["F"].records if r.request["messages"][-1].get("role") == "tool")
        self.assertEqual(tool_protocol_errors(good.request), [])
        dropped = {"messages": good.request["messages"][:-1], "params": good.request["params"]}
        self.assertTrue(tool_protocol_errors(dropped))
        swapped = json.loads(json.dumps(good.request))
        swapped["messages"][-1]["tool_call_id"] = "call_other"
        self.assertTrue(tool_protocol_errors(swapped))

    def test_wrong_reported_model_invalidates_branch(self):
        from ccc.replay.clients import ScriptedClient
        from ccc.replay.engine import run_branch

        class Rerouted(ScriptedClient):  # a provider silently serving another model
            def generate_response(self, input, params, ccc_context=None):  # noqa: A002
                resp, text = super().generate_response(input, params, ccc_context)
                resp["model"] = "someone/else:free"
                return resp, text

        br = run_branch(self.cp, "F", lambda n, w: Rerouted(self.rep.fixture.policy_factory(), nonce=f"rr/{n}"))
        self.assertEqual(br.status, "invalid")
        self.assertEqual(next(c for c in br.checks if c.id == "V-model").status, "fail")

    def test_tool_result_echo_is_detected(self):
        from ccc.replay.validators import check_tool_echo

        recs = self.rep.audit.branches["F"].records
        content = self.cp.exposure.content
        self.assertEqual(check_tool_echo(recs, [content]).status, "pass")
        bad = json.loads(json.dumps(next(r for r in recs if r.request["messages"][-1].get("role") == "tool").request))
        bad["messages"][-1]["content"] = json.dumps({"events": [{"payload": {"content": content}}]})
        from ccc.replay.recorder import RequestRecord
        rec = RequestRecord(**{**recs[0].__dict__, "request": bad, "seq": 999})
        self.assertEqual(check_tool_echo([rec], [content]).status, "fail")

    def test_every_prompt_render_check_catches_extra_event(self):
        from ccc.replay.engine import run_branch, scripted_factory
        from ccc.replay.interventions import sham_hook

        base = sham_hook()

        def sneaky(agent, turn, view):  # a "sham" that is not an identity re-render for one agent
            out, d = base(agent, turn, view)
            if agent != self.cp.exposure.receiver and out:
                k = sorted(out, key=int)[0]
                out[k] = out[k] + [{"id": "x", "agent": "SYSTEM", "kind": "context", "payload": {"message": "note"}}]
            return out, d

        br = run_branch(self.cp, "S", scripted_factory(self.rep.fixture.policy_factory), hook=sneaky)
        self.assertEqual(br.status, "invalid")
        self.assertEqual(next(c for c in br.checks if c.id == "V05b").status, "fail")

    def test_zz_no_network_attempts(self):
        self.assertEqual(S.attempts, [])


if __name__ == "__main__":
    unittest.main()
