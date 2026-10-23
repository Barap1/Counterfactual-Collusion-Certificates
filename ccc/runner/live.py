"""Local-only Ollama transport and fail-closed model residency attestation.

No server startup, discovery, credentials, redirects, or remote fallback.
"""
import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlsplit

from ccc.infra.budget_guard import GuardedChatClient
from .manifest import digest, parse_instant

KEEP_ALIVE = -1
CANARY_MESSAGES = [{"role": "user", "content": "Write one short sentence about a copper lighthouse."}]
CANARY_PARAMS = {"temperature": 0.7, "seed": 731921, "max_tokens": 16, "reasoning_effort": "none"}


class ModelReload(ValueError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Ollama redirects forbidden")


def local_listener(port):
    """Inspect OS listeners, not merely the URL. Wildcard/LAN listeners fail closed."""
    result = subprocess.run(["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-Fpn"],
                            capture_output=True, text=True, check=True)
    names = [s[1:] for s in result.stdout.splitlines() if s.startswith("n")]
    if not names or any(n not in (f"127.0.0.1:{port}", f"[::1]:{port}") for n in names):
        raise ValueError("Ollama server must listen on loopback only")
    return sorted(set(s[1:] for s in result.stdout.splitlines() if s.startswith("p")))


class OllamaSession:
    def __init__(self, model):
        self.model = model
        endpoint = urlsplit(model["base_url"])
        self.origin = f"http://127.0.0.1:{endpoint.port or 80}"
        self.port = endpoint.port or 80
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        self.pids = local_listener(self.port)
        tags = self.get("/api/tags")
        self.tag = self.entry(tags)
        self.verify_digest(self.tag)
        self.version = self.get("/api/version")
        self.history = []
        self.canary_output = None
        self.initial = self.snapshot()
        if (parse_instant(self.initial["expires_at"]) - datetime.now(timezone.utc)).total_seconds() < 6 * 3600:
            raise ValueError("resident lease must cover at least six hours; operator must set OLLAMA_KEEP_ALIVE=-1")
        self.identity = self.token(self.initial)
        self.session_id = digest([self.version, self.pids, self.identity])

    def get(self, path):
        with self.opener.open(self.origin + path, timeout=30) as response:
            return json.load(response)

    def entry(self, data):
        entries = [x for x in data.get("models", [])
                   if x.get("name", x.get("model")) == self.model["requested_id"]]
        if len(entries) != 1:
            raise ValueError("exact model must already be installed and resident; runner never loads it")
        return entries[0]

    def verify_digest(self, entry):
        if entry.get("digest", "").removeprefix("sha256:") != self.model["weight_digest"]:
            raise ValueError("Ollama exact model digest mismatch")

    def snapshot(self):
        data = self.get("/api/ps")
        self.history.append({"checked_at": datetime.now(timezone.utc).isoformat(), "ps": data})
        entry = self.entry(data)
        self.verify_digest(entry)
        if parse_instant(entry["expires_at"]) <= datetime.now(timezone.utc):
            raise ModelReload("model_reload: residency expired")
        if entry.get("context_length") != 32768:
            raise ValueError("resident Ollama model must have context_length 32768")
        return entry

    @staticmethod
    def token(entry):
        # With infinite keep_alive the expiry is constant, unlike finite leases.
        fields = ("digest", "size_vram", "context_length", "expires_at")
        if any(entry.get(k) is None for k in fields):
            raise ValueError("/api/ps lacks required fingerprint fields")
        return {k: entry[k] for k in fields} | {
            "load_identity": entry.get("loaded_at") or entry.get("load_session_id")}

    def check(self):
        try:
            entry = self.snapshot()
            if (local_listener(self.port) != self.pids or self.get("/api/version") != self.version
                    or self.token(entry) != self.identity):
                raise ModelReload("model_reload: model-load session changed")
            return entry
        except ModelReload:
            raise
        except Exception as exc:
            raise ModelReload("model_reload: residency cannot be verified") from exc

    def canary(self, guard, root, phase):
        """Fixed stochastic probe; compare UTF-8 content bytes, never response IDs."""
        from .storage import put
        client = OllamaChatClient(guard, backend=self.model["backend"],
            model=self.model["requested_id"], base_url=self.model["base_url"],
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
            if response.get("model") != self.model["requested_id"] or not output:
                raise ModelReload("model_reload: invalid canary response")
            encoded = output.encode("utf-8")
            if self.canary_output is None:
                self.canary_output = encoded
            elif self.canary_output != encoded:
                raise ModelReload("model_reload: canary mismatch")
        except ModelReload:
            raise
        except Exception as exc:
            raise ModelReload("model_reload: canary cannot be verified") from exc

    def transport(self, url, headers, body, timeout):
        if url != self.origin + "/v1/chat/completions":
            raise ValueError("unexpected Ollama call URL")
        request = urllib.request.Request(url, headers=headers, data=body, method="POST")
        with self.opener.open(request, timeout=timeout) as response:
            return response.status, response.read()

    def attestation(self):
        return {"weight_digest": self.tag["digest"], "load_session_id": self.session_id,
                "initial_ps": self.initial, "server_version": self.version, "listener_pids": self.pids, "keep_alive": KEEP_ALIVE}


class OllamaChatClient(GuardedChatClient):
    def build_payload(self, messages, params):
        payload = super().build_payload(messages, params)
        # Included before guard admission/hashing and immutable wire evidence.
        payload.update(keep_alive=KEEP_ALIVE, options={"num_ctx": 32768})
        return payload
