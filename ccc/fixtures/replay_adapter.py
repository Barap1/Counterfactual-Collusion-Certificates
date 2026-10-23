"""Dependency-free adapter to ccc.replay.clients.Policy / PolicyCall.

``ScriptedClient(make_policy(world), nonce=...)`` accepts this callable. The
fixture's private structural rule stays in the Python closure, never a prompt.
This adapter does not claim a fixture is a Jira snapshot or change that engine.
"""

from __future__ import annotations

from typing import Any, Protocol

from .runner import assert_blinded, canonical, detector_input
from .worlds import FixtureWorld


class PolicyCallLike(Protocol):
    agent: str
    messages: list[dict[str, Any]]
    tool_names: list[str]


def policy_messages(world: FixtureWorld, arm: str = "F", *, joint_mask: bool = False,
                    agent_id: str | None = None) -> list[dict]:
    """Public payload as a legal chat request, for the offline scripted client.

    Replay validators must validate the full audit payload before issuing this
    call. Each agent request contains ONLY that agent's read surfaces: a masked
    receiver must never receive the sender's intact copy in another field.
    """
    payload = detector_input(world, arm, joint_mask=joint_mask)
    agent_id = world.receiver if agent_id is None else agent_id
    if agent_id not in world.agents:
        raise ValueError("unknown agent")
    payload["observations"] = [o for o in payload["observations"] if o["agent_id"] == agent_id]
    return [{"role": "user", "content": canonical(payload)}]


def make_policy(world: FixtureWorld):
    """Return a ``PolicyCall -> {content, tool_calls}`` scripted policy.

    This is the deterministic structural decision, before optional execution
    noise in ``run_branch``. Use ``commit_dispatch`` if that tool is offered;
    otherwise return the same structured decision in assistant content.
    """
    import json

    def policy(call: PolicyCallLike) -> dict:
        user = next((m.get("content") for m in reversed(call.messages) if m.get("role") == "user"), None)
        if not isinstance(user, str):
            raise ValueError("fixture policy requires a public fixture payload")
        payload = json.loads(user)
        assert_blinded(payload)
        if payload["world_id"] != world.world_id:
            raise ValueError("world identity mismatch")
        own_reads = [o for o in payload["observations"] if o["agent_id"] == call.agent]
        if not own_reads or len(own_reads) != len(payload["observations"]):
            raise ValueError("unknown agent")
        if call.agent == world.sender:
            decision = {"text": world.message}
        elif call.agent == world.receiver:
            primary = any(e["event_id"] == "event_0" for o in own_reads for e in o["messages"])
            secondary = any(e["event_id"] == "event_1" for o in own_reads for e in o["messages"])
            if world.rule in ("shared", "committed"):
                # The receiver uses its delivered state, not an unseen message.
                active = own_reads[0]["shared_state"] == "route"
            else:
                active = world.action(primary, secondary, True)
            decision = {"action": "route" if active else "base"}
        else:
            decision = {"action": "wait"}
        if call.agent == world.receiver and "commit_dispatch" in call.tool_names:
            return {"content": "", "tool_calls": [{"name": "commit_dispatch", "arguments": decision}]}
        return {"content": canonical(decision), "tool_calls": []}

    return policy
