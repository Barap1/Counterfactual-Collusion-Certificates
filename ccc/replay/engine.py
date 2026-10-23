"""Checkpoint / branch executor for F (factual), S (sham) and K (receiver-mask) arms.

Primary strategy: A (explicit snapshot). The source run snapshots the dynamic state at every
turn boundary; a branch rebuilds the static world from the spec (new env, protocol, agents,
clients), verifies the static hash, and loads the boundary snapshot from bytes.

Cross-check strategy: B (prefix reconstruction). ``make_checkpoint(..., strategy="prefix")``
rebuilds the world from the initial state by replaying the recorded pre-boundary responses
through a hash-checked ``ReplayClient`` and requires the reconstructed state to equal the
snapshot byte-for-byte. B is also the path for runs recorded without snapshots.

After the fork every model call is fresh (``ScriptedClient`` offline; the INF-001 controller
later). Nothing recorded after the boundary is ever fed to a branch.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

from .canonical import request_sha256, state_bytes
from .clients import Policy, PrefixMismatch, ReplayClient, ReplaySource, ScriptedClient
from .interventions import ExposureSpec, receiver_mask_hook, sham_hook
from .recorder import RequestRecord, request_payload
from .validators import (FAIL, NA, PASS, CheckResult, check_fresh, check_mask_leaks, check_model_identity,
                         check_prior_exposure, check_render_every_prompt, check_tool_echo, check_tool_protocol, ok)
from .world import ColosseumWorld, RestoreError, Snapshot, WorldSpec, upstream_provenance

CHECKPOINT_SCHEMA = "ccc.checkpoint.v1"
ARMS = ("F", "S", "K")
PolicyFactory = Callable[[], Policy]


class NoCallClient:
    """Client for worlds that must not call a model (restore validation)."""

    cache_mode = "analysis_only"
    accepts_ccc_context = True

    def generate_response(self, input, params, ccc_context=None):  # noqa: A002
        raise RuntimeError("model call attempted in an analysis-only world")


def scripted_factory(policy_factory: PolicyFactory):
    def make(agent_name: str, world: ColosseumWorld):
        return ScriptedClient(policy_factory(), nonce=f"{world.spec.world_id}/{world.branch_id}/{world.replicate_id}/{agent_name}")
    return make


# ----------------------------------------------------------------------------------------------
# Source run
# ----------------------------------------------------------------------------------------------
@dataclass
class SourceRun:
    spec: WorldSpec
    world: ColosseumWorld

    @property
    def ledger(self):
        return self.world.ledger

    @property
    def observations(self):
        return self.world.protocol.observations

    @property
    def response_ids(self) -> set:
        return {r.response_id for r in self.ledger.records}


def record_source_run(spec: WorldSpec, client_factory) -> SourceRun:
    w = ColosseumWorld(spec, client_factory, branch_id="source", snapshot_every_turn=True)
    w.run_turns()
    return SourceRun(spec, w)


def candidate_exposures(source: SourceRun, *, kinds=("communication",)) -> List[ExposureSpec]:
    """Every (communication event, other participant) pair with the receiver's earliest exposure."""
    out = []
    # posted_turn: the turn after which the event first exists
    first_seen_cursor = {}
    for cur in sorted(source.world.snapshots):
        import json
        d = json.loads(source.world.snapshots[cur].dynamic)
        for b in d["megaboard"]["blackboards"]:
            for e in b["logs"]:
                first_seen_cursor.setdefault(e["id"], cur)
    for b in source.world.protocol.megaboard.blackboards:
        for e in b.logs:
            if e.get("kind") not in kinds:
                continue
            posted_turn = first_seen_cursor[e["id"]] - 1
            for r in sorted(b.agents):
                if r == e.get("agent"):
                    continue
                seen = [o["turn_index"] for o in source.observations if o["agent"] == r
                        and e["id"] in {i for ids in o["visible_event_ids"].values() for i in ids}]
                if not seen:
                    continue
                out.append(ExposureSpec(event_id=e["id"], sender=e["agent"], receiver=r,
                                        blackboard_id=str(b.blackboard_id), channel_participants=tuple(sorted(b.agents)),
                                        content=str((e.get("payload") or {}).get("content") or ""),
                                        posted_turn=posted_turn, first_exposure_turn=min(seen)))
    return out


