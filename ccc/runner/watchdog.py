"""Out-of-process watchdog for an EXP-001 runner process (stdlib only).

Usage: python -m ccc.runner.watchdog --run-pid PID --output DIR --interval 30 \
           [--hard-stop 2026-10-24T09:15:00Z] [--ollama-pid PID]

Polls safety conditions and stops the run PID (SIGTERM, then SIGKILL after 20 s) on any
trigger, writing DIR/WATCHDOG_STOP.json. If the run PID exits on its own, writes
DIR/WATCHDOG_EXIT.json and exits 0. Fails closed: any unreadable probe is a trigger.
"""
import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "ops" / "budget_ledger.jsonl"
OLLAMA_PID_FILE = ROOT / "runs" / "exp001" / "ollama.pid"
OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "gemma4:26b"
BACKEND = "ollama_local"
DIGEST = "5571076f3d70050487b26b341705799e0ab29b808164f90d20d4cf84f699d251"
MIN_DISK_FREE_GB = 20
MIN_MEM_FREE_PCT = 10
HARD_DEADLINE = datetime(2026, 10, 24, 9, 15, 0, tzinfo=timezone.utc)  # default for --hard-stop
KILL_GRACE_S = 20
COST_FIELDS = ("api_cost_usd", "new_out_of_pocket_usd")


class Trigger(Exception):
    def __init__(self, check, reason):
        super().__init__(f"{check}: {reason}")
        self.check = check
        self.reason = reason


def utc_now():
    return datetime.now(timezone.utc)


def parse_hard_stop(text):
    """Parse an ISO 8601 deadline that must be explicitly UTC (ending in Z or +00:00)."""
    if not (text.endswith("Z") or text.endswith("+00:00")):
        raise argparse.ArgumentTypeError(f"--hard-stop must be UTC (end with Z or +00:00): {text!r}")
    iso = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        dt = datetime.fromisoformat(iso)
    except ValueError:
        raise argparse.ArgumentTypeError(f"--hard-stop is not ISO 8601: {text!r}")
    if dt.utcoffset() is None or dt.utcoffset().total_seconds() != 0:
        raise argparse.ArgumentTypeError(f"--hard-stop must be UTC: {text!r}")
    return dt.astimezone(timezone.utc)


def pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass
    state = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
    return bool(state) and not state.startswith("Z")


def descendants(pid):
    out = subprocess.run(["ps", "-A", "-o", "pid=,ppid="], capture_output=True, text=True).stdout
    kids = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            kids.setdefault(int(parts[1]), []).append(int(parts[0]))
    found, stack = [], [pid]
    while stack:
        for child in kids.get(stack.pop(), []):
            found.append(child)
            stack.append(child)
    return found


def signal_tree(pid, sig):
    for target in [pid] + descendants(pid):
        try:
            os.kill(target, sig)
        except ProcessLookupError:
            pass


def fetch_ps():
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(OLLAMA_URL + "/api/ps", timeout=10) as resp:
        return json.loads(resp.read().decode())


def disk_free_gb(path):
    return shutil.disk_usage(path).free / 1e9


def memory_free_pct():
    out = subprocess.run(["memory_pressure"], capture_output=True, text=True, check=True).stdout
    m = re.search(r"System-wide memory free percentage:\s*(\d+)%", out)
    if not m:
        raise ValueError("memory_pressure output has no free percentage")
    return int(m.group(1))


def read_ollama_pid(path=OLLAMA_PID_FILE):
    return int(Path(path).read_text().strip())


def model_entry(ps, name=MODEL):
    for entry in ps.get("models", []):
        if entry.get("name") == name or entry.get("model") == name:
            return entry
    return None


