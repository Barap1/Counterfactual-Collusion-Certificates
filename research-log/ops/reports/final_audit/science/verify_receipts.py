#!/usr/bin/env python3
"""Read-only stdlib audit of preserved receipts; never executes benchmark code."""
import collections, gzip, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PAR=ROOT/'docs/enh/r2/run_par'; SER=ROOT/'docs/enh/r2/run'
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def comp(a,b):
    aa,bb=a.read_bytes(),b.read_bytes()
    return {'compressed_identical':aa==bb,'decompressed_identical':gzip.decompress(aa)==gzip.decompress(bb)}
report={'verification':'EXECUTED; read-only, stdlib-only; no benchmark execution'}
freeze=load(ROOT/'docs/enh/r2/FREEZE.json'); complete=load(PAR/'COMPLETE.json')
report['frozen_sources']={p:{'expected':h,'actual':sha(ROOT/p),'equal':sha(ROOT/p)==h} for p,h in complete['hashes'].items()}
assert all(v['equal'] for v in report['frozen_sources'].values())
report['protocol']={'expected':freeze['protocol']['sha256'],'actual':sha(ROOT/freeze['protocol']['path'])}
assert report['protocol']['expected']==report['protocol']['actual']
report['freeze']={'actual':sha(ROOT/'docs/enh/r2/FREEZE.json'),'receipt':load(PAR/'manifest.json')['prospective_freeze_sha256']}
assert report['freeze']['actual']==report['freeze']['receipt']
for name,path in [('historical_gate',ROOT/'ops/reports/codex_runs/gate1_failed/run_par_prev/GATE.json'),('current_gate',PAR/'GATE.json')]:
    g=load(path);report[name]={'path':str(path.relative_to(ROOT)),'sha256':sha(path),'status':g['status'],'infrastructure_error':g.get('infrastructure_error'),'compared':g['compared'],'mismatch_count':len(g['mismatches']),'missing_count':sum(x.endswith(': missing') for x in g['mismatches']),'independent_seeds':len(g['seeds'])}
g=load(PAR/'GATE.json');rows=[]
for eps in ('0','0.1'):
    for folder in ('units','partitions'):
        details=[]
        for s in g['seeds']:
            rel=Path(folder)/f'{s}-eps-{eps}.json.gz'
            details.append({'path':str(rel),**comp(SER/rel,PAR/rel)})
        rows.append({'epsilon':eps,'kind':folder,'files':len(details),'compressed_identical':sum(x['compressed_identical'] for x in details),'decompressed_identical':sum(x['decompressed_identical'] for x in details),'comparisons':details})
report['post_run_gate40']=rows
v2=load(PAR/'GATE_v2.json');selfrows=[]
for folder in ('units','partitions'):
    for eps in ('0','0.1'):
        aa=PAR/'gate_v2/A'/folder;bb=PAR/'gate_v2/B'/folder
        ps=sorted(aa.glob(f'*-eps-{eps}.json.gz'))
        selfrows.append({'kind':folder,'epsilon':eps,'files':len(ps),'A_B_identical':sum(comp(p,bb/p.name)['compressed_identical'] for p in ps),'A_final_identical':sum(comp(p,PAR/folder/p.name)['compressed_identical'] for p in ps),'A_serial_identical':sum(comp(p,SER/folder/p.name)['compressed_identical'] for p in ps)})
report['gate_v2']={'independent_seeds':len(v2['seeds']),'recorded_platform':v2['platform'],'recorded_self_check':v2['self_check'],'recorded_eps0':v2['cross_platform_eps0'],'actual':selfrows}
runtime=collections.Counter();bad=[];checksum_count=0;identical=0
receipts=sorted((PAR/'execution/modal/methods').glob('*.json'))
for p in receipts:
    r=load(p);runtime[r['runtime']['python']]+=1
    assert not r['failures'],p
    identical+=r['task']['identity']==v2['identity']
    for rel,h in r['sha256'].items():
        checksum_count+=1
        if sha(PAR/rel)!=h:bad.append(rel)
report['method_receipts']={'count':len(receipts),'runtime_python_counts':dict(runtime),'identity_equal_to_gate_v2':identical,'artifact_checksum_count':checksum_count,'artifact_checksum_failures':bad}
assert not bad and identical==len(receipts)==2100
res=load(PAR/'RESULTS.json');report['aggregate_verdicts']={k:v['status'] for k,v in res['rq'].items()}
assert report['aggregate_verdicts']=={'RQ1':'pass','RQ2':'pass','RQ3':'fail','RQ4':'fail','RQ4b':'fail','RQ5':'fail','RQ6':'descriptive'}
report['RQ3']=res['rq']['RQ3'];assert res['rq']['RQ3']['by_epsilon']['0']['cp95'][0]<.25<res['rq']['RQ3']['by_epsilon']['0']['cp95'][1]
report['source_hashes']={str(p.relative_to(ROOT)):sha(p) for p in [PAR/'RESULTS.json',PAR/'RESULTS.md',PAR/'GATE.json',PAR/'GATE_v2.json',ROOT/'scripts/eps_platform_check.py']}
(OUT/'receipt_verification.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in {'frozen_sources','post_run_gate40','RQ3'}},indent=2))
