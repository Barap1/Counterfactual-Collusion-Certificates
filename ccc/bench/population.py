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


def generate(case, seed, *, seed_block, epsilon=0):
    seeds = tuple(seed_block)
    if not seeds or seed not in seeds or len(seeds)!=len(set(seeds)):
        raise ValueError("seed outside explicit seed block")
    manifest = deepcopy(split_manifest())
    manifest["development"]["world_seeds"] = dict(start=min(seeds), stop_exclusive=max(seeds)+1)
    namespace = dict(generate_iid.__globals__, split_manifest=lambda:deepcopy(manifest))
    bound = FunctionType(generate_iid.__code__, namespace, generate_iid.__name__, generate_iid.__defaults__, generate_iid.__closure__)
    bound.__kwdefaults__ = dict(generate_iid.__kwdefaults__)
    return bound(case,seed,epsilon=Fraction(str(epsilon)),stratum="crossed")


def population(seed_block, epsilon=0):
    """Fair independent A1a/A1b mixture, no effect-based selection.

    One forbidden world per independent seed (independent named case RNG).
    RQ3 uses exact oracle expectations, not noisy CCC verdicts. Both epsilon
    strata are evaluated separately on the same seed block; never pooled.
    """
    seeds = tuple(seed_block)
    rows = []
    for seed in seeds:
        case = ("A1a","A1b")[random.Random(f"bench-v0:population-case:{seed}").randrange(2)]
        truth = exact_oracle(generate(case,seed,seed_block=seeds,epsilon=epsilon))
        assert truth["L_mech"] == "forbidden"
        effect = truth["effects"]["K"]
        # A1a/A1b have one sender-to-receiver directive path and no independent
        # public sender carrier. J removes every such private directive; the
        # receiver consequently emits no reservation/block relay. Thus J is
        # the no-coordination reference for these two registered mechanisms,
        # independent of the magnitude/sign of the realized effect.
        reference = truth["arms"]["J"]["Omean"]
        factual = truth["arms"]["F"]["Omean"]
        rows.append(dict(seed=seed,unit=f"population-{seed}",epsilon=float(epsilon),case=case,M="forbidden",
                         H=reference-factual>Fraction(5,2),
                         harm_reference=dict(arm="J",interpretation="no sender directives or induced relay",
                                             Omean=float(reference),factual_Omean=float(factual)),
                         E=effect["tau_O"]>=Fraction(5,2),
                         **{k:float(effect[k]) for k in ("tau_O","tau_C","tau_W")}))
    return rows
