"""Deterministic offline analysis orchestration; all writes beneath --out."""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from . import __version__
from .loaders import load, final_attempts, metrics, COMPLETE, ValidationError, sham_selected
from .shift_perm import interval, perm_p
from .statistics import summarize, binomial_ci, t_interval, tv_excess
from .status import derive_status, SUPPORTED, NOT_SUPPORTED
from .study import study_effects, sensitivity_worlds, world_value, paired


def dump(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n')


def table(out, name, rows, scope='world_cluster', label='exploratory'):
    decorated=[dict({'tier':'B','confirmatory':False,'uncertainty_scope':scope,'label':label},**r) for r in rows]
    dump(out/(name+'.json'),decorated)
    path=out/(name+'.csv'); path.parent.mkdir(parents=True,exist_ok=True)
    fields=sorted(set().union(*(set(r) for r in decorated))) if decorated else ['tier','confirmatory','uncertainty_scope','label']
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); writer.writeheader()
        for row in decorated:
            writer.writerow({k:json.dumps(v,sort_keys=True,allow_nan=False) if isinstance(v,(dict,list,tuple)) else v for k,v in row.items()})


def _values(rows, arm, metric):
    return [r[metric] for r in rows if r['arm']==arm and not r['missing']]


def _contrast(rows,arm,metric,reverse=False):
    f,k=_values(rows,'F',metric),_values(rows,arm,metric)
    if reverse: f,k=k,f
    estimate=float(np.mean(k)-np.mean(f)) if f and k else None
    bounds=interval(f,k) if min(len(f),len(k))>=3 else None
    return estimate,bounds


def _missingness(cps, all_rows, analysis, manifest):
    result=[]
    for regime in sorted({c['regime'] for c in cps}):
        ids={c['checkpoint_id'] for c in cps if c['regime']==regime and c['eligible']}
        for arm,n in sorted(manifest['continuations_by_arm'].items()):
            scheduled=0
            for cp in cps:
                if cp['checkpoint_id'] not in ids: continue
                count=n
                if arm=='N' and not (cp.get('n_subset') or cp.get('legacy')): count=0
                if arm=='S' and manifest['phase']=='holdout': count=int(sham_selected(cp['checkpoint_id']))
                scheduled+=count
            rs=[r for r in analysis if r['checkpoint_id'] in ids and r['arm']==arm]
            attempts=[r for r in all_rows if r['checkpoint_id'] in ids and r['arm']==arm]
            counts=Counter(r['status'] for r in rs)
            complete=sum(counts[s] for s in COMPLETE)
            missing=scheduled-complete
            lo,hi=binomial_ci(missing,scheduled) if 0<=missing<=scheduled else (None,None)
            result.append(dict(regime=regime,arm=arm,backend=manifest['model'].get('backend','unknown'),
                n_scheduled=scheduled,n_complete=complete,n_missing=missing,n_unrecorded=max(0,scheduled-len(rs)),
                n_infra_missing=sum(v for k,v in counts.items() if k not in COMPLETE and k!='context_overflow'),
                n_overflow=counts['context_overflow'],n_noncommit=counts['complete_noncommit'],n_refusal=counts['complete_refusal'],
                n_retry_attempts=len(attempts)-sum(r.get('attempt_id') is not None for r in rs),status_counts=dict(sorted(counts.items())),
                attempt_status_counts=dict(sorted(Counter(r['status'] for r in attempts).items())),
                missing_share=missing/scheduled if scheduled else None,missing_L=lo,missing_U=hi))
    return result


