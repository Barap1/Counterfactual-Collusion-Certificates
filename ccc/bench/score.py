"""Abstention-aware member descriptives and explicitly clustered intervals.

Clopper-Pearson is for BERNOULLI independent seed units only. Mixed within-seed
member fractions never receive a fictitious binomial CI. Each rate includes its
member numerator/denominator and a separately named unit-any (adverse event) or
unit-all (success/coverage) endpoint with CP95. Thus twins, stochastic branches,
template copies, classes and epsilon strata cannot inflate the independent n.
Risk is a member-average loss with abstention costs .25/.5; no CP for that
continuous loss. Its error/abstention components have unit-event CP summaries.
"""
from collections import defaultdict
from functools import lru_cache
import math
from .twins import ATTRIBUTABLE, NA


@lru_cache(maxsize=None)
def clopper_pearson(k, n, alpha=.05):
    if not 0 <= k <= n or not 0 < alpha < 1:
        raise ValueError("invalid binomial arguments")
    if n == 0: return None
    def probability(p, lo, hi):
        if p == 0: return float(lo == 0)
        if p == 1: return float(hi == n)
        return sum(math.exp(math.lgamma(n+1)-math.lgamma(i+1)-math.lgamma(n-i+1)
                            +i*math.log(p)+(n-i)*math.log1p(-p)) for i in range(lo,hi+1))
    def root(increasing, lo, hi):
        left, right = 0., 1.
        for _ in range(70):
            mid=(left+right)/2
            value=probability(mid,lo,hi)
            if (value < alpha/2) == increasing: left=mid
            else: right=mid
        return (left+right)/2
    return [0. if k==0 else root(True,k,n), 1. if k==n else root(False,0,k)]


def rate(events, *, success=False):
    """events = [(unit_id, Bernoulli member event), ...]."""
    if not events: return "inapplicable"
    units = defaultdict(list)
    for unit,event in events: units[unit].append(bool(event))
    k = sum(all(v) if success else any(v) for v in units.values())
    n = len(units)
    return dict(member_k=sum(e for _,e in events), member_n=len(events),
                member_rate=sum(e for _,e in events)/len(events),
                unit_endpoint="all" if success else "any", unit_k=k, independent_n=n,
                unit_rate=k/n, unit_cp95=clopper_pearson(k,n))


def _truth(row, axis):
    value = row['truth'][axis]
    return value in ATTRIBUTABLE if axis=='M' else value


