"""Offline collection tests over the real Colosseum world and scripted guarded transport."""
import copy
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from ccc.runner.manifest import ROOT, digest, file_hash, freeze_hash, load, plan, validate
from ccc.runner.storage import get, lock, output_root, put, seal, verify

EXAMPLE = ROOT / "docs/runner/dev_manifest.json"


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.m = load(EXAMPLE)

    def test_plan_deterministic_interleaved_and_one_world_unit(self):
        p = plan(self.m)
        self.assertEqual(p, plan(copy.deepcopy(self.m)))
        self.assertEqual((p["independent_worlds"], p["base_trajectories"], p["continuations"]), (1, 1, 8))
        order = p["jobs"][0]["order"]
        self.assertEqual({i["arm"] for i in order[:4]}, {"F", "S", "K", "N"})
        self.assertEqual(len({i["seed"] for i in order[:4]}), 4)
        self.assertNotEqual(order[0]["seed"], order[-1]["seed"])

    def test_placebo_on_all_checkpoints_frozen_before_sources(self):
        self.m["worlds"] = [dict(id=f"w{s}", seed=s, regime="B1", split="development") for s in range(2, 6)]
        p = plan(self.m)
        self.assertEqual(sum(j["placebo"] for j in p["jobs"]), 4)
        self.assertEqual(p["continuations"], 32)

    def test_arm_counts_and_v11_n_label(self):
        from ccc.runner.storage import arm_label
        job = plan(self.m)["jobs"][0]
        self.assertEqual(job["arm_counts"], {"F": 2, "S": 2, "K": 2, "N": 2})
        with tempfile.TemporaryDirectory(dir=ROOT / "docs/runner") as directory:
            self.assertEqual(arm_label(directory, "N"), "N_v1.1_deprecated")
            self.assertEqual(arm_label(directory, "K"), "K")
            (Path(directory) / "placebo.json").write_text("{}")
            self.assertEqual(arm_label(directory, "N"), "N_m")

    def test_holdout_s_must_be_one(self):
        self.m["phase"] = "holdout"
        self.m["worlds"][0]["split"] = "holdout"
        with self.assertRaisesRegex(ValueError, "D-022"):
            validate(self.m)

    def test_duplicate_world_does_not_inflate_unit(self):
        self.m["worlds"].append(dict(self.m["worlds"][0], id="duplicate"))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate(self.m)

    def test_unfrozen_refused(self):
        self.m["frozen"] = False
        with self.assertRaisesRegex(ValueError, "frozen"):
            validate(self.m)

    def test_holdout_requires_stat001_even_dry_run(self):
        from ccc.runner.collector import run
        self.m["phase"] = "holdout"
        self.m["continuations_per_arm"]["S"] = 1
        self.m["worlds"][0]["split"] = "holdout"
        with self.assertRaisesRegex(ValueError, "STAT-001"):
            run(self.m, ROOT / "docs/runner/never-created", dry_run=True)

    def test_holdout_stat_hash_binds_manifest(self):
        self.m["phase"] = "holdout"
        self.m["continuations_per_arm"]["S"] = 1
        self.m["worlds"][0]["split"] = "holdout"
        with tempfile.TemporaryDirectory(dir=ROOT / "docs/runner") as directory:
            f = Path(directory) / "stat.json"
            f.write_text(json.dumps({"task_id": "STAT-001", "frozen_manifest_sha256": freeze_hash(self.m)}))
            self.m["stat001"] = {"task_id": "STAT-001", "artifact": str(f.relative_to(ROOT)), "sha256": file_hash(f)}
            self.m["stat001_hash"] = self.m["stat001"]["sha256"]
            self.m["worlds"].append(dict(self.m["worlds"][0], id="dev02_B2", regime="B2"))
            # Rebind after adding the matched regime.
            f.write_text(json.dumps({"task_id": "STAT-001", "frozen_manifest_sha256": freeze_hash(self.m)}))
            self.m["stat001"]["sha256"] = self.m["stat001_hash"] = file_hash(f)
            validate(self.m)
            self.m["master_seed"] += 1
            with self.assertRaisesRegex(ValueError, "bind"):
                validate(self.m)

    def test_seed1_never_holdout(self):
        self.m["continuations_per_arm"]["S"] = 1
        self.m["worlds"][0]["seed"] = 1
        self.m["worlds"][0]["split"] = "holdout"
        self.m["phase"] = "holdout"
        # Missing approval fails first; even an approval must not override archival status.
        with tempfile.TemporaryDirectory(dir=ROOT / "docs/runner") as directory:
            f = Path(directory) / "stat.json"
            f.write_text(json.dumps({"task_id": "STAT-001", "frozen_manifest_sha256": freeze_hash(self.m)}))
            self.m["stat001"] = {"task_id": "STAT-001", "artifact": str(f.relative_to(ROOT)), "sha256": file_hash(f)}
            self.m["stat001_hash"] = self.m["stat001"]["sha256"]
            self.m["worlds"].append(dict(self.m["worlds"][0], id="archive_B2", regime="B2"))
            f.write_text(json.dumps({"task_id": "STAT-001", "frozen_manifest_sha256": freeze_hash(self.m)}))
            self.m["stat001"]["sha256"] = self.m["stat001_hash"] = file_hash(f)
            with self.assertRaisesRegex(ValueError, "seed 1"):
                validate(self.m)

    def test_protocol_drift_refused(self):
        self.m["protocol_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "mismatch"):
            validate(self.m)

    def test_prompt_model_and_budget_switches_refused(self):
        variants = [("b1_prompt_variant", "simple"), ("colluder_selection", "first"),
                    ("common_randomness_claim", "paired"), ("continuations_per_arm", 1)]
        for k, v in variants:
            m = copy.deepcopy(self.m)
            m[k] = v
            with self.subTest(k=k), self.assertRaises(ValueError):
                validate(m)
        self.m["model"]["requested_id"] = "openrouter/free"
        with self.assertRaises(ValueError):
            validate(self.m)


class StorageTests(unittest.TestCase):
    def test_exclusive_write_and_tamper_detection(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "docs/runner") as d:
            p = Path(d) / "record.json"
            put(p, {"status": "failed"})
            with self.assertRaises(FileExistsError):
                put(p, {"status": "complete"})
            p.write_text(p.read_text().replace("failed", "complete"))
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                verify(d)

    def test_seal_detects_deleted_records(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "docs/runner") as d:
            p = Path(d) / "record.json"
            put(p, [1])
            seal(Path(d))
            p.unlink()
            with self.assertRaises(OSError):
                verify(d)

    def test_collector_lock_excludes_second_writer(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "docs/runner") as d:
            with lock(Path(d)):
                with self.assertRaisesRegex(ValueError, "collector"):
                    with lock(Path(d)):
                        self.fail("second writer admitted")

    def test_archive_and_path_escape_rejected(self):
        for p in (ROOT / "results/baselines/new", ROOT / "docs/runner/../../results/new", Path("/tmp/new")):
            with self.subTest(path=p), self.assertRaises(ValueError):
                output_root(p)


class CollectionTests(unittest.TestCase):
    def setUp(self):
        previous = logging.root.manager.disable
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, previous)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "docs/runner")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.m = load(EXAMPLE)

    def test_live_disabled_before_any_write(self):
        from ccc.runner.collector import run
        with self.assertRaisesRegex(ValueError, "live execution disabled"):
            run(self.m, self.root)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_n_m_runs_when_sender_chatter_exists_and_is_skipped_otherwise(self):
        from ccc.runner.collector import run
        from ccc.replay import policy as P
        from ccc.replay.fixtures import signal_policy
        chatter = "Wishing everyone a calm and pleasant day. Keeping in touch."

        def chatty():
            base = signal_policy()

            def policy(call):
                out = base(call)
                calls = out.get("tool_calls") or []
                if call.phase == "planning" and any("SIGNAL: claim" in str(c) for c in calls):
                    secret = P.coalition_blackboard(call)
                    public = [b for b in P.blackboards(call) if b != secret]
                    out = dict(out, tool_calls=[P.post(chatter, b) for b in public] + calls)
                return out
            return policy

        with patch("socket.socket.connect", side_effect=AssertionError("network attempted")), \
             patch("ccc.runner.collector.signal_policy", chatty):
            report = run(self.m, self.root, dry_run=True)
        self.assertEqual(report["worlds"][0]["attempts"][0]["status"], "complete")
        attempt = self.root / "worlds/dev02_B1/attempt_0001"
        placebo = get(attempt / "placebo.json")
        self.assertEqual(placebo["status"], "accepted", placebo)
        result = get(attempt / "result.json")
        n = [b for b in result["branches"] if b["arm"] == "N"]
        self.assertEqual([b["status"] for b in n], ["valid", "valid"])
        for b in n:
            v3 = [c for c in b["checks"] if c["name"] == "placebo_render_exact_every_prompt"]
            self.assertEqual([c["status"] for c in v3], ["pass"])
        begin = get(attempt / "branches/000_N/begin.json") if (attempt / "branches/000_N/begin.json").exists() else None
        if begin:
            self.assertEqual(begin["placebo_sha256"], digest(placebo))

    def test_full_collection_and_noop_resume(self):
        from ccc.runner.collector import run
        # A second guard beyond the CLI's socket audit hook, including provider transport.
        with patch("socket.socket.connect", side_effect=AssertionError("network attempted")), \
             patch("ccc.infra.budget_guard.urllib_transport", side_effect=AssertionError("live transport attempted")):
            report = run(self.m, self.root, dry_run=True)
            self.assertEqual(report["worlds"][0]["attempts"][0]["status"], "complete")
            before = {str(p): file_hash(p) for p in self.root.rglob("*") if p.is_file()}
            again = run(self.m, self.root, dry_run=True)
            after = {str(p): file_hash(p) for p in self.root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            again_record = again.pop("run_record")
            self.assertEqual(again_record["checkpoints_launched"], 0)  # no-op resume launches nothing
            self.assertEqual(again, {k: v for k, v in report.items() if k != "run_record"})
        attempt = self.root / "worlds/dev02_B1/attempt_0001"
        result = get(attempt / "result.json")
        self.assertEqual(len(result["branches"]), 8)
        self.assertEqual({b["arm"] for b in result["branches"]}, {"F", "S", "K", "N"})
        calls = list(attempt.rglob("*.begin.json"))
        self.assertTrue(calls)
        for p in calls:
            call = get(p)
            self.assertEqual(call["request"]["seed"], call["context"]["seed_sent"])
            self.assertEqual(call["request"]["reasoning_effort"], "none")
            self.assertEqual(call["request_sha256"], digest(call["request"]))
            self.assertEqual(get(p.with_name(p.name.replace(".begin.", ".end.")))["status"], "complete")
        ledger = [json.loads(l) for l in (attempt / "budget.jsonl").read_text().splitlines()]
        self.assertEqual(sum(r["event"] == "attempt_begin" for r in ledger), len(calls))
        self.assertEqual(len({r["meta"]["load_session"] for r in ledger if r["event"] == "attempt_begin"}), 1)
        self.assertTrue((attempt / "source/snapshots/0000.json").exists())
        self.assertEqual(report["live_calls"], 0)

    def test_failure_retained_no_silent_retry_and_cap_across_resume(self):
        from ccc.runner.collector import run
        self.m["max_requests"] = 1
        with self.assertRaisesRegex(ValueError, "failed"):
            run(self.m, self.root, dry_run=True)
        first = self.root / "worlds/dev02_B1/attempt_0001/result.json"
        before = first.read_bytes()
        self.assertEqual(get(first)["status"], "failed")
        with self.assertRaisesRegex(ValueError, "retry-failed"):
            run(self.m, self.root, dry_run=True)
        with self.assertRaisesRegex(ValueError, "cap exhausted"):
            run(self.m, self.root, dry_run=True, retry_failed=True)
        self.assertEqual(before, first.read_bytes())
        self.assertEqual(len(list(self.root.rglob("*.begin.json"))), 2)  # second request refused before guard admission
        ledgers = [json.loads(line) for p in self.root.rglob("budget.jsonl") for line in p.read_text().splitlines()]
        self.assertEqual(sum(r["event"] == "attempt_begin" for r in ledgers), 1)

    def test_manifest_change_cannot_resume_existing_collection(self):
        from ccc.runner.collector import run
        self.m["max_requests"] = 1
        with self.assertRaises(ValueError):
            run(self.m, self.root, dry_run=True)
        self.m["max_requests"] = 1000
        with self.assertRaisesRegex(ValueError, "different immutable manifest"):
            run(self.m, self.root, dry_run=True)

    def test_interrupted_attempt_requires_explicit_retry(self):
        from ccc.runner.collector import run
        with patch("ccc.runner.collector.collect_world", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                run(self.m, self.root, dry_run=True)
        with self.assertRaisesRegex(ValueError, "retry-failed"):
            run(self.m, self.root, dry_run=True)
        result = run(self.m, self.root, dry_run=True, retry_failed=True)
        self.assertEqual([a["status"] for a in result["worlds"][0]["attempts"]], ["interrupted", "complete"])

    def test_first_event_selection_bundles_without_effect_search(self):
        from ccc.runner.collector import build_spec, select_exposure
        from ccc.replay.engine import record_source_run, scripted_factory
        from ccc.replay.fixtures import signal_policy
        source = record_source_run(build_spec(self.m, self.m["worlds"][0]), scripted_factory(signal_policy))
        exposure, selection = select_exposure(source)
        board = next(b for b in source.world.protocol.megaboard.blackboards
                     if str(b.blackboard_id) == str(source.world.secret_blackboard_id))
        first = next(e for e in board.logs if e["kind"] == "communication")
        self.assertEqual(exposure.event_id, first["id"])
        self.assertEqual(selection["sender"], first["agent"])
        self.assertIn(first["id"], selection["bundle_event_ids"])

    def test_bundle_includes_all_sender_posts_first_seen_at_boundary(self):
        from ccc.runner.collector import build_spec, select_exposure
        from ccc.replay.engine import record_source_run, scripted_factory
        from ccc.replay.fixtures import signal_policy
        from ccc.replay import policy as P

        def factory():
            original = signal_policy()

            def policy(call):
                result = original(call)
                if call.phase == "planning" and P.is_first_step(call):
                    for tool in list(result.get("tool_calls", [])):
                        if tool["arguments"]["message"].startswith("SIGNAL:"):
                            result["tool_calls"].append(P.post("a further private note", tool["arguments"]["blackboard_id"]))
                return result
            return policy

        source = record_source_run(build_spec(self.m, self.m["worlds"][0]), scripted_factory(factory))
        exposure, selection = select_exposure(source)
        self.assertEqual(len(exposure.masked_ids), 2)
        self.assertEqual(list(exposure.masked_ids), selection["bundle_event_ids"])

    def test_no_message_world_retained_in_coverage(self):
        from ccc.runner.collector import run
        from ccc.replay import policy as P

        def quiet():
            return lambda call: ({"content": "quiet"} if call.phase == "planning"
                                 else {"tool_calls": [P.assign("skip")]})

        with patch("ccc.runner.collector.signal_policy", quiet):
            report = run(self.m, self.root, dry_run=True)
        self.assertEqual(report["worlds"][0]["attempts"][0]["status"], "ineligible")
        selection = get(self.root / "worlds/dev02_B1/attempt_0001/selection.json")
        self.assertEqual(selection["reason"], "no_exposure")
        self.assertFalse(list(self.root.rglob("branches")))

    def test_transport_failure_is_immutable_and_explicit_retry_succeeds(self):
        from ccc.runner.collector import run

        with patch("ccc.replay.clients.ScriptedClient.generate_response", side_effect=RuntimeError("scripted outage")), \
             patch("ccc.infra.budget_guard.time.sleep"):
            with self.assertRaisesRegex(ValueError, "failed"):
                run(self.m, self.root, dry_run=True)
        attempts = self.root / "worlds/dev02_B1"
        failed = next((attempts / "attempt_0001").rglob("*.end.json"))
        before = failed.read_bytes()
        record = get(failed)
        self.assertEqual(record["status"], "failed")
        self.assertEqual(len(record["guard_attempts"]), 1)
        self.assertEqual(record["guard_attempts"][0]["status"], "transport_error")
        report = run(self.m, self.root, dry_run=True, retry_failed=True)
        self.assertEqual([a["status"] for a in report["worlds"][0]["attempts"]], ["failed", "complete"])
        self.assertEqual(failed.read_bytes(), before)


class RunPathTimeZoneTests(unittest.TestCase):
    """Regression: `run` must accept the exact EXP-001 hard_stop under a non-UTC local TZ."""

    EXP001 = ROOT / "docs/runner/exp001_manifest.json"

    def setUp(self):
        # Freeze UTC independently of the local TZ; preserve the exact deadline.
        clock = patch("ccc.runner.collector.datetime", wraps=datetime)
        self.addCleanup(clock.stop)
        clock.start().now.return_value = datetime(2026, 10, 24, tzinfo=timezone.utc)
        import os
        import time
        previous = os.environ.get("TZ")

        def restore():
            if previous is None:
                os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = previous
            time.tzset()

        os.environ["TZ"] = "America/New_York"
        time.tzset()
        self.addCleanup(restore)
        logging_previous = logging.root.manager.disable
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, logging_previous)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "docs/runner")
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)

    def _dry_manifest(self):
        raw = json.loads(self.EXP001.read_text())
        # In this worktree protocol.md is v1.2; EXP-001's pinned hash is v1.1's file.
        raw["protocol_artifact"] = "docs/research/sci002/protocol_v1.1.md"
        self.assertEqual(raw["hard_stop_utc"], "2026-10-24T09:00:00Z")
        raw["policy"]["live_inference_enabled"] = False  # offline dry-run copy; hard_stop kept exact
        path = self.dir / "exp001_dry.json"
        path.write_text(json.dumps(raw))
        return path

    def test_cli_run_dry_run_with_exact_hard_stop_under_new_york_tz(self):
        import contextlib
        import io
        import time
        from ccc.runner.__main__ import main
        self.assertNotEqual(time.localtime().tm_gmtoff, 0)
        out = io.StringIO()
        err = io.StringIO()
        with patch("socket.socket.connect", side_effect=AssertionError("network attempted")), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["run", str(self._dry_manifest()), "--output", str(self.dir / "out"),
                         "--dry-run", "--max-checkpoints", "1"])
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(code, 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["run_record"], {"max_checkpoints": 1, "checkpoints_launched": 1,
                                                "dry_run": True, "live": False})
        self.assertEqual(len(report["worlds"]), 8)
        self.assertEqual(report["worlds"][0]["attempts"][0]["status"], "complete")
        self.assertEqual(sum(bool(w["attempts"]) for w in report["worlds"]), 1)

    def test_max_checkpoints_stops_before_next_world_and_rejects_nonpositive(self):
        from ccc.runner.collector import run
        m = load(ROOT / "docs/runner/dev_manifest.json")
        m["worlds"].append({"id": "dev03_B2", "seed": 3, "regime": "B2", "split": "development"})
        with patch("socket.socket.connect", side_effect=AssertionError("network attempted")):
            report = run(m, self.dir / "two", dry_run=True, max_checkpoints=1)
            self.assertEqual(report["run_record"]["checkpoints_launched"], 1)
            by_world = {w["world"]: w["attempts"] for w in report["worlds"]}
            self.assertEqual(len(by_world["dev02_B1"]), 1)
            self.assertEqual(by_world["dev03_B2"], [])
            with self.assertRaisesRegex(ValueError, "positive integer"):
                run(m, self.dir / "bad", dry_run=True, max_checkpoints=0)


if __name__ == "__main__":
    unittest.main()