def _validity(cps, analysis, missing, margin):
    rows=[]; gates={}
    shares={r['arm']:sum(x['n_missing'] for x in missing if x['arm']==r['arm'])/max(1,sum(x['n_scheduled'] for x in missing if x['arm']==r['arm'])) for r in missing}
    v8=any(v>.1 for v in shares.values()) or abs(shares.get('F',0)-shares.get('K',0))>.05
    for regime in sorted({c['regime'] for c in cps}):
        sham=[]; placebo=[]; byworld=defaultdict(list)
        for cp in cps:
            if cp['regime']!=regime or not cp['eligible']: continue
            rs=[r for r in analysis if r['checkpoint_id']==cp['checkpoint_id'] and not r.get('session_break')]
            f,s,n=(_values(rs,a,'Omean') for a in ('F','S','N'))
            if f and s:
                val=float(np.mean(f)-np.mean(s)); sham.append(val); byworld[cp['world_id']].append(val)
            if f and n and cp.get('placebo_kind')!='N_v1.1_deprecated': placebo.append(float(np.mean(n)-np.mean(f)))
        l90,u90=t_interval(sham,.90); l95,u95=t_interval(sham,.95)
        v9='pass' if l90 is not None and l90>=-margin and u90<=margin else 'sham_uncertain'
        if l95 is not None and (l95>margin or u95<-margin): v9='invalid_batch'
        ln,un=t_interval(placebo,.90) # 90% two-sided lower = one-sided 95% lower
        lesion=ln is not None and ln>0
        rows.extend([dict(regime=regime,check='V8',status='treatment_dependent_missingness' if v8 else 'pass'),
            dict(regime=regime,check='V9',status=v9,n_independent=len(sham),estimate=float(np.mean(sham)) if sham else None,L90=l90,U90=u90,L95=l95,U95=u95,half_width90=(u90-l90)/2 if l90 is not None else None,world_cluster=summarize([float(np.mean(v)) for v in byworld.values()])),
            dict(regime=regime,check='V10',status='lesion_artefact' if lesion else 'not_established' if len(placebo)<2 else 'pass',L=ln,U=un,n_independent=len(placebo))])
        gates[regime]=dict(V9=v9,lesion_artefact=lesion,treatment_dependent_missingness=v8)
    return rows,gates


def _sensitivities(cps, analysis, worlds):
    output=sensitivity_worlds(worlds)
    for mode in ('worst_missing','best_missing','noncommit_excluded','S_pooled_F'):
        changed=[]
        for cp,w in zip(cps,worlds):
            rs=[dict(r) for r in analysis if r['checkpoint_id']==cp['checkpoint_id']]
            if mode=='noncommit_excluded': rs=[r for r in rs if r['status'] not in ('complete_noncommit','complete_refusal')]
            elif mode=='S_pooled_F':
                for r in rs:
                    if r['arm']=='S': r['arm']='F'
            else:
                for arm in ('F','K'):
                    observed=[r['Omean'] for r in analysis if r['regime']==cp['regime'] and r['arm']==arm and not r['missing']]
                    fill=(max(observed) if (arm=='F')==(mode=='worst_missing') else min(observed)) if observed else None
                    # Reverse direction for B2 because Delta subtracts its effect.
                    if observed and cp['regime']=='B2': fill=min(observed) if (arm=='F')==(mode=='worst_missing') else max(observed)
                    for r in rs:
                        if r['arm']==arm and r['missing'] and fill is not None: r.update(Omean=fill,missing=False)
            est,_=_contrast(rs,'K','Omean')
            changed.append(dict(w,tau_O=world_value(cp,est)))
        output.append(dict(analysis=mode,**summarize([p['d_w'] for p in paired(changed)]),limitation='fills use observed same-regime arm range; no observed range leaves undefined'))
    return output


