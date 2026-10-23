"""Immutable on-disk branch attempts and hash-linked ccc.event.v1 JSONL.

Each invocation creates a new attempt directory, including failed/invalid attempts. Request
and response artifacts are JSON payloads, never HTTP headers. The default is a scratch root;
callers retaining scientific evidence must supply ledger_dir under an approved writable root.
"""
import json
from pathlib import Path
import tempfile
import uuid

from .canonical import request_bytes, sha256_bytes


def _write(path, data):
    with path.open("xb") as handle:
        handle.write(data)


def persist_branch(checkpoint, result, ledger_dir=None):
    from ccc.paths import REPO_ROOT
    from .world import _scratch_root
    root = Path(ledger_dir) if ledger_dir is not None else _scratch_root() / "branch_ledgers"
    root = root.resolve()
    permitted = (REPO_ROOT.resolve(), Path(tempfile.gettempdir()).resolve(), Path("/private/tmp"))
    if not any(root.is_relative_to(p) for p in permitted) or root.is_relative_to(REPO_ROOT / "results" / "baselines"):
        raise ValueError("ledger_dir must be under an approved writable root outside the pilot archive")
    attempt = uuid.uuid4().hex
    directory = root / f"{result.arm}_{attempt}"
    directory.mkdir(parents=True, exist_ok=False)
    hashes = {}

    def artifact(name, data):
        _write(directory / name, data)
        hashes[name] = sha256_bytes(data)
        return name

    import subprocess
    from .clients import ScriptedClient, ReplayClient, ReusingClient
    scripted = bool(result.world) and all(isinstance(agent.client._inner,
        (ScriptedClient, ReplayClient, ReusingClient)) for agent in result.world.env.agents)
    reported_ids = sorted({r.model_resolved for r in result.records if r.model_resolved})
    try:
        commit = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                                capture_output=True, text=True, check=False).stdout.strip() or None
    except OSError:
        commit = None
    artifact("run.json", request_bytes({
        "schema_version": "ccc.run.v1", "experiment_id": checkpoint.spec.world_id,
        "protocol_sha256": checkpoint.manifest["protocol_sha256"],
        "analysis_commit": commit, "ccc_commit": commit,
        "upstream_commit": checkpoint.manifest["code"].get("upstream_commit"),
        "working_tree": "ENG-003 changes may be uncommitted; source hashes in source_hashes.json",
        "phase": "development", "world_ids": [checkpoint.spec.world_id],
        "regimes": [checkpoint.spec.prompt_variant],
        "model": {"requested_id": checkpoint.spec.model_name,
                  "resolved_id": reported_ids[0] if len(reported_ids) == 1 else None,
                  "reported_ids": reported_ids,
                  "provider": "scripted" if scripted else "unclassified",
                  "endpoint_kind": "local" if scripted else None,
                  "weight_digest": None, "quantization": None,
                  "parameters": checkpoint.source.world.generation_params, "context_limit": None},
        "intervention": {"selection_rule_version": "caller_declared; select_protocol_exposure available",
                         "eligible_surface": checkpoint.exposure.observation_surface,
                         "arms": [result.arm], "continuation_horizon": {
                             "start": checkpoint.boundary, "end": len(checkpoint.source.world.schedule)},
                         "repeated_exposure_policy": checkpoint.exposure.repeated_exposure_policy,
                         "neutral_vocabulary_sha256": checkpoint.manifest["neutral_vocabulary_sha256"]},
        "sampling": {"world_seed_manifest": {"seed": checkpoint.spec.seed, "spec_sha256": checkpoint.spec.sha256},
                     "continuations_per_arm": 1, "branch_order_seed": result.execution_metadata.get("branch_order_seed"),
                     "execution": result.execution_metadata, "common_randomness_claim": "none"},
        "policy": {"new_out_of_pocket_usd": 0, "automatic_model_fallback": False,
                   "live_inference_enabled": False if scripted or not result.world else None,
                   "max_requests": (len(checkpoint.source.world.schedule)-checkpoint.boundary) *
                                   (int(checkpoint.source.world.cfg["simulation"]["max_conversation_steps"])+1)},
    }))
    # Hash the replay implementation as well as the raw payload artifacts.
    source_hashes = {path.name: sha256_bytes(path.read_bytes()) for path in Path(__file__).parent.glob("*.py")}
    artifact("source_hashes.json", request_bytes(source_hashes))
    artifact("world_spec.json", request_bytes(checkpoint.spec.to_json()))
    artifact("static_state.json", request_bytes(checkpoint.source.world.static_state()))
    artifact("prefix.jsonl", b"".join(request_bytes(r.to_json()) + b"\n"
                                     for r in checkpoint.source.ledger.before(checkpoint.boundary)))
    artifact("checkpoint.json", request_bytes(checkpoint.manifest))
    artifact("snapshot.json", checkpoint.snapshot.dynamic)
    rows, previous = [], None
    for record in result.records:
        stem = f"call_{record.seq:06d}"
        request = artifact(stem + ".request.json", request_bytes(record.request))
        response = artifact(stem + ".response.json", request_bytes(record.response))
        row = {"schema_version": "ccc.event.v1", "run_id": checkpoint.spec.world_id,
               "world_id": checkpoint.spec.world_id, "branch_id": directory.name, "arm": result.arm,
               "replicate_id": result.replicate_id, "attempt_id": attempt,
               "logical_turn": record.turn_index, "event_type": "model_response",
               "agent_id": record.agent, "request_id": record.response_id,
               "request_sha256": record.request_sha256, "request_artifact": request,
               "response_artifact": response, "response_sha256": hashes[response],
               "cache_mode": record.cache_mode, "model_resolved": record.model_resolved,
               "model_requested": record.request["params"].get("model"),
               "finish_reason": record.finish_reason, "status": record.status,
               "api_cost_usd": record.api_cost_usd, "latency_ms": record.latency_ms,
               "usage": record.usage, "context_overflow": record.context_overflow,
               "error": record.error, "python_rng_state_after": record.python_rng_state_after, "seq": record.seq, "previous_event_sha256": previous}
        row["event_sha256"] = sha256_bytes(request_bytes(row))
        previous = row["event_sha256"]
        rows.append(request_bytes(row) + b"\n")
    artifact("events.jsonl", b"".join(rows))
    artifact("branch.json", request_bytes({
        "schema_version": "ccc.branch.v1", "world_id": checkpoint.spec.world_id,
        "arm": result.arm, "replicate_id": result.replicate_id, "attempt_id": attempt,
        "checkpoint_id": checkpoint.snapshot.snapshot_id, "status": result.status,
        "regime": checkpoint.spec.prompt_variant,
        "reasons": result.reasons, "outcomes": result.outcomes,
        "checks": [c.to_json() for c in result.checks], "last_event_sha256": previous,
        "record_count": len(result.records), "evidence_tier": "offline_replay" if scripted else "unclassified",
        "execution": result.execution_metadata,
    }))
    artifact("prompt_audits.json", request_bytes(result.world.prompt_audits if result.world else []))
    _write(directory / "hashes.json", request_bytes(hashes))
    return str(directory / "events.jsonl")


