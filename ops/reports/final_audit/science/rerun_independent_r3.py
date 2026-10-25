#!/usr/bin/env python3
"""Re-execute preserved stdlib R3 reconstruction, redirecting only root/output paths.

Does not import project modules, generate worlds, or write preserved run artifacts.
Run after other substantial local workers finish (loads the 42,000 stored rows).
"""
import ast,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
OUT=HERE/'independent_current';OUT.mkdir(exist_ok=True)
def execute(name):
    p=HERE/'historical_r3'/name; tree=ast.parse(p.read_text())
    replacements={'ROOT':ROOT,'RUN':ROOT/'docs/enh/r2/run_par','OUT':OUT,'P':OUT,'R':ROOT/'docs/enh/r2/run_par'}
    changed=[]
    for n in tree.body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in replacements:
            key=n.targets[0].id;n.value=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(value=str(replacements[key]))],keywords=[]);changed.append(key)
    assert set(changed)==({'ROOT','RUN','OUT'} if name=='audit.py' else {'P','R'}),(name,changed)
    ast.fix_missing_locations(tree)
    print('EXECUTED',name,'source sha256',hashlib.sha256(p.read_bytes()).hexdigest(),'path substitutions',changed,flush=True)
    exec(compile(tree,str(p),'exec'),{'__name__':'__main__'})
execute('audit.py');execute('compare.py')
x=json.loads((OUT/'comparison.json').read_text()); assert x['differences']==[],x
(OUT/'EXECUTION.json').write_text(json.dumps({'classification':'EXECUTED final-audit read-only independent R3 reconstruction','changed_semantics':'none; only absolute root/output Path assignments replaced via AST','differences':len(x['differences']),'source_sha256':{f:hashlib.sha256((HERE/'historical_r3'/f).read_bytes()).hexdigest() for f in ('audit.py','compare.py')}},indent=2)+'\n')
