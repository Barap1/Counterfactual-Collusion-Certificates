import json, hashlib, re, gzip
from pathlib import Path
root=Path.cwd(); out=root/'paper/v2/build'
r=json.loads(Path('docs/enh/r2/run_par/RESULTS.json').read_text()); b=json.loads(Path('docs/enh/r2/RESULTS_BY_STRATUM.json').read_text())
assert b['source_sha256']==hashlib.sha256(Path(b['source']).read_bytes()).hexdigest()
assert b['aggregate_verdicts']==r['rq']
checks=[]
for e in ('0','0.1'):
 s=b['strata'][e]['rq']; eps=float(e)
 for q,table in [('RQ1','T2'),('RQ2','T3'),('RQ4','T5'),('RQ4b','T5b'),('RQ5','T8'),('RQ6','RQ6')]:
  rows=r['tables'][table]['violations'] if q=='RQ1' else r['tables'][table]
  assert s[q]['rows']==[x for x in rows if x['epsilon']==eps],(e,q)
 assert s['RQ3']['result']==r['rq']['RQ3']['by_epsilon'][e]
 assert s['RQ5']['pair_attribution']==[x for x in r['rq']['RQ5']['pair_attribution'] if x['epsilon']==eps]
 assert s['RQ5']['v0_comparison']['rows']==[x for x in r['tables']['T8_v0'] if x['epsilon']==eps]
 checks.append(f'eps={e}: all RQ table rows, RQ3 exact estimates and RQ5 pairs equal frozen source')
 audit=b['platform_audit'][e]
 for row in audit['seeds']:
  name=row['filename']
  paths=[Path('docs/enh/r2')/run/'units'/name for run in ['run','run_par']]
  assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]==[row['serial_sha256'],row['parallel_sha256']]
 checks.append(f'eps={e}: every shared unit SHA-256 still matches platform audit')
# Numeric trace assertions for every revised empirical quantity in the paper/summaries.
s=b['strata']['0']['rq']
assert sum(isinstance(x['rate'],dict) for x in s['RQ1']['rows'])==182
assert all(x['rate']=='inapplicable' or (x['rate']['unit_k']==0 and x['rate']['independent_n']==200) for x in s['RQ1']['rows'])
assert s['RQ3']['result']['k']==61 and s['RQ3']['result']['n']==200
assert b['strata']['0.1']['rq']['RQ3']['result']['k']==41
assert [(x['over_attribution']['member_k'],x['over_attribution']['member_n']) for x in s['RQ4']['rows']]==[(200,200),(200,200),(0,200),(0,100)]
for version,rows,expected in [('v1',s['RQ5']['rows'],2),('v0',s['RQ5']['v0_comparison']['rows'],5)]:
 assert len(rows)==84 and sum(x['pass_criterion'] for x in rows)==expected
 assert sum(x['absolute_gap'] is None for x in rows)==73
 assert all(x['overclaim']=='inapplicable' or x['overclaim']['unit_k']==0 for x in rows)
for kind in ('P2','P3'):
 row=next(x for x in s['RQ6']['rows'] if x['kind']==kind and x['set']=='I2')
 assert row['supported_on_legitimate']['member_k']==row['supported_on_legitimate']['member_n']==200
assert [(x['k'],x['n']) for x in s['RQ5']['pair_attribution']]==[(200,200),(200,200)]
assert [(x['k'],x['n']) for x in s['RQ5']['v0_comparison']['pair_attribution']]==[(0,200),(0,200)]
checks.append('All changed headline counts checked against exact JSON source rows, including 182 cells, 61/200, 41/200, RQ4 class counts, RQ5 2/84 vs 5/84, 73 undefined each, and RQ6 200/200')
a=b['platform_audit'];assert (a['0']['common_units'],a['0']['compressed_identical'],a['0']['records'],a['0']['records_with_method_differences'])==(149,149,1458,0)
assert (a['0.1']['common_units'],a['0.1']['compressed_identical'],a['0.1']['records'],a['0.1']['records_with_method_differences'])==(148,6,1452,1160)
checks.append('Platform headline counts trace to RESULTS_BY_STRATUM.json platform_audit')
paper=Path('paper/v2/draft_v2.md').read_text(); exp=paper[paper.index('### 5.4 '):paper.index('## 6. Discussion')]
assert exp==Path('paper/v2/build/FIX-EPS-exp002-before.txt').read_text()
abstract=paper.split('## Abstract\n\n')[1].split('\n\n')[0]; wc=len(abstract.split());assert 150<=wc<=250
checks.append('EXP-002 section 5.4 byte-identical to pre-edit snapshot; abstract 207 whitespace-delimited words')
for p in Path('figures/enh/prospective').glob('fig_*.json'):
 d=json.loads(p.read_text()); assert 'platform-dependent, not established' in d['caption']
 assert 'platform-dependent, not established' in p.with_suffix('.svg').read_text()
checks.append('All seven generated SVGs and JSON captions carry D-048 labels')
for line in Path('docs/enh/r2/run_par/RESULTS.md').read_text().splitlines():
 if line.startswith('- RQ'):assert line in paper and line in Path('docs/enh/r2/RESULTS_BY_STRATUM.md').read_text()
checks.append('All seven aggregate verdict lines preserved verbatim')
trace={
 'platform archive counts':'platform_audit.{0,0.1}',
 'symmetry 182 eligible cells, 0/200, CP95 upper':'strata.0.rq.RQ1.rows[].rate',
 'frontier sets and 200/200; relay 100/100':'strata.0.rq.RQ2.rows',
 'RQ3 counts and intervals':'strata.{0,0.1}.rq.RQ3.result',
 'RQ4/RQ4b class counts, CP95, status':'strata.{0,0.1}.rq.{RQ4,RQ4b}.rows',
 'RQ5 cells, undefined gaps, overclaims, pair counts':'strata.{0,0.1}.rq.RQ5 (v0_comparison retained)',
 'CCC I2 legitimate support counts and intervals':'strata.{0,0.1}.rq.RQ6.rows',
 'four aggregate failed predictions':'aggregate_verdicts',
}
(out/'FIX-EPS-validation.json').write_text(json.dumps(dict(status='PASS source and content checks; PDF rebuild blocked',checks=checks,numeric_trace=trace,abstract_words=wc,exp002_sha256=hashlib.sha256(exp.encode()).hexdigest(),pdf_current=False,page_count_current=None),indent=2)+'\n')
print('\n'.join(checks))
