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
from .interventions import ExposureSpec, receiver_mask_hook, sham_hook, neutral_placebo_hook, channel_mask_hook
from .prompt_diff import check_prompt_diffs
from .leak_scan import scan_leaks
from .recorder import RequestRecord, request_payload
from .validators import (FAIL, NA, PASS, CheckResult, check_fresh, check_mask_leaks, check_model_identity,
                         check_prior_exposure, check_placebo_render, check_render_every_prompt, check_tool_echo, check_tool_protocol, ok)
from .world import ColosseumWorld, RestoreError, Snapshot, WorldSpec, upstream_provenance, DYNAMIC_SCHEMA

CHECKPOINT_SCHEMA = "ccc.checkpoint.v1"
ARMS = ("F", "S", "K", "N", "C", "N_v1.1_deprecated")
DEFAULT_ARMS = ("F", "S", "K")
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

    @property
    def request_ids(self) -> set:
        return {r.client_request_id for r in self.ledger.records if r.client_request_id}


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


def event_rows(source: SourceRun) -> List[Dict[str, Any]]:
    """Plain event rows for the placebo selector (AMD §3.1): ``turn_index`` is the turn after which
    the event first exists, ``seq`` the event-log timestamp. No outcome or model output is read."""
    import json
    first_seen = {}
    for cur in sorted(source.world.snapshots):
        d = json.loads(source.world.snapshots[cur].dynamic)
        for b in d["megaboard"]["blackboards"]:
            for e in b["logs"]:
                first_seen.setdefault(e["id"], cur)
    rows = []
    for b in source.world.protocol.megaboard.blackboards:
        for e in b.logs:
            rows.append({"id": e["id"], "agent": e.get("agent"), "kind": e.get("kind"),
                         "board": str(b.blackboard_id),
                         "content": str((e.get("payload") or {}).get("content") or ""),
                         "turn_index": first_seen[e["id"]] - 1, "seq": e.get("ts", 0)})
    return rows


