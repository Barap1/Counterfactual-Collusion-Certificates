import csv,json
from pathlib import Path
out=Path('docs/analysis/exp001_dev_v2')
def load(p):
    if p.suffix=='.csv': return list(csv.DictReader(p.read_text().splitlines()))
    kw=dict(parse_int=lambda x:('NUM',x),parse_float=lambda x:('NUM',x))
    if p.suffix=='.jsonl': return [json.loads(x,**kw) for x in p.read_text().splitlines()]
    return json.loads(p.read_text(),**kw)
def diff(a,b,path=''):
    if a==b:return []
    if isinstance(a,dict):
        assert a.keys() <= b.keys(),path
        added=[(path+'/'+k, '<absent>', b[k]) for k in b.keys()-a.keys()]
        return added + sum((diff(a[k],b[k],path+'/'+k) for k in a),[])
    if isinstance(a,list):
        assert len(a)==len(b),path
        return sum((diff(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
    assert not isinstance(a,tuple),(path,a,b)
    return [(path,a,b)]
report=['# DEV analysis correction','', 'Non-confirmatory study decisions remain exploratory. All original output files were compared; every pre-existing numeric JSON token and every pre-existing non-label CSV cell is identical (except the disclosed stale-lock warning). Label strings, disclosed source provenance hashes, additive metadata fields, and the stale-lock warning marker path differ. Every pre-existing numeric field is identical; additive fields are listed explicitly below, including n_eligibility_unobserved=0. Thus the expected label-only comparison does not hold against this older archive. ["NUM", token] denotes an exact serialized JSON number. Originals and runner data were preserved.','']
for old,new,held in [(Path('docs/analysis/exp001_dev'),out,False),(Path('docs/analysis/exp002_heldout_v2'),Path('/tmp/ccc-heldout-decision-check'),True)]:
    changes=[]
    files=sorted(p.relative_to(new) for p in new.rglob('*') if p.is_file() and p.suffix in ('.json','.jsonl','.csv'))
    if not held: assert set(files)=={p.relative_to(old) for p in old.rglob('*') if p.is_file()}
    for rel in files:
        ds=diff(load(old/rel),load(new/rel),str(rel))
        for path,a,b in ds:
            assert '/code_hashes/' in path or (not held and (path.split('/')[-1] in ('label','tier','inference_tier','decision') or '/limitations/' in path or path=='aggregate.json/synthetic' or (a=='<absent>') or (path.startswith('validation_report.json/warnings/') and a.startswith('stale_lock_ignored:') and b.startswith('stale_lock_ignored:')))),(path,a,b)
        changes+=ds
        if not held: report.append(f'- `{rel}`: '+ ('identical' if not ds else ', '.join(sorted({d[0].split('/')[-1] for d in ds})))+'.')
    report+=['','## '+('Held-out comparison' if held else 'Every differing DEV field'),f'{len(files)} output files compared.']
    report+=['- `'+p+'`: '+json.dumps(a)+' → '+json.dumps(b) for p,a,b in changes]
    print('heldout' if held else 'DEV',len(files),'files;',len(changes),'differing fields')
    if held: assert len(changes)==1 and changes[0][0]=='aggregate.json/code_hashes/study.py',changes
report+=['','## Commands and validation','- `export PATH="$PWD/starter/collusion_hackathon/colosseum/.venv/bin:$PATH"` (system Python lacks NumPy).','- `python -m ccc.analysis run --input docs/runner/exp001-live --out docs/analysis/exp001_dev_v2`','- `python -m ccc.analysis run --input docs/runner/exp002-live --out /tmp/ccc-heldout-decision-check --watchdog-dir docs/runner/exp002-live.watchdog`','- `python docs/analysis/exp001_dev_v2/verify_correction.py` (all JSON, JSONL and CSV outputs compared).','- `PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest discover -s tests/analysis -t .`','- `/bin/zsh scripts/reproduce_offline.sh`','Initial unittest discovery without the offline guard failed its network-guard expectation (DNS resolution error); rerun with the guard. No experiment/model calls or commits.']
(out/'CORRECTION.md').write_text('\n'.join(report)+'\n')
