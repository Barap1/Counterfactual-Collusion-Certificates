"""ENG-003 SCI-002 v1 regressions. No inference, no writes to archived results."""
import copy
import dataclasses
import itertools
import json
from pathlib import Path
import random
import tempfile
import unittest

from tests.replay import _support as S


def setUpModule():
    S.block_network()


def tearDownModule():
    S.restore_network()


class Hardening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from ccc.replay.fixtures import run_fixture, signal_fixture
        cls.report = run_fixture(signal_fixture())
        cls.cp = cls.report.audit.checkpoint

    def test_shuffled_interleaved_replicates_and_protocol_selector(self):
        from ccc.replay.engine import audit_replicates, scripted_factory, select_protocol_exposure
        from unittest.mock import patch
        chosen = select_protocol_exposure(self.report.source)
        self.assertEqual(chosen.event_id, self.cp.exposure.event_id)
        with patch("ccc.replay.engine.run_branch") as branch:
            from ccc.replay.engine import BranchResult
            branch.side_effect = lambda cp, arm, fac, **kw: BranchResult(arm, kw["replicate_id"], None, [], None, "failed")
            result = audit_replicates(self.cp, None, replicate_ids=("x", "y", "z"), branch_order_seed=5)
            actual = [(c.kwargs["replicate_id"], c.args[1]) for c in branch.call_args_list]
            expected = [(rep, arm) for rep in ("x", "y", "z") for arm in ("F", "S", "K")]
            self.assertCountEqual(actual, expected)
            self.assertNotEqual(actual, expected)
            self.assertEqual(len(result), 3)
            self.assertTrue(all(c.kwargs["execution_metadata"]["schedule"] == actual for c in branch.call_args_list))
        with self.assertRaises(ValueError):
            audit_replicates(self.cp, None, replicate_ids=("x", "x"))

    def test_source_model_mismatch_fails_V6(self):
        from ccc.replay.engine import make_checkpoint
        record = self.report.source.ledger.records[0]
        saved = record.response["model"]
        try:
            record.response["model"] = "unexpected/model"
            checkpoint = make_checkpoint(self.report.source, self.cp.exposure)
            self.assertFalse(checkpoint.valid)
            self.assertEqual(next(c for c in checkpoint.validation if c.id == "V6").status, "fail")
        finally:
            record.response["model"] = saved

    def test_checkpoint_all_local_rngs_and_board_roundtrip(self):
        from ccc.replay.engine import scripted_factory
        from ccc.replay.world import ColosseumWorld
        fac = scripted_factory(self.report.fixture.policy_factory)
        a, b = [ColosseumWorld(self.cp.spec, fac, branch_id=str(i)) for i in range(2)]
        a.restore(self.cp.snapshot)
        b.restore(self.cp.snapshot)
        self.assertEqual(a.dynamic_state(), b.dynamic_state())
        self.assertEqual(a.protocol.megaboard.ccc_clock, b.protocol.megaboard.ccc_clock)
        self.assertEqual([a.env.rng.random() for _ in range(20)], [b.env.rng.random() for _ in range(20)])
        self.assertEqual([a.run_rng.random() for _ in range(20)], [b.run_rng.random() for _ in range(20)])
        caller = random.getstate()
        with a._rng_scope():
            draws_a = [random.random() for _ in range(20)]
        with b._rng_scope():
            draws_b = [random.random() for _ in range(20)]
        self.assertEqual(draws_a, draws_b)
        self.assertEqual(caller, random.getstate())
        b.protocol.megaboard.blackboards[0].logs[0]["payload"]["message"] += "changed"
        self.assertNotEqual(a.dynamic_state(), b.dynamic_state())

    def test_rng_consuming_client_prefix_reconstruction(self):
        from ccc.replay.engine import record_source_run, scripted_factory, make_checkpoint, candidate_exposures
        from ccc.replay.fixtures import signal_policy
        def factory():
            policy = signal_policy()
            def draw(call):
                random.random()
                return policy(call)
            return draw
        source = record_source_run(self.cp.spec, scripted_factory(factory))
        exposure = next(e for e in candidate_exposures(source) if e.content.startswith("SIGNAL:"))
        cp = make_checkpoint(source, exposure)
        self.assertTrue(cp.valid, [c.to_json() for c in cp.validation])

    def test_N_and_C_exact_every_call_and_original_indices(self):
        from ccc.replay.engine import run_branch, scripted_factory
        from ccc.replay.neutral import FILLERS
        from ccc.replay.prompt_diff import check_prompt_diffs
        for arm in ("K", "N", "C"):
            # Keep the historical filler regression under its explicit deprecated label.
            label = "N_v1.1_deprecated" if arm == "N" else arm
            branch = run_branch(self.cp, label, scripted_factory(self.report.fixture.policy_factory))
            self.assertEqual(branch.arm, label)
            self.assertEqual(branch.status, "valid", (arm, [c.to_json() for c in branch.checks]))
            audits = branch.world.prompt_audits
            self.assertEqual(len(audits), len(branch.records))
            self.assertEqual(check_prompt_diffs(arm, audits, self.cp.exposure).status, "pass")
            if arm == "N":
                for audit in audits:
                    if audit["agent"] != self.cp.exposure.receiver:
                        continue
                    raw = {e["id"]: e for es in audit["raw_events"].values() for e in es}
                    for events in audit["delivered_events"].values():
                        for event in events:
                            if event["id"] in self.cp.exposure.masked_ids:
                                self.assertEqual(len(event["payload"]["content"]), len(raw[event["id"]]["payload"]["content"]))
            if arm == "K":
                probe = next(a for a in audits if a["agent"] == self.cp.exposure.receiver)
                for board, events in probe["raw_events"].items():
                    for i, event in enumerate(events, 1):
                        if event["id"] not in self.cp.exposure.masked_ids:
                            from terrarium.blackboard import format_blackboard_events_for_prompt
                            block = format_blackboard_events_for_prompt([event])
                            block = f"[{i}]" + block[3:]
                            self.assertIn(block, probe["request"]["messages"][1]["content"])
        self.assertGreaterEqual(len(FILLERS), 5)
        self.assertFalse(any(any(c.isdigit() for c in filler) for filler in FILLERS))

    def test_independent_diff_catches_payload_change_and_renumbering(self):
        from ccc.replay.prompt_diff import check_prompt_diffs
        branch = self.report.audit.branches["K"]
        audits = branch.world.prompt_audits
        for mutate in ("extra", "system", "renumber", "params", "nonreceiver"):
            altered = copy.deepcopy(audits)
            probe = next(a for a in altered if a["agent"] == self.cp.exposure.receiver)
            if mutate == "extra":
                probe["request"]["messages"][1]["content"] += "summary of removed context"
            elif mutate == "system":
                probe["request"]["messages"][0]["content"] += "changed"
            elif mutate == "renumber":
                text = probe["request"]["messages"][1]["content"]
                probe["request"]["messages"][1]["content"] = text.replace("[1]", "[999]", 1)
            elif mutate == "params":
                probe["request"]["params"]["temperature"] = 0.99
            else:
                probe = next(a for a in altered if a["agent"] != self.cp.exposure.receiver)
                probe["request"]["messages"][1]["content"] += "changed"
            self.assertEqual(check_prompt_diffs("K", altered, self.cp.exposure).status, "fail", mutate)

    def test_channel_covers_new_sender_posts_but_preserves_actions(self):
        from ccc.replay.engine import run_branch, scripted_factory
        from ccc.replay.fixtures import run_fixture, signal_fixture
        report = run_fixture(signal_fixture(resend_if_no_ack=True))
        cp = report.audit.checkpoint
        k = report.audit.branches["K"]
        c = run_branch(cp, "C", scripted_factory(report.fixture.policy_factory))
        self.assertEqual((k.status, c.status), ("valid", "valid"))
        self.assertIn("resend_detected", next(x for x in k.checks if x.id == "V07").details["flags"])
        for audit in c.world.prompt_audits:
            if audit["agent"] == cp.exposure.receiver:
                for board, events in audit["delivered_events"].items():
                    self.assertFalse(any(e["kind"] == "communication" and e["agent"] == cp.exposure.sender
                                         for e in events if str(board) == str(cp.exposure.blackboard_id)))
                    raw_actions = [e for e in audit["raw_events"][board] if e["kind"] != "communication"]
                    self.assertTrue(all(e in events for e in raw_actions))

    def test_native_verbatim_and_paraphrase_resends_are_valid(self):
        from ccc.fixtures.jira import generate_jira
        from ccc.fixtures.native_replay import as_replay_fixture
        from ccc.replay.fixtures import run_fixture
        for variant in ("A5a-verbatim", "A5a-paraphrase"):
            report = run_fixture(as_replay_fixture(generate_jira(variant, 12000, profile="golden")))
            self.assertTrue(report.audit.valid, {a:b.reasons for a,b in report.audit.branches.items()})
            self.assertTrue(all(report.expectations.values()))
            v07 = next(c for c in report.audit.branches["K"].checks if c.id == "V07")
            if variant == "A5a-verbatim":
                self.assertIn("resend_detected", v07.details["flags"])
            # v1.2 (AMD-IMP-1): a generic-verb paraphrase ("route T") has an empty tuple set, so only
            # Jaccard applies; a paraphrase resend is a documented undetected semantic carrier.

    def test_mask_identical_rerender_on_every_message_surface_is_invalid(self):
        from ccc.replay.leak_scan import scan_leaks
        ex = self.cp.exposure
        base = next(r for r in self.report.audit.branches["K"].records if r.agent == ex.receiver)
        surfaces = ("memory", "summary", "megaboard", "blackboard", "tool", "assistant")
        for surface in surfaces:
            payload = copy.deepcopy(base.request)
            if surface in ("tool", "assistant"):
                payload["messages"].append({"role": surface, "content": ex.content, "tool_call_id": "echo"})
            else:
                payload["messages"][1]["content"] += f"\n=== {surface.upper()} ===\n{ex.content}"
            rec = dataclasses.replace(base, request=payload)
            check = scan_leaks(ex, [rec], self.report.audit.branches["K"].world.prompt_audits,
                               task_ids=tuple(self.report.source.world.env.tasks))
            # A newly generated assistant message is a post-fork carrier. Passive memory and
            # tool echoes are forbidden re-renders, independently of matching content elsewhere.
            self.assertEqual(check.status, "pass" if surface == "assistant" else "fail", surface)

    def test_current_assignment_and_summary_paraphrase_are_scanned(self):
        from ccc.replay.leak_scan import scan_leaks
        from ccc.replay.interventions import ExposureSpec
        ex = ExposureSpec("masked", "Ada", "Bea", "1", ("Ada", "Bea"), "I will take T1", 0, 1)
        base = next(r for r in self.report.audit.branches["K"].records if r.agent == self.cp.exposure.receiver)
        for section, content, status, flag in (
            ("CURRENT ASSIGNMENTS", "- Ada: T1", "pass", "state_redundant"),
            ("MEMORY", "Ada has committed to T1", "fail", None),
            ("SUMMARY", "Ada is taking T1", "fail", None),
        ):
            rec = dataclasses.replace(base, agent="Bea", turn_index=1,
                request={"messages": [{"role":"system","content":"hello"},
                {"role":"user","content":f"=== {section} ===\n{content}"}], "params":{}})
            check = scan_leaks(ex, [rec], task_ids=("T1",))
            self.assertEqual(check.status, status, check.details)
            if flag:
                self.assertIn(flag, check.details["flags"])
                self.assertEqual(check.details["first_leak"]["turn_index"], 1)

    def test_W_is_sum_and_unknown_duplicate_discrepancy_is_recorded(self):
        env = self.report.source.world.env
        names = env.agent_names
        choices = ["skip", *list(env.tasks)[:6], "unknown"]
        mismatches = 0
        for values in itertools.product(choices, repeat=4):
            assignment = dict(zip(names, values))
            joint, rewards = env._rewards(assignment)
            W = sum(rewards.values())
            coalition = [rewards[a] for a in self.report.source.world.colluders]
            outsiders = [rewards[a] for a in names if a not in self.report.source.world.colluders]
            self.assertAlmostEqual(W, sum(coalition) + sum(outsiders))
            if abs(W-joint) > 1e-9:
                mismatches += 1
                self.assertGreater(values.count("unknown"), 1)
                self.assertAlmostEqual(joint-W, 20*(values.count("unknown")-1))
        self.assertEqual(mismatches, 323)
        saved = env.assignment
        try:
            env.assignment = {a:"unknown" for a in names}
            outcome = self.report.source.world.outcomes()
            self.assertEqual(outcome["W"], sum(outcome["agent_rewards"].values()))
            self.assertEqual(outcome["joint_reward_minus_W"], 60)
        finally:
            env.assignment = saved

    def test_ledger_hash_chain_failed_attempt_and_no_overwrite(self):
        from ccc.replay.engine import run_branch, scripted_factory
        from ccc.replay.ledger import verify_branch
        with tempfile.TemporaryDirectory() as directory:
            fac = scripted_factory(self.report.fixture.policy_factory)
            branch = run_branch(self.cp, "K", fac, ledger_dir=directory)
            result = verify_branch(branch.ledger_path)
            self.assertEqual(result["records"], len(branch.records))
            again = run_branch(self.cp, "K", fac, ledger_dir=directory)
            self.assertNotEqual(branch.ledger_path, again.ledger_path)
            manifest = json.loads((Path(branch.ledger_path).parent/"run.json").read_text())
            self.assertEqual(manifest["model"]["resolved_id"], self.cp.spec.model_name)
            self.assertFalse(manifest["policy"]["live_inference_enabled"])
            self.assertEqual(self.cp.manifest["protocol_version"], "SCI-002 v1")
            for name in ("world_spec.json", "static_state.json", "prefix.jsonl"):
                self.assertTrue((Path(branch.ledger_path).parent/name).is_file())
            row = json.loads(Path(branch.ledger_path).read_text().splitlines()[0])
            self.assertEqual(row["model_resolved"], self.cp.spec.model_name)
            self.assertIsNone(row["api_cost_usd"])
            path = Path(branch.ledger_path).parent / row["response_artifact"]
            path.write_text("{}")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                verify_branch(branch.ledger_path)
            bad = dataclasses.replace(self.cp, validation=[dataclasses.replace(self.cp.validation[0], status="fail")])
            invalid = run_branch(bad, "F", fac, ledger_dir=directory)
            self.assertEqual(verify_branch(invalid.ledger_path)["records"], 0)
            self.assertEqual(json.loads((Path(invalid.ledger_path).parent/"branch.json").read_text())["status"], "invalid")
        with self.assertRaises(ValueError):
            run_branch(self.cp, "F", fac, ledger_dir=S.REPO/"results/baselines")


if __name__ == "__main__":
    unittest.main()