def verify_branch(events_path):
    """Verify payload hashes, safe relative artifact paths, and JSONL hash chain; raises on drift."""
    directory = Path(events_path).resolve().parent
    hashes = json.loads((directory / "hashes.json").read_bytes())
    for name, expected in hashes.items():
        path = (directory / name).resolve()
        if not path.is_relative_to(directory) or name != path.name:
            raise ValueError("unsafe artifact path")
        if sha256_bytes(path.read_bytes()) != expected:
            raise ValueError(f"artifact hash mismatch: {name}")
    previous = None
    rows = [json.loads(line) for line in (directory / "events.jsonl").read_bytes().splitlines()]
    summary = json.loads((directory / "branch.json").read_bytes())
    for seq, row in enumerate(rows):
        digest = row.pop("event_sha256")
        if row["previous_event_sha256"] != previous or row["seq"] != seq or sha256_bytes(request_bytes(row)) != digest:
            raise ValueError("event chain mismatch")
        if hashes.get(row["request_artifact"]) != row["request_sha256"] or hashes.get(row["response_artifact"]) != row["response_sha256"]:
            raise ValueError("request/response lineage mismatch")
        previous = digest
    if summary["record_count"] != len(rows) or summary["last_event_sha256"] != previous:
        raise ValueError("branch summary mismatch")
    return {"records": len(rows), "artifacts": len(hashes), "last_event_sha256": previous}
