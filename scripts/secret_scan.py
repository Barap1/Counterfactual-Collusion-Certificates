"""Scan tracked working/staged bytes and named generated artifacts, without excerpts."""
import gzip
import os
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)

def forbidden(p):
    s=p.as_posix()
    return (s.startswith(('docs/runner/exp002', 'runs/exp002', '.git/', 'starter/')) or
            s=='ops/budget_ledger.jsonl' or p.name in ('.env','compute.env') or s.endswith('.local.json'))
patterns=[
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'\b(?:sk-or-v1-|sk-proj-)[A-Za-z0-9_-]{16,}'),
    re.compile(rb'\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}'),
    re.compile(rb'\bAKIA[0-9A-Z]{16}\b'),
    re.compile(rb'(?i)(?:api[_-]?key|access[_-]?token|secret)\s*[=:]\s*[\x22\x27]?[A-Za-z0-9_/-]{24,}'),
    re.compile(rb'https://docs\.google\.com/(?:document|spreadsheets|presentation)/d/[A-Za-z0-9_-]+'),
    # Drive IDs: /d/ tokens, mixed-case/digit quoted tokens, or known 1-prefixed format.
    re.compile(rb'''(?<![A-Za-z0-9_-])(?:/d/[A-Za-z0-9_-]{44}|[\x22\x27](?=[A-Za-z0-9_-]{0,43}[A-Z])(?=[A-Za-z0-9_-]{0,43}[a-z])(?=[A-Za-z0-9_-]{0,43}[0-9])[A-Za-z0-9_-]{44})(?![A-Za-z0-9_-])|(?<![A-Za-z0-9_-])1(?=[A-Za-z0-9_-]{0,43}[G-Zg-z_-])[A-Za-z0-9_-]{43}(?![A-Za-z0-9_-])'''),
]
secrets=[]
env=ROOT/'.env'
if env.exists():
    from dotenv import dotenv_values
    for key,value in dotenv_values(env,interpolate=False).items():
        if re.search(r'(?i)(key|token|secret|password)',key) and value:
            secrets.append(value.encode())
else:
    print('Exact-value check unavailable: local .env absent')
release_only='--release-only' in sys.argv
extra_roots=[a for a in sys.argv[1:] if a != '--release-only']
tracked=subprocess.check_output(['git','ls-files','-z','--','.',':!:docs/runner/exp002-*',':!:runs/exp002',':!:ops/budget_ledger.jsonl',':!:starter']).split(b'\0')
files=set() if release_only else {Path(os.fsdecode(n)) for n in tracked if n and not forbidden(Path(os.fsdecode(n)))}
# Scan newly prepared artifacts as well as tracked files, pruning before traversal.
for top in ['scripts','docs/release']+extra_roots:
    p=Path(top)
    if p.is_absolute():
        p=p.resolve().relative_to(ROOT)
    if '..' in p.parts or forbidden(p): raise SystemExit('Refusing excluded scan root')
    if p.is_file(): files.add(p); continue
    for current, dirs, names in os.walk(p, followlinks=False):
        dirs[:]=[d for d in dirs if not forbidden(Path(current)/d) and not (Path(current)/d).is_symlink()]
        files.update(Path(current)/n for n in names if not forbidden(Path(current)/n))
count=0; findings=[]
def scan(data,label):
    global count
    if data[:2]==b'\x1f\x8b': data=gzip.decompress(data)
    count+=1
    if count % 250 == 0: print(f"Scan progress: {count} blobs",flush=True)
    rules=[str(i+1) for i,r in enumerate(patterns) if r.search(data)]
    exact=any(v in data for v in secrets)
    if rules or exact:
        safe=label if not any(v in label.encode() for v in secrets) else '[redacted path]'
        findings.append((safe,rules,exact))
for p in sorted(files):
    if not p.is_symlink() and p.is_file(): scan(p.read_bytes(),str(p))
# Check staged blobs independently, including files whose working copies changed.
if not release_only:
    with subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE) as batch:
        for name in tracked:
            if not name: continue
            p=Path(os.fsdecode(name))
            if forbidden(p) or b'\n' in name: continue
            batch.stdin.write(b':'+name+b'\n'); batch.stdin.flush()
            header=batch.stdout.readline().split()
            if len(header)==3 and header[1]==b'blob':
                size=int(header[2]); data=batch.stdout.read(size); batch.stdout.read(1)
                scan(data,'staged:'+str(p))
        batch.stdin.close()
for label,rules,exact in findings:
    print(f'Flagged path={label!r}; regex rules={rules}; exact credential match={exact}')
# Never print matched content or credential values.
print(f'Scanned {count} working/generated/staged blobs; {len(findings)} flagged blobs; exact-value source available={env.exists()}')
raise SystemExit(1 if findings else 0)
