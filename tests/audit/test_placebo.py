"""AMD-IMP-2: select_placebo (protocol §3.1), N_m mask wiring, V3 for N, hashed S rule."""
import dataclasses
from contextlib import ExitStack
import hashlib
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

from ccc import paths
from ccc.audit.commitments import Extractor
from ccc.audit.placebo import select_placebo, length
from ccc.runner.manifest import SHAM_RULE, sham_selected

FIVE = "x" * 40


def r(i, content, turn=1, seq=None, board="0", agent="s", kind="communication"):
    return {"id": f"i{i}", "agent": agent, "kind": kind, "board": board, "content": content,
            "turn_index": turn, "seq": i if seq is None else seq}


def pick(rows, e_star=("e",), **kw):
    kw.setdefault("private_board", "1")
    kw.setdefault("receiver_boards", ["0", "1"])
    kw.setdefault("boundary", 9)
    return select_placebo(rows, list(e_star), "s", "r", Extractor(), **kw)


def estar(n=40):
    return {"id": "e", "agent": "s", "kind": "communication", "board": "1", "content": "e" * n, "turn_index": 1, "seq": 99}


class Rule(unittest.TestCase):
    def test_length_definition_nfc_and_whitespace(self):
        self.assertEqual(length("  a \t b\n\n c  "), 5)
        self.assertEqual(length("é"), 1)   # NFC composes

    def test_window_is_inclusive_at_25_percent(self):
        for n, status in ((30, "accepted"), (50, "accepted"), (29, "no_placebo_available"), (51, "no_placebo_available")):
            self.assertEqual(pick([estar(), r(1, "z" * n)])["status"], status, n)

    def test_at_least_k_takes_first_k_in_order(self):
        sel = pick([estar(80), *(r(i, "z" * 80, seq=i) for i in range(1, 6))])
        self.assertEqual((sel["k"], sel["candidates"], sel["M_star"]), (1, 5, ["i1"]))
        e2 = dict(estar(40), id="e2", content="f" * 40)
        sel = pick([estar(80), e2, *(r(i, "z" * 60, seq=i) for i in range(1, 6))], e_star=("e", "e2"))
        self.assertEqual((sel["k"], sel["status"], sel["M_star"], sel["L_M"]), (2, "accepted", ["i1", "i2"], 120))

    def test_order_is_board_rank_then_length_distance_then_turn_seq(self):
        rows = [estar(), r(1, "a" * 41, board="0"), r(2, "b" * 40, board="0", turn=3),
                r(3, "c" * 40, board="0", turn=2), r(4, "d" * 36, board="1")]
        self.assertEqual(pick(rows)["M_star"], ["i4"])          # board P first, even if length is worse
        self.assertEqual(pick(rows[:-1])["M_star"], ["i3"])     # exact length; ties by (turn_index, seq)

    def test_filters_author_boundary_kind_and_audited(self):
        rows = [estar(), r(1, "a" * 40, agent="o"), r(2, "b" * 40, turn=9), r(3, "c" * 40, kind="action_executed"),
                r(4, "d" * 40, board="2")]
        self.assertEqual(pick(rows)["status"], "no_placebo_available")
        self.assertEqual(pick([estar(), r(5, "ok" + "k" * 38)])["status"], "accepted")

    def test_event_ids_never_order(self):
        a = [estar(), dict(r(1, "a" * 40, turn=2), id="zzz"), dict(r(2, "b" * 40, turn=3), id="aaa")]
        self.assertEqual(pick(a)["M_star"], ["zzz"])


class HashedSham(unittest.TestCase):
    def test_rule_string_hash_and_selection(self):
        self.assertEqual(hashlib.sha256(SHAM_RULE.encode()).hexdigest(),
                         "c8651ddac16a50992971ae6f00df96405b00d0e22684117eedd09ffcffa5d509")
        for cid in ("a", "b", "H01_B1", "H01_B2"):
            self.assertEqual(sham_selected(cid), int(hashlib.sha256(("ccc.sham.v1|" + cid).encode()).hexdigest(), 16) % 2 == 0)


