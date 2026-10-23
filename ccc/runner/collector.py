"""Checkpoint collection using replay's public APIs and the INF-001 guarded client.

Collection deliberately resumes at world boundaries: no resumed process may mix branches
from different model-load sessions. Failures require an explicit new world attempt.
"""
from __future__ import annotations

import dataclasses
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from ccc.infra.budget_guard import BudgetGuard, GuardPolicy, GuardedChatClient, Ledger, scrub
from ccc.replay import engine
from ccc.replay.clients import ScriptedClient
from ccc.replay.fixtures import signal_policy
from ccc.replay.interventions import ExposureSpec
from ccc.replay.world import ColosseumWorld, WorldSpec

from .manifest import ROOT, canonical, digest, file_hash, plan, validate, call_seed, parse_time
from .live import OllamaSession, OllamaChatClient, ModelReload
from .storage import get, lock, output_root, put, seal, verify


LIVE_LEDGER = ROOT / "ops/budget_ledger.jsonl"


class MirrorLedger:
    def __init__(self, shared, local):
        self.shared, self.local = shared, local

    def records(self):
        return self.shared.records()

    def append(self, record):
        # Shared admission evidence first; failure prevents the request from launching.
        self.shared.append(record)
        self.local.append(record)


def build_spec(m, w):
    cfg = json.loads(canonical(m["world_template"]))
    cfg["environment"]["assignment_filling"] = False
    cfg["experiment"]["collusion"].update(
        colluder_selection="random", coalition_prompt="always" if w["regime"] == "B1" else "never",
        extra_channel_members="colluders")
    cfg["llm_models"][0] = {"label": m["experiment_id"], "llm": {"provider": "openrouter", "openrouter": {
        "model": m["model"]["requested_id"], "params": m["model"]["parameters"]}}}
    cfg["experiment"]["sweeps"][0]["prompt_variants"] = ["deception"]
    return WorldSpec.from_batch_config(cfg, seed=w["seed"], model_name=m["model"]["requested_id"])


def select_exposure(source):
    """SCI-002 §4: first pair-channel communication, first exposure, full sender bundle.

    Candidate effects/outcomes are never inspected. The first event is selected even if
    ineligible; no fallback search for a later eligible or more effective message.
    """
    world = source.world
    boards = [b for b in world.protocol.megaboard.blackboards
              if str(b.blackboard_id) == str(world.secret_blackboard_id) and set(b.agents) == set(world.colluders)]
    if len(boards) != 1:
        return None, {"reason": "no_exposure", "detail": "missing designated pair board"}
    board = boards[0]
    events = [e for e in board.logs if e.get("kind") == "communication" and e.get("agent") in world.colluders]
    if not events:
        return None, {"reason": "no_exposure"}
    first = events[0]
    sender = first["agent"]
    receiver = next(a for a in world.colluders if a != sender)
    candidates = engine.candidate_exposures(source)
    exposure = next((e for e in candidates if e.event_id == first["id"] and e.receiver == receiver), None)
    if exposure is None:
        return None, {"reason": "no_exposure", "event_id": first["id"]}
    boundary = exposure.first_exposure_turn
    # A committed assignment or an earlier execution turn cannot be selected away.
    state = json.loads(world.snapshots[boundary].dynamic)
    assigned = dict(state["env"]["assignment"])
    if assigned.get(receiver) is not None or any(t.agent == receiver and t.phase == "execution"
                                              for t in world.schedule[:boundary]):
        return None, {"reason": "post_decision", "event_id": first["id"]}
    bundle = [e for e in candidates if e.sender == sender and e.receiver == receiver
              and e.blackboard_id == exposure.blackboard_id and e.first_exposure_turn == boundary]
    from ccc.replay.validators import check_prior_exposure
    for member in bundle:
        integrity = check_prior_exposure(member, boundary, source.observations, source.ledger.records)
        if integrity.status == "fail":
            return None, {"reason": "pre_exposed", "event_id": first["id"], "check": integrity.to_json()}
    ids = {e.event_id for e in bundle}
    ordered = [e["id"] for e in events if e["id"] in ids]
    exposure = dataclasses.replace(exposure, copy_event_ids=tuple(i for i in ordered if i != first["id"]))
    return exposure, {"rule": "sci002.first_private_bundle.v1", "bundle_event_ids": ordered,
                      "sender": sender, "receiver": receiver, "boundary": boundary}


