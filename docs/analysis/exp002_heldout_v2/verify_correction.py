import csv, json, re
from pathlib import Path
old=Path('docs/analysis/exp002_heldout')
new=Path('docs/analysis/exp002_heldout_v2')
allowed={'label','tier','confirmatory','inference_tier','decision','claim_id','text','scope','limitations'}
changes=[]
numeric_count=0
def compare(a,b,path):
    global numeric_count
    if type(a) in (int,float):
        assert type(a)==type(b) and repr(a)==repr(b), (path,a,b)
        numeric_count+=1
    if a==b: return
    if isinstance(a,dict):
        assert a.keys()==b.keys(),path
        for k in a: compare(a[k],b[k],path+'/'+k)
    elif isinstance(a,list):
        assert len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)): compare(x,y,path+'/'+str(i))
    else:
        assert path.split('/')[-1] in allowed or '/limitations/' in path or '/code_hashes/' in path,(path,a,b)
        changes.append((path,a,b))
files=sorted(p.relative_to(old) for p in old.rglob('*') if p.is_file())
assert set(files)=={p.relative_to(new) for p in new.rglob('*') if p.is_file()} - {Path(x) for x in ('CORRECTION.md','output_diff.json','verify_correction.py')}
lines=[]
for rel in files:
    a=(old/rel).read_text(); b=(new/rel).read_text(); start=len(changes)
    if rel.suffix=='.csv':
        aa=list(csv.DictReader(a.splitlines()));bb=list(csv.DictReader(b.splitlines()))
        # Compare original serialized numeric tokens (including nested JSON cells).
        for ra,rb in zip(aa,bb):
            for k in ra:
                if k not in allowed:
                    assert ra[k]==rb[k],(rel,k)
        compare(aa,bb,str(rel))
    else:
        if rel.suffix=='.jsonl':
            aa=[json.loads(x,parse_int=lambda x:('NUM',x),parse_float=lambda x:('NUM',x)) for x in a.splitlines()];bb=[json.loads(x,parse_int=lambda x:('NUM',x),parse_float=lambda x:('NUM',x)) for x in b.splitlines()]
        else:
            aa=json.loads(a,parse_int=lambda x:('NUM',x),parse_float=lambda x:('NUM',x))
            bb=json.loads(b,parse_int=lambda x:('NUM',x),parse_float=lambda x:('NUM',x))
        compare(aa,bb,str(rel))
    fields=sorted({x[0].split('/')[-1] for x in changes[start:]})
    lines.append(f"- `{rel}`: "+(', '.join(fields) if a!=b else 'byte-identical')+'.')
(new/'output_diff.json').write_text(json.dumps(changes,indent=2)+'\n')
report="""# Disclosed label correction (D-034 / REV-001 F-1)

The original docs/analysis/exp002_heldout and all collection artifacts were preserved.
No estimator, numeric value, threshold, statistical test, seed, ordering, or data selection changed.
Delta_total and S1–S3 are confirmatory when the preregistered floors pass in holdout, with tier A-confirmatory.
Delta_total is supported only when bootstrap L > 0 AND exact one-sided sign-flip p <= 0.05; otherwise not supported.
The held-out result is not supported. Delta_conditional remains descriptive; Tier-B case certificates remain exploratory.
General table labels now describe this distinction without attributing study exploratory status to DEV-001.
The existing claim candidate's identifier, text, scope and tier, and aggregate limitation wording reflect the corrected labels/decision.

Every original output file was compared below. Every numeric field is byte-identical in its serialized representation
(JSON numeric tokens compared as literal strings; CSV numeric cells compared verbatim, including nested cells).
No original output file was omitted. Detailed old/new field values: output_diff.json.
The sole non-label/decision differences are the mandatory aggregate.json code_hashes for study.py and pipeline.py.
These truthfully identify the edited source; therefore the literal request that *only* label/decision fields differ
cannot hold for source provenance hashes. No hashes were falsified or copied from the old analysis.

## Per-file comparison
"""+'\n'.join(lines)+"""

## Commands and validation
- `starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.analysis run --input docs/runner/exp002-live --watchdog-dir docs/runner/exp002-live.watchdog --out docs/analysis/exp002_heldout_v2` (exit 0).
- `PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest discover -s tests/analysis -t .`
- Comparison: `starter/collusion_hackathon/colosseum/.venv/bin/python docs/analysis/exp002_heldout_v2/verify_correction.py` (all assertions passed).
- Initial unguarded unittest discovery exposed an obsolete exploratory-label assertion and the suite's required network-guard expectation; the label assertion was corrected and the suite rerun with its offline guard.
Guarded suite result: 57 tests run, OK (1 guard-required skip of the real manifest contract test).
No live/model calls or commits. Owner remains sole author.
"""
(new/'CORRECTION.md').write_text(report)
print(len(files),'files compared;',len(changes),'changed fields; numeric serialization unchanged')
