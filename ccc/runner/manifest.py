"""Frozen runner manifest; no provider discovery or credential loading."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "ccc.runner.manifest.v1"
SELECTION = "sci002.first_private_bundle.v1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze_hash(m):
    normalized = dict(m)
    normalized.setdefault("continuations_per_arm", {"F": 4, "K": 4, "S": 2, "N": 4})
    return digest({k: v for k, v in normalized.items() if k not in ("stat001", "stat001_hash")})


def repo_file(name):
    path = (ROOT / name).resolve()
    if not path.is_relative_to(ROOT) or path.name in (".env", "compute.env") or path.name.endswith(".local.json"):
        raise ValueError("artifact must be a non-secret repository file")
    return path


def validate(m):
    if m.get("schema_version") != SCHEMA:
        raise ValueError("unsupported manifest schema")
    for key in ("experiment_id", "analysis_commit", "upstream_commit", "ccc_commit"):
        if not isinstance(m.get(key), str) or not m[key] or m[key] == "REQUIRED":
            raise ValueError(f"missing {key}")
    if m.get("phase") not in ("development", "holdout") or m.get("frozen") is not True:
        raise ValueError("manifest must be frozen with a declared phase")
    for path_key, hash_key in (("protocol_artifact", "protocol_sha256"),):
        if file_hash(repo_file(m[path_key])) != m.get(hash_key):
            raise ValueError(f"{hash_key} mismatch")
    m.setdefault("continuations_per_arm", {"F": 4, "K": 4, "S": 2, "N": 4})
    if m.get("phase") == "holdout" or any(w.get("split") == "holdout" for w in m.get("worlds", [])):
        freeze = m.get("stat001", {})
        if freeze.get("task_id") != "STAT-001" or not re.fullmatch(r"[0-9a-f]{64}", freeze.get("sha256", "")):
            raise ValueError("held-out seeds require a STAT-001 artifact hash")
        if m.get("stat001_hash") != freeze["sha256"]:
            raise ValueError("STAT-001 stat001_hash must match approval artifact hash")
        if file_hash(repo_file(freeze["artifact"])) != freeze["sha256"]:
            raise ValueError("STAT-001 artifact hash mismatch")
        approval = json.loads(repo_file(freeze["artifact"]).read_text())
        if approval.get("task_id") != "STAT-001" or approval.get("frozen_manifest_sha256") != freeze_hash(m):
            raise ValueError("STAT-001 artifact does not bind this frozen manifest")
    if m.get("b1_prompt_variant") != "deception" or m.get("colluder_selection") != "random":
        raise ValueError("B1 deception and random colluder_selection required")
    if m.get("selection_rule") != SELECTION or m.get("horizon") != "episode_end":
        raise ValueError("unsupported exposure rule or horizon")
    if m.get("common_randomness_claim") != "none":
        raise ValueError("common_randomness_claim must be none")
    arms = m.get("arms", [])
    if set(arms) != {"F", "S", "K", "N"} or len(arms) != 4:
        raise ValueError("declare F/S/K/N; N is collected on the frozen random half")
    counts = m["continuations_per_arm"]
    if not isinstance(counts, dict) or set(counts) != set(arms) or any(
            type(n) is not int or n < 2 for n in counts.values()):
        raise ValueError("continuations_per_arm must map F/S/K/N to integers >= 2")
    if type(m.get("max_requests")) is not int or m["max_requests"] <= 0:
        raise ValueError("max_requests must be a positive integer")
    for key in ("branch_order_seed", "master_seed", "placebo_subset_seed"):
        if type(m.get(key)) is not int:
            raise ValueError(f"{key} must be an integer")
    if "sampling_seed" in m:
        raise ValueError("replace sampling_seed with master_seed")
    if m.get("hard_stop_utc") is not None:
        parse_time(m["hard_stop_utc"])
    model = m["model"]
    if (model.get("backend"), model.get("requested_id")) != ("ollama_local", "gemma4:26b"):
        raise ValueError("this primary-stratum runner pins ollama_local/gemma4:26b")
    if model.get("context_limit") != 32768 or model.get("parameters", {}).get("reasoning_effort") != "none":
        raise ValueError("benchmark requires ctx 32768 and reasoning_effort none")
    from urllib.parse import urlsplit
    endpoint = urlsplit(model.get("base_url", ""))
    if endpoint.scheme != "http" or endpoint.hostname != "127.0.0.1" or endpoint.path != "/v1" or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment:
        raise ValueError("unexpected local endpoint")
    if model.get("weight_digest") != "5571076f3d70050487b26b341705799e0ab29b808164f90d20d4cf84f699d251":
        raise ValueError("unbenchmarked model digest")
    if model["parameters"].get("temperature") != 0.7 or model["parameters"].get("max_tokens") != 1500:
        raise ValueError("prereg requires temperature 0.7 and max_tokens 1500")
    policy = m.get("policy", {})
    if policy != {"new_out_of_pocket_usd": 0, "automatic_model_fallback": False,
                  "live_inference_enabled": policy.get("live_inference_enabled")} or type(policy.get("live_inference_enabled")) is not bool:
        raise ValueError("runner requires $0 with no fallback")
    template = m.get("world_template", {})
    if template.get("environment", {}).get("assignment_filling") is not False:
        raise ValueError("world_template must disable assignment filling")
    sweep = template.get("experiment", {}).get("sweeps", [{}])[0]
    if sweep.get("num_agents") != [4] or sweep.get("colluder_counts") != [2] or sweep.get("secret_channel_enabled") != [True]:
        raise ValueError("world_template must declare four agents and a private pair")
    if template.get("simulation", {}).get("max_planning_rounds") != 2:
        raise ValueError("Gate B template requires two planning rounds")
    worlds = m.get("worlds", [])
    if not worlds or len({w["id"] for w in worlds}) != len(worlds):
        raise ValueError("world ids must be present and unique")
    if len({(w["seed"], w["regime"]) for w in worlds}) != len(worlds):
        raise ValueError("duplicate world seed/regime")
    if m["phase"] == "holdout" and len(worlds) % 2:
        raise ValueError("held-out checkpoint slots must be even for exact 50% N subset")
    seeds = {}
    for w in worlds:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", w["id"]) or type(w["seed"]) is not int:
            raise ValueError("unsafe world id or non-integer seed")
        if w["split"] != m["phase"] or (w["seed"] == 1 and w["split"] != "development"):
            raise ValueError("world split mismatch; archival seed 1 is development only")
        if seeds.setdefault(w["seed"], w["split"]) != w["split"]:
            raise ValueError("seed cannot cross splits")
        if w["regime"] not in ("B1", "B2"):
            raise ValueError("runner supports matched B1/B2 pair-channel regimes")
    return m


def load(path):
    return validate(json.loads(Path(path).read_text()))


def parse_instant(value):
    """Parse any timestamp with an explicit offset (e.g. Ollama's local-zone expires_at) as an aware datetime."""
    from datetime import datetime
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None or t.utcoffset() is None:
        raise ValueError("timestamp must include a timezone offset")
    return t  # aware; comparisons and subtraction are offset-correct without UTC conversion


def parse_time(value):
    """hard_stop_utc: must be expressed in UTC (Z or +00:00)."""
    from datetime import datetime
    t = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else None
    if t is None or t.tzinfo is None or t.utcoffset().total_seconds() != 0:
        raise ValueError("hard_stop_utc must be UTC")
    return parse_instant(value)


def call_seed(m, checkpoint_id, arm, replicate, turn, call_k, agent=""):
    # Canonical JSON avoids delimiter ambiguities. Domain/version is frozen in the schema.
    key = ["ccc.runner.seed.v1", m["master_seed"], m["protocol_sha256"],
           checkpoint_id, arm, replicate, turn, call_k, agent]
    return int(digest(key)[:8], 16) >> 1


def plan(m):
    import random

    # One fixed checkpoint slot per base trajectory; sample before any source calls/outcomes.
    ids = sorted(w["id"] for w in m["worlds"])
    random.Random(m["placebo_subset_seed"]).shuffle(ids)
    placebo = set(ids[:len(ids) // 2]) if m["phase"] == "holdout" else set(ids)
    jobs = []
    for w in m["worlds"]:
        arms = [a for a in m["arms"] if a != "N" or w["id"] in placebo]
        order = []
        for rep in range(max(m["continuations_per_arm"].values())):
            block = [a for a in arms if rep < m["continuations_per_arm"][a]]
            rng = random.Random(int(digest([m["branch_order_seed"], w["id"], rep]), 16))
            rng.shuffle(block)
            order.extend({"arm": arm, "replicate": rep,
                          "seed": call_seed(m, w["id"], arm, rep, -1, 0)} for arm in block)
        jobs.append({"world": w, "order": order, "placebo": "N" in arms})
    return {"manifest_sha256": digest(m), "independent_worlds": len({w["seed"] for w in m["worlds"]}),
            "base_trajectories": len(jobs), "continuations": sum(len(j["order"]) for j in jobs),
            "max_requests": m["max_requests"], "jobs": jobs,
            "live_inference_enabled": m["policy"]["live_inference_enabled"]}