class DurableClient:
    """GuardedChatClient plus immutable begin/end records, including swallowed failures."""
    accepts_ccc_context = True
    cache_mode = "fresh"

    def __init__(self, guard, model, root, world, agent, seed, session_id, *, manifest, checkpoint_id, arm, replicate, live_session=None):
        self.root, self.world, self.agent, self.seed = root, world, agent, seed
        self.manifest, self.checkpoint_id, self.arm, self.replicate = manifest, checkpoint_id, arm, replicate
        self.live_session = live_session
        self.call_k = 0
        self.errors = []
        self.context = {}
        scripted = ScriptedClient(signal_policy(), nonce=f"{session_id}/{world.branch_id}/{agent}")

        def transport(url, headers, body, timeout):
            # Explicit scripted transport: never calls urllib, Ollama, or a key loader for remote APIs.
            payload = json.loads(body)
            response, _ = scripted.generate_response(payload["messages"], payload, ccc_context=self.context)
            return 200, canonical(response)

        client_type = OllamaChatClient if live_session else GuardedChatClient
        self.inner = client_type(guard, backend=model["backend"], model=model["requested_id"],
                                       base_url=model["base_url"], transport=live_session.transport if live_session else transport,
                                       fixed_params=model["parameters"] | {"seed": seed},
                                       meta={"load_session": session_id, "mode": "live_local" if live_session else "scripted_dry_run"})

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def generate_response(self, input, params, ccc_context=None):
        self.context = dict(ccc_context or {})
        self.seed = call_seed(self.manifest, self.checkpoint_id, self.arm, self.replicate,
                              self.context.get("turn_index", -1), self.call_k, self.agent)
        self.call_k += 1
        self.inner.fixed_params["seed"] = self.seed
        call_id = uuid.uuid4().hex
        base = self.root / "calls" / call_id
        payload = self.inner.build_payload(input, params)
        context = self.context | {"seed_sent": self.seed, "load_session_id": self.inner.meta["load_session"],
                                  "evidence_tier": "live_local" if self.live_session else "scripted_dry_run"}
        put(base.with_suffix(".begin.json"), {"context": context, "request": payload,
                                              "request_sha256": digest(payload)})
        try:
            if self.live_session:
                self.live_session.check()
            response, text = self.inner.generate_response(input, params)
            if self.live_session:
                self.live_session.check()
            if response.get("model") != self.inner.model:
                raise ValueError("provider-reported model differs from frozen model")
            put(base.with_suffix(".end.json"), {"status": "complete", "response": response,
                                                "response_sha256": digest(response),
                                                "guard_attempts": self.inner.last_attempt_records})
            return response, text
        except Exception as exc:
            # Preserve even if upstream BaseAgent swallows the error on continuation steps.
            self.errors.append(scrub(f"{type(exc).__name__}: {exc}"))
            put(base.with_suffix(".end.json"), {"status": "failed", "error": self.errors[-1],
                                                "guard_attempts": self.inner.last_attempt_records})
            raise


def archive_world(root, world):
    put(root / "records.json", {"records": [r.to_json() for r in world.ledger.records],
                                 "observations": world.protocol.observations,
                                 "turns": world.turn_records, "errors": world.errors})
    snap = world.snapshot()
    put(root / "final_state.json", {"static": world.static_state(), "dynamic": json.loads(snap.dynamic),
                                     "snapshot_id": snap.snapshot_id, "static_sha256": snap.static_sha256,
                                     "dynamic_sha256": snap.dynamic_sha256})


