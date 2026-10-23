"""Model-request recorder.

Hook point: the per-agent client object that ``terrarium.agents.base.BaseAgent`` calls
(``init_context`` / ``generate_response`` / ``process_tool_calls`` / ``get_usage``; see
``BaseAgent._multi_step_response_generation``). Wrapping the client records every submitted
request exactly as the upstream agent built it, without patching upstream code.

Never records headers or credentials: the wrapped client builds those internally and they are
not part of ``(input, params)``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .canonical import deep_copy_json, request_sha256

CACHE_MODES = ("prefix_replay", "fresh", "analysis_only")


@dataclass
class RequestRecord:
    seq: int                      # global order within one world execution
    branch_id: str
    replicate_id: str
    turn_index: int
    agent: str
    phase: str
    planning_round: Optional[int]
    step: int                     # 1-based model call within the agent turn
    request: Dict[str, Any]       # {"messages": [...], "params": {...}} as submitted
    request_sha256: str
    response: Dict[str, Any]
    response_id: Optional[str]
    cache_mode: str
    finish_reason: Optional[str]
    latency_ms: Optional[float]
    status: str = "complete"
    error: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class CallLedger:
    records: List[RequestRecord] = field(default_factory=list)

    def for_agent(self, agent: str) -> List[RequestRecord]:
        return [r for r in self.records if r.agent == agent]

    def at_or_after(self, turn_index: int) -> List[RequestRecord]:
        return [r for r in self.records if r.turn_index >= turn_index]

    def before(self, turn_index: int) -> List[RequestRecord]:
        return [r for r in self.records if r.turn_index < turn_index]


def request_payload(input_messages: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    return {"messages": deep_copy_json(input_messages), "params": deep_copy_json(params)}


class RecordingClient:
    """Transparent wrapper around an upstream-compatible client."""

    def __init__(self, inner: Any, ledger: CallLedger, context: Callable[[], Dict[str, Any]]):
        self._inner = inner
        self._ledger = ledger
        self._context = context
        self._steps: Dict[tuple, int] = {}

    # --- AbstractClient surface used by BaseAgent ---------------------------------------
    def init_context(self, system_prompt: str, user_prompt: str):
        return self._inner.init_context(system_prompt, user_prompt)

    def get_usage(self, response: Any, current_usage: Dict[str, int]):
        return self._inner.get_usage(response, current_usage)

    async def process_tool_calls(self, response, context, execute_tool_callback):
        return await self._inner.process_tool_calls(response, context, execute_tool_callback)

    def generate_response(self, input, params):  # noqa: A002 - upstream signature
        ctx = dict(self._context())
        key = (ctx["turn_index"], ctx["agent"])
        step = self._steps.get(key, 0) + 1
        self._steps[key] = step
        payload = request_payload(input, params)
        sha = request_sha256(payload)
        ctx["step"] = step
        ctx["request_sha256"] = sha
        t0 = time.perf_counter()
        status, error = "complete", None
        try:
            response, text = self._inner.generate_response(input=input, params=params, **_ccc_kwargs(self._inner, ctx))
        except Exception as exc:  # recorded as failed, never as a numeric outcome
            status, error = "failed", f"{type(exc).__name__}: {exc}"
            self._append(ctx, payload, sha, {}, status, error, (time.perf_counter() - t0) * 1000)
            raise
        self._append(ctx, payload, sha, response, status, error, (time.perf_counter() - t0) * 1000)
        return response, text

    def _append(self, ctx, payload, sha, response, status, error, latency_ms):
        resp = deep_copy_json(response) if isinstance(response, dict) else {"repr": repr(response)}
        choices = resp.get("choices") or [{}]
        self._ledger.records.append(RequestRecord(
            seq=len(self._ledger.records), branch_id=ctx["branch_id"], replicate_id=ctx["replicate_id"],
            turn_index=ctx["turn_index"], agent=ctx["agent"], phase=ctx["phase"],
            planning_round=ctx.get("planning_round"), step=ctx["step"], request=payload,
            request_sha256=sha, response=resp, response_id=resp.get("id"),
            cache_mode=getattr(self._inner, "cache_mode", "fresh"),
            finish_reason=(choices[0] or {}).get("finish_reason"), latency_ms=latency_ms,
            status=status, error=error))

    def __getattr__(self, name):
        return getattr(self._inner, name)


def _ccc_kwargs(inner: Any, ctx: Dict[str, Any]) -> Dict[str, Any]:
    """CCC clients accept the logical call context; upstream clients do not."""
    return {"ccc_context": ctx} if getattr(inner, "accepts_ccc_context", False) else {}
