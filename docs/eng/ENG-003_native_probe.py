"""Offline native probe evidence; run from repo root with PYTHONPATH=."""
import json
import os
from pathlib import Path
import sys
from tests.replay.offline_runner import guard

os.environ['CCC_STARTER_ROOT'] = str(Path.cwd() / 'starter/collusion_hackathon')
sys.addaudithook(guard)
from ccc.fixtures.jira import generate_jira
from ccc.fixtures.native_replay import as_replay_fixture
from ccc.replay.fixtures import run_fixture
from ccc.replay.ledger import persist_branch, verify_branch
from ccc.replay.canonical import sha256_bytes

for case in ('A1a','A1b','A2a','A2b','A2-boundary','A3a','A3b','A4b','A5a-verbatim','A5a-paraphrase','A5b'):
    report = run_fixture(as_replay_fixture(generate_jira(case,12000,profile='golden')))
    if case == 'A5a-verbatim':
        path = persist_branch(report.audit.checkpoint, report.audit.branches['K'], Path.cwd()/'docs/eng/ENG-003_ledger_evidence')
        verification = verify_branch(path)
        summary = {'ledger_path':str(Path(path).relative_to(Path.cwd())), 'verification':verification,
                   'hash_manifest_sha256':sha256_bytes((Path(path).parent/'hashes.json').read_bytes())}
        with (Path.cwd()/'docs/eng/ENG-003_ledger_evidence_v3.json').open('x') as output:
            output.write(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'case':case,'valid':report.audit.valid,'expectations':report.expectations,
        'failed_checks':[c.to_json() for c in report.audit.cross_checks if c.status=='fail'],
        'branches':{a:{'status':b.status,'checks':[c.to_json() for c in b.checks if c.status=='fail'],
                       'flags':next(c for c in b.checks if c.id=='V07').details.get('flags',[])} for a,b in report.audit.branches.items()}}))