def collect_world(m, job, root, guard, session, live_session=None):
    tier = "live_local" if live_session else "scripted_dry_run"
    spec = build_spec(m, job["world"])
    put(root / "spec.json", spec.to_json())
    clients = []

    def factory(seed, location, arm="source", replicate=0):
        def make(agent, world):
            c = DurableClient(guard, m["model"], location, world, agent, seed, session, manifest=m,
                              checkpoint_id=job["world"]["id"], arm=arm, replicate=replicate, live_session=live_session)
            clients.append(c)
            return c
        return make

    source_root = root / "source"
    source_seed = int(digest([m["master_seed"], job["world"]["seed"], "source"]), 16) % 2**31
    world = ColosseumWorld(spec, factory(source_seed, source_root), branch_id="source", snapshot_every_turn=True)
    source = engine.SourceRun(spec, world)
    initial = world.snapshot()
    put(source_root / "snapshots" / "0000.json", {"dynamic": json.loads(initial.dynamic),
        "dynamic_sha256": initial.dynamic_sha256, "static_sha256": initial.static_sha256,
        "cursor": 0, "snapshot_id": initial.snapshot_id})
    try:
        while world.cursor < len(world.schedule):
            world.run_turns(world.cursor + 1)
            snap = world.snapshot()
            put(source_root / "snapshots" / f"{world.cursor:04}.json",
                {"dynamic": json.loads(snap.dynamic), "dynamic_sha256": snap.dynamic_sha256,
                 "static_sha256": snap.static_sha256, "cursor": world.cursor, "snapshot_id": snap.snapshot_id})
            if world.errors or any(c.errors for c in clients):
                raise ValueError("source contains failed calls; retained as infrastructure failure")
    finally:
        archive_world(source_root, world)
    if world.errors or any(c.errors for c in clients):
        raise ValueError("source contains failed calls; retained as infrastructure failure")
    exposure, selection = select_exposure(source)
    put(root / "selection.json", selection)
    if exposure is None:
        return {"status": "ineligible", "selection": selection, "outcomes": None}
    if m.get("hard_stop_utc") and datetime.now(timezone.utc) >= parse_time(m["hard_stop_utc"]):
        return {"status": "stopped_hard_stop", "reason": "hard_stop", "outcomes": None}
    checkpoint = engine.make_checkpoint(source, exposure)
    put(root / "checkpoint.json", checkpoint.manifest)
    put(root / "checkpoint_state.json", {"dynamic": json.loads(checkpoint.snapshot.dynamic),
                                         "static": world.static_state()})
    if not checkpoint.valid:
        return {"status": "ineligible", "reason": "restore_fail", "outcomes": None,
                "checks": [c.to_json() for c in checkpoint.validation]}
    if live_session:
        put(root / "session_before.json", live_session.check())
    results = []

    def invalidate():
        # Defer branch result publication until session checks pass. All scheduled branches
        # are explicitly invalid, including ones not launched after the residency failure.
        launched = {(r["replicate"], r["arm"]): r for r in results}
        invalid = []
        for item in job["order"]:
            key = (item["replicate"], item["arm"])
            record = launched.get(key, item | {"launched": False})
            record.update(status="invalid", reasons=["model_reload"], outcomes=None)
            put(root / "branches" / f"{key[0]:03}_{key[1]}" / "result.json", record)
            invalid.append(record)
        put(root / "invalidation.json", {"reason": "model_reload", "scope": "all_checkpoint_branches"})
        return {"status": "invalid", "reason": "model_reload", "branches": invalid, "outcomes": None}

    response_ids = set()
    branches = {}
    for item in job["order"]:
        arm, rep = item["arm"], item["replicate"]
        location = root / "branches" / f"{rep:03}_{arm}"
        put(location / "begin.json", item | {"load_session": session, "checkpoint_sha256": digest(checkpoint.manifest)})
        if arm not in engine.ARMS:
            raise ValueError(f"replay dependency does not yet support {arm}; ENG-003 integration required")
        kwargs = {}
        # ENG-003 supplies N's hook and frozen filler API; never generate filler from outcomes.
        if arm == "N":
            from ccc.replay.interventions import neutral_placebo_hook
            kwargs["hook"] = neutral_placebo_hook(exposure)
        result = engine.run_branch(checkpoint, arm, factory(item["seed"], location, arm, rep),
                                   replicate_id=str(rep), other_response_ids=response_ids,
                                   ledger_dir=location / "replay_ledger",
                                   execution_metadata=item | {"load_session": session,
                                       "evidence_tier": tier, "common_randomness_claim": "none"}, **kwargs)
        if result.world is not None:
            archive_world(location, result.world)
        failures = [c.errors for c in clients if c.root == location and c.errors]
        reload_detected = live_session and any("model_reload" in e for errors in failures for e in errors)
        if reload_detected:
            results.append(item | {"client_failures": failures, "launched": True})
            return invalidate()
        status = "failed" if failures else result.status
        record = item | {"status": status, "reasons": result.reasons, "client_failures": failures,
                         "checks": [c.to_json() for c in result.checks],
                         "outcomes": result.outcomes if status == "valid" else None}
        results.append(record)
        response_ids.update(r.response_id for r in result.records if r.response_id)
        branches[(rep, arm)] = result
    cross = []
    for rep in range(m["continuations_per_arm"]["F"]):
        f = branches.get((rep, "F"))
        for arm, check in (("S", engine.check_sham_identity), ("K", engine.check_targeted_exposure)):
            other = branches.get((rep, arm))
            if f and other and f.world is not None and other.world is not None:
                cross.append(check(checkpoint, f, other).to_json())
    if live_session:
        try:
            put(root / "session_after.json", live_session.check())
        except ModelReload:
            return invalidate()
    for record in results:
        put(root / "branches" / f"{record['replicate']:03}_{record['arm']}" / "result.json", record)
    put(root / "cross_checks.json", cross)
    valid = all(r["status"] == "valid" for r in results) and all(c["status"] in ("pass", "na") for c in cross)
    return {"status": "complete" if valid else "invalid", "branches": results, "cross_checks": cross,
            "evidence_tier": tier, "load_session": session}


