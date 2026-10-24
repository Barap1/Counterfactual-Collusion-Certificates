"""Stream the archive; never extract it or print raw trace content."""
import collections
import hashlib
import json
import tarfile
from pathlib import Path
counts=collections.Counter(); checks=collections.Counter(); mismatch=[]; total=0; apple=0
with tarfile.open('docs/runner/archives/exp002-live.tar.gz') as archive:
    for member in archive:
        if not member.isfile(): continue
        if any(x.startswith('._') for x in Path(member.name).parts):
            apple+=1; continue
        raw=archive.extractfile(member).read()
        p=Path('docs/runner')/member.name
        if not p.exists() or p.read_bytes()!=raw: mismatch.append(member.name)
        total+=1
        if member.name.endswith('/result.json') and '/branches/' in member.name:
            b=json.loads(raw); b=b.get('data',b); counts[b['status']]+=1
            for c in b.get('checks',[]): checks[c['id']+':'+c['status']]+=1
report=dict(archive_sha256=hashlib.sha256(Path('docs/runner/archives/exp002-live.tar.gz').read_bytes()).hexdigest(),
            regular_files_compared=total, apple_metadata_skipped=apple, mismatches=mismatch,
            branch_statuses=dict(counts), branch_checks=dict(checks), extraction='none; streamed in memory')
Path('docs/enh/fix/raw_verification.json').write_text(json.dumps(report,indent=2)+'\n')
assert not mismatch, mismatch
print(total,'regular files match; branches:',dict(counts))
