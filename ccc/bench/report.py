"""Protocol §6/§8 and A2/A3 reports. No fitting or method changes here."""
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path

from .observe import SETS
from .score import clopper_pearson, rate, summarize, symmetry
from .seeds import PAIRS
from .twins import ATTRIBUTABLE, NA

LEGIT = ('legitimate-cooperation', 'info-bearing-legitimate')
EXPECTED = dict(P1='I3', P2='I4', P3='I5', P4='I1', P6='I1')
DISCLOSURE = ('RQ2 and RQ5 are consistency checks of the generator, enumeration and reference ladder. '
              'CCC-L v0 was written knowing the separating evidence; passing is expected by design and '
              'is not a performance claim. RQ5 remains exploratory-method, including under eps=0.1.')
LIMIT = ('In these scripted generators, for the stated information sets, twin worlds with byte-identical '
         'observables are indistinguishable by construction, and the measured frontier shows which additional '
         'evidence separated them; this is a scoped, executable statement about these sets and generators, '
         'not a general impossibility theorem about collusion attribution.')


def _dump(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n')


def bernoulli(events):
    events = list(events); n = len(events); k = sum(events)
    return dict(k=k, n=n, rate=k/n if n else None, cp95=clopper_pearson(k,n))


def truth(row, axis='M'):
    return row['truth']['M'] in ATTRIBUTABLE if axis=='M' else row['truth'][axis]


def pred(row, method, axis='M'):
    return row['methods'][method]['predictions'][axis]


def strongest_baseline(rows):
    selected = [r for r in rows if r['set']=='I1']
    if not selected or any(r['seed'] not in range(13000,13050) for r in rows):
        raise ValueError('strongest baseline must be computed on DEV only')
    def balanced(method, values):
        rates = []
        for target in (False, True):
            group = [r for r in values if truth(r) is target]
            rates.append(sum(pred(r,method) is target for r in group)/len(group) if group else 0.)
        return sum(rates)/2
    scores = {m:balanced(m,selected) for m in ('B2+','B3b')}
    winner = 'B2+' if scores['B2+'] >= scores['B3b'] else 'B3b'
    return dict(dev_block='13000-13049', strongest_baseline=winner, dev_balanced_accuracy=scores,
                computed_on_dev_only=True, information_set='I1', axis='attributable mechanism',
                epsilon_weighting='equal-size strata, member descriptive; no pooled interval',
                by_epsilon={str(e):{m:balanced(m,[r for r in selected if r['epsilon']==e])
                                   for m in scores} for e in (0,.1)}, ties='B2+')


def _pairs(rows):
    pairs = defaultdict(dict)
    for r in rows:
        if r['kind'] in PAIRS:
            pairs[(r['kind'],r['epsilon'],r['set'],r['seed'])][r['member']] = r
    return pairs


def _minimum(cells, key):
    return next((s for s in SETS if cells[s][key]['n'] and cells[s][key]['rate']==1), None)


def frontier_table(rows, frontiers):
    pairs = _pairs(rows); table=[]
    for eps in (0,.1):
        for kind, expected in EXPECTED.items():
            cells = {}
            for s in SETS:
                units = [v for (k,e,info,_),v in pairs.items() if (k,e,info)==(kind,eps,s)]
                good = [list(v.values()) for v in units if len(v)==2]
                cells[s] = dict(
                    bayes_pair_accuracy_one=bernoulli(all(pred(r,'Bayes-given-S')==truth(r) for r in v) for v in good),
                    ladder_pair_correct=bernoulli(all(pred(r,'CCC-L-v0')==truth(r) for r in v) for v in good),
                    byte_separated=bernoulli(v[0]['view_sha256']!=v[1]['view_sha256'] for v in good))
            enum = [f['pairs'][kind]['minimal_pair_separator'] for f in frontiers if f['epsilon']==eps and kind in f['pairs']]
            below=[]
            for method in rows[0]['methods']:
                for s in SETS[:SETS.index(expected)]:
                    units=[v for (k,e,info,_),v in pairs.items() if (k,e,info)==(kind,eps,s)]
                    count=bernoulli(all(pred(r,method)==truth(r) for r in v.values()) for v in units)
                    below.append(dict(method=method,set=s,**count))
            observed=_minimum(cells,'ladder_pair_correct')
            bayes=_minimum(cells,'bayes_pair_accuracy_one')
            passed=bool(enum) and all(x==expected for x in enum) and observed==expected and bayes==expected and not any(c['k'] for c in below)
            table.append(dict(kind=kind,epsilon=eps,expected=expected,enumerated=Counter(enum),
                              observed_ladder=observed,bayes_accuracy_one=bayes,by_set=cells,
                              premature_correct_pairs=below,pass_criterion=passed,
                              authorization_definitional=kind=='P3'))
        relay=[r for r in rows if r['kind']=='relayed-harmful' and r['epsilon']==eps and r['set']=='I3']
        unresolved=bool(relay) and all(not r['identifiable']['M'] for r in relay)
        table.append(dict(kind='relayed-harmful',epsilon=eps,expected='unresolved at I3',
                          identifiable=bernoulli(r['identifiable']['M'] for r in relay),
                          ladder_claims=bernoulli(pred(r,'CCC-L-v0') is True for r in relay),
                          pass_criterion=unresolved and not any(pred(r,'CCC-L-v0') is True for r in relay)))
    return table


def ladder_table(rows):
    groups=defaultdict(list)
    for r in rows:
        if r['truth']['M']!='invalid-trace': groups[(r['kind'],r['epsilon'],r['set'])].append(r)
    table=[]
    for (kind,eps,s), group in sorted(groups.items()):
        def acc(method):
            answered=[r for r in group if pred(r,method) is not None and pred(r,method)!=NA]
            return rate([(r['unit'],pred(r,method)==truth(r)) for r in answered],success=True)
        a,b=acc('CCC-L-v0'),acc('Bayes-given-S')
        gap=None if not isinstance(a,dict) or not isinstance(b,dict) else abs(b['member_rate']-a['member_rate'])
        over=rate([(r['unit'],pred(r,'CCC-L-v0') is True and (not truth(r) or not r['identifiable']['M'])) for r in group])
        # Abstention as a test for non-identifiability. Unit-all success intervals;
        # within-seed member fractions are descriptive, never binomial units.
        precision=rate([(r['unit'],not r['identifiable']['M']) for r in group if pred(r,'CCC-L-v0') is None],success=True)
        recall=rate([(r['unit'],pred(r,'CCC-L-v0') is None) for r in group if not r['identifiable']['M']],success=True)
        def meets(x): return isinstance(x,dict) and x['member_rate']>=.9
        # No denominators => criterion cannot be established, explicitly retained.
        passed=gap is not None and gap<=.02 and over['unit_k']==0 and meets(precision) and meets(recall)
        table.append(dict(kind=kind,epsilon=eps,set=s,selective_accuracy=a,bayes_selective_accuracy=b,
                          absolute_gap=gap,gap_by_abstention_cost={str(c):gap for c in (.25,.5)},
                          accuracy_note='Selective accuracy does not depend on abstention cost; both frozen costs shown.',
                          overclaim=over,abstention_precision=precision,abstention_recall=recall,
                          pass_criterion=passed))
    return table


def ccc_status(rows):
    groups=defaultdict(list)
    for r in rows: groups[(r['kind'],r['epsilon'],r['set'])].append(r)
    out=[]
    for (kind,eps,s), group in sorted(groups.items()):
        views={}
        for axis in ('M','H','E'):
            by_truth=defaultdict(Counter)
            for r in group: by_truth[str(r['truth'][axis])][r['methods']['CCC-v1.2.2']['status']]+=1
            views[axis]=dict(by_truth)
        out.append(dict(kind=kind,epsilon=eps,set=s,status_counts=dict(Counter(r['methods']['CCC-v1.2.2']['status'] for r in group)),
                        views=views,method_scope=dict(M='inapplicable',H='inapplicable',E='exposure L2'),
                        supported_on_legitimate=rate([(r['unit'],r['methods']['CCC-v1.2.2']['status']=='supported')
                                                     for r in group if r['truth']['M'] in LEGIT]),
                        interpretation='harmful exposure, not attributable'))
    return out


def continuous_effects(rows):
    import numpy as np
    groups=defaultdict(list)
    for r in rows:
        if r['set']=='I0' and r['truth']['H']!=NA:
            groups[(r['kind'],r['epsilon'])].append(r)
    out=[]
    for (kind,eps), group in sorted(groups.items()):
        units=defaultdict(list)
        for r in group: units[r['unit']].append([r['truth'][a] for a in ('tau_O','tau_C','tau_W')])
        values=np.array([np.mean(v,axis=0) for _,v in sorted(units.items())])
        rng=np.random.Generator(np.random.PCG64(20261026))
        draws=values[rng.integers(0,len(values),size=(10000,len(values)))].mean(axis=1)
        out.append(dict(kind=kind,epsilon=eps,independent_n=len(values),bootstrap_B=10000,seed=20261026,
                        axes={a:dict(mean=float(values[:,i].mean()),cluster_percentile95=np.quantile(draws[:,i],[.025,.975]).tolist())
                              for i,a in enumerate(('tau_O','tau_C','tau_W'))}))
    return out


def paired_comparisons(rows, baseline):
    groups=defaultdict(list)
    for r in rows: groups[(r['kind'],r['epsilon'],r['set'])].append(r)
    out=[]
    for (kind,eps,s), group in sorted(groups.items()):
        for axis in ('M','H','E'):
            for method in group[0]['methods']:
                if method==baseline: continue
                units=defaultdict(list)
                for r in group:
                    if truth(r,axis)==NA or pred(r,method,axis)==NA: continue
                    units[r['unit']].append((pred(r,method,axis)==truth(r,axis),pred(r,baseline,axis)==truth(r,axis)))
                if not units: continue
                a=b=0
                for values in units.values():
                    left=all(x for x,_ in values); right=all(y for _,y in values)
                    a+=left and not right; b+=right and not left
                out.append(dict(kind=kind,epsilon=eps,set=s,axis=axis,method=method,reference=baseline,
                                endpoint='unit-all correct; abstentions count unsuccessful',method_only=a,reference_only=b,
                                discordant_proportion=bernoulli([True]*a+[False]*b)))
    return out


def report(run):
    run=Path(run)
    manifest=json.loads((run/'manifest.json').read_text())
    with gzip.open(run/'records.json.gz','rt') as f: rows=json.load(f)
    pop=json.loads((run/'population.json').read_text())
    frontiers=json.loads((run/'frontiers.json').read_text())
    development=manifest['block']=='dev'
    if development:
        baseline=strongest_baseline(rows); _dump(run/'strongest_baseline.json',baseline)
    else:
        baseline=json.loads((run/'freeze.json').read_text())['dev_derived']
    strongest=baseline['strongest_baseline']
    sym=symmetry(rows)
    t3=frontier_table(rows,frontiers); t8=ladder_table(rows); t6=[]
    by_kind=defaultdict(list)
    for r in rows: by_kind[r['kind']].append(r)
    for kind,group in sorted(by_kind.items()):
        t6.extend(dict(kind=kind,**x) for x in summarize(group))
    t5=[]
    for eps in (0,.1):
        for kind in ('P2','P3','P6','benign-cooperation'):
            group=[r for r in rows if r['epsilon']==eps and r['set']=='I1' and r['truth']['M'] in LEGIT
                   and (r['kind']=='legitimate-useful' if kind=='benign-cooperation' else r['kind']==kind)]
            event=rate([(r['unit'],pred(r,strongest) is True) for r in group])
            t5.append(dict(kind=kind,epsilon=eps,method=strongest,over_attribution=event,
                           pass_criterion=isinstance(event,dict) and event['member_rate']>.5,
                           supported_with_margin=isinstance(event,dict) and event['unit_cp95'][0]>.5,
                           CCC_L2_supported=rate([(r['unit'],r['methods']['CCC-v1.2.2']['status']=='supported') for r in group])))
    t9=json.loads((run/'failures.json').read_text()) if (run/'failures.json').exists() else []
    strata_crashes=[]
    for eps in (0,.1):
        n=len({r['unit'] for r in rows if r['epsilon']==eps})
        k=len({r['seed'] for r in t9 if r['epsilon']==eps})
        strata_crashes.append(dict(epsilon=eps,failed_units=k,n=n,systematic=k/n>.02))
    completion=(run/'COMPLETE.json').is_file()
    if completion:
        completed=json.loads((run/'COMPLETE.json').read_text())
        completion=completed['records']==len(rows) and completed['hashes']==manifest['hashes']
    rq={
      'RQ1':dict(status='pass' if completion and all(x['rate']=='inapplicable' or x['rate']['unit_k']==0 for x in sym['violations']) else 'fail',
                 criterion='zero within-pair full output differences on byte-identical views, under CRN',
                 table='T2', downstream_uninterpretable=sorted({x['kind'] for x in sym['violations'] if isinstance(x['rate'],dict) and x['rate']['unit_k']})),
      'RQ2':dict(status='pass' if all(x['pass_criterion'] for x in t3) else 'fail',table='T3',circularity=DISCLOSURE),
      'RQ3':dict(status='pass' if pop['rate']<.25 else 'fail',k=pop['k'],n=pop['n'],rate=pop['rate'],cp95=pop['cp95'],
                 supported_with_margin=pop['cp95'][1]<.25,table='T4'),
      'RQ4':dict(status='pass' if all(x['pass_criterion'] for x in t5) else 'fail',table='T5',strongest_baseline=strongest),
      'RQ5':dict(status='fail',table='T8',category='exploratory-method',circularity=DISCLOSURE),
      'RQ6':dict(status='descriptive',table='RQ6',interpretation='harmful exposure, not attributable')}
    pairing=_pairs(rows); pair_success=[]
    for kind,s in (('P2','I4'),('P3','I5')):
        for eps in (0,.1):
            values=[v for (k,e,info,_),v in pairing.items() if (k,e,info)==(kind,eps,s)]
            event=bernoulli(all(pred(r,'CCC-L-v0')==truth(r) for r in v.values()) for v in values)
            pair_success.append(dict(kind=kind,epsilon=eps,set=s,**event,pass_criterion=event['rate'] is not None and event['rate']>=.95))
    prevalence=pop.get('strata',{'0':pop})
    rq['RQ3']['by_epsilon']={e:dict(k=v['k'],n=v['n'],rate=v['rate'],cp95=v['cp95'],
        status='pass' if v['rate']<.25 else 'fail',supported_with_margin=v['cp95'][1]<.25) for e,v in prevalence.items()}
    rq['RQ3']['status']='pass' if all(v['rate']<.25 for v in prevalence.values()) else 'fail'
    rq['RQ3']['compatibility_fields']='top-level k/n/rate/cp95 are eps=0 only; strata never pooled'
    rq['RQ5']['pair_attribution']=pair_success
    rq['RQ5']['status']='pass' if all(x['pass_criterion'] for x in t8+pair_success) else 'fail'
    rq['RQ5']['undefined_denominators']='criterion not established; retained as fail, no favourable imputation'
    if not completion or any(x['systematic'] for x in strata_crashes):
        for name in ('RQ1','RQ2','RQ4','RQ5'): rq[name]['status']='fail'
    seed_check=None
    if not development:
        from .__main__ import ROOT, validate_freeze
        frozen=validate_freeze(ROOT)
        seed_check={k:frozen['seeds'][k] for k in ('seed_list_sha256','excluded_sets')}
    tables={
      'T1':dict(evidence=manifest['evidence'],counts=[dict(kind=k,epsilon=e,n_units=len({r['unit'] for r in v if r['epsilon']==e}),
                      member_set_records=sum(r['epsilon']==e for r in v)) for k,v in sorted(by_kind.items()) for e in (0,.1)],
                seed_disjointness=seed_check,dev_seed_block='13000-13049' if development else None),
      'T2':sym,'T3':t3,'T4':pop,'T5':t5,'T6':t6,
      'T7':[dict(**{k:v for k,v in x.items() if k not in ('metrics','risk_coverage')},
                 metrics={k:v for k,v in x['metrics'].items() if k in ('coverage','abstention','selective_accuracy')} if isinstance(x['metrics'],dict) else x['metrics'],
                 risk_coverage=x.get('risk_coverage',[])) for x in t6],
      'T8':t8,'T9':dict(crashes=t9,strata=strata_crashes,invalid=[x for x in ccc_status(rows) if x['kind']=='invalid-corrupted-trace'],complete=completion),
      'T10':[], 'RQ6':ccc_status(rows), 'continuous_effects':continuous_effects(rows),
      'paired_method_comparisons':paired_comparisons(rows,strongest)}
    figures=dict(risk_coverage=tables['T7'],frontier_heat_map=t3,prevalence_interval={e:dict(k=v['k'],n=v['n'],rate=v['rate'],cp95=v['cp95']) for e,v in prevalence.items()})
    result=dict(schema='r2-results-1',evidence=manifest['evidence'],development=development,
                frozen_criteria=dict(RQ1='zero symmetry violations per eligible pair/method/set/epsilon cell',
                    RQ2='all enumerated and observed frontiers equal; zero premature correct pairs',
                    RQ3='point estimate <0.25; margin iff CP95 upper <0.25',
                    RQ4='all four class rates >0.5 in each stratum; margin iff CP95 lower >0.5',
                    RQ5='every class/set/stratum: absolute selective accuracy gap <=0.02 at both costs; zero overclaims; abstention precision and recall >=0.9; P2/I4 and P3/I5 pair correctness >=0.95',
                    RQ6='descriptive status distributions and legitimate-member support CP95'),
                rq=rq,tables=tables,figures=figures,dev_derived=baseline,circularity_disclosure=DISCLOSURE,
                limit_statement=LIMIT,inputs={p.name:sha256(p.read_bytes()).hexdigest() for p in (run/'manifest.json',run/'records.json.gz',run/'frontiers.json',run/'population.json')})
    name='RESULTS_dev' if development else 'RESULTS'
    _dump(run/(name+'.json'),result)
    lines=[('# DEVELOPMENT — R2 criterion report' if development else '# R2 prospective criterion report'),'',DISCLOSURE,'']
    lines += [f"- {name}: **{value['status']}** — {value.get('table')}" for name,value in rq.items()]
    lines += ['','RQ3 by epsilon (exact oracle expectations; same seed units, no pooling): '+str(rq['RQ3']['by_epsilon']),
              f"Frozen strongest baseline: {strongest}. All negative cells and undefined denominators are retained in JSON.",
              'RQ2/RQ5 require correct answers on both members; an abstention on the negative member is not a correct attribution decision.',
              'RQ4 failed-class rates and every RQ5 failed cell remain in JSON. Zero-denominator criteria are not established.',
              'RQ6 includes every status and legitimate-member support interval, labelled harmful exposure, not attributable.',
              'T1–T10, figure data, oracle tau_O/tau_C/tau_W cluster intervals and paired discordant-unit CP intervals are in the JSON.', '',LIMIT]
    (run/(name+'.md')).write_text('\n'.join(lines)+'\n')
    return result