def status(root):
    root = output_root(root)
    checked = verify(root)
    if not (root / "manifest.json").exists():
        return {"status": "not_started", "verified_artifacts": checked}
    m = get(root / "manifest.json")
    worlds = []
    for job in plan(m)["jobs"]:
        attempts = sorted((root / "worlds" / job["world"]["id"]).glob("attempt_*"))
        entries = []
        for attempt in attempts:
            outcome = get(attempt / "result.json") if (attempt / "result.json").exists() else {"status": "interrupted"}
            entries.append({"path": str(attempt.relative_to(root)), "status": outcome["status"]})
        worlds.append({"world": job["world"]["id"], "attempts": entries})
    return {"manifest_sha256": digest(m), "verified_artifacts": checked, "worlds": worlds,
            "live_calls": sum(r.get("event") == "attempt_begin"
                              for p in root.rglob("budget.jsonl")
                              for r in (json.loads(line) for line in p.read_text().splitlines()))
                          if m["policy"]["live_inference_enabled"] else 0,
            "evidence_tier": "live_local" if m["policy"]["live_inference_enabled"] else "scripted_dry_run"}


def run(m, root, *, dry_run=False, live=False, retry_failed=False):
    validate(m)
    if dry_run == live:
        raise ValueError("live execution disabled unless --live is explicit; choose --live or --dry-run")
    if live and not m["policy"]["live_inference_enabled"]:
        raise ValueError("manifest does not authorize live inference")
    if dry_run and m["policy"]["live_inference_enabled"]:
        raise ValueError("use a separate offline manifest/output for dry runs")
    if m.get("hard_stop_utc") and datetime.now(timezone.utc) >= parse_time(m["hard_stop_utc"]):
        raise ValueError("hard stop reached; no new checkpoints may launch")
    live_session = OllamaSession(m["model"]) if live else None
    root = output_root(root)
    with lock(root):
        verify(root)
        code = {str(p.relative_to(ROOT)): file_hash(p)
                for folder in (ROOT / "ccc/runner", ROOT / "ccc/replay", ROOT / "ccc/infra")
                for p in sorted(folder.glob("*.py"))}
        if (root / "manifest.json").exists():
            if digest(get(root / "manifest.json")) != digest(m):
                raise ValueError("output is pinned to a different immutable manifest")
            if get(root / "code.json") != code:
                raise ValueError("collection code changed; use a new output root and manifest version")
        else:
            put(root / "manifest.json", m)
            put(root / "plan.json", plan(m))
            put(root / "code.json", code)
            if live_session:
                put(root / "run_manifest.json", {"manifest_sha256": digest(m), "ollama": live_session.attestation()})
        for job in plan(m)["jobs"]:
            wroot = root / "worlds" / job["world"]["id"]
            attempts = sorted(wroot.glob("attempt_*"))
            if attempts:
                result_file = attempts[-1] / "result.json"
                previous = get(result_file) if result_file.exists() else {"status": "interrupted"}
                if previous["status"] in ("complete", "ineligible"):
                    continue
                if not retry_failed:
                    raise ValueError("failed/interrupted world retained; --retry-failed starts a new whole-world attempt")
                reloads = sum(get(a / "result.json").get("reason") == "model_reload"
                              for a in attempts if (a / "result.json").exists())
                if reloads >= 2:
                    raise ValueError("repeated model_reload; preregistered single checkpoint retry exhausted")
            if m.get("hard_stop_utc") and datetime.now(timezone.utc) >= parse_time(m["hard_stop_utc"]):
                break
            if live:
                live_session = OllamaSession(m["model"])
            attempt = wroot / f"attempt_{len(attempts) + 1:04}"
            session = live_session.session_id if live else f"scripted-session-{uuid.uuid4().hex}"
            put(attempt / "begin.json", {"world": job["world"], "load_session": session,
                                          "retry_of": str(attempts[-1].relative_to(root)) if attempts else None})
            # The cap covers this entire collection, including failures and explicit retries.
            used = sum(1 for _ in root.rglob("*.begin.json"))
            remaining = m["max_requests"] - used
            if remaining <= 0:
                put(attempt / "result.json", {"status": "failed", "error": "frozen request cap exhausted"})
                seal(attempt)
                raise ValueError("frozen request cap exhausted")
            guard = BudgetGuard(run_id=f"{m['experiment_id']}/{job['world']['id']}/{len(attempts)+1}/{uuid.uuid4().hex}",
                                task_id="EXP-001" if live else "EXP-000b", max_calls=remaining, policy=GuardPolicy(max_retries=0),
                                ledger_path=LIVE_LEDGER if live else attempt / "budget.jsonl", purpose="EXP-001 local live" if live else "scripted dry-run; no network")
            if live:
                local_ledger = Ledger(attempt / "budget.jsonl")
                for record in guard.ledger.records():
                    if record.get("run_id") == guard.run_id:
                        local_ledger.append(record)
                guard.ledger = MirrorLedger(guard.ledger, local_ledger)
            try:
                result = collect_world(m, job, attempt, guard, session, live_session=live_session)
            except Exception as exc:
                result = {"status": "failed", "error": scrub(f"{type(exc).__name__}: {exc}"), "outcomes": None}
            finally:
                if live_session:
                    put(attempt / "session_checks.json", live_session.history)
                guard.close("collection attempt closed")
            put(attempt / "result.json", result)
            seal(attempt)
            if result["status"] == "stopped_hard_stop":
                break
            if result["status"] in ("failed", "invalid"):
                raise ValueError(f"world attempt {result['status']}; evidence retained at {attempt}")
    return status(root)