class Watchdog:
    def __init__(self, run_pid, output, interval, *, ledger=LEDGER, ollama_pid=None, root=ROOT,
                 fetch=fetch_ps, disk=disk_free_gb, mem=memory_free_pct, alive=pid_alive,
                 kill=signal_tree, clock=utc_now, sleep=time.sleep, log=print, hard_stop=HARD_DEADLINE):
        self.run_pid = run_pid
        self.hard_stop = hard_stop
        self.output = Path(output)
        self.interval = interval
        self.ledger = Path(ledger)
        self.root = Path(root)
        self.ollama_pid = ollama_pid
        self.fetch, self.disk, self.mem = fetch, disk, mem
        self.alive, self.kill, self.clock, self.sleep, self.log = alive, kill, clock, sleep, log
        self.ledger_offset = 0
        self.initial = None

    # --- checks -------------------------------------------------------
    def start(self):
        self.ledger_offset = self.ledger.stat().st_size if self.ledger.exists() else 0
        if self.ollama_pid is None:
            self.ollama_pid = read_ollama_pid()
        try:
            entry = model_entry(self.fetch())
        except Exception as exc:  # fail closed
            raise Trigger("ps", f"initial /api/ps unreadable: {exc}")
        self.check_model(entry, initial=True)

    def check_model(self, entry, initial=False):
        if entry is None:
            raise Trigger("ps", f"{MODEL} not listed by /api/ps")
        if entry.get("digest") != DIGEST:
            raise Trigger("ps", f"digest changed: {entry.get('digest')}")
        if initial:
            self.initial = {"size_vram": entry.get("size_vram")}
            if self.initial["size_vram"] is None:
                raise Trigger("ps", "size_vram missing at watchdog start")
        elif entry.get("size_vram") != self.initial["size_vram"]:
            raise Trigger("ps", f"size_vram changed: {entry.get('size_vram')} != {self.initial['size_vram']}")

    def check_ps(self):
        try:
            entry = model_entry(self.fetch())
        except Exception as exc:  # fail closed
            raise Trigger("ps", f"/api/ps unreadable: {exc}")
        self.check_model(entry)

    def check_ledger(self):
        if not self.ledger.exists():
            raise Trigger("ledger", "ledger missing")
        with self.ledger.open("rb") as fh:
            fh.seek(self.ledger_offset)
            data = fh.read()
        last_nl = data.rfind(b"\n")
        if last_nl < 0:
            return  # no complete new line yet
        for raw in data[:last_nl].split(b"\n"):
            if not raw.strip():
                continue
            try:
                rec = json.loads(raw)
            except ValueError:
                raise Trigger("ledger", "unparsable new ledger line")
            self.check_record(rec)
        self.ledger_offset += last_nl + 1

    @staticmethod
    def check_record(rec):
        if not isinstance(rec, dict):
            raise Trigger("ledger", "non-object new ledger line")
        if "backend" in rec and rec["backend"] != BACKEND:
            raise Trigger("ledger", f"backend {rec['backend']!r} is not {BACKEND}")
        for key in ("model_requested", "model_resolved"):
            if rec.get(key) is not None and rec[key] != MODEL:
                raise Trigger("ledger", f"{key} {rec[key]!r} is not {MODEL}")
        if rec.get("event") == "attempt_end":
            for field in COST_FIELDS:
                value = rec.get(field)
                if value is None:
                    raise Trigger("ledger", f"live call missing {field}")
                try:
                    if float(value) != 0:
                        raise Trigger("ledger", f"live call {field}={value}")
                except (TypeError, ValueError):
                    raise Trigger("ledger", f"live call {field} unparsable {value!r}")

    def check_disk(self):
        free = self.disk(self.root)
        if free < MIN_DISK_FREE_GB:
            raise Trigger("disk", f"free {free:.1f} GB < {MIN_DISK_FREE_GB} GB")

    def check_memory(self):
        try:
            pct = self.mem()
        except Exception as exc:  # fail closed
            raise Trigger("memory", f"memory_pressure unreadable: {exc}")
        if pct < MIN_MEM_FREE_PCT:
            raise Trigger("memory", f"free {pct}% < {MIN_MEM_FREE_PCT}%")

    def check_ollama(self):
        if not self.alive(self.ollama_pid):
            raise Trigger("ollama", f"server pid {self.ollama_pid} is gone")

    def check_deadline(self):
        if self.clock() > self.hard_stop:
            raise Trigger("deadline", f"now past {self.hard_stop.strftime('%Y-%m-%dT%H:%M:%SZ')}")

    def check_all(self):
        self.check_ledger()
        self.check_ps()
        self.check_disk()
        self.check_memory()
        self.check_ollama()
        self.check_deadline()

    # --- actions ------------------------------------------------------
    def write(self, name, payload):
        self.output.mkdir(parents=True, exist_ok=True)
        (self.output / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    def stop_run(self, trigger):
        self.log(f"TRIGGER {trigger.check}: {trigger.reason}; stopping run pid {self.run_pid}")
        self.kill(self.run_pid, signal.SIGTERM)
        for _ in range(KILL_GRACE_S):
            if not self.alive(self.run_pid):
                break
            self.sleep(1)
        killed = False
        if self.alive(self.run_pid):
            self.kill(self.run_pid, signal.SIGKILL)
            killed = True
        self.write("WATCHDOG_STOP.json", {
            "reason": trigger.reason, "check": trigger.check, "run_pid": self.run_pid,
            "stopped_utc": self.clock().isoformat(), "sigkill_used": killed,
            "run_still_alive": self.alive(self.run_pid)})
        return 3

    def run(self):
        self.start()
        self.log(f"watchdog started run_pid={self.run_pid} ollama_pid={self.ollama_pid} "
                 f"ledger_offset={self.ledger_offset} initial_size_vram={self.initial['size_vram']}")
        while True:
            if not self.alive(self.run_pid):
                self.write("WATCHDOG_EXIT.json", {"run_pid": self.run_pid, "exited_utc": self.clock().isoformat(),
                                                  "ledger_offset_end": self.ledger_offset})
                self.log("run pid exited on its own")
                return 0
            try:
                self.check_all()
            except Trigger as trig:
                return self.stop_run(trig)
            self.sleep(self.interval)


def main(argv=None):
    p = argparse.ArgumentParser(description="EXP-001 runner watchdog")
    p.add_argument("--run-pid", type=int, required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--interval", type=float, default=30)
    p.add_argument("--ollama-pid", type=int, default=None, help="default: runs/exp001/ollama.pid")
    p.add_argument("--hard-stop", type=parse_hard_stop, default=None, metavar="ISO8601_UTC",
                   help="UTC deadline ending in Z or +00:00 (default: 2026-10-24T09:15:00Z)")
    args = p.parse_args(argv)
    hard_stop = HARD_DEADLINE
    if args.hard_stop is not None:
        if args.hard_stop <= utc_now():
            p.error(f"--hard-stop {args.hard_stop.strftime('%Y-%m-%dT%H:%M:%SZ')} is in the past")
        hard_stop = args.hard_stop
    dog = Watchdog(args.run_pid, args.output, args.interval, ollama_pid=args.ollama_pid,
                   hard_stop=hard_stop,
                   log=lambda msg: print(f"{utc_now().isoformat()} {msg}", flush=True))
    try:
        return dog.run()
    except Trigger as trig:
        # start-time failure: the run is stopped by the same path
        return dog.stop_run(trig)


if __name__ == "__main__":
    sys.exit(main())
