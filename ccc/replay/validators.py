"""Validity checks (module 10 test matrix IDs). Each returns a CheckResult; none raises on failure."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .recorder import RequestRecord

PASS, FAIL, UNKNOWN, NA = "pass", "fail", "unknown", "not_applicable"


@dataclass
class CheckResult:
    id: str
    name: str
    status: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "status": self.status, "details": self.details}


def ok(results: Iterable[CheckResult]) -> bool:
    return all(r.status in (PASS, NA) for r in results)


# ----------------------------------------------------------------------------------------------
# Leak detection: content fingerprints over everything the receiver's model actually received
# ----------------------------------------------------------------------------------------------
def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def _shingles(text: str, k: int = 8) -> set:
    toks = _norm(text).split(" ")
    return {" ".join(toks[i:i + k]) for i in range(max(0, len(toks) - k + 1))}


def request_text(rec_or_payload: Any) -> List[tuple]:
    """[(surface, text)] for every message/tool argument in one submitted request."""
    payload = rec_or_payload.request if isinstance(rec_or_payload, RequestRecord) else rec_or_payload
    out = []
    for i, m in enumerate(payload.get("messages") or []):
        if isinstance(m.get("content"), str):
            out.append((f"messages[{i}].{m.get('role')}", m["content"]))
        for j, tc in enumerate(m.get("tool_calls") or []):
            out.append((f"messages[{i}].tool_calls[{j}]", json.dumps(tc, sort_keys=True)))
    return out


def find_content(content: str, texts: List[tuple], event_ids: Sequence[str] = (), *, k: int = 8,
                 min_overlap: float = 0.5) -> List[Dict[str, Any]]:
    """Heuristic: exact normalized substring, >= min_overlap of k-token shingles, or a raw event id.
    Absence of a hit is NOT proof the information is absent (paraphrase is undetected)."""
    needle = _norm(content)
    sh = _shingles(content, k)
    hits = []
    for surface, text in texts:
        t = _norm(text)
        if needle and needle in t:
            hits.append({"surface": surface, "match": "exact"})
            continue
        if sh:
            frac = len(sh & _shingles(text, k)) / len(sh)
            if frac >= min_overlap:
                hits.append({"surface": surface, "match": "shingle", "overlap": round(frac, 3)})
                continue
        for eid in event_ids:
            if eid and eid in text:
                hits.append({"surface": surface, "match": "event_id", "event_id": eid})
                break
    return hits


# ----------------------------------------------------------------------------------------------
# V08 tool protocol
# ----------------------------------------------------------------------------------------------
def tool_protocol_errors(payload: Dict[str, Any]) -> List[str]:
    msgs = payload.get("messages") or []
    errs: List[str] = []
    if len(msgs) < 2 or msgs[0].get("role") != "system" or msgs[1].get("role") != "user":
        errs.append("request must start with system, user")
    seen_ids = set()
    i = 2
    while i < len(msgs):
        m = msgs[i]
        role = m.get("role")
        if role == "assistant":
            calls = m.get("tool_calls") or []
            for n, tc in enumerate(calls):
                cid = tc.get("id")
                if not cid or cid in seen_ids:
                    errs.append(f"messages[{i}] tool_call {n}: missing or duplicate id {cid!r}")
                seen_ids.add(cid)
                try:
                    json.loads((tc.get("function") or {}).get("arguments") or "{}")
                except json.JSONDecodeError:
                    errs.append(f"messages[{i}] tool_call {n}: arguments not JSON")
                nxt = msgs[i + 1 + n] if i + 1 + n < len(msgs) else None
                if not nxt or nxt.get("role") != "tool" or nxt.get("tool_call_id") != cid:
                    errs.append(f"messages[{i}] tool_call {cid!r}: not followed by its tool result in order")
            i += 1 + len(calls)
        elif role == "tool":
            errs.append(f"messages[{i}]: orphan tool result {m.get('tool_call_id')!r}")
            i += 1
        else:
            errs.append(f"messages[{i}]: unexpected role {role!r} after the prompt")
            i += 1
    return errs


def check_tool_protocol(records: Sequence[RequestRecord]) -> CheckResult:
    bad = {}
    for r in records:
        e = tool_protocol_errors(r.request)
        if e:
            bad[r.seq] = e
    return CheckResult("V08", "tool_protocol", FAIL if bad else PASS, {"requests_checked": len(records), "errors": bad})


# ----------------------------------------------------------------------------------------------
# V09/V10 freshness and cache-mode integrity
# ----------------------------------------------------------------------------------------------
def check_fresh(branch_records: Sequence[RequestRecord], boundary: int, source_response_ids: set,
                other_branch_response_ids: set = frozenset()) -> CheckResult:
    d: Dict[str, Any] = {"post_fork_requests": len(branch_records)}
    problems = []
    if not branch_records:
        problems.append("no model requests after the fork (continuation not regenerated)")
    if any(r.turn_index < boundary for r in branch_records):
        problems.append("branch issued requests before the boundary (prefix must come from the checkpoint)")
    modes = sorted({r.cache_mode for r in branch_records})
    d["cache_modes"] = modes
    if modes and modes != ["fresh"]:
        problems.append(f"cache_mode mixture after fork: {modes}")
    ids = [r.response_id for r in branch_records]
    if any(i is None for i in ids):
        problems.append("response without id (cannot prove freshness)")
    if len(set(ids)) != len(ids):
        problems.append("duplicate response ids within branch")
    reused = sorted({i for i in ids if i in source_response_ids})
    if reused:
        problems.append(f"{len(reused)} response(s) reused from the source run")
    cross = sorted({i for i in ids if i in other_branch_response_ids})
    if cross:
        problems.append(f"{len(cross)} response(s) shared with another branch/replicate")
    failed = [r.seq for r in branch_records if r.status != "complete"]
    if failed:
        problems.append(f"failed requests: {failed}")
    d["problems"] = problems
    return CheckResult("V09", "fresh_continuation", FAIL if problems else PASS, d)


# ----------------------------------------------------------------------------------------------
# V06/V07 exposure integrity (prior exposure, persistent-mask leaks)
# ----------------------------------------------------------------------------------------------
def check_prior_exposure(exposure, boundary: int, observations: List[Dict[str, Any]],
                         source_records: Sequence[RequestRecord]) -> CheckResult:
    masked = set(exposure.masked_ids)
    prior_views = [o for o in observations if o["agent"] == exposure.receiver and o["turn_index"] < boundary
                   and masked & {i for ids in o["visible_event_ids"].values() for i in ids}]
    prior_texts = [(f"seq{r.seq}:{s}", t) for r in source_records
                   if r.agent == exposure.receiver and r.turn_index < boundary for s, t in request_text(r)]
    prior_hits = find_content(exposure.content, prior_texts, exposure.masked_ids)
    at_boundary = [o for o in observations if o["agent"] == exposure.receiver and o["turn_index"] == boundary]
    exposed_at_boundary = any(masked & {i for ids in o["visible_event_ids"].values() for i in ids} for o in at_boundary)
    problems = []
    if prior_views:
        problems.append(f"receiver already saw the event at turns {[o['turn_index'] for o in prior_views]}")
    if prior_hits:
        problems.append(f"receiver's earlier requests already contain the content: {prior_hits[:3]}")
    if not exposed_at_boundary:
        problems.append("receiver is not exposed at the boundary turn (no eligible exposure here)")
    if exposure.posted_turn >= boundary:
        problems.append("event is not in the pre-boundary state")
    return CheckResult("V06", "pre_exposure_checkpoint", FAIL if problems else PASS,
                       {"boundary": boundary, "problems": problems})


def check_mask_leaks(exposure, branch_records: Sequence[RequestRecord]) -> CheckResult:
    """Scan every request the receiver submitted inside the mask horizon (all surfaces)."""
    hits = []
    for r in branch_records:
        if r.agent != exposure.receiver or not exposure.in_horizon(r.turn_index):
            continue
        for h in find_content(exposure.content, request_text(r), exposure.masked_ids):
            hits.append({"seq": r.seq, "turn_index": r.turn_index, "step": r.step, **h})
    return CheckResult("V07", "mask_no_leak", FAIL if hits else PASS,
                       {"policy": exposure.repeated_exposure_policy, "leaks": hits,
                        "note": "string/shingle heuristic; paraphrased copies are not detected"})


# ----------------------------------------------------------------------------------------------
# V03 isolation
# ----------------------------------------------------------------------------------------------
def _containers(obj, acc):
    if isinstance(obj, (dict, list, set)):
        acc.add(id(obj))
        for v in (obj.values() if isinstance(obj, dict) else obj):
            _containers(v, acc)
    return acc


def world_containers(world) -> set:
    mb, env, pr = world.protocol.megaboard, world.env, world.protocol
    acc: set = set()
    acc.add(id(mb.blackboards))
    for b in mb.blackboards:
        for part in (b.logs, b.participants, b.agents, b.template):
            _containers(part, acc)
    for part in (env.assignment, env.joint_reward_history, env.agent_rewards_history, pr.tool_events):
        _containers(part, acc)
    for e in pr.tool_events:
        _containers(e.arguments, acc)
        _containers(e.result, acc)
    return acc


def check_isolation(worlds: Sequence[Any], snapshot, snapshot_bytes_before: bytes) -> CheckResult:
    problems = []
    if snapshot.dynamic != snapshot_bytes_before or not snapshot.verify():
        problems.append("checkpoint snapshot bytes changed")
    sets = [world_containers(w) for w in worlds]
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            shared = sets[i] & sets[j]
            if shared:
                problems.append(f"worlds {i} and {j} share {len(shared)} mutable containers")
    return CheckResult("V03", "branch_isolation", FAIL if problems else PASS,
                       {"worlds": len(worlds), "problems": problems})


# ----------------------------------------------------------------------------------------------
# Per-prompt render exactness, model identity, tool-result echo (SCI-002 protocol V1/V3/V6, V2)
# ----------------------------------------------------------------------------------------------
def check_render_every_prompt(arm: str, observations: List[Dict[str, Any]], exposure) -> CheckResult:
    """F/S: delivered == upstream render at every prompt. K: receiver prompts in horizon show
    exactly the underlying events minus the masked ids (order kept); every other prompt is unmasked."""
    masked = set(exposure.masked_ids)
    problems = []
    for o in observations:
        active = arm == "K" and o["agent"] == exposure.receiver and exposure.in_horizon(o["turn_index"])
        for bb, under in o["underlying_event_ids"].items():
            want = [i for i in under if i not in masked] if active else list(under)
            if o["visible_event_ids"][bb] != want:
                problems.append(f"turn {o['turn_index']} {o['agent']} bb {bb}: visible ids != expected")
        if not active and o["contexts_sha256"] != o["upstream_contexts_sha256"]:
            problems.append(f"turn {o['turn_index']} {o['agent']}: render differs from upstream render")
    return CheckResult("V05b", "render_exact_every_prompt", FAIL if problems else PASS,
                       {"prompts_checked": len(observations), "problems": problems[:20]})


def check_model_identity(records: Sequence[RequestRecord], configured_model: str) -> CheckResult:
    bad = [{"seq": r.seq, "requested": r.request["params"].get("model"), "reported": (r.response or {}).get("model")}
           for r in records if r.request["params"].get("model") != configured_model
           or (r.response or {}).get("model") != configured_model]
    return CheckResult("V-model", "model_identity", FAIL if bad else PASS,
                       {"configured": configured_model, "mismatches": bad[:20]})


def check_tool_echo(records: Sequence[RequestRecord], board_contents: Sequence[str]) -> CheckResult:
    """No tool result may carry blackboard message text (a hidden exposure surface)."""
    contents = [c for c in {_norm(c) for c in board_contents} if len(c) >= 12]
    hits = []
    for r in records:
        for i, m in enumerate(r.request.get("messages") or []):
            if m.get("role") == "tool":
                t = _norm(m.get("content"))
                hits += [{"seq": r.seq, "message": i} for c in contents if c in t]
    return CheckResult("V-echo", "tool_results_do_not_echo_boards", FAIL if hits else PASS, {"hits": hits[:20]})
