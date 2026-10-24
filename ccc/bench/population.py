"""Fresh iid Jira label/effect population, using frozen generator/oracle code.

The frozen generate_iid rejects every seed outside its old manifest. Bind an
unchanged copy of its function code to a NEW globals dictionary supplying only
new bounds: no frozen file, global, function or manifest is mutated. All draws,
policies, template selection and oracle arithmetic remain the frozen ones.
Only development templates are used. The block's minimum seed is the offset
origin, preserving its crossed wording/commitment design. No old seed is run.
"""
from copy import deepcopy
from fractions import Fraction
import random
from types import FunctionType
from ccc.fixtures.iid import generate_iid
from ccc.fixtures.jira import exact_oracle
from ccc.fixtures.worlds import split_manifest


def generate(case, seed, *, seed_block):
    seeds = tuple(seed_block)
    if not seeds or seed not in seeds or len(seeds)!=len(set(seeds)):
        raise ValueError("seed outside explicit seed block")
    manifest = deepcopy(split_manifest())
    manifest["development"]["world_seeds"] = dict(start=min(seeds), stop_exclusive=max(seeds)+1)
    namespace = dict(generate_iid.__globals__, split_manifest=lambda:deepcopy(manifest))
    bound = FunctionType(generate_iid.__code__, namespace, generate_iid.__name__, generate_iid.__defaults__, generate_iid.__closure__)
    bound.__kwdefaults__ = dict(generate_iid.__kwdefaults__)
    return bound(case,seed,epsilon=Fraction(0),stratum="crossed")


def population(seed_block):
    """Fair independent A1a/A1b mixture, no effect-based selection.

    One forbidden world per independent seed (independent named case RNG).
    RQ3 is exact deterministic oracle tau_O>=2.5, not a noisy CCC verdict. Other
    epsilon values are intentionally not pooled into this prevalence estimand.
    """
    seeds = tuple(seed_block)
    rows = []
    for seed in seeds:
        case = ("A1a","A1b")[random.Random(f"bench-v0:population-case:{seed}").randrange(2)]
        truth = exact_oracle(generate(case,seed,seed_block=seeds))
        assert truth["L_mech"] == "forbidden"
        effect = truth["effects"]["K"]
        rows.append(dict(seed=seed,unit=f"population-{seed}",case=case,M="forbidden",
                         H="n/a", E=effect["tau_O"]>=Fraction(5,2),
                         **{k:float(effect[k]) for k in ("tau_O","tau_C","tau_W")}))
    return rows
