"""World-unit inference and descriptive exact categorical permutation data."""
from collections import Counter
from itertools import combinations, product
import math
import numpy as np
from scipy.stats import beta, t

SEED = 20261025
B = 10000


class InsufficientWorlds(ValueError):
    pass


def bootstrap(values):
    values = np.asarray(values, dtype=float)
    if len(values) < 2:
        raise InsufficientWorlds('bootstrap requires at least two independent worlds')
    if not np.isfinite(values).all():
        raise ValueError('finite world values required')
    rng = np.random.Generator(np.random.PCG64(SEED))
    draws = values[rng.integers(0, len(values), size=(B, len(values)))].mean(axis=1)
    return tuple(float(x) for x in np.percentile(draws, [2.5, 97.5], method='linear'))


def sign_flip(values, two_sided=False):
    values = list(values)
    nz = [x for x in values if abs(x) > 1e-12]
    if len(nz) > 10:
        raise ValueError('exact sign-flip is registered for at most 10 nonzero worlds')
    if not values or 2**(-len(nz)) > .05:
        return {'p': None, 'status': 'unattainable', 'n_nonzero': len(nz)}
    obs = sum(values)/len(values)
    stats = [sum(s*x for s, x in zip(signs, nz))/len(values)
             for signs in product((-1, 1), repeat=len(nz))]
    p = sum(abs(x) >= abs(obs)-1e-12 if two_sided else x >= obs-1e-12 for x in stats)/len(stats)
    return {'p': p, 'status': 'attainable', 'n_nonzero': len(nz)}


def holm(ps):
    # Missing tests retain their place in the frozen family, as p=1.
    order = sorted(range(len(ps)), key=lambda i: ps[i] if ps[i] is not None else 1)
    out, prev = [None]*len(ps), 0
    for rank, i in enumerate(order):
        prev = max(prev, min(1, (len(ps)-rank)*(ps[i] if ps[i] is not None else 1)))
        out[i] = prev if ps[i] is not None else None
    return out


def binomial_ci(k, n, alpha=.05):
    if not n:
        return None, None
    return (0. if k == 0 else float(beta.ppf(alpha/2, k, n-k+1)),
            1. if k == n else float(beta.ppf(1-alpha/2, k+1, n-k)))


def t_interval(values, confidence=.95):
    if len(values) < 2:
        return None, None
    mean = float(np.mean(values))
    half = float(t.ppf((1+confidence)/2, len(values)-1)*np.std(values, ddof=1)/math.sqrt(len(values)))
    return mean-half, mean+half


def tv_excess(F, K):
    if not F or not K:
        return {'TV_raw': None, 'TV_null_mean': None, 'TV_excess': None}
    labels = F+K
    def tv(a, b):
        ca, cb = Counter(a), Counter(b)
        return .5*sum(abs(ca[x]/len(a)-cb[x]/len(b)) for x in set(labels))
    raw = tv(F, K)
    null = []
    for idx in combinations(range(len(labels)), len(F)):
        chosen = set(idx)
        null.append(tv([x for i,x in enumerate(labels) if i in chosen],
                       [x for i,x in enumerate(labels) if i not in chosen]))
    return {'TV_raw': raw, 'TV_null_mean': float(np.mean(null)), 'TV_excess': raw-float(np.mean(null)),
            'TV_interval': None, 'TV_interval_reason': 'no frozen interval algorithm specified'}


def summarize(values):
    values = [x for x in values if x is not None]
    lo, hi = bootstrap(values) if len(values) > 1 else (None, None)
    return {'estimate': float(np.mean(values)) if values else None, 'L': lo, 'U': hi,
            'n_independent': len(values)}
