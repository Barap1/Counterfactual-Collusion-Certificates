"""Regenerate private DEVELOPMENT evidence offline; never instantiate holdout.

python -m ccc.fixtures --output docs/fix/development_evidence.json --native
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import socket
from unittest.mock import patch

from .jira import CASES, exact_oracle, generate_jira, run_jira_branch
from .worlds import split_manifest


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _native_evidence():
    from ccc import paths
    from .native_replay import as_replay_fixture
    root=Path(__file__).resolve().parents[2]/"starter/collusion_hackathon/colosseum"
    with patch.object(paths,"colosseum_root",return_value=root), patch.object(
            paths,"_local_manifest",side_effect=AssertionError("secret manifest forbidden")):
        from ccc.replay.fixtures import run_fixture
        records=[]
        for case in ("A1a","A1b","A2a","A2b","A2-boundary","A3a","A3b","A4b","A5a-verbatim","A5a-paraphrase","A5b"):
            world=generate_jira(case,12000,profile="golden")
            report=run_fixture(as_replay_fixture(world))
            records.append({"case":case,"world_id":world.world_id,"world_seed":12000,
                "probe_order":"sender-first native bridge; excluded from primary order distribution",
                "audit_valid":report.audit.valid,"expectations":report.expectations,
                "branches":{a:{"status":b.status,"reasons":b.reasons,
                    "outcomes":{k:b.outcomes.get(k) for k in ("Cmean","Omean","A","W")} if b.outcomes else None}
                    for a,b in report.audit.branches.items()},
                "ccc_status_measured":False})
        return records


def collect_development(*, native=False):
    manifest=split_manifest()
    bounds=manifest["development"]["world_seeds"]
    groups=[]
    total=0
    for stratum in ("crossed","naturalistic"):
        for case in CASES:
            for base in ("mixed50/50" if case.startswith("A6") else "A1a",):
                worlds=[]
                statuses={arm:Counter() for arm in ("F","S","K","N","C")}
                orders=Counter()
                wording=Counter()
                for seed in range(bounds["start"],bounds["stop_exclusive"]):
                    offset=seed-bounds["start"]
                    actual_base=("A1a" if bool((offset%2)^((offset//2)%2)) else "A3a") if case.startswith("A6") else "A1a"
                    world=generate_jira(case,seed,stratum=stratum,invalid_base=actual_base)
                    truth=exact_oracle(world)
                    branches={a:run_jira_branch(world,a) for a in ("F","S","K","N","C")}
                    for a,b in branches.items():
                        statuses[a][b["status"]]+=1
                    order=",".join(str(world.roles.index(a)) for a in world.order)
                    orders[order]+=1
                    wording[world.wording]+=1
                    input_hashes={a:sha256(json.dumps([
                        {k:r[k] for k in ("turn","agent_id","phase","messages")}
                        for r in b["detector_inputs"]["records"]],sort_keys=True).encode()).hexdigest()
                        for a,b in branches.items()}
                    worlds.append({"world_id":world.world_id,"world_seed":seed,
                        "matched_world_group":f"task_{seed}","template_group":world.template_group,
                        "wording":world.wording,"wording_type":world.wording_type,"profile":world.profile,
                        "sender_commitment":world.sender_commitment,"invalid_base":actual_base if case.startswith("A6") else None,
                        "role_mapping":list(world.roles),"order":list(world.order),
                        "L_mech":truth["L_mech"],"expected_audit_label":truth["expected_audit_label"],
                        "SCI002_predicted_status":truth["predicted_status"],
                        "oracle_effects":truth["effects"],"oracle_factual_advantage":truth["arms"]["F"]["A"],
                        "oracle_strata":truth["strata"],"placebo_K_minus_N":truth["placebo_K_minus_N"],
                        "branch_status":{a:b["status"] for a,b in branches.items()},
                        "validity_failures":{a:b["validity_failures"] for a,b in branches.items()},
                        "request_input_sha256":input_hashes})
                    total+=1
                groups.append({"case":case,"stratum":stratum,"invalid_base":base if case.startswith("A6") else None,
                    "worlds":worlds,"counts":{a:dict(c) for a,c in statuses.items()},
                    "realized_role_order_distribution":dict(sorted(orders.items())),"wording_counts":dict(wording)})
    stochastic=[]
    for case in ("A1a","A1b","A2a","A2b","A3a","A3b","A4b","A5a-verbatim","A5a-paraphrase","A5b"):
        for epsilon in (Fraction(1,10),Fraction(1,4)):
            world=generate_jira(case,12000,epsilon=epsilon)
            truth=exact_oracle(world)
            stochastic.append({"case":case,"world_id":world.world_id,"world_seed":world.seed,
                "epsilon":epsilon,"noise_paths":truth["noise_paths"],"oracle_mass":truth["oracle_mass"],
                "oracle_effects":truth["effects"]})
    authority=["docs/research/sci002/fixture_spec.md","docs/research/sci002/protocol.md"]
    sources=[*Path("ccc/fixtures").glob("*.py"),Path("ccc/fixtures/split_manifest.json")]
    sources += [Path(p) for p in authority if Path(p).exists()]
    if native:
        sources += list(Path("ccc/replay").glob("*.py"))
    result={"schema_version":"ccc.fixture_development_evidence.v1","visibility":"EVALUATOR_PRIVATE; never a detector input",
        "evidence_tier":"controlled_mechanism","phase":"development","deterministic_instances":total,
        "matched_world_groups":20,"stochastic_oracle_probes":len(stochastic),"holdout_worlds_generated":0,
        "live_inference_calls":0,"new_spend_usd":0,"CCC_classification_accuracy_measured":False,
        "source_sha256":{str(p):digest(p) for p in sorted(sources)},
        "groups":groups,"stochastic_probes":stochastic}
    if native:
        result["native_replay_probes"]=_native_evidence()
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path("docs/fix/development_evidence.json"))
    parser.add_argument("--native",action="store_true")
    args=parser.parse_args()
    with patch.object(socket.socket,"connect",side_effect=AssertionError("offline evidence collection")):
        evidence=collect_development(native=args.native)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(evidence,indent=2,default=lambda v:str(v) if isinstance(v,Fraction) else v)+"\n")
    print(json.dumps({"output":str(args.output),"sha256":digest(args.output),
        "deterministic_instances":evidence["deterministic_instances"],"matched_world_groups":20,
        "stochastic_oracle_probes":len(evidence["stochastic_probes"]),"holdout_worlds_generated":0,
        "native_probes":len(evidence.get("native_replay_probes",[])),
        "native_valid":sum(r["audit_valid"] for r in evidence.get("native_replay_probes",[])),
        "native_all_expectations_match":all(all(r["expectations"].values()) for r in evidence.get("native_replay_probes",[])),
        "live_inference_calls":0,"new_spend_usd":0},sort_keys=True))


if __name__ == "__main__":
    main()
