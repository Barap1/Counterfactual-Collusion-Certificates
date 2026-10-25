"""Lifecycle control for the EXP-003 Modal server: prefetch / start / status / stop.

`start` spawns a detached daemon that owns an *ephemeral* Modal app (it ends when the daemon ends), enforces a
wall-clock deadline, and on exit appends a `modal_run` row to ops/budget_ledger.jsonl. The per-session bearer
token lives only in the daemon environment and a 0600 file under the user temp dir (deleted at stop); it is never
printed.  Usage: python -m ccc.exp003.modal_ctl {prefetch|start|status|stop} [--gpu L40S --parallel 1 --max-minutes 90]
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

SESSION_FILE = Path(tempfile.gettempdir()) / f"exp003_modal_session_{os.getuid()}.json"


def _write_session(d: dict) -> None:
    fd = os.open(SESSION_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        json.dump(d, fh)


def load_session() -> dict:
    return json.loads(SESSION_FILE.read_text())


def public_state() -> dict:
    try:
        s = load_session()
    except OSError:
        return {"session": None}
    return {"session": {k: v for k, v in s.items() if k != "token"}}


def http(url: str, token: str, path: str, body: dict | None = None, timeout: float = 60):
    req = urllib.request.Request(url.rstrip("/") + path, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                                 method="GET" if body is None else "POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def app_list() -> str:
    return subprocess.run(["modal", "app", "list"], capture_output=True, text=True).stdout


def verify_stopped(app_id):
    """Unknown CLI state is unverified, so the liability remains reserved."""
    try:
        result = subprocess.run(["modal", "app", "list", "--json"], capture_output=True, text=True, timeout=15)
        if result.returncode:
            return False
        rows = json.loads(result.stdout)
        if not isinstance(rows, list):
            return False
        if any(not isinstance(r, dict) or not r.get("App ID", r.get("app_id")) for r in rows):
            return False
        matching = [r for r in rows if r.get("App ID", r.get("app_id")) == app_id]
        return not matching or all(str(r.get("State", r.get("state", ""))).lower() == "stopped" for r in matching)
    except Exception:
        return False


def stop_remote(app_id):
    try:
        subprocess.run(["modal", "app", "stop", app_id], capture_output=True, timeout=15, check=True)
        return verify_stopped(app_id)
    except Exception:
        return False


class Lifetime:
    """Independent timer keeps enforcing caps while the main thread blocks on cold start/requests."""
    def __init__(self, row, *, path=None, shutdown=None, clock=None):
        import threading
        from . import budget
        self.row, self.path = row, path or budget.DEFAULT_LEDGER
        self.shutdown, self.clock = shutdown or stop_remote, clock or time.time
        self.app_id = None
        self.signalled = False
        self.done = threading.Event()
        self.thread = threading.Thread(target=self.watch, daemon=True)

    def tick(self):
        from . import budget
        self.row, reason = budget.tick_session(self.row, path=self.path, now=self.clock())
        if reason and self.app_id:
            # This does not wait for the HTTP request or for app.run().__exit__.
            if self.shutdown(self.app_id):
                self.done.set()
        return reason

    def watch(self):
        from . import budget
        while not self.done.wait(budget.TICK_SECONDS):
            try:
                reason = self.tick()
            except Exception:
                # Accounting failure must also terminate; keep the reservation.
                reason = "accounting_failure"
                if self.app_id:
                    self.shutdown(self.app_id)
            if reason and not self.signalled:
                self.signalled = True
                os.kill(os.getpid(), signal.SIGTERM)


def _reservation(seconds, gpu, cpu, mem):
    from . import budget
    return budget.reserve_session(seconds, gpu, cpu=cpu, mem_gib=mem)


def _cpu_action(action, ref=None):
    from . import budget
    # Reserve before importing Modal/server (which can create a volume).
    cpu_only = os.environ.get("EXP003_GPU") == "none"
    row = _reservation(3600 if action == "prefetch" else 900, None,
                       float(os.environ.get("EXP003_CPU", "8" if cpu_only else "4")),
                       int(os.environ.get("EXP003_MEM_MIB", "32768" if cpu_only else "16384"))/1024)
    os.environ["EXP003_DEADLINE_EPOCH"] = str(row["deadline_epoch"])
    lifetime = Lifetime(row)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    signal.signal(signal.SIGALRM, lambda *_: sys.exit(0))
    signal.setitimer(signal.ITIMER_REAL, max(.001, row["deadline_epoch"]-time.time()))
    lifetime.thread.start()
    try:
        from . import modal_server as ms
        with ms.prefetch_app.run():
            lifetime.app_id = ms.prefetch_app.app_id
            facts = ms.prefetch.remote(ref) if action == "prefetch" else ms.identity_check.remote()
        print(json.dumps({action: facts}, indent=1))
    finally:
        verified = bool(lifetime.app_id) and stop_remote(lifetime.app_id)
        lifetime.done.set()
        lifetime.thread.join(timeout=31)
        signal.setitimer(signal.ITIMER_REAL, 0)
        budget.close_session(lifetime.row, verified)
    return 0


def prefetch(ref="gemma4:26b"):
    return _cpu_action("prefetch", ref)


def identity():
    return _cpu_action("identity")


def serve():
    from . import budget
    row = json.loads(os.environ["EXP003_RESERVATION"])
    # Reservation timestamp covers process startup/import time as well as cold start.
    lifetime = Lifetime(row)
    token = os.environ["EXP003_MODAL_TOKEN"]
    deadline = row["deadline_epoch"]
    state = {"pid": os.getpid(), "token": token, "gpu": row["gpu"], "t_start": row["started_epoch"],
             "deadline_epoch": deadline, "ready": False, "url": None}
    def bye(*_):
        raise SystemExit(0)
    signal.signal(signal.SIGTERM, bye)
    signal.signal(signal.SIGINT, bye)
    signal.signal(signal.SIGALRM, bye)
    signal.setitimer(signal.ITIMER_REAL, max(.001, deadline-time.time()))
    lifetime.thread.start()
    _write_session(state)
    try:
        from . import modal_server as ms
        with ms.app.run():
            lifetime.app_id = ms.app.app_id
            state['app_id'] = lifetime.app_id
            url = ms.Server().web.get_web_url()
            state['url'] = url
            _write_session(state)
            # Alarm + watchdog enforce deadline during this blocking cold-start call.
            info = http(url, token, "/exp003/info", timeout=max(.001, min(1500, deadline-time.time())))
            state.update(ready=True, server_info=info)
            _write_session(state)
            while time.time() < deadline:
                time.sleep(1)
    finally:
        verified = bool(lifetime.app_id) and stop_remote(lifetime.app_id)
        lifetime.done.set()
        lifetime.thread.join(timeout=31)
        signal.setitimer(signal.ITIMER_REAL, 0)
        budget.close_session(lifetime.row, verified)
        state.update(ready=False, ended=True, teardown_verified=verified, token="")
        _write_session(state)
    return 0


def start(args) -> int:
    frozen = None
    if not args.development:
        if not args.manifest:
            raise ValueError('held-out start requires --manifest; GPU spike requires --development')
        from .manifest import load
        m = load(args.manifest)
        from .freeze import verify_launch_window
        frozen = verify_launch_window(m)
        if m['phase'] != 'holdout' or m['backend'] != 'modal':
            raise ValueError('held-out Modal manifest required')
    elif args.manifest:
        raise ValueError('choose held-out manifest or explicitly labelled development')
    if SESSION_FILE.exists():
        try:
            s = load_session()
            os.kill(s["pid"], 0)
            print("session already running; stop it first")
            return 1
        except (OSError, KeyError):
            SESSION_FILE.unlink()
    from . import budget
    if args.storage_usd is None:
        raise ValueError("explicit conservative cumulative unledgered storage liability required: --storage-usd")
    cpu = float(os.environ.get("EXP003_CPU", "8" if args.gpu == "none" else "4"))
    mem = int(os.environ.get("EXP003_MEM_MIB", "32768" if args.gpu == "none" else "16384"))/1024
    admission = {}
    if frozen is not None:
        from .feasibility import projection
        from .manifest import digest
        p = projection(m, frozen)
        config = dict(gpu=args.gpu, cpu=cpu, mem_gib=mem, parallel=args.parallel, scaledown=args.scaledown)
        if config != p['config']:
            raise ValueError('launch configuration differs from measured frozen configuration')
        # The remote function has a fixed 7200-second timeout ceiling.
        if min(args.max_minutes*60, 7200) < p['seconds']:
            raise ValueError('requested lifetime cannot cover projected block including startup')
        if args.storage_usd < frozen['feasibility_budget']['storage_usd']:
            raise ValueError('storage liability below frozen reconciliation')
        admission = dict(minimum_seconds=p['seconds'], minimum_usd=p['cost'],
                         reconciled_prior_usd=frozen['feasibility_budget']['reconciled_prior_usd'],
                         binding=dict(launch_config=config, manifest_sha256=digest(m),
                                      measured_cost_sha256=p['measured_cost_sha256']))
    row = budget.reserve_session(args.max_minutes*60, None if args.gpu == "none" else args.gpu,
                                 cpu=cpu, mem_gib=mem, storage_usd=args.storage_usd, **admission)
    env = dict(os.environ, EXP003_MODAL_TOKEN=secrets.token_urlsafe(32), EXP003_GPU=args.gpu,
               EXP003_PARALLEL=str(args.parallel), EXP003_RESERVATION=json.dumps(row),
               EXP003_DEADLINE_EPOCH=str(row['deadline_epoch']),
               EXP003_SCALEDOWN_S=str(args.scaledown),
               EXP003_TIMEOUT_S=str(max(1, int(row['deadline_epoch']-time.time()))))
    log = open(Path(tempfile.gettempdir()) / "exp003_modal_daemon.log", "ab")
    daemon = subprocess.Popen([sys.executable, "-m", "ccc.exp003.modal_ctl", "_serve"], env=env, stdout=log, stderr=log,
                     stdin=subprocess.DEVNULL, start_new_session=True,
                     cwd=Path(__file__).resolve().parents[2])
    t0 = time.time()
    while time.time() - t0 < args.wait:
        time.sleep(5)
        if daemon.poll() is not None:
            print("daemon exited early; see $TMPDIR/exp003_modal_daemon.log")
            return 3
        try:
            s = load_session()
        except (OSError, ValueError):
            continue
        if s.get("ready"):
            print(json.dumps(public_state(), indent=1))
            return 0
        if s.get("ended"):
            break
    print("server not ready; see status / stop")
    print(json.dumps(public_state(), indent=1))
    return 2


def stop() -> int:
    try:
        s = load_session()
    except OSError:
        print("no session file")
    else:
        try:
            os.kill(s["pid"], signal.SIGTERM)
        except OSError:
            pass
        for _ in range(120):
            try:
                os.kill(s["pid"], 0)
                time.sleep(2)
            except OSError:
                break
        print(json.dumps(public_state(), indent=1))
    print(app_list())
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["identity", "prefetch", "start", "status", "stop", "_serve"])
    p.add_argument("--gpu", default=os.environ.get("EXP003_GPU", "L40S"))
    p.add_argument("--parallel", type=int, default=1)
    p.add_argument("--max-minutes", type=float, default=90)
    p.add_argument("--scaledown", type=int, default=180)
    p.add_argument("--storage-usd", type=float, default=None)
    p.add_argument("--manifest", type=Path)
    p.add_argument("--development", action="store_true")
    p.add_argument("--ref", default="gemma4:26b")
    p.add_argument("--wait", type=float, default=1800)
    a = p.parse_args(argv)
    if a.cmd == "_serve":
        return serve()
    if a.cmd == "identity":
        return identity()
    if a.cmd == "prefetch":
        return prefetch(a.ref)
    if a.cmd == "start":
        return start(a)
    if a.cmd == "stop":
        return stop()
    print(json.dumps(public_state(), indent=1))
    print(app_list())
    return 0


if __name__ == "__main__":
    sys.exit(main())
