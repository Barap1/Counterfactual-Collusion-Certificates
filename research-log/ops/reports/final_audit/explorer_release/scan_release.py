"""Read-only tracked-tree/history scan. Never reads local secret files or prints values.

This detects selected credential formats and private-reference exposure; it does
not prove the absence of all secrets. Historical findings require owner decisions.
"""
import collections
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def forbidden(path):
    p=Path(path)
    return p.name in {'.env','compute.env'} or p.name.endswith('.local.json') or p.name.startswith('.env.')

rules = {
    'openai_or_openrouter_key':re.compile(rb'\bsk-(?:or-v1-)?[A-Za-z0-9_-]{28,}\b'),
    'github_token':re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    'aws_access_key_id':re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'slack_token':re.compile(rb'\bxox[baprs]-[A-Za-z0-9-]{20,}\b'),
    'google_api_key':re.compile(rb'\bAIza[A-Za-z0-9_-]{30,}\b'),
    'huggingface_token':re.compile(rb'\bhf_[A-Za-z0-9]{25,}\b'),
    'private_key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'bearer_token':re.compile(rb'\bBearer\s+[A-Za-z0-9_.-]{30,}'),
}
doc = re.compile(rb'docs\.google\.com/(?:document|spreadsheets|presentation)/d/([A-Za-z0-9_-]{25,})')
email = re.compile(rb'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
paths = git('ls-files','-z').decode().split('\0')[:-1]
secret_paths=[p for p in paths if forbidden(p)]
doc_ids={}
hits=[]
current_docs=[]
personal=[]
archive_personal=[]
archives=[]

def scan(raw,path,phase,sha=None):
    for rule,pattern in rules.items():
        matches=list(pattern.finditer(raw))
        if matches:
            hits.append(dict(phase=phase,path=path,rule=rule,count=len(matches),lines=sorted({raw[:m.start()].count(b'\n')+1 for m in matches}),blob=sha))
    ds=list(doc.finditer(raw))
    for m in ds:
        fingerprint=hashlib.sha256(m.group(1)).hexdigest()[:16]
        doc_ids[fingerprint]=m.group(1)
        if phase=='current':
            current_docs.append(dict(path=path,line=raw[:m.start()].count(b'\n')+1,id_fingerprint=fingerprint))
    if path in {'ops/reports/PUB-001_early.md','docs/spec/12_paper_and_drive.md','CCC_MASTER_SPEC.md','docs/enh/writing/NOTES_judging_raw.md'}:
        for line in raw.splitlines():
            if not re.search(rb'(?i)doc|drive',line):continue
            for value in re.findall(rb'(?<![A-Za-z0-9_-])([A-Za-z0-9_-]{44})(?![A-Za-z0-9_-])',line):
                if not re.fullmatch(rb'[a-fA-F0-9]+',value):doc_ids[hashlib.sha256(value).hexdigest()[:16]]=value
    if phase=='current':
        emails=[m for m in email.finditer(raw) if not any(x in m.group().lower() for x in (b'example.',b'localhost',b'noreply',b'domain.com',b'email.com',b'w3.org'))]
        if emails:personal.append(dict(path=path,count=len(emails),lines=sorted({raw[:m.start()].count(b'\n')+1 for m in emails})))
    if phase=='archive':
        emails=list(email.finditer(raw))
        usernames=list(re.finditer(rb'/Users/[A-Za-z0-9_-]+',raw))
        if emails or usernames:archive_personal.append(dict(path=path,email_count=len(emails),local_username_path_count=len(usernames)))

for path in paths:
    if forbidden(path):continue
    p=ROOT/path
    if p.is_file() and p.suffix not in {'.gz','.png','.jpg','.jpeg','.pdf','.woff','.woff2','.zip'}:
        scan(p.read_bytes(),path,'current')

objects=[]
for line in git('rev-list','--objects','--all').decode().splitlines():
    parts=line.split(' ',1)
    if len(parts)==2 and not forbidden(parts[1]):objects.append(parts)
batch=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
history_docs=[]
history_bare_docs=[]
public_objects={line.split(b' ',1)[0].decode() for line in git('rev-list','--objects','origin/main').splitlines()}
history_text_bytes=0
for oid,path in objects:
    batch.stdin.write((oid+'\n').encode());batch.stdin.flush()
    header=batch.stdout.readline().decode().strip().split()
    if len(header)!=3:continue
    size=int(header[2]);raw=batch.stdout.read(size);batch.stdout.read(1)
    if header[1]!='blob' or b'\0' in raw or path.endswith(('.gz','.pdf','.png','.jpg','.jpeg','.zip')):continue
    history_text_bytes+=len(raw)
    scan(raw,path,'history',oid)
    for m in doc.finditer(raw):
        history_docs.append(dict(path=path,line=raw[:m.start()].count(b'\n')+1,id_fingerprint=hashlib.sha256(m.group(1)).hexdigest()[:16],blob=oid,reachable_from_origin_main=oid in public_objects))
    for fingerprint,value in doc_ids.items():
        if value in raw:history_bare_docs.append(dict(path=path,id_fingerprint=fingerprint,lines=[i for i,line in enumerate(raw.splitlines(),1) if value in line],blob=oid,reachable_from_origin_main=oid in public_objects))
batch.stdin.close();batch.wait()

# Bare historical IDs can survive after their URL was removed. Report paths/lines only.
bare_current=[]
for path in paths:
    if forbidden(path):continue
    p=ROOT/path
    if not p.is_file() or p.suffix in {'.gz','.pdf','.png','.jpg','.jpeg','.zip'}:continue
    raw=p.read_bytes()
    for fingerprint,value in doc_ids.items():
        if value in raw:
            bare_current.append(dict(path=path,id_fingerprint=fingerprint,lines=[i for i,line in enumerate(raw.splitlines(),1) if value in line]))

# Original raw-run archives and existing tracked release archives, streamed member by member.
for path in paths:
    if not path.endswith(('.tar.gz','.tgz')):continue
    count=0;bytes_scanned=0;before=len(hits);doc_before=len(doc_ids)
    with tarfile.open(ROOT/path,'r|gz') as tf:
        for m in tf:
            if not m.isfile() or forbidden(m.name):continue
            raw=tf.extractfile(m).read();count+=1;bytes_scanned+=len(raw)
            scan(raw,path+'::'+m.name,'archive')
    archives.append(dict(path=path,members=count,bytes=bytes_scanned,credential_findings=len(hits)-before,new_document_ids=len(doc_ids)-doc_before,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()))

metadata=git('log','--all','--format=%ae%n%ce').splitlines()
authors=len(set(e for e in metadata if b'noreply' not in e))
tracked_bytes=sum((ROOT/p).stat().st_size for p in paths if (ROOT/p).is_file())
largest=sorted([dict(path=p,bytes=(ROOT/p).stat().st_size) for p in paths if (ROOT/p).is_file()],key=lambda x:x['bytes'],reverse=True)[:15]
report=dict(scope='Tracked current files + every unique text blob on all local refs + streamed tracked raw/release tar archives. No .env, compute.env, or *.local.json contents read. Regex detection is bounded, not a security proof.',tracked_files=len(paths),tracked_bytes=tracked_bytes,history_objects=len(objects),history_text_bytes=history_text_bytes,forbidden_tracked_paths=secret_paths,credential_findings=hits,current_google_document_references=current_docs,current_bare_historical_doc_ids=bare_current,historical_google_document_reference_blobs=history_docs,distinct_document_id_fingerprints=sorted(doc_ids),current_email_paths=personal,distinct_non_noreply_commit_emails=authors,archives=archives,largest_files=largest)
report['archive_personal_data_paths']=archive_personal
report['historical_bare_document_reference_blobs']=history_bare_docs
report['origin_main_snapshot']=git('rev-parse','origin/main').decode().strip()
report['historical_forbidden_paths']=sorted(set(git('log','--all','--format=','--name-only','--','.env','**/.env','compute.env','**/compute.env','*.local.json','**/*.local.json').decode().split()))
(OUT/'release-scan.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in {'historical_google_document_reference_blobs','current_email_paths','largest_files'}},indent=2))
print('Historical Doc-reference blob occurrences:',len(history_docs),'Current email-containing files:',len(personal))