# ----------------------------------------------------------------------------------------------
# Checkpoint
# ----------------------------------------------------------------------------------------------
@dataclass
class Checkpoint:
    spec: WorldSpec
    exposure: ExposureSpec
    boundary: int
    snapshot: Snapshot
    strategy: str
    source: SourceRun
    validation: List[CheckResult]
    manifest: Dict[str, Any]

    @property
    def valid(self) -> bool:
        return ok(self.validation)


def _restore_round_trip(source: SourceRun, snap: Snapshot, boundary: int) -> CheckResult:
    """V01: restore into a fresh world; equal state hash and identical next observation/request."""
    try:
        w = ColosseumWorld(source.spec, lambda n, wd: NoCallClient(), branch_id="restore_check")
        w.restore(snap)
    except RestoreError as exc:
        return CheckResult("V01", "snapshot_restore_round_trip", FAIL, {"error": str(exc)})
    if boundary >= len(w.schedule):
        return CheckResult("V01", "snapshot_restore_round_trip", PASS, {"note": "terminal boundary"})
    t = w.schedule[boundary]
    w.protocol.turn_index = boundary
    contexts = asyncio.run(w.protocol._prefetch_blackboard_events(t.agent, phase=t.phase, iteration=1))
    kw = {"planning_round": t.planning_round} if t.phase == "planning" else {}
    actx = dict(w.env.build_agent_context(t.agent, phase=t.phase, iteration=1, **kw))
    actx.update(w._extra_fields(t.agent))
    msgs = [{"role": "system", "content": w.env.prompts.get_system_prompt()},
            {"role": "user", "content": w.env.prompts.get_user_prompt(t.agent, actx, contexts)}]
    src_req = next((r for r in source.ledger.records if r.turn_index == boundary and r.step == 1), None)
    same_msgs = src_req is not None and request_sha256(src_req.request["messages"]) == request_sha256(msgs)
    src_obs = next((o for o in source.observations if o["turn_index"] == boundary), None)
    same_obs = src_obs is not None and src_obs["contexts_sha256"] == request_sha256(contexts)
    status = PASS if (same_msgs and same_obs) else FAIL
    return CheckResult("V01", "snapshot_restore_round_trip", status,
                       {"state_sha256": w.dynamic_sha256(), "same_next_observation": same_obs,
                        "same_next_request_messages": same_msgs})


def _prefix_reconstruction(source: SourceRun, snap: Snapshot, boundary: int) -> CheckResult:
    """V02: deterministic prefix reconstruction from recorded responses equals the snapshot."""
    replay = ReplaySource(source.ledger.before(boundary))
    w = ColosseumWorld(source.spec, lambda n, wd: ReplayClient(replay), branch_id="prefix_check")
    err = None
    try:
        w.run_turns(boundary)
    except PrefixMismatch as exc:
        err = str(exc)
    except Exception as exc:  # BaseAgent re-raises first-step failures
        err = f"{type(exc).__name__}: {exc}"
    if replay.errors:  # report the FIRST mismatch, even if upstream swallowed it
        err = replay.errors[0] + (f" (+{len(replay.errors) - 1} later)" if len(replay.errors) > 1 else "")
    err = err or ("; ".join(w.errors) if w.errors else None)
    if err is None and not replay.exhausted:
        err = f"recorded prefix not fully consumed ({replay.pos}/{len(replay.records)})"
    same = err is None and w.snapshot().dynamic == snap.dynamic
    modes = sorted({r.cache_mode for r in w.ledger.records})
    return CheckResult("V02", "prefix_reconstruction", PASS if same and modes in ([], ["prefix_replay"]) else FAIL,
                       {"error": err, "requests_replayed": len(w.ledger.records), "cache_modes": modes,
                        "state_equal_to_snapshot": same})


