"""Paired-world estimands, registered secondary family and sensitivities."""
from collections import defaultdict
from .statistics import summarize, sign_flip, holm, binomial_ci

CAVEATS = ('Delta compares regimes, not realized collusion; depends on the chosen B1 prompt variant; '
           'sender identity, t_star and suffix length are regime dependent.')


def world_value(cp, effect, force_zero=False):
    if not cp['eligible']:
        if force_zero or cp.get('ineligible_reason') in ('no_exposure','post_decision'): return 0.
        return None
    return effect


def paired(worlds, metric='tau_O', conditional=False, force_zero=False):
    groups = defaultdict(dict)
    for w in worlds:
        v = world_value(w,w.get(metric),force_zero)
        groups[w['world_id']][w['regime']] = (v,w['eligible'])
    result = []
    for wid, g in sorted(groups.items()):
        if 'B1' not in g or 'B2' not in g: continue
        a,b = g['B1'],g['B2']
        if a[0] is None or b[0] is None or (conditional and not (a[1] and b[1])): continue
        result.append({'world_id':wid,'B1':a[0],'B2':b[0],'d_w':a[0]-b[0]})
    return result


def study_effects(worlds, phase, m_O):
    pairs = paired(worlds)
    ds = [p['d_w'] for p in pairs]
    groups = defaultdict(dict)
    for w in worlds: groups[w['world_id']][w['regime']]=w
    attempted = sum('B1' in g and 'B2' in g for g in groups.values())
    good = sum(all(r in g and g[r]['eligible'] and min(g[r]['n_F'],g[r]['n_K'])>=3 for r in ('B1','B2')) for g in groups.values())
    floor = attempted>=8 and sum(abs(x)>1e-12 for x in ds)>=6 and good>=4
    # D-034: Tier-B case verdicts are exploratory; study inference follows the preregistered floors.
    confirmatory = floor and phase == 'holdout'
    tier = 'A-confirmatory' if confirmatory else 'feasibility'
    flip = sign_flip(ds)
    summary = summarize(ds)
    decision = ('supported' if summary['L'] is not None and summary['L'] > 0
                and flip['p'] is not None and flip['p'] <= .05 else 'not supported') if confirmatory else 'exploratory'
    labels = dict(tier=tier, label=tier)
    rows = [dict(effect='Delta_total',**summary,**labels,p_raw=flip['p'],test_status=flip['status'],
                 inference_tier=tier,confirmatory=confirmatory,caveats=CAVEATS,
                 decision=decision,matched_pairs_attempted=attempted,eligible_complete_pairs=good)]
    rows.append(dict(effect='Delta_conditional',**summarize([x['d_w'] for x in paired(worlds,conditional=True)]),confirmatory=False))
    for regime in sorted({w['regime'] for w in worlds}):
        ws = [w for w in worlds if w['regime']==regime]
        for metric in ('tau_O','tau_C','tau_W','tau_A'):
            vals = [world_value(w,w.get(metric)) for w in ws]
            row = dict(effect=metric,regime=regime,**summarize(vals),confirmatory=False)
            if sum(v is not None for v in vals)<5: row.update(L=None,U=None)
            rows.append(row)
        k = sum(w['eligible'] for w in ws); lo,hi = binomial_ci(k,len(ws))
        rows.append(dict(effect='eligibility_rate',regime=regime,estimate=k/len(ws),L=lo,U=hi,n_independent=len(ws),n_eligibility_unobserved=sum(not w.get('eligibility_observed',True) for w in ws),rate_definition='observed eligible / attempted worlds; unobserved eligibility retained in denominator',confirmatory=False))
    # Difference of paired binary eligibility: conservative exact CP rectangle,
    # Bonferroni simultaneous 95% coverage; never mislabel as a binomial difference.
    matched = [g for g in groups.values() if 'B1' in g and 'B2' in g]
    if matched:
        n=len(matched); k1=sum(g['B1']['eligible'] for g in matched); k2=sum(g['B2']['eligible'] for g in matched)
        a=binomial_ci(k1,n,alpha=.025); b=binomial_ci(k2,n,alpha=.025)
        rows.append(dict(effect='eligibility_difference',estimate=(k1-k2)/n,L=a[0]-b[1],U=a[1]-b[0],n_independent=n,confirmatory=False,interval_method='Bonferroni exact binomial rectangle'))
    svalues = [[w['tau_O'] for w in worlds if w['regime']==r and w['tau_O'] is not None] for r in ('B1','B2')]
    svalues.append([p['d_w'] for p in paired(worlds,metric='tau_C')])
    ps=[sign_flip(vals,two_sided=i>0)['p'] for i,vals in enumerate(svalues)]
    for i,(vals,p,adj) in enumerate(zip(svalues,ps,holm(ps)),1):
        rows.append(dict(effect=f'S{i}',**summarize(vals),p_raw=p,p_holm=adj,confirmatory=confirmatory,inference_tier=tier,**labels))
    return rows,pairs


def sensitivity_worlds(worlds):
    out=[]
    for name,opts in [('ineligible_zero',{'force_zero':True}),('drop_ineligible',{'conditional':True})]:
        out.append(dict(analysis=name,**summarize([p['d_w'] for p in paired(worlds,**opts)])))
    pairs=paired(worlds)
    for p in pairs:
        out.append(dict(analysis='leave_one_world_out',omitted_world=p['world_id'],**summarize([q['d_w'] for q in pairs if q!=p])))
    return out
