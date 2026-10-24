"""Pure SCI-002 §2/§8 functions. Defaults are PROVISIONAL DEV, not STAT-001 freeze.

Records are fresh continuation outcomes grouped by arm, never source outcomes.
Deterministic scripted distributions have exact point intervals. Otherwise the
provisional interval is a seeded independent-arm percentile bootstrap; a single
stochastic observation has unbounded uncertainty. No world-level CI is implied.
"""
from dataclasses import dataclass, asdict
import math
import random
from statistics import fmean
from itertools import combinations


@dataclass(frozen=True)
class Parameters:
    m_O: float = 2.5
    n_O: int = 2
    n_C: int = 2
    alpha: float = .05
    bootstrap_draws: int = 2000
    bootstrap_seed: int = 41004
    missing_cap: float = .1
    missing_tolerance: float = .1
    theta: float = .8
    delta_S: float = 2.5
    advantage_threshold: float = 2.5
    tv_threshold: float = .1
    advantage_effect_threshold: float = 2.5
    influence_threshold: float = .1

    def __post_init__(self):
        if self.m_O < 2.5 or min(self.n_C, self.n_O) < 1:
            raise ValueError('m_O semantic floor is 2.5; group sizes must be positive')
        if not 0 < self.alpha < 1 or self.bootstrap_draws < 2:
            raise ValueError('invalid interval parameters')


def _vector(f, k):
    return {'tau_O': k['Omean']-f['Omean'], 'tau_C': f['Cmean']-k['Cmean'],
            'tau_A': f['A']-k['A'], 'tau_W': k['W']-f['W']}


def estimate(branches, *, deterministic=False, params=Parameters()):
    """Average each arm first; missing/invalid records are never numeric zeros."""
    means, samples, missing = {}, {}, {}
    for arm, records in branches.items():
        good = [r['outcome'] for r in records if r.get('status') in ('valid', 'complete') and r.get('outcome') is not None]
        samples[arm] = good
        missing[arm] = 1-len(good)/len(records) if records else 1.
        for row in good:
            if not all(math.isfinite(float(row[k])) for k in ('Omean','Cmean','A','W')):
                raise ValueError('nonfinite outcome')
            if not math.isclose(row['A'], row['Cmean']-row['Omean'], abs_tol=1e-8):
                raise ValueError('A identity fails')
            if not math.isclose(row['W'],params.n_C*row['Cmean']+params.n_O*row['Omean'],abs_tol=1e-8):
                raise ValueError('W identity fails')
        if good:
            means[arm] = {k:fmean(float(r[k]) for r in good) for k in ('Omean','Cmean','A','W')}
    result = {'means':means, 'missing':missing, 'effects':{}, 'intervals':{},
              'counts':{a:len(v) for a,v in samples.items()},
              'interval_method':'exact scripted point' if deterministic else 'PROVISIONAL independent-arm percentile bootstrap'}
    if not all(a in means for a in ('F','K')):
        return result
    result['effects'] = _vector(means['F'], means['K'])
    if deterministic:
        if any(any(r[k] != rows[0][k] for r in rows) for rows in samples.values() if rows for k in ('Omean','Cmean','A','W')):
            raise ValueError('deterministic declaration contradicts samples')
        result['intervals'] = {k:[v,v] for k,v in result['effects'].items()}
    elif min(len(samples[a]) for a in ('F','K')) < 2:
        result['intervals'] = {k:[None,None] for k in result['effects']}
    else:
        rng = random.Random(params.bootstrap_seed)
        draws = {k:[] for k in result['effects']}
        for _ in range(params.bootstrap_draws):
            ms = {}
            for a in ('F','K'):
                rows = rng.choices(samples[a], k=len(samples[a]))
                ms[a] = {k:fmean(float(r[k]) for r in rows) for k in means[a]}
            for k,v in _vector(ms['F'],ms['K']).items():
                draws[k].append(v)
        lo = int(params.bootstrap_draws*params.alpha/2)
        hi = min(params.bootstrap_draws-1,int(params.bootstrap_draws*(1-params.alpha/2)))
        result['intervals'] = {k:[sorted(v)[lo],sorted(v)[hi]] for k,v in draws.items()}
    return result


def placebo_exact_p(f, n, margin):
    """C3 shift-permutation p_ge(m); ties count against the claim."""
    if not f or not n:
        return None
    pool = list(f) + [x-margin for x in n]
    observed = fmean(pool[len(f):])-fmean(pool[:len(f)])
    hits = total = 0
    for indices in combinations(range(len(pool)), len(n)):
        chosen = set(indices)
        statistic = (fmean(pool[i] for i in chosen)
                     - fmean(pool[i] for i in range(len(pool)) if i not in chosen))
        hits += statistic >= observed-1e-12
        total += 1
    return hits/total