def make_checkpoint(source: SourceRun, exposure: ExposureSpec, *, boundary: Optional[int] = None,
                    strategy: str = "snapshot", snapshot_override: Optional[Snapshot] = None) -> Checkpoint:
    boundary = exposure.first_exposure_turn if boundary is None else boundary
    snap = snapshot_override or source.world.snapshots[boundary]
    checks = [check_prior_exposure(exposure, boundary, source.observations, source.ledger.records),
              _restore_round_trip(source, snap, boundary)]
    if strategy not in ("snapshot", "prefix"):
        raise ValueError("strategy must be 'snapshot' or 'prefix'")
    # Both strategies run V02: under "snapshot" it cross-validates A against B; under "prefix"
    # the reconstructed state is the checkpoint and must equal the recorded per-turn state.
    checks.append(_prefix_reconstruction(source, snap, boundary))
    prefix = source.ledger.before(boundary)
    manifest = {
        "schema_version": CHECKPOINT_SCHEMA, "world_id": source.spec.world_id, "spec_sha256": source.spec.sha256,
        "source_run": {"branch_id": "source", "requests": len(source.ledger.records)},
        "snapshot_id": snap.snapshot_id, "static_sha256": snap.static_sha256, "dynamic_sha256": snap.dynamic_sha256,
        "strategy": strategy, "scheduler_cursor": boundary,
        "next_turn": source.world.schedule[boundary].__dict__ if boundary < len(source.world.schedule) else None,
        "prefix_request_sha256": [r.request_sha256 for r in prefix],
        "environment_state_schema": "ccc.colosseum.dynamic.v1",
        "agent_history": "none persisted across turns: BaseAgent builds a fresh [system,user] context every turn",
        "blackboard_visibility": "Megaboard.get(bb, agent) membership; rendered by format_blackboard_events_for_prompt",
        "rng_records": {"env.rng": "captured (random.Random state in snapshot)",
                        "run rng (colluder selection, agent shuffle)": "consumed before turn 0; recomputed from seed",
                        "global random": "not captured (only TogetherClient retry jitter)",
                        "provider sampling": "inaccessible"},
        "exposure": exposure.to_json(),
        "code": upstream_provenance(),
        "model_backend": {"model_name": source.world.model_name, "generation_params": source.world.generation_params},
        "assignment_filling": (source.world.cfg.get("environment") or {}).get("assignment_filling", True),
        "state_coverage_note": STATE_COVERAGE_NOTE,
        "restore_validation": {c.id: c.status for c in checks},
    }
    return Checkpoint(source.spec, exposure, boundary, snap, strategy, source, checks, manifest)


STATE_COVERAGE_NOTE = (
    "Captured: Megaboard blackboards (participants, logs, template, suspended) + logical clock; env.assignment "
    "(insertion order); env.rng state; env score histories; protocol.tool_events and current_planning_round; "
    "scheduler cursor. Rebuilt from spec and hash-verified: tasks, costs, agent_private, names, colluders, roles, "
    "turn order, network blackboards, system prompt, tool schemas, generation params, schedule. Not captured: "
    "per-turn BaseAgent fields (overwritten before use), logger files, provider-side state (sampling RNG, KV "
    "cache, routing, silent model updates), global `random` (retry jitter only), wall-clock timestamps "
    "(replaced by a logical clock).")


# ----------------------------------------------------------------------------------------------
# Branches
# ----------------------------------------------------------------------------------------------
@dataclass
class BranchResult:
    arm: str
    replicate_id: str
    world: Optional[ColosseumWorld]
    checks: List[CheckResult]
    outcomes: Optional[Dict[str, Any]]
    status: str
    reasons: List[str] = field(default_factory=list)

    @property
    def records(self) -> List[RequestRecord]:
        return self.world.ledger.records if self.world else []

    def receiver_requests(self, receiver: str) -> List[RequestRecord]:
        return [r for r in self.records if r.agent == receiver]

    def observation(self, agent: str, turn_index: int) -> Optional[Dict[str, Any]]:
        if not self.world:
            return None
        return next((o for o in self.world.protocol.observations if o["agent"] == agent and o["turn_index"] == turn_index), None)


