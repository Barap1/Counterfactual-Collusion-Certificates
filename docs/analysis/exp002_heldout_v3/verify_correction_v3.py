"""Compare every generated field/cell, preserving literal numeric tokens.

Run from repository root. No baseline output is modified. A numeric change aborts
before writing a success report. Added validity records are matched by identity,
so new rows cannot conceal changes in existing records.
"""
import csv
import hashlib
import io
import json
from pathlib import Path

OLD=Path('docs/analysis/exp002_heldout_v2')
NEW=Path('docs/analysis/exp002_heldout_v3')
EXTRAS={'CORRECTION.md','output_diff.json','verify_correction.py'}
NEW_EXTRAS={'CORRECTION.md','output_diff_v3.json','verify_correction_v3.py'}
class Number(str):
    pass

def parse(text):
    return json.loads(text,parse_int=Number,parse_float=Number)

changes=[]; numbers=0

def change(path,a,b):
    changes.append(dict(path=path,old=a,new=b))

def compare(a,b,path):
    global numbers
    if isinstance(a,Number) or isinstance(b,Number):
        assert isinstance(a,Number) and isinstance(b,Number) and str(a)==str(b), ('NUMERIC CHANGE: STOP',path,a,b)
        numbers+=1
        return
    assert type(a)==type(b), ('type changed',path,a,b)
    if isinstance(a,dict):
        assert a.keys()==b.keys(), ('keys changed',path)
        for key in a: compare(a[key],b[key],path+'/'+key)
    elif isinstance(a,list):
        if path.endswith('/reasons'):
            if a!=b: change(path,a,b)
        else:
            assert len(a)==len(b), ('length changed',path)
            for i,(x,y) in enumerate(zip(a,b)): compare(x,y,path+'/'+str(i))
    elif a!=b: change(path,a,b)

def validity(a,b,path):
    def index(rows):
        result={}
        for row in rows:
            key='|'.join(str(row.get(k,'')) for k in ('checkpoint_id','regime','check'))
            assert key not in result, ('duplicate validity row',key)
            result[key]=row
        return result
    aa,bb=index(a),index(b)
    for key in sorted(aa.keys()|bb.keys()):
        if key not in aa:
            # New records contain only categorical validity metadata.
            assert bb[key]['check'] in {'V1','V2','V3','V4','V5','V6','V7'}
            assert not any(isinstance(v,Number) for v in bb[key].values())
            change(path+'/'+key,None,bb[key])
        else:
            assert key in bb, ('removed validity record',key)
            compare(aa[key],bb[key],path+'/'+key)

files=sorted(p.relative_to(OLD) for p in OLD.rglob('*') if p.is_file() and p.name not in EXTRAS)
assert set(files)=={p.relative_to(NEW) for p in NEW.rglob('*') if p.is_file() and p.name not in NEW_EXTRAS}
file_reports=[]
for rel in files:
    a=(OLD/rel).read_text(); b=(NEW/rel).read_text(); start=len(changes)
    if rel.suffix=='.csv':
        aa=list(csv.DictReader(io.StringIO(a))); bb=list(csv.DictReader(io.StringIO(b)))
        # Compare every serialized cell, parsing nested JSON cells for numeric checks.
        def cells(rows):
            return [{k:parse(v) if v.startswith(('{','[')) else v for k,v in row.items()} for row in rows]
        aa,bb=cells(aa),cells(bb)
    elif rel.suffix=='.jsonl':
        aa=[parse(line) for line in a.splitlines()]; bb=[parse(line) for line in b.splitlines()]
    else:
        assert rel.suffix=='.json',rel
        aa,bb=parse(a),parse(b)
    if rel.stem=='validity_checks': validity(aa,bb,str(rel))
    else: compare(aa,bb,str(rel))
    file_reports.append(dict(file=str(rel),byte_identical=a==b,changed_fields=len(changes)-start))

for item in changes:
    p=item['path']
    assert (p.startswith('validity_checks.') or
            (p.startswith('checkpoint_certificates.') and (p.endswith('/all_valid') or p.endswith('/reasons'))) or
            p in {'aggregate.json/code_hashes/loaders.py','aggregate.json/code_hashes/study.py'}), ('unexpected field change', item)
old_c=json.loads((OLD/'checkpoint_certificates.json').read_text())
new_c=json.loads((NEW/'checkpoint_certificates.json').read_text())
assert [x['checkpoint_id'] for x in old_c]==[x['checkpoint_id'] for x in new_c]
status_changes=[dict(checkpoint_id=a['checkpoint_id'],old=a['status'],new=b['status'],reasons=b['reasons'])
                for a,b in zip(old_c,new_c) if a['status']!=b['status']]
assert not status_changes, status_changes  # Expected here; never silently accept a new verdict.
report=dict(files=file_reports,changes=changes,status_changes=status_changes,
            numeric_tokens_compared=numbers,numeric_tokens_byte_identical=True,
            baseline_sha256={str(rel):hashlib.sha256((OLD/rel).read_bytes()).hexdigest() for rel in files},
            statuses={x['status']:sum(y['status']==x['status'] for y in new_c) for x in new_c})
(NEW/'output_diff_v3.json').write_text(json.dumps(report,indent=2)+'\n')
print(len(files),'files;',len(changes),'changed fields;',numbers,'identical numeric tokens; status changes:',status_changes)