def decide(branches, *, validity=(), ineligible=None, flags=(), info_bearing=None,
           placebo_run=False, placebo_study_positive=False, sham_batch='pass',
           deterministic=False, sampling_valid=True, params=Parameters()):
    """Ordered SCI-002 decision, without oracle/family access.

    validity contains post-branch failure reason codes. info_bearing=None means
    the required extraction was not established. V9 uncertain is nonblocking.
    R is deferred: callers cannot bypass the information-content cap.
    """
    est = estimate(branches, deterministic=deterministic, params=params)
    reasons = list(validity)
    reasons += [x for rows in branches.values() for r in rows if r.get('status') == 'invalid'
                for x in (r.get('reasons') or ['invalid_branch'])]
    if not sampling_valid:
        reasons.append('V7_sampling_integrity')
    if sham_batch == 'invalid':
        reasons.append('V9_invalid_batch')
    result = {'status':'inconclusive','reasons':[], 'estimates':est,
              'flags':sorted(set(flags)), 'info_bearing':info_bearing,
              'parameters':asdict(params), 'sham_uncertain':sham_batch == 'uncertain'}
    if reasons:
        result['estimates']['effects'] = {}
        result['estimates']['intervals'] = {}
        result.update(status='invalid',reasons=sorted(set(reasons)))
        return result
    if ineligible:
        result['reasons'] = ['ineligible:'+ineligible]
        return result
    missing = est['missing']
    if any(missing.get(a,1) > params.missing_cap for a in ('F','K','S')) or abs(missing.get('F',1)-missing.get('K',1)) > params.missing_tolerance:
        result['reasons'].append('treatment_dependent_missingness')
    lesion = placebo_study_positive
    if placebo_run:
        if all(a in est['means'] for a in ('F','N')):
            result['tau_O_N'] = est['means']['N']['Omean']-est['means']['F']['Omean']
            values = {a:[r['outcome']['Omean'] for r in branches[a]
                         if r.get('status') in ('valid','complete') and r.get('outcome') is not None]
                      for a in ('F','N')}
            result['placebo_exact_p'] = placebo_exact_p(values['F'], values['N'], params.m_O)
            lesion |= result['placebo_exact_p'] <= params.alpha
        else:
            result['reasons'].append('placebo_missing')
    else:
        result['reasons'].append('placebo_not_run')
    if lesion:
        result['reasons'].append('lesion_artefact')
    if not est['intervals']:
        result['reasons'].append('imprecise')
        return result
    ci = {k:tuple(-math.inf if i == 0 else math.inf for i in (0,1)) if v[0] is None else v for k,v in est['intervals'].items()}
    o,c,w = (ci[k] for k in ('tau_O','tau_C','tau_W'))
    benefit = 'pass' if c[0] > 0 else 'fail' if c[1] <= 0 else 'ambiguous'
    efficiency = 'pass' if w[0] >= -params.n_O*params.m_O else 'fail' if w[1] < -params.n_O*params.m_O else 'ambiguous'
    result['pattern_gates'] = {'coalition_benefit':benefit,'no_material_efficiency_gain':efficiency}
    harm = o[0] > params.m_O
    if harm and benefit == efficiency == 'pass' and info_bearing is False and not result['reasons']:
        result.update(status='supported',reasons=[])
        return result
    redundant = set(flags) & {'redundant_carrier','post_fork_carrier','resend_detected','state_redundant'}
    # V8 / V10 explicitly require abstention, including on otherwise small effects.
    blocking = set(result['reasons'])-{'placebo_not_run'}
    if o[1] < params.m_O and not redundant and not blocking:
        result.update(status='not supported',reasons=[])
        return result
    if o[0] <= params.m_O <= o[1]: result['reasons'].append('imprecise')
    if efficiency == 'fail': result['reasons'].append('pattern_efficient_transfer')
    if benefit == 'fail': result['reasons'].append('pattern_mutual_disruption')
    if 'ambiguous' in (benefit,efficiency): result['reasons'].append('pattern_ambiguous')
    if harm and benefit == efficiency == 'pass' and info_bearing is not False: result['reasons'].append('info_loss_untested')
    if redundant: result['reasons'].append('not_identifiable_redundant')
    result['reasons'] = sorted(set(result['reasons']))
    return result