def run_branch(cp: Checkpoint, arm: str, client_factory, *, replicate_id: str = "0", hook=None,
               other_response_ids: set = frozenset()) -> BranchResult:
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}")
    checks: List[CheckResult] = []
    if not cp.valid:
        return BranchResult(arm, replicate_id, None, list(cp.validation), None, "invalid",
                            [f"checkpoint {c.id} {c.status}" for c in cp.validation if c.status not in (PASS, NA)])
    world = ColosseumWorld(cp.spec, client_factory, branch_id=f"{arm}", replicate_id=replicate_id)
    try:
        world.restore(cp.snapshot)
    except RestoreError as exc:
        return BranchResult(arm, replicate_id, None, [CheckResult("V15", "restore", FAIL, {"error": str(exc)})], None,
                            "invalid", [f"restore failed: {exc}"])
    if hook is None:
        hook = {"F": None, "S": sham_hook(), "K": receiver_mask_hook(cp.exposure)}[arm]
    world.set_view_hook(hook, {"F": "none", "S": "sham_identity", "K": "receiver_mask"}[arm] if hook is not None else "none")
    status, reasons = "valid", []
    try:
        world.run_turns()
    except Exception as exc:
        status, reasons = "failed", [f"{type(exc).__name__}: {exc}"]
    if world.errors:
        status, reasons = "failed", reasons + world.errors
    checks.append(check_tool_protocol(world.ledger.records))
    checks.append(check_fresh(world.ledger.records, cp.boundary, cp.source.response_ids, other_response_ids))
    checks.append(check_mask_leaks(cp.exposure, world.ledger.records) if arm == "K"
                  else CheckResult("V07", "mask_no_leak", NA, {}))
    checks.append(check_render_every_prompt(arm, world.protocol.observations, cp.exposure))
    checks.append(check_model_identity(world.ledger.records, world.model_name))
    board_text = [str((e.get("payload") or {}).get("content") or "") for b in world.protocol.megaboard.blackboards
                  for e in b.logs if e.get("kind") == "communication"]
    checks.append(check_tool_echo(world.ledger.records, board_text))
    if status == "valid" and not ok(checks):
        status = "invalid"
        reasons += [f"{c.id} {c.name} failed" for c in checks if c.status == FAIL]
    outcomes = world.outcomes() if status != "failed" else None
    return BranchResult(arm, replicate_id, world, checks, outcomes, status, reasons)


# ----------------------------------------------------------------------------------------------
# Cross-arm checks
# ----------------------------------------------------------------------------------------------
def check_sham_identity(cp: Checkpoint, F: BranchResult, S: BranchResult) -> CheckResult:
    """V04: F and S deliver byte-identical receiver input at the boundary (before sampling)."""
    rcv, b = cp.exposure.receiver, cp.boundary
    fo, so = F.observation(rcv, b), S.observation(rcv, b)
    fr = next((r for r in F.records if r.agent == rcv and r.turn_index == b and r.step == 1), None)
    sr = next((r for r in S.records if r.agent == rcv and r.turn_index == b and r.step == 1), None)
    same_obs = bool(fo and so and fo["contexts_sha256"] == so["contexts_sha256"])
    same_req = bool(fr and sr and fr.request_sha256 == sr.request_sha256)
    src = next((r for r in cp.source.ledger.records if r.agent == rcv and r.turn_index == b and r.step == 1), None)
    same_src = bool(src and fr and src.request_sha256 == fr.request_sha256)
    passed = same_obs and same_req and same_src and so["hook"] == "sham_identity"
    return CheckResult("V04", "sham_identity", PASS if passed else FAIL,
                       {"same_observation": same_obs, "same_first_request": same_req,
                        "same_as_source_request": same_src,
                        "request_sha256": fr.request_sha256 if fr else None})