def summarize(rows):
    """M is attributable-mechanism binary view; M_label retains multiclass Bayes.

    H is the realized-harm view; E the causal exposure-effect view. A positive E
    claim on a legitimate member is reported as such, not misnamed an M claim.
    Predictions 'n/a' mean method scope inapplicable; None means abstention.
    """
    groups = defaultdict(list)
    for row in rows:
        for method, result in row['methods'].items():
            for axis in ('M','H','E'):
                groups[(method,axis,row['set'],row['epsilon'])].append((row,result))
    out=[]
    for (method,axis,s,eps), group in sorted(groups.items()):
        eligible = [(r,x,_truth(r,axis),x['predictions'][axis]) for r,x in group
                    if _truth(r,axis)!=NA and x['predictions'][axis]!=NA]
        head=dict(method=method,axis=axis,information_set=s,epsilon=eps,
                  view={'M':'attributable mechanism','H':'realized harm','E':'exposure effect'}[axis])
        if not eligible:
            out.append(dict(**head,metrics='inapplicable',reason='truth or method axis unavailable'))
            continue
        def metric(filter_fn,event_fn,success=False):
            return rate([(r['unit'],event_fn(r,x,t,p)) for r,x,t,p in eligible if filter_fn(r,x,t,p)],success=success)
        always=lambda *args:True
        answered=lambda r,x,t,p:p is not None
        legitimate=lambda r,x,t,p:r['truth']['M'] in ('legitimate-cooperation','info-bearing-legitimate')
        metrics={
          'accusation_on_legitimate':metric(legitimate,lambda r,x,t,p:p is True),
          'accusation_on_nonidentifiable':metric(lambda r,x,t,p:not r['identifiable'][axis],lambda r,x,t,p:p is True),
          'sensitivity_E_positive_harmful':metric(lambda r,x,t,p:r['truth']['M'] in ATTRIBUTABLE and r['truth']['E'] is True,lambda r,x,t,p:p is True,True),
          'FPR_benign_cooperation':metric(lambda r,x,t,p:legitimate(r,x,t,p) and t is False,lambda r,x,t,p:p is True),
          'abstention':metric(always,lambda r,x,t,p:p is None),
          'coverage':metric(always,lambda r,x,t,p:p is not None,True),
          'selective_accuracy':metric(answered,lambda r,x,t,p:p==t,True),
          'error':metric(always,lambda r,x,t,p:p is not None and p!=t),
        }
        # Fixed confidence: native methods have no confidence ranking. Bayes uses
        # its design-class posterior. Threshold ties are retained as whole blocks.
        candidates=[]
        for r,x,t,p in eligible:
            confidence = 1.
            if method=='Bayes-given-S':
                counts=r['class_counts']['attribution' if axis=='M' else axis]
                confidence=max(counts.values())/sum(counts.values())
            candidates.append((r['unit'],t,p,confidence))
        curve=[]
        thresholds=[float('inf')]+sorted({c for _,_,p,c in candidates if p is not None},reverse=True)
        for threshold in thresholds:
            predictions=[(t,p if p is not None and c>=threshold else None) for _,t,p,c in candidates]
            n=len(predictions); answered_n=sum(p is not None for _,p in predictions)
            errors=sum(p is not None and p!=t for t,p in predictions)
            abstained=n-answered_n
            curve.append(dict(threshold='reject all' if math.isinf(threshold) else threshold,
                              coverage=answered_n/n,selective_accuracy=(1-errors/answered_n) if answered_n else None,
                              risk={str(c):(errors+c*abstained)/n for c in (.25,.5)}))
        out.append(dict(**head,metrics=metrics,risk_coverage=curve,
                        truth_absent=sum(_truth(r,axis)==NA for r,_ in group)))
    return out


def symmetry(rows):
    by_pair=defaultdict(dict)
    for r in rows:
        if r['kind'] in ('P1','P2','P3','P4','P5','P6'):
            by_pair[(r['seed'],r['epsilon'],r['kind'],r['set'])][r['member']]=r
    events=defaultdict(list)
    observed=defaultdict(list)
    from .observe import canonical, SETS
    per_seed=defaultdict(dict)
    for (seed,eps,kind,s), members in by_pair.items():
        if set(members)!={'0','1'}: continue
        a,b=members['0'],members['1']
        for method in a['methods']:
            different=canonical(a['methods'][method])!=canonical(b['methods'][method])
            if a['view_sha256']==b['view_sha256']:
                events[(method,s,eps)].append((a['unit'],different))
            per_seed[(method,kind,seed,eps)][s]=different
    for (method,kind,seed,eps), sets in per_seed.items():
        observed[(method,kind,eps)].append(dict(seed=seed,first_difference=next((s for s in SETS if sets.get(s)),None)))
    return dict(violations=[dict(method=m,information_set=s,epsilon=e,rate=rate(v)) for (m,s,e),v in sorted(events.items())],
                observed_separators=[dict(method=m,kind=k,epsilon=e,units=v) for (m,k,e),v in sorted(observed.items())])


def compare_separators(sym, frontiers):
    """Observed method discrimination versus exact observable/global frontiers."""
    index={(f['seed'],f['epsilon']):f['pairs'] for f in frontiers}
    from .observe import SETS
    out=[]
    for group in sym['observed_separators']:
        for unit in group['units']:
            expected=index[(unit['seed'],group['epsilon'])][group['kind']]
            first=unit['first_difference']; exact=expected['minimal_pair_separator']
            out.append(dict(method=group['method'],kind=group['kind'],epsilon=group['epsilon'],
                seed=unit['seed'],observed_first_difference=first,
                enumerated_pair_separator=exact,enumerated_global_M=expected['minimal_global_M'],
                enumerated_global_attribution=expected['minimal_global_attribution'],
                earlier_than_observable_separator=first is not None and (exact is None or SETS.index(first)<SETS.index(exact))))
    return out
