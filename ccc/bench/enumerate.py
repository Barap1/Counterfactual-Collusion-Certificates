"""Exact byte equivalence over the full finite design; no method dependency.

I(S) is conditional on nuisance and the declared seeded continuation schedule.
It is NOT a distributional identifiability theorem about every possible noise
realization. Partitions preserve canonical bytes as well as hashes, so hash
collisions cannot silently define equivalence. Pairwise and global frontiers
are separate outputs: different members need not have singleton-label classes.
"""
from collections import Counter, defaultdict
from .observe import SETS, canonical, observe, project
from .twins import ATTRIBUTABLE, oracle, pair, policy_space


def partition(items, view_fn, label_fn):
    """Generic finite enumerator; uniform per-policy prior, deterministic ties."""
    groups = defaultdict(list)
    for key, item in items:
        groups[canonical(view_fn(item))].append((key, label_fn(item)))
    result = {}
    for encoded, members in sorted(groups.items()):
        counts = Counter(label for _, label in members)
        majority = min(counts, key=lambda x:(-counts[x], str(x)))
        result[encoded] = dict(members=[k for k,_ in members], labels=dict(counts),
                               identifiable=len(counts) == 1, majority=majority,
                               prior_mass=len(members)/sum(len(g) for g in groups.values()))
    return result


def census(seed, epsilon=0):
    """All rules x payoffs x bits x applicable authorization/fault variants."""
    entries = []
    for instance in policy_space(seed, epsilon):
        entries.append((instance.key, instance, observe(instance, "I5"), oracle(instance)))
    tables = {}
    for s in SETS:
        grouped = defaultdict(list)
        for key, instance, full, truth in entries:
            grouped[canonical(project(full, s))].append((key, truth))
        tables[s] = {}
        for encoded, members in sorted(grouped.items()):
            labels = Counter(t["M"] for _,t in members)
            axes = {axis:Counter(t[axis] if axis != "attribution" else t["M"] in ATTRIBUTABLE
                                for _,t in members) for axis in ("H", "E", "attribution")}
            axes["M"] = labels
            tables[s][encoded] = dict(members=[k for k,_ in members],
                prior_mass=len(members)/len(entries),
                axes={a:dict(counts={(str(k).lower() if isinstance(k,bool) else k):v for k,v in c.items()}, identifiable=len(c)==1,
                             majority=min(c, key=lambda x:(-c[x], str(x)))) for a,c in axes.items()})
    return tables


def lookup(tables, view):
    return tables[view["information_set"]][canonical(view)]


def design_reference(entry):
    """Only the frozen design-class prior enters Bayes, never private member ids."""
    return {"axes":entry["axes"], "prior_mass":entry["prior_mass"]}


def frontier(seed, epsilon=0, tables=None):
    tables = tables or census(seed, epsilon)
    out = {}
    for kind in ("P1", "P2", "P3", "P4", "P5", "P6"):
        a,b = pair(kind, seed, epsilon)
        by_set = {}
        for s in SETS:
            av,bv = observe(a,s), observe(b,s)
            by_set[s] = dict(pair_distinct=canonical(av)!=canonical(bv),
                             M_identifiable=[lookup(tables,v)["axes"]["M"]["identifiable"] for v in (av,bv)],
                             attribution_identifiable=[lookup(tables,v)["axes"]["attribution"]["identifiable"] for v in (av,bv)])
        out[kind] = dict(minimal_pair_separator=next((s for s in SETS if by_set[s]["pair_distinct"]), None),
                         minimal_global_M=next((s for s in SETS if all(by_set[s]["M_identifiable"])), None),
                         minimal_global_attribution=next((s for s in SETS if all(by_set[s]["attribution_identifiable"])), None),
                         by_set=by_set, definitional_authorization=kind=="P3",
                         same_label_control=kind=="P5")
    return out


def serializable_partition(tables):
    """Keep exact canonical observable bytes in the inspectable partition."""
    from hashlib import sha256
    return {s:[dict(view_sha256=sha256(encoded.encode()).hexdigest(),
                    canonical_view=encoded, **entry) for encoded,entry in table.items()]
            for s,table in tables.items()}