def check_targeted_exposure(cp: Checkpoint, F: BranchResult, K: BranchResult) -> CheckResult:
    """V05: at the boundary only the receiver's declared surface changes, exactly by the mask."""
    from terrarium.blackboard import format_blackboard_events_for_prompt  # upstream formatter

    rcv, b, masked = cp.exposure.receiver, cp.boundary, set(cp.exposure.masked_ids)
    fo, ko = F.observation(rcv, b), K.observation(rcv, b)
    problems = []
    if not (fo and ko):
        return CheckResult("V05", "targeted_exposure", FAIL, {"problems": ["missing boundary observation"]})
    events_f = {bb: e for bb, e in _events_at(cp.snapshot, rcv).items()}
    for bb, ctx in fo["contexts"].items():
        expected = format_blackboard_events_for_prompt([e for e in events_f[bb] if e.get("id") not in masked])
        if ko["contexts"][bb] != expected:
            problems.append(f"blackboard {bb}: K view != upstream rendering of F view minus masked ids")
        if bb != cp.exposure.blackboard_id and ko["contexts"][bb] != ctx and not (masked & {e["id"] for e in events_f[bb]}):
            problems.append(f"blackboard {bb}: changed although it holds no masked event")
    if ko["contexts"] == fo["contexts"]:
        problems.append("K view identical to F view (nothing was masked)")
    fr = next((r for r in F.records if r.agent == rcv and r.turn_index == b and r.step == 1), None)
    kr = next((r for r in K.records if r.agent == rcv and r.turn_index == b and r.step == 1), None)
    if fr and kr:
        f_user, k_user = fr.request["messages"][1]["content"], kr.request["messages"][1]["content"]
        rebuilt = f_user
        for bb in fo["contexts"]:
            if fo["contexts"][bb] != ko["contexts"][bb]:
                rebuilt = rebuilt.replace(fo["contexts"][bb], ko["contexts"][bb], 1)
        if rebuilt != k_user:
            problems.append("K user prompt differs from F beyond the masked blackboard text")
        if fr.request["messages"][0] != kr.request["messages"][0] or fr.request["params"] != kr.request["params"]:
            problems.append("system prompt or params differ")
    else:
        problems.append("missing boundary request")
    # mask confined to the receiver: every other agent still sees the event whenever it exists
    for o in K.world.protocol.observations:
        if o["agent"] != rcv:
            under = {i for ids in o["underlying_event_ids"].values() for i in ids}
            vis = {i for ids in o["visible_event_ids"].values() for i in ids}
            if (masked & under) - vis:
                problems.append(f"non-receiver {o['agent']} lost the event at turn {o['turn_index']}")
    return CheckResult("V05", "targeted_exposure", FAIL if problems else PASS, {"problems": problems})


def _events_at(snap: Snapshot, agent: str) -> Dict[str, List[Dict[str, Any]]]:
    import json
    d = json.loads(snap.dynamic)
    return {str(b["blackboard_id"]): b["logs"] for b in d["megaboard"]["blackboards"] if agent in b["agents"]}


@dataclass
class AuditResult:
    checkpoint: Checkpoint
    branches: Dict[str, BranchResult]
    cross_checks: List[CheckResult]

    @property
    def valid(self) -> bool:
        return self.checkpoint.valid and all(b.status == "valid" for b in self.branches.values()) and ok(self.cross_checks)


def audit(cp: Checkpoint, client_factory, *, replicate_id: str = "0") -> AuditResult:
    seen: set = set()
    branches: Dict[str, BranchResult] = {}
    for arm in ARMS:
        br = run_branch(cp, arm, client_factory, replicate_id=replicate_id, other_response_ids=frozenset(seen))
        branches[arm] = br
        seen |= {r.response_id for r in br.records}
    cross = []
    if all(branches[a].world is not None for a in ARMS):
        cross = [check_sham_identity(cp, branches["F"], branches["S"]),
                 check_targeted_exposure(cp, branches["F"], branches["K"])]
    return AuditResult(cp, branches, cross)
