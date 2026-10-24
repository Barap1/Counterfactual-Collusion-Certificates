"""Exact pre/post-A4 DEV comparison and exhaustive numeric field delta ledger."""
from collections import Counter
import gzip
import json
from pathlib import Path

base=Path('docs/enh/bench'); old=base/'bench_align_snapshot'; new=base/'dev_run'
def read(path):
    data=path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix=='.gz' else data)
prior=read(old/'records.json.gz'); current=read(new/'records.json.gz')
assert len(prior)==len(current)==13800
assert {r['seed'] for r in current}==set(range(13000,13050))
for a,b in zip(prior,current):
    assert a=={**b,'methods':{m:v for m,v in b['methods'].items() if m!='CCC-L-v1'}}
counts=Counter((r['kind'],r['epsilon'],r['set']) for r in current if r['methods']['CCC-L-v1']['status']=='L3 excluded')
changes=[]
IDs=('method','reference','axis','information_set','set','kind','epsilon','seed','member','threshold')
def fields(value,path):
    if type(value) in (int,float): return {path:value}
    if isinstance(value,dict):
        return {p:v for k,x in value.items() for p,v in fields(x,path+'/'+str(k)).items()}
    if isinstance(value,list):
        keys=[json.dumps({k:x[k] for k in IDs if k in x},sort_keys=True,separators=(',',':'))
              if isinstance(x,dict) else '{}' for x in value]
        keyed=len(set(keys))==len(keys) and all(k!='{}' for k in keys)
        return {p:v for i,x in enumerate(value) for p,v in fields(x,path+'/'+(keys[i] if keyed else str(i))).items()}
    return {}
for name in ('RESULTS_dev.json','scores.json','symmetry.json','separators.json','frontiers.json','population.json','strongest_baseline.json'):
    before=fields(read(old/(name+'.gz')),'')
    after=fields(read(new/name),'')
    for key in sorted(before.keys()|after.keys()):
        if before.get(key)!=after.get(key):
            changes.append(dict(artifact=name,path=key,before=before.get(key),after=after.get(key)))
result=dict(evidence='development',records=13800,seeds='13000-13049',
    original_12_method_outputs_and_all_observations_identical=True,
    methods_before=12,methods_after=13,
    v1_exclusions=[dict(kind=k,epsilon=e,set=s,member_records=n) for (k,e,s),n in sorted(counts.items())],
    rq_before={k:v['status'] for k,v in read(old/'RESULTS_dev.json.gz')['rq'].items()},
    rq_after={k:v['status'] for k,v in read(new/'RESULTS_dev.json')['rq'].items()},
    numeric_changes=changes,numeric_changed_fields=len(changes),
    numeric_path_rule='semantic list ids when unique, positional otherwise; added/removed numbers use null; booleans excluded')
(base/'align2_numeric_delta.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('numeric_changes','v1_exclusions')},indent=2))
print('v1 excluded member/set records:',sum(counts.values()))
