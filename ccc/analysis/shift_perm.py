"""Exact conditional shift-permutation inference on the frozen cent grid."""
from functools import lru_cache
from itertools import combinations
import numpy as np


@lru_cache(None)
def _labels(n, k):
    a = np.zeros((len(list(combinations(range(n), k))), n))
    for row, idx in zip(a, combinations(range(n), k)):
        row[list(idx)] = 1
    return a


def perm_p(F, K, m=0, side='ge'):
    if not len(F) or not len(K):
        raise ValueError('both arms must be nonempty')
    if side not in ('ge', 'le'):
        raise ValueError('side must be ge or le')
    pool = np.array([*F, *(x-m for x in K)], dtype=float)
    if not np.isfinite(pool).all():
        raise ValueError('finite outcomes required')
    sums = (_labels(len(pool), len(K)) * pool).sum(axis=1)
    stats = sums/len(K) - (pool.sum()-sums)/len(F)
    obs = np.mean(K)-m-np.mean(F)
    return float(np.mean(stats >= obs-1e-12) if side == 'ge' else np.mean(stats <= obs+1e-12))


def _bound(F, K, side, alpha):
    # Each assignment's statistic minus observed is affine in m. Thus the
    # tail probabilities are monotone, and binary search is the exact grid scan.
    lo, hi = 0, 12000
    if side == 'ge':
        while lo < hi:
            mid = (lo+hi)//2
            if perm_p(F, K, (mid-6000)/100, side) > alpha:
                hi = mid
            else:
                lo = mid+1
        return (lo-6000)/100
    while lo < hi:
        mid = (lo+hi+1)//2
        if perm_p(F, K, (mid-6000)/100, side) > alpha:
            lo = mid
        else:
            hi = mid-1
    return (lo-6000)/100


def lower(F, K, alpha=0.05):
    return _bound(F, K, 'ge', alpha)


def upper(F, K, alpha=0.05):
    return _bound(F, K, 'le', alpha)


def interval(F, K, alpha=0.05):
    return lower(F, K, alpha), upper(F, K, alpha)
