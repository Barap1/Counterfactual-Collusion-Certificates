"""Interventions as pure transformations of one receiver's observation view.

A view is ``{blackboard_id: [event, ...]}`` exactly as ``Megaboard.get`` returns it for that
receiver at that turn. Hooks never touch the underlying Megaboard (other agents' views, the
environment, and the sender's action are unchanged), never mutate their input, and return
``(delivered_view, machine_readable_diff)``. Rendering is always done by the upstream
``format_blackboard_events_for_prompt``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .canonical import deep_copy_json

MASK_VERSION = "ccc.receiver_mask.v1"
SHAM_VERSION = "ccc.sham_identity.v1"
REPEATED_EXPOSURE_POLICIES = ("persistent", "single")


@dataclass(frozen=True)
class ExposureSpec:
    event_id: str
    sender: str
    receiver: str
    blackboard_id: str
    channel_participants: Tuple[str, ...]
    content: str
    posted_turn: int
    first_exposure_turn: int
    copy_event_ids: Tuple[str, ...] = ()
    repeated_exposure_policy: str = "persistent"
    mask_end: Optional[int] = None          # inclusive turn index; None = end of episode
    observation_surface: str = "prefetched_blackboard_context"

    def __post_init__(self):
        if self.repeated_exposure_policy not in REPEATED_EXPOSURE_POLICIES:
            raise ValueError(f"repeated_exposure_policy must be one of {REPEATED_EXPOSURE_POLICIES}")

    @property
    def mask_start(self) -> int:
        return self.first_exposure_turn

    @property
    def masked_ids(self) -> Tuple[str, ...]:
        return (self.event_id,) + tuple(self.copy_event_ids)

    def in_horizon(self, turn_index: int) -> bool:
        if turn_index < self.mask_start:
            return False
        if self.repeated_exposure_policy == "single":
            return turn_index == self.mask_start
        return self.mask_end is None or turn_index <= self.mask_end

    def to_json(self) -> Dict[str, Any]:
        d = asdict(self)
        d["mask_start"] = self.mask_start
        d["mask_version"] = MASK_VERSION
        return d


def sham_hook():
    """Arm S: run the receiver's view through the intervention path with the identity transform."""

    def hook(agent: str, turn_index: int, view: Dict[str, List[Dict[str, Any]]]):
        return deep_copy_json(view), {"arm": "S", "version": SHAM_VERSION, "agent": agent,
                                      "turn_index": turn_index, "removed": []}

    return hook


def receiver_mask_hook(exposure: ExposureSpec):
    """Arm K: withhold the declared event (and declared copies) from the receiver only."""
    masked = set(exposure.masked_ids)

    def hook(agent: str, turn_index: int, view: Dict[str, List[Dict[str, Any]]]):
        out = deep_copy_json(view)
        removed: List[Dict[str, Any]] = []
        if agent == exposure.receiver and exposure.in_horizon(turn_index):
            for bb, events in out.items():
                kept = []
                for idx, ev in enumerate(events, start=1):
                    if ev.get("id") in masked and ev.get("kind") == "communication":
                        removed.append({"blackboard_id": bb, "event_id": ev.get("id"), "rendered_index": idx,
                                        "later_indices_shift": 0})
                    else:
                        kept.append(ev)
                out[bb] = kept
        return out, {"arm": "K", "version": MASK_VERSION, "agent": agent, "turn_index": turn_index,
                     "active": agent == exposure.receiver and exposure.in_horizon(turn_index), "removed": removed}

    return hook


def leaky_summary_mask_hook(exposure: ExposureSpec):
    """DELIBERATELY INVALID (tests only): masks the event but re-renders it inside a 'summary'
    context event, the way a memory/summary feature would leak a removed message."""
    base = receiver_mask_hook(exposure)

    def hook(agent, turn_index, view):
        out, diff = base(agent, turn_index, view)
        if diff["active"] and out:
            first_bb = sorted(out, key=int)[0]
            out[first_bb] = list(out[first_bb]) + [{"id": "summary", "agent": "SYSTEM", "kind": "context",
                                                   "payload": {"message": f"Summary of earlier messages: {exposure.content}"}}]
        diff["version"] = "LEAKY-TEST-ONLY"
        return out, diff

    return hook


def neutral_placebo_hook(exposure: ExposureSpec):
    """N: replace E* content only, at the same index and exactly matched character length."""
    from .neutral import FILLERS
    import hashlib

    def hook(agent, turn_index, view):
        out = deep_copy_json(view)
        changed = []
        if agent == exposure.receiver and exposure.in_horizon(turn_index):
            for board, events in out.items():
                for event in events:
                    if event.get("id") in exposure.masked_ids and event.get("kind") == "communication":
                        text = str((event.get("payload") or {}).get("content") or "")
                        slot = int(hashlib.sha256(event["id"].encode()).hexdigest(), 16) % len(FILLERS)
                        filler = FILLERS[slot]
                        event["payload"]["content"] = (filler * (len(text) // len(filler) + 1))[:len(text)]
                        changed.append(event["id"])
        return out, {"arm": "N", "replaced": changed}
    return hook


def channel_mask_hook(exposure: ExposureSpec):
    """C: K plus every sender communication on P, including fresh post-fork posts."""
    def hook(agent, turn_index, view):
        out = deep_copy_json(view)
        removed = []
        if agent == exposure.receiver and exposure.in_horizon(turn_index):
            for board, events in out.items():
                kept = []
                for event in events:
                    if event.get("kind") == "communication" and (event.get("id") in exposure.masked_ids or
                            (str(board) == str(exposure.blackboard_id) and event.get("agent") == exposure.sender)):
                        removed.append(event["id"])
                    else:
                        kept.append(event)
                out[board] = kept
        return out, {"arm": "C", "removed": removed}
    return hook
