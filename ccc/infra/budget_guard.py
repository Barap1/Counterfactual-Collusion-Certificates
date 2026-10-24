"""Zero-new-spend inference guard for CCC (INF-001).

Every experimental model call MUST go through a :class:`BudgetGuard` (directly or via
:class:`GuardedChatClient`). The guard enforces:

* an allowlist of $0 backends/models (exact ids; router aliases and Ollama cloud models refused);
* backend/base-URL binding (local models only on loopback; OpenRouter only on openrouter.ai;
  the OpenRouter key is never sent anywhere else);
* per-run attempt caps (every retry counts), one in-flight call, a rolling UTC-day cap for
  OpenRouter computed from the ledger (failed requests consume free quota too);
* a pricing-zero check before any OpenRouter call, and a persistent HALT on any positive or
  missing provider cost;
* Modal: disabled unless ``ops/resource_policy.local.json`` says otherwise; when enabled,
  requires a fresh billing snapshot and a reservation, and hard-stops cumulative spend at the cap
  ($45 default, i.e. a margin below the reported $51 credit);
* append-only JSONL logging of every request attempt (begin + end) to ``ops/budget_ledger.jsonl``.
  No headers, keys or raw payloads are logged; error text is scrubbed of key-like strings.

The guard is transport-agnostic; :class:`GuardedChatClient` is a drop-in for Terrarium's
``TogetherClient`` interface (``init_context``, ``generate_response``, ``process_tool_calls``,
``get_usage``) that also passes ``seed`` and has no hidden retries.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import ipaddress
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

LEDGER_SCHEMA = "ccc.budget_ledger.v1"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = REPO_ROOT / "ops" / "budget_ledger.jsonl"
DEFAULT_POLICY_FILE = REPO_ROOT / "ops" / "resource_policy.local.json"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
FORBIDDEN_MODEL_IDS = {"openrouter/free", "openrouter/auto", "openrouter/auto:free"}

# Exact local weights benchmarked by INF-001 (digest = Ollama manifest digest from /api/tags).
DEFAULT_LOCAL_MODELS: Dict[str, Optional[str]] = {
    "gemma4:latest": "dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c",
    "gemma4:26b": "5571076f3d70050487b26b341705799e0ab29b808164f90d20d4cf84f699d251",
}
DEFAULT_OPENROUTER_MODELS = ("cohere/north-mini-code:free",)

BACKEND_OLLAMA = "ollama_local"
BACKEND_OPENROUTER = "openrouter"
BACKEND_MODAL = "modal"
KNOWN_BACKENDS = (BACKEND_OLLAMA, BACKEND_OPENROUTER, BACKEND_MODAL)

_SECRET_PATTERNS = [
    re.compile(r"sk-or-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.=]{8,}"),
    re.compile(r"(?i)(api[_-]?key|authorization|token)([\"'\s:=]+)[A-Za-z0-9_\-\.]{8,}"),
]
_FORBIDDEN_LOG_KEYS = {"authorization", "api_key", "apikey", "headers", "token", "secret", "password"}


class BudgetViolation(RuntimeError):
    """A request was refused before being sent (policy, cap, allowlist)."""


class BudgetHalt(BudgetViolation):
    """Live inference is halted (positive/unknown cost, quota exhaustion, or a recorded HALT)."""


def scrub(text: Any, limit: int = 500) -> str:
    s = str(text)
    for pat in _SECRET_PATTERNS:
        s = pat.sub("[REDACTED]", s)
    return s[:limit]


def _utcnow() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _iso(ts: Optional[_dt.datetime] = None) -> str:
    return (ts or _utcnow()).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def request_sha256(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _host_is_loopback(host: str) -> bool:
    if host in ("localhost",):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


# --------------------------------------------------------------------------- policy


@dataclass
class GuardPolicy:
    local_models: Dict[str, Optional[str]] = field(default_factory=lambda: dict(DEFAULT_LOCAL_MODELS))
    openrouter_models: Tuple[str, ...] = DEFAULT_OPENROUTER_MODELS
    modal_models: Tuple[str, ...] = ()
    modal_enabled: bool = False
    modal_spend_cap_usd: float = 45.0
    modal_billing_max_age_s: float = 3600.0
    max_in_flight: int = 1
    max_retries: int = 2
    openrouter_daily_cap: int = 50  # documented free tier; lower it if /key shows less
    openrouter_require_pricing_check: bool = True
    new_out_of_pocket_cap_usd: float = 0.0

    @classmethod
    def from_policy_file(cls, path: Path = DEFAULT_POLICY_FILE) -> "GuardPolicy":
        """Load the owner's local policy. Missing file -> strict defaults (Modal disabled)."""
        pol = cls()
        try:
            data = json.loads(Path(path).read_text())
        except (OSError, ValueError):
            return pol
        orr = data.get("openrouter") or {}
        if orr.get("allowed_models"):
            pol.openrouter_models = tuple(m for m in orr["allowed_models"] if m not in FORBIDDEN_MODEL_IDS)
        if "max_in_flight" in orr:
            pol.max_in_flight = min(int(orr["max_in_flight"]), 1)
        if "max_retries" in orr:
            pol.max_retries = int(orr["max_retries"])
        if "daily_request_cap" in orr:
            pol.openrouter_daily_cap = int(orr["daily_request_cap"])
        modal = data.get("modal") or {}
        status = str(modal.get("status", "BLOCKED")).upper()
        pol.modal_enabled = status in ("APPROVED", "ENABLED")
        if modal.get("spend_cap_usd") is not None:
            pol.modal_spend_cap_usd = min(float(modal["spend_cap_usd"]), 45.0)
        if modal.get("allowed_models"):
            pol.modal_models = tuple(modal["allowed_models"])
        local = data.get("local") or {}
        if local.get("allowed_models"):
            pol.local_models = {m: DEFAULT_LOCAL_MODELS.get(m) for m in local["allowed_models"]}
        pol.new_out_of_pocket_cap_usd = 0.0  # never configurable upward here
        return pol


