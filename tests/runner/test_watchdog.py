"""Watchdog triggers exercised with fakes only: no sockets, no Ollama, no model calls."""
import json
import signal
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from ccc.runner import watchdog as wd

DIGEST = wd.DIGEST
GOOD_PS = {"models": [{"name": wd.MODEL, "model": wd.MODEL, "digest": DIGEST, "size_vram": 17398172220}]}
NOW = datetime(2026, 10, 23, 22, 0, 0, tzinfo=timezone.utc)


class Fakes:
    """Mutable fake world; each test changes one thing and runs one check."""

    def __init__(self, tmp):
        self.dir = Path(tmp)
        self.ledger = self.dir / "ledger.jsonl"
        self.ledger.write_text("")  # pre-existing history is ignored by design
        self.ps = GOOD_PS
        self.disk_gb = 500.0
        self.mem_pct = 66
        self.run_alive = True
        self.ollama_alive = True
        self.now = NOW
        self.kills = []
        self.sleeps = 0
        self.kill_ignores_term = False

    def build(self, out="out"):
        def fetch():
            if isinstance(self.ps, Exception):
                raise self.ps
            return self.ps

        def alive(pid):
            return self.run_alive if pid == 111 else self.ollama_alive

        def kill(pid, sig):
            self.kills.append((pid, sig))
            if sig == signal.SIGKILL or not self.kill_ignores_term:
                if sig == signal.SIGKILL or not self.kill_ignores_term:
                    self.run_alive = False

        def sleep(_s):
            self.sleeps += 1

        return wd.Watchdog(111, self.dir / out, 30, ledger=self.ledger, ollama_pid=222, root=self.dir,
                           fetch=fetch, disk=lambda _p: self.disk_gb, mem=lambda: self.mem_pct,
                           alive=alive, kill=kill, clock=lambda: self.now, sleep=sleep, log=lambda m: None)

    def append(self, *recs):
        with self.ledger.open("a") as fh:
            for r in recs:
                fh.write(json.dumps(r) + "\n")


GOOD_END = {"event": "attempt_end", "backend": "ollama_local", "model_requested": wd.MODEL,
            "model_resolved": wd.MODEL, "api_cost_usd": 0.0, "new_out_of_pocket_usd": 0.0, "status": "ok"}


class WatchdogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.f = Fakes(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_once(self, dog):
        try:
            dog.start()
            dog.check_all()
        except wd.Trigger as trig:
            return dog.stop_run(trig), trig
        return None, None

    def assert_triggered(self, check_name, dog=None):
        dog = dog or self.f.build()
        rc, trig = self.run_once(dog)
        self.assertEqual(rc, 3)
        self.assertEqual(trig.check, check_name)
        stop = json.loads((self.f.dir / "out" / "WATCHDOG_STOP.json").read_text())
        self.assertEqual(stop["check"], check_name)
        self.assertIn(trig.reason, stop["reason"])
        self.assertEqual(self.f.kills[0], (111, signal.SIGTERM))
        return stop

    # (a) ledger
    def ledger_trigger(self, *recs):
        dog = self.f.build()
        dog.start()  # offset recorded here; only lines appended afterwards are checked
        self.f.append(*recs)
        try:
            dog.check_all()
        except wd.Trigger as trig:
            dog.stop_run(trig)
            return trig
        self.fail("expected a ledger trigger")

    def test_clean_run_has_no_trigger(self):
        dog = self.f.build()
        dog.start()
        self.f.append(GOOD_END)
        dog.check_all()  # no exception

    def test_positive_cost_triggers(self):
        trig = self.ledger_trigger(dict(GOOD_END, api_cost_usd=0.01, new_out_of_pocket_usd=0.01))
        self.assertEqual(trig.check, "ledger")

    def test_missing_cost_triggers(self):
        rec = {k: v for k, v in GOOD_END.items() if k not in ("api_cost_usd", "new_out_of_pocket_usd")}
        self.assertIn("missing", self.ledger_trigger(rec).reason)

    def test_wrong_backend_triggers(self):
        self.assertIn("openrouter", self.ledger_trigger(dict(GOOD_END, backend="openrouter")).reason)

    def test_wrong_model_triggers(self):
        self.assertIn("gemma4:31b", self.ledger_trigger(dict(GOOD_END, model_resolved="gemma4:31b")).reason)

    def test_partial_line_waits_then_is_checked(self):
        dog = self.f.build()
        dog.start()
        with self.f.ledger.open("a") as fh:
            fh.write('{"event": "attempt_end", "backend": "openr')  # still being written
        dog.check_ledger()  # incomplete line: no trigger yet
        with self.f.ledger.open("a") as fh:
            fh.write('outer"}\n')
        with self.assertRaises(wd.Trigger):
            dog.check_ledger()

    # (b) /api/ps
    def test_model_missing_from_ps_triggers(self):
        self.f.ps = {"models": []}
        self.assert_triggered("ps")

    def test_digest_change_triggers(self):
        self.f.ps = {"models": [dict(GOOD_PS["models"][0], digest="deadbeef")]}
        self.assert_triggered("ps")

    def test_size_vram_change_triggers(self):
        dog = self.f.build()
        dog.start()
        self.f.ps = {"models": [dict(GOOD_PS["models"][0], size_vram=1)]}
        with self.assertRaises(wd.Trigger) as cm:
            dog.check_ps()
        self.assertIn("size_vram changed", cm.exception.reason)

    def test_ps_unreachable_triggers(self):
        self.f.ps = OSError("connection refused")
        self.assert_triggered("ps")

    # (c) disk
    def test_low_disk_triggers(self):
        self.f.disk_gb = 19.9
        self.assert_triggered("disk")

    # (d) memory
    def test_low_memory_triggers(self):
        self.f.mem_pct = 9
        self.assert_triggered("memory")

    def test_memory_probe_failure_triggers(self):
        dog = self.f.build()
        dog.mem = lambda: (_ for _ in ()).throw(ValueError("no output"))
        self.assert_triggered("memory", dog)

    def test_memory_pressure_parse(self):
        fake = type("R", (), {"stdout": "The system has 1 (...)\nSystem-wide memory free percentage: 66%\n"})()
        with patch.object(wd.subprocess, "run", return_value=fake):
            self.assertEqual(wd.memory_free_pct(), 66)

    # (e) ollama server
    def test_ollama_gone_triggers(self):
        self.f.ollama_alive = False
        self.assert_triggered("ollama")

    # (f) deadline
    def test_after_deadline_triggers(self):
        self.f.now = datetime(2026, 10, 24, 9, 15, 1, tzinfo=timezone.utc)
        self.assert_triggered("deadline")

    def test_before_deadline_ok(self):
        self.f.now = datetime(2026, 10, 24, 9, 14, 59, tzinfo=timezone.utc)
        dog = self.f.build()
        dog.start()
        dog.check_deadline()

    # kill escalation and exit
    def test_sigkill_after_grace_when_term_ignored(self):
        self.f.kill_ignores_term = True
        self.f.disk_gb = 1.0
        dog = self.f.build()
        dog.start()
        with self.assertRaises(wd.Trigger) as cm:
            dog.check_all()
        self.assertEqual(dog.stop_run(cm.exception), 3)
        self.assertEqual(self.f.kills, [(111, signal.SIGTERM), (111, signal.SIGKILL)])
        stop = json.loads((self.f.dir / "out" / "WATCHDOG_STOP.json").read_text())
        self.assertTrue(stop["sigkill_used"])
        self.assertEqual(self.f.sleeps, wd.KILL_GRACE_S)

    def test_exits_cleanly_when_run_exits_on_its_own(self):
        self.f.run_alive = False
        rc = self.f.build().run()
        self.assertEqual(rc, 0)
        exit_rec = json.loads((self.f.dir / "out" / "WATCHDOG_EXIT.json").read_text())
        self.assertEqual(exit_rec["run_pid"], 111)
        self.assertFalse((self.f.dir / "out" / "WATCHDOG_STOP.json").exists())

    def test_run_loop_stops_on_trigger_mid_run(self):
        calls = {"n": 0}
        dog = self.f.build()
        original = dog.check_all

        def flaky():
            calls["n"] += 1
            if calls["n"] == 3:
                self.f.disk_gb = 1.0
            original()
        dog.check_all = flaky
        self.assertEqual(dog.run(), 3)
        self.assertEqual(calls["n"], 3)
        self.assertTrue((self.f.dir / "out" / "WATCHDOG_STOP.json").exists())


if __name__ == "__main__":
    unittest.main()