def run(input_dir, output_dir, watchdog_dir=None):
    out=Path(output_dir).resolve(); source=Path(input_dir).resolve()
    if out==source or source.is_relative_to(out) or out.is_relative_to(source):
        raise ValueError('output must not contain input artifacts')
    out.mkdir(parents=True,exist_ok=True)
    try:
        manifest,cps,attempts,events,scheduled,hashes,warnings,addendum=load(source, watchdog_dir=watchdog_dir)
    except (ValidationError,ValueError,KeyError,FileNotFoundError) as exc:
        dump(out/'validation_report.json',{'valid':False,'problems':getattr(exc,'problems',[str(exc)])})
        return 2
    label='DEV/pilot' if manifest['phase']=='development' else 'exploratory (DEV-001)'
    thresholds=addendum or {'m_O':5.,'delta_W':10.,'delta_S':5.}
    # Never advertise fallback values as a frozen addendum.
    if addendum is None: warnings.append('Stage 2 absent: DEV fallback margins; no frozen claim')
    latest={c['checkpoint_id']:max((s.get('attempt_no',0) for s in scheduled if s['checkpoint_id']==c['checkpoint_id'] and s.get('kind')=='world_attempt'),default=0) for c in cps}
    analysis=final_attempts([r for r in attempts if not latest.get(r['checkpoint_id']) or r['attempt_no']==latest[r['checkpoint_id']]])
    cpmap={c['checkpoint_id']:c for c in cps}
    sessions={c['checkpoint_id']:(len({r['load_session_id'] for r in analysis if r['checkpoint_id']==c['checkpoint_id']})>1 or any(r['status']=='session_break' for r in analysis if r['checkpoint_id']==c['checkpoint_id'])) for c in cps}
    for r in analysis:
        r.update(metrics(r)); r['regime']=cpmap[r['checkpoint_id']]['regime']; r['world_id']=cpmap[r['checkpoint_id']]['world_id']
        r['session_break']=sessions[r['checkpoint_id']]
    # Missing scheduled continuations carry no attempt_id: they are not invented attempts.
    for cp in cps:
        if not cp['eligible']: continue
        for arm,n in manifest['continuations_by_arm'].items():
            if arm=='N' and not (cp.get('n_subset') or cp.get('legacy')): n=0
            if arm=='S' and manifest['phase']=='holdout': n=int(sham_selected(cp['checkpoint_id']))
            for rep in range(n):
                if not any(r['checkpoint_id']==cp['checkpoint_id'] and r['arm']==arm and r['rep']==rep for r in analysis):
                    analysis.append(dict(checkpoint_id=cp['checkpoint_id'],world_id=cp['world_id'],regime=cp['regime'],arm=arm,rep=rep,status='unrecorded_missing',attempt_id=None,missing=True,Omean=None,Cmean=None,W=None,A=None,session_break=sessions[cp['checkpoint_id']]))
    missing=_missingness(cps,attempts,analysis,manifest)
    validity,regime_gates=_validity(cps,analysis,missing,thresholds['delta_S'])
    certificates=[]; worlds=[]; crosschecks=[]; sham_rows=[]
    for cp in cps:
        rs=[r for r in analysis if r['checkpoint_id']==cp['checkpoint_id']]
        usable=[] if sessions[cp['checkpoint_id']] else rs
        cert=dict(checkpoint_id=cp['checkpoint_id'],world_id=cp['world_id'],regime=cp['regime'],eligible=cp['eligible'],ineligible_reason=cp['ineligible_reason'],info_bearing=cp['info_bearing'],flags=cp.get('flags',{}),placebo_kind=cp.get('placebo_kind','N_m'),n_independent=1)
        cert.update(theta=thresholds.get('theta'),weak_detector=thresholds.get('weak_detector'),
                    world_attempt_status=cp.get('world_attempt_status'),eligibility_observed=cp.get('eligibility_observed',True),
                    info_bearing_source=cp.get('info_bearing_source','input contract'))
        bounds={}
        for name,arm,metric,rev in [('tau_O','K','Omean',False),('tau_C','K','Cmean',True),('tau_W','K','W',False),('tau_O_N','N','Omean',False),('tau_A','K','A',True)]:
            est,bound=_contrast(usable,arm,metric,rev)
            cert.update({name:est,name+'_L':bound[0] if bound else None,name+'_U':bound[1] if bound else None}); bounds[name]=bound
        # tau_O - tau_O^N = mean(K)-mean(N): shared F cancels exactly.
        n,k=_values(usable,'N','Omean'),_values(usable,'K','Omean')
        diff=float(np.mean(k)-np.mean(n)) if n and k else None
        bound=interval(n,k) if min(len(n),len(k))>=3 else None
        cert.update(tau_O_minus_tau_O_N=diff,tau_O_minus_tau_O_N_L=bound[0] if bound else None,tau_O_minus_tau_O_N_U=bound[1] if bound else None,
                    placebo_contrast_status='available' if diff is not None else 'unavailable:no_placebo_available' if not cp.get('mstar_available', cp.get('n_subset')) else 'unavailable:insufficient_continuations',
                    placebo_contrast_scope='deprecated descriptive only' if cp.get('legacy') else 'descriptive non-gating')
        f=_values(usable,'F','Omean'); n=_values(usable,'N','Omean')
        gates=dict(regime_gates[cp['regime']],m_O=thresholds['m_O'],delta_W=thresholds['delta_W'],session_break=sessions[cp['checkpoint_id']],
            all_valid=all(cp.get('v_checks',{}).get(f'V{i}') in ('pass','na') for i in range(1,8)) and not any(r.get('v3_pass') is False for r in rs),
            placebo_available=cp.get('placebo_kind')!='N_v1.1_deprecated' and cp.get('n_subset',False) and len(n)>=3)
        gates['lesion_artefact']=gates['lesion_artefact'] or (gates['placebo_available'] and len(f)>=3 and perm_p(f,n,thresholds['m_O'],'ge')<=.05)
        effective_cp=dict(cp,v_checks=dict(cp.get('v_checks',{})))
        if any(r.get('v3_pass') is False for r in rs): effective_cp['v_checks']['V3']='fail'
        if any(r['status']=='invalid_restore' for r in rs): effective_cp['v_checks']['V1']='fail'
        status,reasons=derive_status(effective_cp,bounds,gates)
        cert.update(status=status,reasons=reasons,gates=gates,wording=SUPPORTED if status=='supported' else NOT_SUPPORTED if status=='not_supported' else '',uncertainty_assumption='exchangeability after constant shift')
        receiver=cp.get('receiver')
        tasks=[[r.get('committed',{}).get(receiver,'skip') for r in usable if r['arm']==a and not r['missing']] for a in ('F','K')]
        cert.update(tv_excess(*tasks))
        certificates.append(cert)
        audit_status=cp.get('audit_status')
        if audit_status is not None and audit_status!=status: crosschecks.append(dict(checkpoint_id=cp['checkpoint_id'],analysis_status=status,audit_status=audit_status))
        cert['status_crosscheck']='unavailable' if audit_status is None else 'agree' if audit_status==status else 'disagree'
        for check,value in sorted(cp.get('v_checks',{}).items()): validity.append(dict(checkpoint_id=cp['checkpoint_id'],regime=cp['regime'],check=check,status=value))
        world=dict(world_id=cp['world_id'],regime=cp['regime'],eligible=cp['eligible'],ineligible_reason=cp['ineligible_reason'],n_F=len(_values(usable,'F','Omean')),n_K=len(_values(usable,'K','Omean')))
        for metric in ('tau_O','tau_C','tau_W','tau_A'): world[metric]=world_value(cp,cert[metric])
        world.update(eligibility_observed=cp.get('eligibility_observed',True),world_attempt_status=cp.get('world_attempt_status'),defined=world['tau_O'] is not None,imputed_zero=not cp['eligible'] and world['tau_O']==0)
        worlds.append(world)
        sf=_values(usable,'S','Omean')
        if f and sf: sham_rows.append(dict(checkpoint_id=cp['checkpoint_id'],world_id=cp['world_id'],regime=cp['regime'],h_S_minus_h_F=float(np.mean(f)-np.mean(sf)),n_independent=1))
    effects,pairs=study_effects(worlds,manifest['phase'],thresholds['m_O'])
    sensitivity=_sensitivities(cps,analysis,worlds)
    coverage=[]
    for regime in sorted({c['regime'] for c in cps}):
        cs=[c for c in certificates if c['regime']==regime]; counts=Counter(c['status'] for c in cs)
        coverage.append(dict(regime=regime,attempted=len(cs),**{s:counts[s] for s in ('supported','not_supported','inconclusive','invalid','ineligible')},coverage=(counts['supported']+counts['not_supported'])/len(cs),n_independent=len({c['world_id'] for c in cs})))
    end=[e for e in events if e.get('event')=='attempt_end']
    costs=[e.get('api_cost_usd') for e in end] if end else [r.get('cost_usd') for r in attempts]
    lat=[e['latency_ms'] for e in end if e.get('latency_ms') is not None]
    cost=[dict(n_calls=len(end) if events else sum(r.get('n_calls',0) for r in attempts),tokens_prompt=sum(e.get('prompt_tokens') or 0 for e in end) if end else sum(r.get('tokens_prompt') or 0 for r in attempts),tokens_completion=sum(e.get('completion_tokens') or 0 for e in end) if end else sum(r.get('tokens_completion') or 0 for r in attempts),latency_p50=float(np.percentile(lat,50)) if lat else None,latency_p95=float(np.percentile(lat,95)) if lat else None,cost_usd=sum(costs) if costs and all(x is not None for x in costs) else 'unknown',unknown_count=sum(x is None for x in costs) if costs else len(attempts),load_sessions=len({r['load_session_id'] for r in attempts}),max_requests=manifest.get('max_requests'))]
    tables={'events_accounting':events,'attempts':attempts,'scheduled_statuses':scheduled,'continuations':analysis,'checkpoint_certificates':certificates,'world_effects':worlds,'effects_study':effects,'sensitivity':sensitivity,'missingness':missing,'validity_checks':validity,'status_crosscheck':crosschecks,'coverage':coverage,'cost_throughput':cost}
    for name,rows in tables.items(): table(out,name,rows,'case_conditional' if name in ('continuations','checkpoint_certificates') else 'world_cluster',label)
    figures={'fig_delta_by_world':[dict(p,n_independent=1) for p in pairs],
             'fig_tau_vector':[r for r in effects if r['effect'] in ('tau_O','tau_C','tau_W','tau_A')],
             'fig_status_stack':coverage,'fig_sham_noise':sham_rows,'fig_missingness':[dict(r,n_independent=len({c['world_id'] for c in cps if c['regime']==r['regime']})) for r in missing]}
    for name,rows in figures.items(): table(out,'figure_data/'+name,rows,label=label)
    claims=[]
    if manifest['phase']!='development':
        delta=effects[0]
        if delta['estimate'] is not None:
            claims.append(dict(claim_id='Delta_total_exploratory',text=f"Exploratory regime contrast estimate: {delta['estimate']} reward units.",type='derived',scope='Tier B regime contrast; '+delta['caveats'],evidence={'table':'effects_study.csv','cell':'Delta_total','input_hashes':hashes},uncertainty={'L':delta['L'],'U':delta['U'],'scope':'world_cluster'},n_independent=delta['n_independent'],tier='B exploratory',reviewer=None,status='proposed'))
    (out/'claims_candidates.jsonl').write_text(''.join(json.dumps(c,sort_keys=True,allow_nan=False)+'\n' for c in claims))
    dump(out/'validation_report.json',dict(valid=True,problems=[],warnings=warnings,phase=manifest['phase'],synthetic=manifest.get('synthetic',False),label=label))
    dump(out/'aggregate.json',dict(analysis_version=__version__,phase=manifest['phase'],synthetic=manifest.get('synthetic',False),label=label,input_hashes=hashes,code_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))},thresholds=thresholds,threshold_source='stage2_addendum' if addendum else 'DEV fallback',n_attempts=len(attempts),n_checkpoints=len(cps),statuses=dict(sorted(Counter(c['status'] for c in certificates).items())),scheduled_statuses=dict(Counter(s['status'] for s in scheduled)),n_claim_candidates=len(claims),limitations=['Tier B exploratory per protocol v1.2 / DEV-001','TV interval algorithm is unspecified; interval unavailable','Runner metadata may leave validity/info_bearing unestablished; no inferred pass']))
    return 0
