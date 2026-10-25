"""Modal transport, identity canaries and guarded EXP-003 CLI.

The run command delegates to ccc.exp003.collector, including PF/PK scheduling.
Configuration supplies the endpoint; the existing session environment supplies
credentials. Importing this module does not read credentials or contact Modal.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from ccc.infra.budget_guard import BACKEND_MODAL, BudgetGuard, GuardPolicy
from ccc.runner.live import CANARY_MESSAGES, CANARY_PARAMS, KEEP_ALIVE, ModelReload, OllamaChatClient, OllamaSession
from ccc.runner.manifest import digest, parse_instant
from . import budget

ROOT = Path(__file__).resolve().parents[2]
TOKEN_ENV = "EXP003_MODAL_TOKEN"
MODEL_ID = "gemma4:26b"
FROZEN_DIGEST = "5571076f3d70050487b26b341705799e0ab29b808164f90d20d4cf84f699d251"


class ModalChatClient(OllamaChatClient):
    """Same wire payload as the local client (keep_alive -1, num_ctx 32768) + the Modal key env name."""
    def __init__(self, *a, **k):
        k.setdefault("key_env_name", TOKEN_ENV)
        super().__init__(*a, **k)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        raise ValueError("redirects forbidden")


class ModalSession(OllamaSession):
    """Residency/identity attestation over the authenticated proxy (no lsof/ps on the local machine)."""

    def __init__(self, model, *, require_digest=True):
        self.model = model
        u = urlsplit(model["base_url"])
        self.origin = f"{u.scheme}://{u.netloc}"
        self.port = u.port or 443
        self.token = os.environ[TOKEN_ENV]
        self.opener = urllib.request.build_opener(NoRedirect())
        tags = self.get("/api/tags")
        self.tag = self.entry(tags)
        self.tag_digest = self.tag.get("digest", "")
        if require_digest:
            self.verify_digest(self.tag)
        self.version = self.get("/api/version")
        self.history, self.canary_output = [], None
        self.initial = self.snapshot()
        if (parse_instant(self.initial["expires_at"]) - datetime.now(timezone.utc)).total_seconds() < 3600:
            raise ValueError("resident lease must cover at least one hour (OLLAMA_KEEP_ALIVE=-1 on the server)")
        info = self.get("/exp003/info")
        self.pids = [info["task_id"], info["ollama_pid"]]
        self.runner_pid = ",".join(info["runner_pids"]) or None
        self.detector = "fingerprint+container_task+runner_pid+canary"
        self.history[-1].update(runner_pid=self.runner_pid, detector=self.detector, task_id=info["task_id"])
        self.identity = self.token_fields(self.initial)
        self.session_id = digest([self.version, self.pids, self.runner_pid, self.identity])

    token_fields = staticmethod(OllamaSession.token)

    CONNECT_RETRIES = 4
    connect_retry_count = 0     # how many pre-request connection failures were retried (reported, never hidden)

    def _open(self, req, timeout):
        """Retry only TLS-handshake/connect failures (the request never reached the server, so no double work)."""
        import ssl, socket, time
        for i in range(self.CONNECT_RETRIES + 1):
            try:
                return self.opener.open(req, timeout=timeout)
            except urllib.error.HTTPError:
                raise
            except urllib.error.URLError as e:
                transient = isinstance(e.reason, (ssl.SSLError, ConnectionError, socket.gaierror)) or \
                    "handshake" in str(e.reason) or "timed out" in str(e.reason) and "handshake" in str(e.reason)
                if not transient or i == self.CONNECT_RETRIES:
                    raise
                ModalSession.connect_retry_count += 1
                time.sleep(2 * (i + 1))

    def get(self, path):
        req = urllib.request.Request(self.origin + path, headers={"Authorization": f"Bearer {self.token}"})
        with self._open(req, 60) as r:
            return json.load(r)

    def check(self):
        try:
            entry = self.snapshot()
            info = self.get("/exp003/info")
            if [info["task_id"], info["ollama_pid"]] != self.pids or ",".join(info["runner_pids"]) != (self.runner_pid or ""):
                raise ModelReload("model_reload: container/ollama/runner changed")
            if self.get("/api/version") != self.version or self.token_fields(entry) != self.identity:
                raise ModelReload("model_reload: model-load session changed")
            return entry
        except ModelReload:
            raise
        except Exception as exc:
            raise ModelReload("model_reload: residency cannot be verified") from exc

    def canary(self, guard, root, phase):
        from ccc.runner.storage import put
        client = ModalChatClient(guard, backend=BACKEND_MODAL, model=MODEL_ID, base_url=self.model["base_url"],
                                 transport=self.transport, meta={"purpose": "reload_canary", "phase": phase,
                                                                 "load_session": self.session_id})
        base = root / "canary" / phase
        put(base.with_suffix(".begin.json"), {"request": client.build_payload(CANARY_MESSAGES, CANARY_PARAMS)})
        try:
            self.check()
            response, output = client.generate_response(CANARY_MESSAGES, CANARY_PARAMS)
            put(base.with_suffix(".end.json"), {"response": response, "output": output,
                                                "guard_attempts": client.last_attempt_records})
            self.check()
            if response.get("model") != MODEL_ID or not output:
                raise ModelReload("model_reload: invalid canary response")
            enc = output.encode("utf-8")
            if self.canary_output is None:
                self.canary_output = enc
            elif self.canary_output != enc:
                raise ModelReload("model_reload: canary mismatch")
        except ModelReload:
            raise
        except Exception as exc:
            raise ModelReload("model_reload: canary cannot be verified") from exc

    def transport(self, url, headers, body, timeout):
        if url != self.origin + "/v1/chat/completions":
            raise ValueError("unexpected Modal call URL")
        req = urllib.request.Request(url, headers=headers, data=body, method="POST")
        try:
            with self._open(req, timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def attestation(self):
        return {"weight_digest": self.tag_digest, "load_session_id": self.session_id, "runner_pid": self.runner_pid,
                "detector": self.detector, "initial_ps": self.initial, "server_version": self.version,
                "container_task_id": self.pids[0], "keep_alive": KEEP_ALIVE, "backend": BACKEND_MODAL,
                "endpoint_host": urlsplit(self.origin).hostname}


def validate_modal(m):
    from .manifest import validate
    if m.get("backend") != "modal":
        raise ValueError("Modal configuration required")
    return validate(m)


class Exp003Guard(BudgetGuard):
    def check_request(self, backend, model, base_url):
        sessions = [r for r in budget.session_rows().values() if r['state'] in ('reserved', 'active')]
        if len(sessions) != 1:
            raise ValueError('one controller-owned active session required')
        _, reason = budget.tick_session(sessions[0])
        if reason:
            raise ValueError('controller monetary/deadline stop: ' + reason)
        return super().check_request(backend, model, base_url)

    def __init__(self, *, task_id, **kw):
        budget.record_billing_snapshot()           # guard needs a fresh (<1 h) snapshot; refreshed per world
        super().__init__(task_id=budget.TASK, **kw)


def _policy(**kw):
    return GuardPolicy(modal_enabled=True, modal_models=(MODEL_ID,), modal_spend_cap_usd=45.0, **kw)


def install():
    raise ValueError("legacy collector patching retired; use ccc.exp003.collector")


def make_manifest(url, out, *, max_requests=400, base="docs/runner/dev_manifest.json"):
    m = json.loads((ROOT / base).read_text())
    m["experiment_id"] = "EXP-003-spike-dev"
    m["model"] = dict(m["model"], backend=BACKEND_MODAL, base_url=url.rstrip("/") + "/v1")
    m["policy"] = dict(m["policy"], live_inference_enabled=True)
    m["max_requests"] = max_requests
    from .manifest import SCHEMA
    from ccc.runner.manifest import file_hash
    m.update(schema_version=SCHEMA, backend="modal",
             protocol_artifact="docs/enh/exp003/PROTOCOL.md",
             protocol_sha256=file_hash(ROOT / "docs/enh/exp003/PROTOCOL.md"),
             arms=["F", "K", "S", "N", "PF", "PK"],
             continuations_per_arm={"F": 4, "K": 4, "S": 2, "N": 4, "PF": 4, "PK": 4})
    seeds = list(dict.fromkeys(w["seed"] for w in m["worlds"]))
    m["worlds"] = [dict(id=f"dev{seed:02}_{regime}", pair_id=f"dev{seed:02}", seed=seed,
                        regime=regime, split="development") for seed in seeds for regime in ("B1", "B2")]
    Path(out).write_text(json.dumps(m, indent=1))
    return m


def canary(url, out):
    """Model-identity canaries against Modal: digest/version/residency + two seeded canary generations that must
    match byte-for-byte (same fixed probe as the EXP-002 runner)."""
    from ccc.runner.storage import put
    model = {"backend": BACKEND_MODAL, "requested_id": MODEL_ID, "base_url": url.rstrip("/") + "/v1",
             "weight_digest": FROZEN_DIGEST, "context_limit": 32768}
    sess = ModalSession(model, require_digest=False)
    out = Path(out)
    result = {"tag_digest": sess.tag_digest.removeprefix("sha256:"), "equals_exp002_weight_digest":
              sess.tag_digest.removeprefix("sha256:") == FROZEN_DIGEST, "server_version": sess.version,
              "attestation": sess.attestation()}
    guard = Exp003Guard(run_id="EXP-003/spike-canary", task_id=budget.TASK, max_calls=6, policy=_policy(max_retries=0),
                        purpose="EXP-003 spike model-identity canary")
    try:
        sess.canary(guard, out, "one")
        sess.canary(guard, out, "two")
        result["canary"] = "pass"
        result["canary_output_sha256"] = digest(sess.canary_output.decode())
    except Exception as exc:
        chain, c = [], exc
        while c:
            chain.append(f"{type(c).__name__}: {str(c)[:160]}")
            c = c.__cause__
        result["canary"] = "FAIL " + " <- ".join(chain)
    finally:
        guard.close("canary done")
    out.mkdir(parents=True, exist_ok=True)
    (out / "canary_result.json").write_text(json.dumps(result, indent=1, default=str))
    print(json.dumps({k: v for k, v in result.items() if k != "attestation"}, indent=1))
    return 0 if result["canary"] == "pass" else 1


def main(argv=None):
    import argparse
    from .modal_ctl import load_session
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("manifest"); a.add_argument("--out", required=True); a.add_argument("--max-requests", type=int, default=400)
    c = sub.add_parser("canary"); c.add_argument("--out", required=True)
    r = sub.add_parser("run"); r.add_argument("manifest"); r.add_argument("--output", required=True)
    r.add_argument("--max-checkpoints", type=int, default=1)
    args = p.parse_args(argv)
    s = load_session()
    os.environ[TOKEN_ENV] = s["token"]
    if args.cmd == "manifest":
        make_manifest(s["url"], args.out, max_requests=args.max_requests)
        print("manifest written")
        return 0
    if args.cmd == "canary":
        return canary(s["url"], args.out)
    from .collector import run
    res = run(json.loads(Path(args.manifest).read_text()), args.output, live=True,
                        max_checkpoints=args.max_checkpoints)
    print(json.dumps(res, sort_keys=True)[:3000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