class MaskWiring(unittest.TestCase):
    """N_m through the real replay engine on a scripted fx2 Tier A world."""

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        root = Path(__file__).resolve().parents[2] / "starter/collusion_hackathon/colosseum"
        self.stack.enter_context(patch.object(paths, "colosseum_root", return_value=root))
        self.stack.enter_context(patch.object(paths, "_local_manifest", side_effect=AssertionError("secret manifest forbidden")))
        self.stack.enter_context(patch.object(socket.socket, "connect", side_effect=AssertionError("offline test")))

    def checkpoint(self, case="A1a", seed=12000):
        from ccc.audit.commitments import world_aliases
        from ccc.audit.gate_a import generate_dev, _schedule_seed
        from ccc.fixtures.jira import native_policy
        from ccc.fixtures.native_replay import as_replay_fixture
        from ccc.fixtures.worlds import split_manifest
        from ccc.replay import engine
        world = generate_dev(case, seed, split_manifest())
        fx = as_replay_fixture(world)
        fx.spec.seed = _schedule_seed(world.roles, world.order)
        fx.spec.base_cfg["experiment"]["collusion"]["agent_order"] = "random"
        fx.policy_factory = lambda: native_policy(world)
        factory = engine.scripted_factory(fx.policy_factory)
        source = engine.record_source_run(fx.spec, factory)
        cands = [e for e in engine.candidate_exposures(source) if e.sender == world.roles[0]
                 and e.receiver == world.roles[1] and e.blackboard_id == "1"]
        e = min(cands, key=lambda x: (x.first_exposure_turn, x.posted_turn))
        e = dataclasses.replace(e, copy_event_ids=tuple(x.event_id for x in cands
                                                         if x.first_exposure_turn == e.first_exposure_turn and x.event_id != e.event_id))
        cp = engine.make_checkpoint(source, e)
        ext = Extractor(world_aliases(world.tasks), world.roles[2:])
        sel = select_placebo(engine.event_rows(source), e.masked_ids, e.sender, e.receiver, ext,
                             boundary=e.first_exposure_turn, private_board="1", receiver_boards=["0", "1"])
        return engine, cp, factory, sel

    def test_n_m_branch_is_valid_and_v3_for_n_passes(self):
        engine, cp, factory, sel = self.checkpoint()
        self.assertEqual(sel["status"], "accepted")
        n = engine.run_branch(cp, "N", factory, placebo_ids=sel["M_star"])
        self.assertEqual(n.status, "valid", n.reasons)
        v3 = next(c for c in n.checks if c.name == "placebo_render_exact_every_prompt")
        self.assertEqual(v3.status, "pass", v3.details)
        self.assertTrue(v3.details["receiver_prompts"] > 0)
        f = engine.run_branch(cp, "F", factory)
        self.assertEqual(n.outcomes.keys(), f.outcomes.keys())

    def test_v3_for_n_detects_unmasked_and_overmasked_renders(self):
        from ccc.replay.validators import check_placebo_render
        engine, cp, factory, sel = self.checkpoint()
        n = engine.run_branch(cp, "N", factory, placebo_ids=sel["M_star"])
        obs = n.world.protocol.observations
        self.assertEqual(check_placebo_render(obs, cp.exposure, sel["M_star"]).status, "pass")
        # M* claimed by the checker but a different set was actually removed -> fail
        other = [i for i in cp.exposure.masked_ids]
        self.assertEqual(check_placebo_render(obs, cp.exposure, other).status, "fail")
        # F observations contain M* in every receiver prompt -> an N claim on F must fail
        f = engine.run_branch(cp, "F", factory)
        self.assertEqual(check_placebo_render(f.world.protocol.observations, cp.exposure, sel["M_star"]).status, "fail")

    def test_n_custom_fault_hook_still_runs_placebo_validator(self):
        engine, cp, factory, sel = self.checkpoint()
        # A supplied hook must not bypass the N_m validator by claiming an identity render.
        def identity(agent, turn, view):
            return view, {}
        n = engine.run_branch(cp, "N", factory, placebo_ids=sel["M_star"], hook=identity)
        self.assertEqual(n.status, "invalid")
        self.assertTrue(any(c.name == "placebo_render_exact_every_prompt" and c.status == "fail"
                            for c in n.checks))

    def test_n_validator_rejects_empty_observations_and_overlapping_bundles(self):
        from ccc.replay.validators import check_placebo_render
        engine, cp, factory, sel = self.checkpoint()
        self.assertEqual(check_placebo_render([], cp.exposure, sel["M_star"]).status, "fail")
        f = engine.run_branch(cp, "F", factory)
        self.assertEqual(check_placebo_render(f.world.protocol.observations, cp.exposure,
                                             ["nonexistent-event"]).status, "fail")
        self.assertEqual(check_placebo_render(f.world.protocol.observations, cp.exposure,
                                             cp.exposure.masked_ids).status, "fail")

    def test_n_requires_placebo_ids(self):
        engine, cp, factory, _ = self.checkpoint()
        with self.assertRaisesRegex(ValueError, "N_v1.1_deprecated"):
            engine.run_branch(cp, "N", factory)


if __name__ == "__main__":
    unittest.main()