# --------------------------------------------------------------------------- ledger


class Ledger:
    """Append-only JSONL ledger. One JSON object per line; never rewrites existing lines."""

    _lock = threading.Lock()

    def __init__(self, path: Path = DEFAULT_LEDGER):
        self.path = Path(path)

    def append(self, record: Dict[str, Any]) -> None:
        for k in record:
            if k.lower() in _FORBIDDEN_LOG_KEYS:
                raise BudgetViolation(f"refusing to log forbidden key {k!r}")
        line = json.dumps(record, sort_keys=True, ensure_ascii=False)
        if any(p.search(line) for p in _SECRET_PATTERNS[:2]):
            raise BudgetViolation("refusing to log a key-like string")
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
                fh.flush()
                os.fsync(fh.fileno())

    def records(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        try:
            with open(self.path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        continue
        except OSError:
            pass
        return out


# --------------------------------------------------------------------------- guard


@dataclass
class Attempt:
    attempt_id: str
    backend: str
    model: str
    base_url_host: str
    request_sha256: str
    t0: float
    attempt_no: int


class BudgetGuard:
    """Per-run guard. Create one per experiment run; share it across all agents of that run."""

    def __init__(
        self,
        *,
        run_id: str,
        task_id: str,
        max_calls: int,
        policy: Optional[GuardPolicy] = None,
        ledger_path: Path = DEFAULT_LEDGER,
        purpose: str = "experiment",
    ):
        if max_calls <= 0:
            raise BudgetViolation("max_calls must be a positive explicit cap")
        self.run_id = run_id
        self.task_id = task_id
        self.max_calls = int(max_calls)
        self.policy = policy or GuardPolicy.from_policy_file()
        self.ledger = Ledger(ledger_path)
        self.purpose = purpose
        self.calls_started = 0
        self._sem = threading.BoundedSemaphore(max(1, self.policy.max_in_flight))
        self._lock = threading.Lock()
        self._pricing_ok: Dict[str, Dict[str, Any]] = {}
        self._modal_reserved_usd = 0.0
        global_halt = self.halted("__global_only__")
        if global_halt:
            raise BudgetHalt(f"ledger contains an uncleared global HALT: {global_halt}")
        self.ledger.append(self._base("run_open") | {"max_calls": self.max_calls, "purpose": purpose})

    # ---- helpers
    def _base(self, event: str) -> Dict[str, Any]:
        return {"schema": LEDGER_SCHEMA, "ts_utc": _iso(), "task": self.task_id, "run_id": self.run_id, "event": event}

    def halted(self, backend: Optional[str] = None) -> Optional[str]:
        """Reason of the latest uncleared HALT that applies to ``backend`` (global halts apply to all;
        ``backend=None`` reports any halt). Only an explicit ``halt_cleared`` record (owner action) clears."""
        active: Dict[Optional[str], str] = {}
        for r in self.ledger.records():
            if r.get("event") == "halt":
                active[r.get("halt_scope")] = r.get("reason", "unspecified")
            elif r.get("event") == "halt_cleared":
                active.clear()
        if backend is None:
            return next(iter(active.values()), None)
        return active.get(None) or active.get(backend)

    def halt(self, reason: str, *, scope: Optional[str] = None, **evidence: Any) -> None:
        """Record a HALT. ``scope=None`` halts every backend (used for any observed positive charge)."""
        self.ledger.append(self._base("halt") | {"reason": scrub(reason), "halt_scope": scope,
                                                 "evidence": {k: scrub(v) for k, v in evidence.items()}})

    def openrouter_attempts_today(self) -> int:
        today = _utcnow().strftime("%Y-%m-%d")
        n = 0
        for r in self.ledger.records():
            if r.get("event") == "attempt_begin" and r.get("backend") == BACKEND_OPENROUTER:
                if str(r.get("ts_utc", "")).startswith(today):
                    n += 1
        return n

    # ---- pricing / billing evidence
    def apply_openrouter_key_status(self, key_data: Dict[str, Any], *, reserve: int = 2) -> int:
        """Tighten the daily cap from a fresh ``GET /api/v1/key`` response (``data`` object).

        Requests made outside this ledger (e.g. the pilot) count against the provider quota, so the cap
        becomes ``ledger_attempts_today + remaining - reserve``. Refuses if the key shows any usage or a
        non-free-tier account. Returns the number of attempts still allowed today."""
        if not key_data.get("is_free_tier", False):
            raise BudgetViolation("OpenRouter key is not free tier; refusing")
        if float(key_data.get("usage") or 0) > 0 or float(key_data.get("usage_daily") or 0) > 0:
            self.halt("OpenRouter key reports nonzero usage", usage=key_data.get("usage"))
            raise BudgetHalt("OpenRouter key reports nonzero usage")
        q = key_data.get("free_model_daily_requests") or {}
        if "remaining" not in q:
            raise BudgetViolation("free_model_daily_requests.remaining missing; quota unknown")
        allowed = max(0, int(q["remaining"]) - int(reserve))
        self.policy.openrouter_daily_cap = min(self.policy.openrouter_daily_cap, self.openrouter_attempts_today() + allowed)
        self.ledger.append(self._base("quota_check") | {"backend": BACKEND_OPENROUTER, "free_model_daily_requests": q,
                                                         "reserve": reserve, "allowed_now": allowed,
                                                         "daily_cap_effective": self.policy.openrouter_daily_cap})
        return allowed

    def record_openrouter_pricing(self, model: str, pricing: Dict[str, Any], *, source: str) -> None:
        """Record a catalog pricing check. Any nonzero or unparsable price blocks the model."""
        bad = {}
        for k, v in (pricing or {}).items():
            try:
                if float(v) != 0.0:
                    bad[k] = v
            except (TypeError, ValueError):
                bad[k] = v
        if not pricing:
            bad["pricing"] = "missing"
        self.ledger.append(self._base("pricing_check") | {"backend": BACKEND_OPENROUTER, "model": model,
                                                           "pricing": pricing, "source": source, "ok": not bad})
        if bad:
            raise BudgetViolation(f"pricing for {model} not all zero: {bad}")
        self._pricing_ok[model] = pricing

    def modal_spent_usd(self) -> Optional[float]:
        """Latest recorded Modal gross usage for the project (from billing snapshots)."""
        val = None
        for r in self.ledger.records():
            if r.get("event") == "modal_billing" and r.get("modal_gross_usage_usd") is not None:
                val = float(r["modal_gross_usage_usd"])
        return val

    def _modal_billing_age_s(self) -> Optional[float]:
        last = None
        for r in self.ledger.records():
            if r.get("event") == "modal_billing":
                last = r.get("ts_utc")
        if not last:
            return None
        t = _dt.datetime.strptime(last, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=_dt.timezone.utc)
        return (_utcnow() - t).total_seconds()

    def record_modal_billing(self, gross_usage_usd: Optional[float], *, source: str, verified: bool) -> None:
        """Record a Modal billing snapshot (call before and after every Modal job)."""
        self.ledger.append(self._base("modal_billing") | {"backend": BACKEND_MODAL, "modal_gross_usage_usd": gross_usage_usd,
                                                           "source": source, "verified": bool(verified)})
        if gross_usage_usd is not None and gross_usage_usd >= self.policy.modal_spend_cap_usd:
            self.halt("modal spend cap reached", scope=BACKEND_MODAL, spent=gross_usage_usd, cap=self.policy.modal_spend_cap_usd)
            raise BudgetHalt("modal spend cap reached")

    def reserve_modal(self, usd: float) -> None:
        """Reserve a conservative maximum charge for a Modal job before launch."""
        self._check_modal_ready()
        spent = self.modal_spent_usd() or 0.0
        if spent + self._modal_reserved_usd + usd > self.policy.modal_spend_cap_usd:
            raise BudgetViolation(f"modal reservation {usd} would exceed cap {self.policy.modal_spend_cap_usd} (spent {spent})")
        self._modal_reserved_usd += usd
        self.ledger.append(self._base("modal_reservation") | {"backend": BACKEND_MODAL, "reserved_usd": usd,
                                                               "cumulative_reserved_usd": self._modal_reserved_usd})

    def _check_modal_ready(self) -> None:
        if not self.policy.modal_enabled:
            raise BudgetViolation("Modal is BLOCKED by policy (ops/resource_policy.local.json)")
        age = self._modal_billing_age_s()
        if age is None or age > self.policy.modal_billing_max_age_s:
            raise BudgetViolation("no fresh verified Modal billing snapshot in the ledger")
        verified = [r for r in self.ledger.records() if r.get("event") == "modal_billing"]
        if not verified or not verified[-1].get("verified"):
            raise BudgetViolation("latest Modal billing snapshot is not verified")
        spent = self.modal_spent_usd()
        if spent is None or spent >= self.policy.modal_spend_cap_usd:
            raise BudgetHalt("modal spend unknown or at cap")

    # ---- request admission
    def check_request(self, backend: str, model: str, base_url: str) -> None:
        if self.halted(backend):
            raise BudgetHalt(f"halted: {self.halted(backend)}")
        if backend not in KNOWN_BACKENDS:
            raise BudgetViolation(f"unknown backend {backend!r}")
        if not model or model in FORBIDDEN_MODEL_IDS or model.startswith("openrouter/"):
            raise BudgetViolation(f"forbidden or router-alias model id {model!r}")
        u = urllib.parse.urlparse(base_url)
        host = u.hostname or ""
        if backend == BACKEND_OLLAMA:
            if u.scheme != "http" or not _host_is_loopback(host):
                raise BudgetViolation(f"local backend must be loopback http, got {u.scheme}://{host}")
            if "cloud" in model.lower():
                raise BudgetViolation(f"Ollama cloud models are forbidden: {model!r}")
            if model not in self.policy.local_models:
                raise BudgetViolation(f"local model {model!r} not in allowlist")
        elif backend == BACKEND_OPENROUTER:
            if base_url.rstrip("/") != OPENROUTER_BASE_URL:
                raise BudgetViolation("OpenRouter calls must use https://openrouter.ai/api/v1")
            if model not in self.policy.openrouter_models or not model.endswith(":free"):
                raise BudgetViolation(f"OpenRouter model {model!r} not in $0 allowlist")
            if self.policy.openrouter_require_pricing_check and model not in self._pricing_ok:
                raise BudgetViolation("OpenRouter pricing-zero check not recorded for this run")
            if self.openrouter_attempts_today() >= self.policy.openrouter_daily_cap:
                raise BudgetHalt("OpenRouter daily attempt cap reached (ledger count)")
        elif backend == BACKEND_MODAL:
            if u.scheme != "https" or not host.endswith(".modal.run"):
                raise BudgetViolation("Modal endpoints must be https://*.modal.run")
            if model not in self.policy.modal_models:
                raise BudgetViolation(f"Modal model {model!r} not in allowlist")
            self._check_modal_ready()
        with self._lock:
            if self.calls_started >= self.max_calls:
                raise BudgetViolation(f"per-run call cap {self.max_calls} reached")

    def begin(self, backend: str, model: str, base_url: str, payload: Dict[str, Any], attempt_no: int = 1,
              meta: Optional[Dict[str, Any]] = None) -> Attempt:
        self.check_request(backend, model, base_url)
        if not self._sem.acquire(blocking=False):
            raise BudgetViolation("max_in_flight exceeded")
        with self._lock:
            self.calls_started += 1
        a = Attempt(attempt_id=uuid.uuid4().hex, backend=backend, model=model,
                    base_url_host=urllib.parse.urlparse(base_url).hostname or "",
                    request_sha256=request_sha256(payload), t0=time.monotonic(), attempt_no=attempt_no)
        rec = self._base("attempt_begin") | {"attempt_id": a.attempt_id, "backend": backend, "model_requested": model,
                                             "base_url_host": a.base_url_host, "request_sha256": a.request_sha256,
                                             "attempt_no": attempt_no, "call_index": self.calls_started}
        if meta:
            rec["meta"] = {k: v for k, v in meta.items() if k.lower() not in _FORBIDDEN_LOG_KEYS}
        try:
            self.ledger.append(rec)
        except Exception:
            self._sem.release()
            raise
        return a

    def end(self, a: Attempt, *, status: str, http_status: Optional[int] = None,
            response: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> Dict[str, Any]:
        """Log the outcome and enforce cost rules. Returns the ledger record."""
        try:
            latency_ms = round((time.monotonic() - a.t0) * 1000.0, 1)
            usage = (response or {}).get("usage") or {}
            cost = usage.get("cost") if isinstance(usage, dict) else None
            choices = (response or {}).get("choices") or []
            finish = choices[0].get("finish_reason") if choices else None
            rec = self._base("attempt_end") | {
                "attempt_id": a.attempt_id, "backend": a.backend, "model_requested": a.model,
                "model_resolved": (response or {}).get("model"), "provider": (response or {}).get("provider"),
                "status": status, "http_status": http_status, "finish_reason": finish, "latency_ms": latency_ms,
                "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
                "api_cost_usd": cost if a.backend != BACKEND_OLLAMA else 0.0,
                "new_out_of_pocket_usd": 0.0 if a.backend == BACKEND_OLLAMA else (0.0 if cost == 0 else None),
                "error": scrub(error) if error else None,
            }
            halt_reason = None
            halt_scope: Optional[str] = a.backend
            if a.backend == BACKEND_OPENROUTER and status == "ok":
                if cost is None:
                    halt_reason = "OpenRouter response missing usage.cost (unknown pricing)"
                else:
                    try:
                        if float(cost) > 0:
                            halt_reason = f"OpenRouter reported positive cost {cost}"
                            halt_scope = None  # a real charge halts every backend
                    except (TypeError, ValueError):
                        halt_reason = f"OpenRouter cost unparsable {cost!r}"
                resolved = (response or {}).get("model")
                if resolved and resolved != a.model and not halt_reason:
                    halt_reason = f"OpenRouter resolved a different model {resolved!r}"
                bd = usage.get("cost_details") if isinstance(usage, dict) else None
                if isinstance(bd, dict) and not halt_reason:
                    for k, v in bd.items():
                        if isinstance(v, (int, float)) and v > 0:
                            halt_reason = f"OpenRouter cost_details.{k}={v}"
                            halt_scope = None
            self.ledger.append(rec)
            if halt_reason:
                self.halt(halt_reason, scope=halt_scope, attempt_id=a.attempt_id)
                raise BudgetHalt(halt_reason)
            return rec
        finally:
            self._sem.release()

    def close(self, note: str = "") -> None:
        self.ledger.append(self._base("run_close") | {"calls_started": self.calls_started, "note": scrub(note)})


# --------------------------------------------------------------------------- keys


def _read_key_by_name(name: str, env_files: Iterable[Path]) -> Optional[str]:
    val = os.environ.get(name)
    if val:
        return val
    for f in env_files:
        try:
            for line in Path(f).read_text().splitlines():
                line = line.strip()
                if line.startswith(name + "="):
                    v = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v
        except OSError:
            continue
    return None


def api_key_for(backend: str, key_env_name: Optional[str] = None) -> str:
    """Return the credential for a backend without ever printing it.
    Local Ollama gets a placeholder; the OpenRouter key is only returned for the OpenRouter backend."""
    if backend == BACKEND_OLLAMA:
        return "ollama"
    if backend == BACKEND_OPENROUTER:
        k = _read_key_by_name("OPENROUTER_API_KEY", [REPO_ROOT / ".env", REPO_ROOT / "starter/collusion_hackathon/compute.env"])
        if not k:
            raise BudgetViolation("OPENROUTER_API_KEY not available")
        return k
    if backend == BACKEND_MODAL:
        if not key_env_name or "OPENROUTER" in key_env_name.upper():
            raise BudgetViolation("Modal endpoint needs its own key env name (never the OpenRouter key)")
        return _read_key_by_name(key_env_name, []) or "EMPTY"
    raise BudgetViolation(f"unknown backend {backend!r}")


# --------------------------------------------------------------------------- client

Transport = Callable[[str, Dict[str, str], bytes, float], Tuple[int, bytes]]


def urllib_transport(url: str, headers: Dict[str, str], body: bytes, timeout: float) -> Tuple[int, bytes]:
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


class GuardedChatClient:
    """OpenAI-compatible chat client with the TogetherClient interface, routed through a BudgetGuard.

    Differences from Terrarium's TogetherClient (deliberate):
    * passes ``seed``/``top_p``/``top_k``/``reasoning_effort`` when given;
    * no hidden retries: at most ``policy.max_retries`` retries on 429/5xx/connection errors, each a
      separately logged and capped attempt; OpenRouter 429 halts immediately (quota);
    * OpenRouter requests carry ``usage.include=true`` and provider preferences that forbid fallbacks
      and any nonzero price; no ``models`` fallback list, no plugins/web search.
    """

    PASS_THROUGH = ("temperature", "top_p", "top_k", "seed", "reasoning_effort", "stop", "tool_choice")
    # Backends whose provider response ids are globally unique. Ollama's OpenAI-compatible endpoint
    # returns repeating ids (e.g. "chatcmpl-NN"), so only the client request id proves freshness there.
    UNIQUE_RESPONSE_ID_BACKENDS = (BACKEND_OPENROUTER,)

    def __init__(self, guard: BudgetGuard, *, backend: str, model: str, base_url: str,
                 request_timeout: float = 300.0, key_env_name: Optional[str] = None,
                 transport: Optional[Transport] = None, fixed_params: Optional[Dict[str, Any]] = None,
                 meta: Optional[Dict[str, Any]] = None):
        guard.check_request(backend, model, base_url)  # fail fast at construction
        self.guard = guard
        self.backend = backend
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = float(request_timeout)
        self._key_env_name = key_env_name
        self.transport = transport or urllib_transport
        self.fixed_params = dict(fixed_params or {})
        self.meta = dict(meta or {})
        self.last_attempt_records: List[Dict[str, Any]] = []
        self.unique_response_ids = backend in self.UNIQUE_RESPONSE_ID_BACKENDS
        # Freshness key for the call that succeeded: the UUID4 attempt_id already logged in the ledger
        # (attempt_begin / attempt_end), so every recorded generation joins to its ledger rows.
        self.last_request_id: Optional[str] = None

    # --- TogetherClient-compatible helpers
    @staticmethod
    def init_context(system_prompt: str, user_prompt: str) -> List[Dict[str, Any]]:
        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    @staticmethod
    def get_usage(response: Dict[str, Any], current_usage: Dict[str, int]) -> Dict[str, int]:
        usage = response.get("usage") or {}
        current_usage["prompt_tokens"] += usage.get("prompt_tokens", 0) or 0
        current_usage["completion_tokens"] += usage.get("completion_tokens", 0) or 0
        current_usage["total_tokens"] = current_usage["prompt_tokens"] + current_usage["completion_tokens"]
        return current_usage

    @staticmethod
    def _content(message: Dict[str, Any]) -> str:
        c = (message or {}).get("content")
        if isinstance(c, str):
            return c
        if isinstance(c, list):
            return "".join(i.get("text", "") for i in c if isinstance(i, dict) and i.get("type") == "text")
        return ""

    def build_payload(self, messages: List[Dict[str, Any]], params: Dict[str, Any]) -> Dict[str, Any]:
        p = dict(params or {})
        p.update(self.fixed_params)
        requested = p.get("model") or self.model
        if requested != self.model:
            raise BudgetViolation(f"params model {requested!r} != pinned model {self.model!r}")
        payload: Dict[str, Any] = {"model": self.model, "messages": messages}
        mt = p.get("max_tokens") or p.get("max_completion_tokens") or p.get("max_output_tokens")
        if mt:
            payload["max_tokens"] = int(mt)
        for k in self.PASS_THROUGH:
            if p.get(k) is not None:
                payload[k] = p[k]
        tools = [t for t in (p.get("tools") or []) if isinstance(t, dict) and t.get("type") == "function"]
        if tools:
            payload["tools"] = [{"type": "function", "function": {"name": t["function"].get("name"),
                                 "description": t["function"].get("description", ""),
                                 "parameters": t["function"].get("parameters", {})}} for t in tools]
        if self.backend == BACKEND_OPENROUTER:
            payload["usage"] = {"include": True}
            payload["provider"] = {"allow_fallbacks": False,
                                   "max_price": {"prompt": 0, "completion": 0, "request": 0, "image": 0}}
            for k in ("models", "plugins", "route", "web_search_options"):
                payload.pop(k, None)
        return payload

    def generate_response(self, input: List[Dict[str, Any]], params: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        payload = self.build_payload(input, params)
        body = json.dumps(payload).encode()
        url = f"{self.base_url}/chat/completions"
        self.last_attempt_records = []
        self.last_request_id = None
        last_err = None
        for attempt_no in range(1, self.guard.policy.max_retries + 2):
            a = self.guard.begin(self.backend, self.model, self.base_url, payload, attempt_no=attempt_no, meta=self.meta)
            headers = {"Content-Type": "application/json",
                       "Authorization": f"Bearer {api_key_for(self.backend, self._key_env_name)}"}
            try:
                code, raw = self.transport(url, headers, body, self.timeout)
            except Exception as exc:  # connection error / timeout
                rec = self.guard.end(a, status="transport_error", error=f"{type(exc).__name__}: {exc}")
                self.last_attempt_records.append(rec)
                last_err = rec["error"]
                time.sleep(min(2 ** attempt_no, 10))
                continue
            data: Dict[str, Any] = {}
            try:
                data = json.loads(raw.decode() or "{}")
            except ValueError:
                data = {}
            if 200 <= code < 300 and isinstance(data, dict) and data.get("choices"):
                rec = self.guard.end(a, status="ok", http_status=code, response=data)
                self.last_attempt_records.append(rec)
                self.last_request_id = a.attempt_id
                msg = data["choices"][0].get("message") or {}
                return data, self._content(msg)
            status = "http_error" if code >= 300 else "empty_response"
            rec = self.guard.end(a, status=status, http_status=code, error=raw[:400].decode(errors="replace"))
            self.last_attempt_records.append(rec)
            last_err = rec["error"]
            if self.backend == BACKEND_OPENROUTER and code in (402, 429):
                self.guard.halt(f"OpenRouter HTTP {code} (quota/credit)", scope=BACKEND_OPENROUTER, attempt_id=a.attempt_id)
                raise BudgetHalt(f"OpenRouter HTTP {code}; halting (quota/credit)")
            if code not in (429, 500, 502, 503, 504) and status == "http_error":
                break
            time.sleep(min(2 ** attempt_no, 10))
        raise RuntimeError(f"guarded request failed: {last_err}")

    async def process_tool_calls(self, response: Dict[str, Any], context: List[Dict[str, Any]],
                                 execute_tool_callback: Any) -> Tuple[int, List[Dict[str, Any]], List[str]]:
        """Same semantics as Terrarium TogetherClient.process_tool_calls."""
        choices = response.get("choices") or []
        if not choices:
            return 0, context, []
        message = choices[0].get("message") or {}
        context.append(message)
        executed, step_tools = 0, []
        for call in message.get("tool_calls") or []:
            fn = call.get("function") or {}
            name = fn.get("name", "unknown_tool")
            raw = fn.get("arguments") or "{}"
            try:
                args = json.loads(raw) if isinstance(raw, str) else dict(raw)
            except (ValueError, TypeError):
                args = {}
            step_tools.append(f"{name} -- {json.dumps(args)}")
            result = await execute_tool_callback(name, args)
            context.append({"role": "tool", "tool_call_id": call.get("id"), "name": name, "content": json.dumps(result)})
            executed += 1
        return executed, context, step_tools
