"""Frozen runner manifest; no provider discovery or credential loading."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "ccc.exp003.manifest.v1"
SELECTION = "sci002.first_private_bundle.v1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


SHAM_RULE = 'int(sha256("ccc.sham.v1|" + checkpoint_id).hexdigest(), 16) % 2 == 0'


def sham_selected(checkpoint_id):
    """D-022 / amendment §6: held-out S (n = 1) runs on a checkpoint iff the hash parity is even."""
    return int(hashlib.sha256(("ccc.sham.v1|" + checkpoint_id).encode()).hexdigest(), 16) % 2 == 0


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
    if m.get("phase") == "holdout" and (m["continuations_per_arm"] or {}).get("S") != 1:
        raise ValueError("held-out S is n = 1 on the hash-selected checkpoints (D-022)")
    if m.get("b1_prompt_variant") != "deception" or m.get("colluder_selection") != "random":
        raise ValueError("B1 deception and random colluder_selection required")
    if m.get("selection_rule") != SELECTION or m.get("horizon") != "episode_end":
        raise ValueError("unsupported exposure rule or horizon")
    if m.get("common_randomness_claim") != "none":
        raise ValueError("common_randomness_claim must be none")
    arms = m.get("arms", [])
    if set(arms) != {"F", "S", "K", "N", "PF", "PK"} or len(arms) != 6:
        raise ValueError("declare F/S/K/N; N_m runs on every checkpoint with M* non-empty (v1.2)")
    counts = m["continuations_per_arm"]
    floor = {a: (1 if a == "S" and m.get("phase") == "holdout" else 2) for a in arms}
    if not isinstance(counts, dict) or set(counts) != set(arms) or any(
            type(n) is not int or n < floor[a] for a, n in counts.items()):
        raise ValueError("continuations_per_arm must map F/S/K/N to integers >= 2 (held-out S >= 1)")

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
    if m.get("backend") not in ("local", "modal") or model.get("backend") != {"local": "ollama_local", "modal": "modal"}[m["backend"]] or model.get("requested_id") != "gemma4:26b":
        raise ValueError("this primary-stratum runner pins ollama_local/gemma4:26b")
    if model.get("context_limit") != 32768 or model.get("parameters", {}).get("reasoning_effort") != "none":
        raise ValueError("benchmark requires ctx 32768 and reasoning_effort none")
    from urllib.parse import urlsplit
    endpoint = urlsplit(model.get("base_url", ""))
    if endpoint.path != "/v1" or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment:
        raise ValueError("endpoint must be a credential-free /v1 URL")
    if m["backend"] == "local" and (endpoint.scheme != "http" or endpoint.hostname not in ("127.0.0.1", "localhost")):
        raise ValueError("local requires loopback HTTP")
    if m["backend"] == "modal" and (endpoint.scheme != "https" or not (endpoint.hostname or "").endswith(".modal.run")):
        raise ValueError("modal requires HTTPS Modal host")
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
    if any(counts[a] != 4 for a in ("F", "K", "N", "PF", "PK")):
        raise ValueError("EXP-003 requires four continuations per primary arm")
    pairs = {}
    for w in worlds:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", w.get("pair_id", "")):
            raise ValueError("shared pair_id required")
        pairs.setdefault(w["pair_id"], []).append(w)
    for pair in pairs.values():
        if len(pair) != 2 or {w["regime"] for w in pair} != {"B1", "B2"} or len({w["seed"] for w in pair}) != 1:
            raise ValueError("pair requires same seed and both regimes")
    if len({w["seed"] for w in worlds}) != len(pairs):
        raise ValueError("different pairs require different seeds")
    expected = [w["id"] for pair in pairs.values() for w in sorted(pair, key=lambda w: w["regime"])]
    if [w["id"] for w in worlds] != expected:
        raise ValueError("worlds must follow frozen pair order, B1 then B2")
    if m["phase"] == "holdout":
        if len(pairs) != 32:
            raise ValueError("holdout requires exactly 32 scheduled pairs")
        if m.get("hard_stop_utc") != "2026-10-25T09:00:00Z":
            raise ValueError("holdout hard stop must be 09:00 UTC")
        if not m.get("seed_exclusion_sha256") or not m.get("freeze_sha256"):
            raise ValueError("freeze and audited seed exclusion hashes required")
        from .freeze import verify_freeze
        verify_freeze(m)
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

    # One fixed checkpoint slot per base trajectory; decided before any source calls/outcomes.
    # v1.2: N_m on ALL checkpoints (whether M* is non-empty is decided at collection time and
    # recorded in placebo.json); held-out S runs on the hash-selected checkpoints only (D-022).
    jobs = []
    for w in m["worlds"]:
        arms = [a for a in m["arms"] if a != "S" or m["phase"] != "holdout" or sham_selected(w["id"])]
        order = []
        for rep in range(max(m["continuations_per_arm"].values())):
            block = [a for a in arms if rep < m["continuations_per_arm"][a]]
            rng = random.Random(int(digest([m["branch_order_seed"], w["id"], rep]), 16))
            rng.shuffle(block)
            order.extend({"arm": arm, "replicate": rep,
                          "seed": call_seed(m, w["id"], arm, rep, -1, 0)} for arm in block)
        counts = {a: sum(i["arm"] == a for i in order) for a in m["arms"]}
        jobs.append({"world": w, "order": order, "placebo": "N" in arms, "arm_counts": counts,
                     "sham_selected": sham_selected(w["id"]) if m["phase"] == "holdout" else True})
    return {"manifest_sha256": digest(m), "independent_worlds": len({w["seed"] for w in m["worlds"]}),
            "base_trajectories": len(jobs), "continuations": sum(len(j["order"]) for j in jobs),
            "max_requests": m["max_requests"], "jobs": jobs,
            "live_inference_enabled": m["policy"]["live_inference_enabled"]}


def fresh_pairs(freeze_commit, excluded_seeds, count=32):
    """Frozen hash stream, sampled only after director freeze; no random runtime state."""
    if not re.fullmatch(r"[0-9a-f]{40,64}", freeze_commit) or not 16 <= count <= 32:
        raise ValueError("director freeze commit and 16..32 pairs required")
    excluded, used, worlds = set(excluded_seeds), set(), []
    index = 0
    while len(used) < count:
        seed = 1_000_000_000 + int(digest(["ccc.exp003.world.v1", freeze_commit, index])[:8], 16) % 1_000_000_000
        index += 1
        if seed in excluded or seed in used:
            continue
        used.add(seed)
        pair_id = f"exp003_pair_{len(used):03}"
        worlds.extend(dict(id=f"{pair_id}_{regime}", pair_id=pair_id, seed=seed,
                           regime=regime, split="holdout") for regime in ("B1", "B2"))
    return worlds


def stream_skips(freeze_commit, excluded_seeds, count=32):
    """Audit every rejected counter without changing the frozen seed algorithm."""
    wanted = fresh_pairs(freeze_commit, excluded_seeds, count)
    excluded, used, skips, i = set(excluded_seeds), set(), [], 0
    while len(used) < len(wanted) // 2:
        seed = 1_000_000_000 + int(digest(["ccc.exp003.world.v1", freeze_commit, i])[:8], 16) % 1_000_000_000
        if seed in excluded or seed in used:
            skips.append(dict(counter=i, seed=seed, reason="excluded" if seed in excluded else "duplicate"))
        else:
            used.add(seed)
        i += 1
    return skips
