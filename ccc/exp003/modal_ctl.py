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


def prefetch(ref: str = "gemma4:26b") -> int:
    from . import budget, modal_server as ms
    import modal
    t0 = time.time()
    with modal.enable_output(), ms.prefetch_app.run():
        facts = ms.prefetch.remote(ref)
    row = budget.append_run(time.time() - t0, None, label="prefetch-cpu", cpu=ms.CPU, mem_gib=ms.MEM_MIB / 1024)
    print(json.dumps({"prefetch": facts, "ledger_estimated_usd": row["estimated_usd"]}, indent=1))
    return 0


def identity() -> int:
    from . import budget, modal_server as ms
    import modal
    t0 = time.time()
    with ms.prefetch_app.run():
        facts = ms.identity_check.remote()
    row = budget.append_run(time.time() - t0, None, label="identity-check-cpu", cpu=ms.CPU, mem_gib=ms.MEM_MIB / 1024)
    print(json.dumps({"identity": facts, "ledger_estimated_usd": row["estimated_usd"]}, indent=1))
    return 0


def serve() -> int:
    """Daemon body (env: EXP003_MODAL_TOKEN, EXP003_GPU, EXP003_PARALLEL, EXP003_DEADLINE_EPOCH)."""
    from . import budget, modal_server as ms
    import modal
    token = os.environ["EXP003_MODAL_TOKEN"]
    deadline = float(os.environ["EXP003_DEADLINE_EPOCH"])
    stop = {"flag": False}
    def _bye(*_):
        stop["flag"] = True
        raise SystemExit(0)      # unblocks a pending cold-start request; `finally` below tears the app down
    signal.signal(signal.SIGTERM, _bye)
    signal.signal(signal.SIGINT, _bye)
    t_start = time.time()
    state = {"pid": os.getpid(), "token": token, "gpu": ms.GPU, "parallel": ms.PARALLEL, "t_start": t_start,
             "deadline_epoch": deadline, "ready": False, "url": None}
    _write_session(state)
    ready_s = None
    try:
        with ms.app.run():
            url = ms.Server().web.get_web_url()
            state["url"] = url
            _write_session(state)
            while not stop["flag"] and time.time() < deadline:
                try:
                    info = http(url, token, "/exp003/info", timeout=1500)   # first call blocks through cold start
                    break
                except Exception as exc:
                    state["last_error"] = type(exc).__name__
                    time.sleep(5)
            else:
                info = None
            if info:
                ready_s = round(time.time() - t_start, 1)
                state.update(ready=True, cold_start_s=ready_s, server_info=info)
                _write_session(state)
            while not stop["flag"] and time.time() < deadline:
                time.sleep(2)
            if time.time() >= deadline:
                state["stopped_reason"] = "deadline"
    finally:
        seconds = time.time() - t_start
        row = budget.append_run(seconds, None if ms.GPU == "none" else ms.GPU, label="serve-session", cpu=ms.CPU, mem_gib=ms.MEM_MIB / 1024,
                                note=f"upper bound: daemon wall incl. cold start {ready_s}s; ephemeral app")
        state.update(ready=False, ended=True, seconds=round(seconds, 1), estimated_usd=row["estimated_usd"])
        state.pop("token", None)
        _write_session(state | {"token": ""})
    return 0


def start(args) -> int:
    if SESSION_FILE.exists():
        try:
            s = load_session()
            os.kill(s["pid"], 0)
            print("session already running; stop it first")
            return 1
        except (OSError, KeyError):
            SESSION_FILE.unlink()
    env = dict(os.environ, EXP003_MODAL_TOKEN=secrets.token_urlsafe(32), EXP003_GPU=args.gpu,
               EXP003_PARALLEL=str(args.parallel),
               EXP003_DEADLINE_EPOCH=str(time.time() + args.max_minutes * 60),
               EXP003_SCALEDOWN_S=str(args.scaledown), EXP003_TIMEOUT_S=str(int(min(args.max_minutes * 60, 7200))))
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
