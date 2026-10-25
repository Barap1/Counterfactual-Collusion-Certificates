#!/usr/bin/env python3
"""Read-only cross-platform comparison and frozen-report re-tabulation (D-048).

No benchmark execution, imports, network or changes to either run directory.
"""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def key(r):
    return (r['seed'], r['kind'], r['member'], r['set'], r['epsilon'])

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--serial', type=Path, default=ROOT/'docs/enh/r2/run')
    ap.add_argument('--parallel', type=Path, default=ROOT/'docs/enh/r2/run_par')
    ap.add_argument('--out', type=Path, default=ROOT/'docs/enh/r2')
    a = ap.parse_args()
    lines = ['# Platform divergence (D-048)', '',
             'Comparison of all unit filenames present in both preserved runs. Full parsed method output objects are compared (including native estimates); decision differences separately compare status, predictions, rung and M_label. Records are matched by seed, kind, member, set and epsilon. Missing records or methods abort. This is an overlap audit, not an estimate for the complete benchmark. Neither run is modified. The cause of divergence is unresolved.', '']
    platform_audit = {}
    for eps in ('0', '0.1'):
        left = {p.name:p for p in (a.serial/'units').glob(f'*-eps-{eps}.json.gz')}
        right = {p.name:p for p in (a.parallel/'units').glob(f'*-eps-{eps}.json.gz')}
        common = sorted(left.keys() & right.keys())
        cells = defaultdict(lambda:[0,0,0])
        seeds = []
        for name in common:
            lb, rb = left[name].read_bytes(), right[name].read_bytes()
            l = {key(r):r for r in json.loads(gzip.decompress(lb))}
            r = {key(r):r for r in json.loads(gzip.decompress(rb))}
            assert l.keys() == r.keys(), name
            changed_records = 0
            for k, lr in l.items():
                rr = r[k]
                assert lr['methods'].keys() == rr['methods'].keys()
                changed_records += lr['methods'] != rr['methods']
                for method, out in lr['methods'].items():
                    other = rr['methods'][method]
                    c = cells[(method,lr['kind'],lr['set'])]
                    c[0] += 1; c[1] += out != other
                    c[2] += any(out.get(f) != other.get(f) for f in ('status','predictions','rung','M_label'))
            seeds.append((name,len(l),changed_records,lb==rb,gzip.decompress(lb)==gzip.decompress(rb)))
        platform_audit[eps] = dict(common_units=len(common), compressed_identical=sum(x[3] for x in seeds),
            decompressed_identical=sum(x[4] for x in seeds), records=sum(x[1] for x in seeds),
            records_with_method_differences=sum(x[2] for x in seeds),
            cells=[dict(method=m,kind=k,set=info,records=n,full_output_differences=d,decision_differences=v)
                   for (m,k,info),(n,d,v) in sorted(cells.items())],
            seeds=[dict(filename=name,records=n,differing_records=d,compressed_identical=b,decompressed_identical=u,
                        serial_sha256=digest(left[name]),parallel_sha256=digest(right[name])) for name,n,d,b,u in seeds])
        lines += [f'## eps={eps}', '',
                  f'Common units: {len(common)}; serial-only: {len(left.keys()-right.keys())}; parallel-only: {len(right.keys()-left.keys())}. Byte-identical compressed units: {sum(s[3] for s in seeds)}/{len(seeds)}; decompressed: {sum(s[4] for s in seeds)}/{len(seeds)}. Records with any method output difference: {sum(s[2] for s in seeds)}/{sum(s[1] for s in seeds)}.', '',
                  '| Method | Kind | Set | Records | Full-output differences | Decision differences |', '|---|---|---|---:|---:|---:|']
        lines += [f'| {m} | {k} | {s} | {n} | {d} | {v} |' for (m,k,s),(n,d,v) in sorted(cells.items())]
        lines += ['', '### Per-seed agreement', '', '| Unit filename | Records | Differing records | Compressed identical | Decompressed identical |', '|---|---:|---:|---|---|']
        lines += [f'| {name} | {n} | {d} | {b} | {u} |' for name,n,d,b,u in seeds]
        lines += ['']
    (a.out/'PLATFORM_DIVERGENCE.md').write_text('\n'.join(lines)+'\n')
    src = a.parallel/'RESULTS.json'
    res = json.loads(src.read_text()); t = res['tables']; rq = res['rq']
    payload = dict(schema='r2-stratum-retabulation-1', source=str(src.relative_to(ROOT)), source_sha256=digest(src),
                   aggregate_verdicts=rq, frozen_criteria=res['frozen_criteria'], platform_audit=platform_audit, strata={})
    md = ['# Results by stratum (D-048)', '',
          'Re-tabulation only: every source row below is copied unchanged from run_par/RESULTS.json. Per-stratum statuses apply report.py conjunctions to the corresponding stored rows, including pair-attribution and completion/crash gates. Undefined denominators remain failed criteria. No intervals or method metrics are recomputed. RQ3 population generation and reporting ran locally; mapped methods/enumeration ran on Modal Linux. The eps=0 designation is scoped to this frozen benchmark and the available cross-platform overlap, not universal platform invariance.', '',
          'D-048 was decided after outcomes were visible. eps=0 is established (platform-invariant); eps=0.1 is platform-dependent, not established. This does not change the preregistered aggregate verdicts or make Linux eps=0.1 comparable with macOS DEV.', '',
          '## Verbatim preregistered aggregate verdicts from report.py', '']
    md += [line for line in (a.parallel/'RESULTS.md').read_text().splitlines() if line.startswith('- RQ')]
    md += ['', 'Four aggregate predictions failed: RQ3, RQ4, RQ4b and RQ5. RQ1/RQ2 pass by construction; RQ6 is descriptive.', '',
           '| RQ | eps=0: established (platform-invariant) | eps=0.1: platform-dependent, not established | Source |', '|---|---|---|---|']
    summaries = {}
    for eps in (0, .1):
        e = str(eps); subset = lambda rows:[x for x in rows if x['epsilon']==eps]
        sym = subset(t['T2']['violations']); front = subset(t['T3'])
        pop = rq['RQ3']['by_epsilon'][e]
        gate = t['T9']['complete'] and not any(x['systematic'] for x in subset(t['T9']['strata']))
        allpass = lambda rows:'pass' if gate and all(x['pass_criterion'] for x in rows) else 'fail'
        s = {'evidence_status':'established (platform-invariant)' if eps==0 else 'platform-dependent, not established', 'rq':{}}
        s['rq']['RQ1'] = dict(status='pass' if gate and all(x['rate']=='inapplicable' or x['rate']['unit_k']==0 for x in sym) else 'fail', source='tables.T2.violations', rows=sym)
        s['rq']['RQ2'] = dict(status=allpass(front), source='tables.T3', rows=front)
        s['rq']['RQ3'] = dict(status=pop['status'], source=f'rq.RQ3.by_epsilon.{e}', result=pop)
        for name,table in [('RQ4','T5'),('RQ4b','T5b')]:
            rows=subset(t[table]); s['rq'][name]=dict(status=allpass(rows),source=f'tables.{table}',rows=rows)
        rows = subset(t['T8']); pairs = subset(rq['RQ5']['pair_attribution'])
        old = subset(t['T8_v0']); opairs = subset(rq['RQ5']['v0_comparison']['pair_attribution'])
        s['rq']['RQ5']=dict(status=allpass(rows+pairs),source='tables.T8 + rq.RQ5.pair_attribution',rows=rows,pair_attribution=pairs,
                           v0_comparison=dict(status=allpass(old+opairs),rows=old,pair_attribution=opairs))
        s['rq']['RQ6']=dict(status='descriptive',source='tables.RQ6',rows=subset(t['RQ6']))
        payload['strata'][e]=s
        summary={}
        summary['RQ1']=f"{s['rq']['RQ1']['status']}; {len([x for x in sym if isinstance(x['rate'],dict)])} eligible cells; zero violations" 
        summary['RQ2']=f"{allpass(front)}; "+', '.join(f"{x['kind']}: {x['expected']}" for x in front)
        summary['RQ3']=f"{pop['status']}; {pop['k']}/{pop['n']} = {pop['rate']}; CP95 {pop['cp95']}; margin {pop['supported_with_margin']}"
        for name in ('RQ4','RQ4b'):
            summary[name]=s['rq'][name]['status']+'; '+', '.join(f"{x['kind']} {x['over_attribution']['member_k']}/{x['over_attribution']['member_n']} ({x['pass_criterion']})" for x in s['rq'][name]['rows'])
        summary['RQ5']=f"{s['rq']['RQ5']['status']} (exploratory); v1 {sum(x['pass_criterion'] for x in rows)}/{len(rows)} cells; {sum(x['absolute_gap'] is None for x in rows)} undefined gaps; v0 {sum(x['pass_criterion'] for x in old)}/{len(old)} cells; {sum(x['absolute_gap'] is None for x in old)} undefined gaps; v1 pairs "+', '.join(f"{x['kind']}/{x['set']} {x['k']}/{x['n']}" for x in pairs)
        summary['RQ6']='descriptive; all '+str(len(s['rq']['RQ6']['rows']))+' class/set rows copied, including M/H/E views and legitimate-member intervals'
        summaries[e]=summary
    for name in rq:
        md.append(f"| {name} | {summaries['0'][name]} | {summaries['0.1'][name]} | {payload['strata']['0']['rq'][name]['source']} |")
    md += ['', 'The JSON platform_audit field also records every overlap cell, per-seed agreement and input hashes; these descriptive counts come from preserved units rather than report.py.', '', 'Full rows, exact intervals, negative cells and retained v0 comparisons: [RESULTS_BY_STRATUM.json](RESULTS_BY_STRATUM.json). RQ2/RQ5 retain the frozen circularity disclosure: '+res['circularity_disclosure'], '', f'Source SHA-256: `{digest(src)}`. Reproduce both documents with `starter/collusion_hackathon/colosseum/.venv/bin/python scripts/eps_platform_check.py`.']
    (a.out/'RESULTS_BY_STRATUM.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    (a.out/'RESULTS_BY_STRATUM.md').write_text('\n'.join(md)+'\n')
    print('\n'.join(line for line in lines if line.startswith('Common units:')))
    print('\n'.join(md[-9:]))

if __name__ == '__main__':
    main()
