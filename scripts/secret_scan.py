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
]
# Tokenize exact-length candidates before checking character classes. Repeated
# bounded lookaheads across large frozen JSON reports made the old rule costly.
drive_candidates = re.compile(rb'''(?<![A-Za-z0-9_-])(/d/|[\x22\x27])?([A-Za-z0-9_-]{44})(?![A-Za-z0-9_-])''')

def has_document_id(data):
    for match in drive_candidates.finditer(data):
        prefix, token = match.groups()
        if prefix == b'/d/':
            return True
        if prefix in (b'"', b"'") and all(any(test(c) for c in token) for test in
                (lambda c: 65 <= c <= 90, lambda c: 97 <= c <= 122, lambda c: 48 <= c <= 57)):
            return True
        if token.startswith(b'1') and re.search(rb'[G-Zg-z_-]', token):
            return True
    return False
# Deliberately never open credentials, even for exact-value comparisons.
# Pattern scanning is limited evidence; it does not establish privacy clearance.
release_only='--release-only' in sys.argv
changed_only='--changed-only' in sys.argv
if release_only and changed_only:
    raise SystemExit('Choose --release-only or --changed-only, not both')
extra_roots=[a for a in sys.argv[1:] if a not in ('--release-only', '--changed-only')]
selection=(['git','diff','--cached','--name-only','--diff-filter=ACM','-z'] if changed_only
           else ['git','ls-files','-z'])
tracked=subprocess.check_output(selection+['--','.',':!:docs/runner/exp002-*',':!:runs/exp002',':!:ops/budget_ledger.jsonl',':!:starter']).split(b'\0')
files=set() if release_only else {Path(os.fsdecode(n)) for n in tracked if n and not forbidden(Path(os.fsdecode(n)))}
# Scan newly prepared artifacts as well as tracked files, pruning before traversal.
for top in ([] if changed_only else ['scripts','docs/release'])+extra_roots:
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
    if has_document_id(data): rules.append('7')
    if rules:
        findings.append((label,rules))
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
for label,rules in findings:
    print(f'Flagged path={label!r}; regex rules={rules}')
# Never print matched content or credential values.
print(f'Scanned {count} working/generated/staged blobs; {len(findings)} flagged blobs; credential files never read')
raise SystemExit(1 if findings else 0)
