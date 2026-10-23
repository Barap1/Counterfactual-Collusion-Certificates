"""Local-only Ollama transport and fail-closed model residency attestation.

No server startup, discovery, credentials, redirects, or remote fallback.
"""
import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlsplit

from ccc.infra.budget_guard import GuardedChatClient
from .manifest import digest, parse_time

KEEP_ALIVE = "24h"


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
        self.history = []
        self.initial = self.snapshot()
        if (parse_time(self.initial["expires_at"]) - datetime.now(timezone.utc)).total_seconds() < 6 * 3600:
            raise ValueError("resident lease must cover at least six hours; operator must set OLLAMA_KEEP_ALIVE=24h")
        self.identity = self.token(self.initial)
        self.session_id = digest([self.pids, self.identity])

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
        if parse_time(entry["expires_at"]) <= datetime.now(timezone.utc):
            raise ModelReload("model_reload: residency expired")
        if entry.get("context_length") != 32768:
            raise ValueError("resident Ollama model must have context_length 32768")
        return entry

    @staticmethod
    def token(entry):
        # Expiry is a lease, not a load identifier: ordinary calls renew it.
        token = entry.get("loaded_at") or entry.get("load_session_id")
        if not token:
            raise ValueError("/api/ps lacks loaded_at/load_session_id; cannot attest no model reload")
        return token

    def check(self):
        try:
            entry = self.snapshot()
            if local_listener(self.port) != self.pids or self.token(entry) != self.identity:
                raise ModelReload("model_reload: model-load session changed")
            return entry
        except ModelReload:
            raise
        except Exception as exc:
            raise ModelReload("model_reload: residency cannot be verified") from exc

    def transport(self, url, headers, body, timeout):
        if url != self.origin + "/v1/chat/completions":
            raise ValueError("unexpected Ollama call URL")
        request = urllib.request.Request(url, headers=headers, data=body, method="POST")
        with self.opener.open(request, timeout=timeout) as response:
            return response.status, response.read()

    def attestation(self):
        return {"weight_digest": self.tag["digest"], "load_session_id": self.session_id,
                "initial_ps": self.initial, "listener_pids": self.pids, "keep_alive": KEEP_ALIVE}


class OllamaChatClient(GuardedChatClient):
    def build_payload(self, messages, params):
        payload = super().build_payload(messages, params)
        # Included before guard admission/hashing and immutable wire evidence.
        payload.update(keep_alive=KEEP_ALIVE, options={"num_ctx": 32768})
        return payload