def placebo_exposure(exposure: ExposureSpec, m_star) -> ExposureSpec:
    """N_m: the K mask code path applied to M* in place of E* (same receiver and horizon)."""
    import dataclasses
    m_star = tuple(m_star)
    return dataclasses.replace(exposure, event_id=m_star[0], copy_event_ids=m_star[1:])


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
    source_identity = check_model_identity(source.ledger.records, source.world.model_name)
    checks.append(CheckResult("V6", source_identity.name, source_identity.status, source_identity.details))
    prefix = source.ledger.before(boundary)
    from ccc.paths import REPO_ROOT
    from .canonical import sha256_bytes, request_bytes
    from .neutral import FILLERS
    protocol_path = REPO_ROOT / "docs/research/sci002/protocol_v1.md"
    if not protocol_path.is_file():
        protocol_path = REPO_ROOT / "docs/research/sci002/protocol.md"
    protocol_bytes = protocol_path.read_bytes()
    if b"**Status:** FREEZE CANDIDATE v1 (" not in protocol_bytes:
        raise ValueError("ENG-003 requires the preserved SCI-002 v1 protocol; revalidation is needed for another version")
    manifest = {
        "schema_version": CHECKPOINT_SCHEMA, "world_id": source.spec.world_id, "spec_sha256": source.spec.sha256,
        "protocol_sha256": sha256_bytes(protocol_bytes),
        "protocol_version": "SCI-002 v1", "protocol_path": str(protocol_path.relative_to(REPO_ROOT)),
        "neutral_vocabulary_sha256": sha256_bytes(request_bytes(FILLERS)),
        "source_run": {"branch_id": "source", "requests": len(source.ledger.records)},
        "snapshot_id": snap.snapshot_id, "static_sha256": snap.static_sha256, "dynamic_sha256": snap.dynamic_sha256,
        "strategy": strategy, "scheduler_cursor": boundary,
        "next_turn": source.world.schedule[boundary].__dict__ if boundary < len(source.world.schedule) else None,
        "prefix_request_sha256": [r.request_sha256 for r in prefix],
        "environment_state_schema": DYNAMIC_SCHEMA,
        "agent_history": "none persisted across turns: BaseAgent builds a fresh [system,user] context every turn",
        "blackboard_visibility": "Megaboard.get(bb, agent) membership; rendered by format_blackboard_events_for_prompt",
        "rng_records": {"env.rng": "captured (random.Random state in snapshot)",
                        "run rng (colluder selection, agent shuffle)": "captured",
                        "global random": "captured; virtualized per serial world",
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
    "scheduler cursor; run RNG and Python global RNG. Rebuilt from spec and hash-verified: tasks, costs, agent_private, names, colluders, roles, "
    "turn order, network blackboards, system prompt, tool schemas, generation params, schedule. Not captured: "
    "per-turn BaseAgent fields (overwritten before use), logger files, provider-side state (sampling RNG, KV "
    "cache, routing, silent model updates), wall-clock timestamps "
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
    ledger_path: Optional[str] = None
    execution_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def records(self) -> List[RequestRecord]:
        return self.world.ledger.records if self.world else []

    def receiver_requests(self, receiver: str) -> List[RequestRecord]:
        return [r for r in self.records if r.agent == receiver]

    def observation(self, agent: str, turn_index: int) -> Optional[Dict[str, Any]]:
        if not self.world:
            return None
        return next((o for o in self.world.protocol.observations if o["agent"] == agent and o["turn_index"] == turn_index), None)


def _world_aliases(world):
    """Per-world binding of the frozen description pattern to task ids (public task table)."""
    from ccc.audit.commitments import world_aliases
    tasks = getattr(world.env, "tasks", None)
    if not isinstance(tasks, dict):
        return None
    try:
        return world_aliases({k: v for k, v in tasks.items() if isinstance(v, dict)})
    except Exception:
        return None


def run_branch(cp: Checkpoint, arm: str, client_factory, *, replicate_id: str = "0", hook=None,
               other_response_ids: set = frozenset(), other_request_ids: set = frozenset(), ledger_dir=None,
               execution_metadata=None, placebo_ids=None) -> BranchResult:
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}")
    checks: List[CheckResult] = []
    from .ledger import persist_branch

    def finish(result):
        result.execution_metadata = dict(execution_metadata or {"order": "single branch; sampling order not established"})
        if arm == "N":
            from ccc.audit.decision import PLACEBO_SURFACE_NOTE
            result.execution_metadata["placebo_control"] = {
                "label": "N_m", "M_star": list(placebo_ids or ()), "surface_note": PLACEBO_SURFACE_NOTE}
        result.ledger_path = persist_branch(cp, result, ledger_dir)
        return result

    if not cp.valid:
        return finish(BranchResult(arm, replicate_id, None, list(cp.validation), None, "invalid",
                            [f"checkpoint {c.id} {c.status}" for c in cp.validation if c.status not in (PASS, NA)]))
    try:
        world = ColosseumWorld(cp.spec, client_factory, branch_id=f"{arm}", replicate_id=replicate_id)
    except Exception as exc:
        return finish(BranchResult(arm, replicate_id, None, [], None, "failed",
                                   [f"world construction: {type(exc).__name__}: {exc}"]))
    try:
        world.restore(cp.snapshot)
    except RestoreError as exc:
        return finish(BranchResult(arm, replicate_id, None, [CheckResult("V15", "restore", FAIL, {"error": str(exc)})], None,
                            "invalid", [f"restore failed: {exc}"]))
    legacy_placebo = arm == "N_v1.1_deprecated"
    validation_arm = "N" if legacy_placebo else arm
    if legacy_placebo and hook is None:
        hook = neutral_placebo_hook(cp.exposure)
    n_exposure = None
    if arm == "N":
        if not placebo_ids:
            raise ValueError("arm N is the v1.2 matched message mask: pass placebo_ids (M*); the v1.1 filler "
                             "placebo is N_v1.1_deprecated and is no longer selected by default")
        n_exposure = placebo_exposure(cp.exposure, placebo_ids)
        if hook is None:
            hook = receiver_mask_hook(n_exposure)
    if hook is None:
        hook = {"F": None, "S": sham_hook(), "K": receiver_mask_hook(cp.exposure),
                "N": None, "C": channel_mask_hook(cp.exposure)}[arm]
    world.set_view_hook(hook, {"F": "none", "S": "sham_identity", "K": "receiver_mask", "N": "matched_message_mask", "C": "channel_mask", "N_v1.1_deprecated": "neutral_placebo"}[arm] if hook is not None else "none")
    status, reasons = "valid", []
    try:
        world.run_turns()
    except Exception as exc:
        status, reasons = "failed", [f"{type(exc).__name__}: {exc}"]
    if world.errors:
        status, reasons = "failed", reasons + world.errors
    checks.append(check_tool_protocol(world.ledger.records))
    checks.append(check_fresh(world.ledger.records, cp.boundary, cp.source.response_ids, other_response_ids,
                              source_request_ids=cp.source.request_ids, other_request_ids=other_request_ids))
    import json
    prefix_ids = [e["id"] for b in json.loads(cp.snapshot.dynamic)["megaboard"]["blackboards"] for e in b["logs"]]
    checks.append(scan_leaks(cp.exposure, world.ledger.records, world.prompt_audits, prefix_ids,
                             tuple(world.env.tasks), _world_aliases(world)) if arm in ("K", "C")
                  else CheckResult("V07", "mask_no_leak", NA, {"arm": arm, "note": "N_m uses V3-N below"}))
    if n_exposure is not None:
        # V3 for N: M* never rendered, E* lines unchanged, render = unmasked render minus exactly M*.
        checks.append(check_prompt_diffs("K", world.prompt_audits, n_exposure))
        checks.append(check_placebo_render(world.protocol.observations, cp.exposure, placebo_ids))
    else:
        checks.append(check_prompt_diffs(validation_arm, world.prompt_audits, cp.exposure))
        checks.append(check_render_every_prompt(validation_arm, world.protocol.observations, cp.exposure))
    expected_params = {r.phase: r.request["params"] for r in cp.source.ledger.records}
    identity = check_model_identity(world.ledger.records, world.model_name, expected_params)
    checks.append(identity)
    checks.append(CheckResult("V6", identity.name, identity.status, identity.details))
    board_text = [str((e.get("payload") or {}).get("content") or "") for b in world.protocol.megaboard.blackboards
                  for e in b.logs if e.get("kind") == "communication"]
    checks.append(check_tool_echo(world.ledger.records, board_text))
    if status == "valid" and not ok(checks):
        status = "invalid"
        reasons += [f"{c.id} {c.name} failed" for c in checks if c.status == FAIL]
    outcomes = world.outcomes() if status != "failed" else None
    result = BranchResult(arm, replicate_id, world, checks, outcomes, status, reasons)
    return finish(result)


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
    problems = []
    rcv, boundary = cp.exposure.receiver, cp.boundary
    factual = next((r for r in F.records if r.agent == rcv and r.turn_index == boundary and r.step == 1), None)
    edited = next((a for a in K.world.prompt_audits if a["agent"] == rcv and a["turn_index"] == boundary and a["step"] == 1), None)
    if not factual or not edited:
        problems.append("missing boundary request")
    else:
        from .canonical import deep_copy_json
        probe = deep_copy_json(edited)
        probe["factual_messages"] = factual.request["messages"][:2]
        check = check_prompt_diffs("K", [probe], cp.exposure)
        problems.extend(check.details["problems"])
    for observation in K.world.protocol.observations:
        if observation["agent"] != rcv and observation["contexts_sha256"] != observation["upstream_contexts_sha256"]:
            problems.append("non-receiver observation changed")
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


def audit(cp: Checkpoint, client_factory, *, replicate_id: str = "0", arms=DEFAULT_ARMS,
          branch_order_seed: int = 0, ledger_dir=None) -> AuditResult:
    seen: set = set()
    seen_requests: set = set()
    branches: Dict[str, BranchResult] = {}
    import random
    order = list(arms)
    if not order or len(set(order)) != len(order) or not set(order) <= set(ARMS):
        raise ValueError("arms must be unique supported arms")
    random.Random(branch_order_seed).shuffle(order)
    for arm in order:
        br = run_branch(cp, arm, client_factory, replicate_id=replicate_id, other_response_ids=frozenset(seen),
                        other_request_ids=frozenset(seen_requests), ledger_dir=ledger_dir,
                        execution_metadata={"branch_order_seed": branch_order_seed, "arm_order": order, "position": len(branches)})
        branches[arm] = br
        seen |= {r.response_id for r in br.records}
        seen_requests |= {r.client_request_id for r in br.records if r.client_request_id}
    cross = []
    if all(a in branches and branches[a].world is not None for a in DEFAULT_ARMS):
        cross = [check_sham_identity(cp, branches["F"], branches["S"]),
                 check_targeted_exposure(cp, branches["F"], branches["K"])]
    return AuditResult(cp, branches, cross)


class ExposureSelectionError(ValueError):
    """No eligible confirmatory exposure (reason remains in the coverage denominator)."""


def select_protocol_exposure(source: SourceRun) -> ExposureSpec:
    """SCI-002 §4: first coalition sender on P; bundle all its co-exposed events at t*.

    Kept separate from candidate_exposures (an exploratory enumeration used by existing fixtures).
    The returned bundle still needs make_checkpoint's pre-exposure/restore validity checks.
    """
    board_id = source.world.secret_blackboard_id
    if board_id is None or len(source.world.colluders) != 2:
        raise ExposureSelectionError("no_exposure")
    board = source.world.protocol.megaboard.blackboards[int(board_id)]
    posts = [e for e in board.logs if e.get("kind") == "communication" and e.get("agent") in source.world.colluders]
    if not posts:
        raise ExposureSelectionError("no_exposure")
    first = posts[0]
    sender = first["agent"]
    receiver = next(a for a in source.world.colluders if a != sender)
    candidates = candidate_exposures(source)
    candidate = next((e for e in candidates if e.event_id == first["id"] and e.receiver == receiver), None)
    if candidate is None:
        raise ExposureSelectionError("post_decision")
    for record in source.ledger.before(candidate.first_exposure_turn):
        if record.agent != receiver:
            continue
        for choice in record.response.get("choices") or []:
            for call in (choice.get("message") or {}).get("tool_calls") or []:
                if (call.get("function") or {}).get("name") == "assign_task":
                    raise ExposureSelectionError("post_decision")
    coexposed = [e.event_id for e in candidates if e.sender == sender and e.receiver == receiver
                 and e.blackboard_id == str(board_id) and e.first_exposure_turn == candidate.first_exposure_turn
                 and e.event_id != candidate.event_id]
    from dataclasses import replace
    return replace(candidate, copy_event_ids=tuple(coexposed))


def audit_replicates(cp: Checkpoint, client_factory, *, replicate_ids=("0",), arms=DEFAULT_ARMS,
                     branch_order_seed: int = 0, ledger_dir=None) -> List[AuditResult]:
    """Fresh, shuffled/interleaved arm × replicate schedule with cross-attempt ID checks."""
    import random
    reps = tuple(str(r) for r in replicate_ids)
    arms = tuple(arms)
    if not reps or len(set(reps)) != len(reps) or not arms or len(set(arms)) != len(arms) or not set(arms) <= set(ARMS):
        raise ValueError("replicate IDs and supported arms must be nonempty and unique")
    schedule = [(rep, arm) for rep in reps for arm in arms]
    random.Random(branch_order_seed).shuffle(schedule)
    groups = {rep: {} for rep in reps}
    seen = set()
    seen_requests: set = set()
    for position, (rep, arm) in enumerate(schedule):
        branch = run_branch(cp, arm, client_factory, replicate_id=rep, ledger_dir=ledger_dir,
                            other_response_ids=frozenset(seen), other_request_ids=frozenset(seen_requests),
                            execution_metadata={
                                "branch_order_seed": branch_order_seed, "schedule": schedule, "position": position})
        groups[rep][arm] = branch
        seen.update(r.response_id for r in branch.records)
        seen_requests.update(r.client_request_id for r in branch.records if r.client_request_id)
    results = []
    for rep in reps:
        branches = groups[rep]
        cross = []
        if all(a in branches and branches[a].world is not None for a in DEFAULT_ARMS):
            cross = [check_sham_identity(cp, branches["F"], branches["S"]),
                     check_targeted_exposure(cp, branches["F"], branches["K"])]
        results.append(AuditResult(cp, branches, cross))
    return results
