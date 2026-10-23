"""Offline model clients: a scripted (fake) LLM and a hash-checked prefix-replay client.

Both subclass Terrarium's ``TogetherClient`` (the client Colosseum's ``provider: openrouter``
route actually uses, ``experiments/common/providers.py::make_openrouter_client``) but never call
its ``__init__`` and never touch ``requests``: ``init_context``, ``get_usage`` and
``process_tool_calls`` are inherited unchanged, so the message/tool-call bookkeeping that feeds
the next request is exactly upstream's.
"""

from __future__ import annotations

import itertools
import random
import json
import threading
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from ccc.adapters.colosseum import ensure_import_path

from .canonical import deep_copy_json, request_sha256
from .recorder import RequestRecord, request_payload

ensure_import_path()
from llm_server.clients.together_client import TogetherClient  # noqa: E402


class PrefixMismatch(RuntimeError):
    """A reconstruction request differs from the recorded request (V02 failure)."""


@dataclass(frozen=True)
class PolicyCall:
    agent: str
    phase: str
    planning_round: Optional[int]
    turn_index: int
    step: int
    messages: List[Dict[str, Any]]
    tool_names: List[str]

    @property
    def text(self) -> str:
        """All text the model would see (system, user, assistant, tool) concatenated."""
        parts = []
        for m in self.messages:
            c = m.get("content")
            if isinstance(c, str):
                parts.append(c)
            for tc in m.get("tool_calls") or []:
                parts.append(json.dumps(tc, sort_keys=True))
        return "\n".join(parts)

    @property
    def user_prompt(self) -> str:
        return next((m.get("content") or "" for m in self.messages if m.get("role") == "user"), "")


Policy = Callable[[PolicyCall], Dict[str, Any]]
"""A policy returns {"content": str, "tool_calls": [{"name": str, "arguments": dict}, ...]}."""


class ScriptedClient(TogetherClient):
    """Deterministic fake LLM. Every call is a *new* call (cache_mode=fresh) with a unique id."""

    cache_mode = "fresh"
    accepts_ccc_context = True
    _ids = itertools.count()
    _ids_lock = threading.Lock()

    def __init__(self, policy: Policy, *, nonce: str):  # noqa: D401 - no super().__init__ on purpose
        self.policy = policy
        self.nonce = nonce
        self.calls = 0

    def generate_response(self, input, params, ccc_context: Optional[Dict[str, Any]] = None):  # noqa: A002
        ctx = ccc_context or {}
        tool_names = [((t or {}).get("function") or {}).get("name") for t in (params.get("tools") or [])]
        call = PolicyCall(agent=ctx.get("agent", ""), phase=ctx.get("phase", ""),
                          planning_round=ctx.get("planning_round"), turn_index=ctx.get("turn_index", -1),
                          step=ctx.get("step", 0), messages=deep_copy_json(input),
                          tool_names=[n for n in tool_names if n])
        out = self.policy(call) or {}
        calls = []
        for i, tc in enumerate(out.get("tool_calls") or []):
            calls.append({"id": f"call_t{call.turn_index}_s{call.step}_{i}", "type": "function",
                          "function": {"name": tc["name"],
                                       "arguments": json.dumps(tc.get("arguments") or {}, sort_keys=True)}})
        message: Dict[str, Any] = {"role": "assistant", "content": str(out.get("content") or "")}
        if calls:
            message["tool_calls"] = calls
        with self._ids_lock:
            uid = next(self._ids)
        self.calls += 1
        response = {"id": f"scripted:{self.nonce}:{uid}", "object": "chat.completion",
                    "model": params.get("model"),
                    "choices": [{"index": 0, "message": message,
                                 "finish_reason": "tool_calls" if calls else "stop"}],
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}
        return response, message["content"]


class ReplaySource:
    """Recorded prefix responses in global call order, consumed exactly once."""

    def __init__(self, records: List[RequestRecord]):
        self.records = sorted(records, key=lambda r: r.seq)
        self.pos = 0
        self.lock = threading.Lock()
        self.errors: List[str] = []  # upstream BaseAgent swallows continuation-step exceptions; keep them

    def _fail(self, msg: str):
        self.errors.append(msg)
        raise PrefixMismatch(msg)

    def next(self, ctx: Dict[str, Any], payload: Dict[str, Any]) -> RequestRecord:
        with self.lock:
            if self.pos >= len(self.records):
                self._fail(f"unexpected extra request at turn {ctx.get('turn_index')} by {ctx.get('agent')}")
            rec = self.records[self.pos]
            sha = request_sha256(payload)
            if (rec.agent, rec.turn_index, rec.step) != (ctx.get("agent"), ctx.get("turn_index"), ctx.get("step")):
                self._fail(f"order mismatch at seq {rec.seq}: recorded {(rec.agent, rec.turn_index, rec.step)} "
                                     f"got {(ctx.get('agent'), ctx.get('turn_index'), ctx.get('step'))}")
            if sha != rec.request_sha256:
                self._fail(f"request hash mismatch at seq {rec.seq} ({rec.agent} turn {rec.turn_index} "
                                     f"step {rec.step}): recorded {rec.request_sha256[:12]} got {sha[:12]}")
            self.pos += 1
            return rec

    @property
    def exhausted(self) -> bool:
        return self.pos == len(self.records)


class ReplayClient(TogetherClient):
    """Returns recorded responses for the pre-boundary prefix; refuses any unrecorded request."""

    cache_mode = "prefix_replay"
    accepts_ccc_context = True

    def __init__(self, source: ReplaySource):
        self.source = source

    def generate_response(self, input, params, ccc_context: Optional[Dict[str, Any]] = None):  # noqa: A002
        rec = self.source.next(ccc_context or {}, request_payload(input, params))
        response = deep_copy_json(rec.response)
        if rec.python_rng_state_after is not None:
            st = rec.python_rng_state_after
            random.setstate((st[0], tuple(st[1]), st[2]))
        choices = response.get("choices") or []
        msg = choices[0]["message"] if choices else {"content": ""}
        return response, self._extract_message_content(msg)


class ReusingClient(TogetherClient):
    """DELIBERATELY INVALID: hands back recorded source responses after the fork.

    Exists only so tests can prove the freshness validator (V09/V10) rejects cached reuse.
    """

    cache_mode = "fresh"  # lies about its mode, as an accidental cache would
    accepts_ccc_context = True

    def __init__(self, recorded: List[RequestRecord]):
        self.queue = {}
        for r in recorded:
            self.queue.setdefault((r.agent, r.step), []).append(r)

    def generate_response(self, input, params, ccc_context: Optional[Dict[str, Any]] = None):  # noqa: A002
        ctx = ccc_context or {}
        q = self.queue.get((ctx.get("agent"), ctx.get("step"))) or []
        rec = q.pop(0) if q else None
        response = deep_copy_json(rec.response) if rec else {"id": None, "choices": [{"message": {"role": "assistant", "content": ""}}]}
        msg = response["choices"][0]["message"]
        return response, self._extract_message_content(msg)
