"""Helpers for writing deterministic scripted policies over the real Jira prompts.

A policy sees only what the model would see (``PolicyCall.messages``); these helpers parse the
upstream ``JiraTicketPrompts`` / ``CollusionPrompts`` rendering.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .clients import PolicyCall


def me(call: PolicyCall) -> str:
    m = re.search(r"^You are agent (\S+)", call.user_prompt, re.M)
    return m.group(1) if m else call.agent


def coalition_blackboard(call: PolicyCall) -> Optional[str]:
    m = re.search(r"^Collusion blackboard_id: (\d+)", call.user_prompt, re.M)
    return m.group(1) if m else None


def blackboards(call: PolicyCall) -> Dict[str, str]:
    """{blackboard_id: rendered text} from the '=== BLACKBOARD COMMUNICATIONS ===' section."""
    text = call.user_prompt
    start = text.find("=== BLACKBOARD COMMUNICATIONS ===")
    if start < 0:
        return {}
    body = text[start:].split("\n=== CURRENT PHASE", 1)[0]
    out: Dict[str, str] = {}
    for m in re.finditer(r"^Blackboard (\d+):\n(.*?)(?=^Blackboard \d+:|\Z)", body, re.M | re.S):
        out[m.group(1)] = m.group(2).strip()
    return out


def tasks(call: PolicyCall) -> List[Dict[str, str]]:
    return [{"id": m.group(1), "priority": m.group(2)}
            for m in re.finditer(r"^- (\S+): .*?\| priority=(\w+) \|", call.user_prompt, re.M)]


def costs(call: PolicyCall) -> Dict[str, float]:
    sec = call.user_prompt.split("=== YOUR COSTS (PRIVATE) ===", 1)
    if len(sec) < 2:
        return {}
    out = {}
    for m in re.finditer(r"^- (\S+): cost=([0-9.]+)", sec[1].split("\n\n", 1)[0], re.M):
        out[m.group(1)] = float(m.group(2))
    return out


def assigned_tasks(call: PolicyCall) -> List[str]:
    sec = call.user_prompt.split("=== CURRENT ASSIGNMENTS ===", 1)
    if len(sec) < 2:
        return []
    return [m.group(1) for m in re.finditer(r"^- \S+: (\S+)", sec[1].split("\n\n", 1)[0], re.M) if m.group(1) != "None"]


def is_first_step(call: PolicyCall) -> bool:
    return not any(m.get("role") in ("assistant", "tool") for m in call.messages)


def post(message: str, blackboard_id: Any) -> Dict[str, Any]:
    return {"name": "post_message", "arguments": {"message": message, "blackboard_id": int(blackboard_id)}}


def assign(task_id: str) -> Dict[str, Any]:
    return {"name": "assign_task", "arguments": {"task_id": task_id}}
