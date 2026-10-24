"""Reproduce saved finished-DEV analyses under the project's offline guard.

Run: starter/collusion_hackathon/colosseum/.venv/bin/python docs/analysis/check_end_to_end.py
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tests.replay.offline_runner import guard
sys.addaudithook(guard)
from ccc.analysis.pipeline import run


def hashes(path):
    return {str(p.relative_to(path)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob('*')) if p.is_file()}


def main():
    results={}
    for name,source,saved in [
        ('pilot3','docs/runner/exp001-pilot3','docs/analysis/pilot3'),
        ('dry-run-v2','docs/runner/dry-run-dev02-v2','docs/analysis/dry-run-v2')]:
        saved=ROOT/saved
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'analysis'
            code=run(ROOT/source,output)
            same=hashes(saved)==hashes(output)
        aggregate=json.loads((saved/'aggregate.json').read_text())
        attempts=json.loads((saved/'attempts.json').read_text())
        results[name]={
            'exit_code':code,'byte_identical_rerun':same,'label':aggregate['label'],
            'n_attempts':aggregate['n_attempts'],
            'attempt_statuses':dict(Counter(r['status'] for r in attempts)),
            'checkpoint_statuses':aggregate['statuses'],
            'scheduled_statuses':aggregate['scheduled_statuses'],
            'n_claim_candidates':aggregate['n_claim_candidates'],'output_hashes':hashes(saved)}
        assert code==0 and same, name
    (ROOT/'docs/analysis/end_to_end.json').write_text(json.dumps(results,sort_keys=True,indent=2)+'\n')
    print(json.dumps({name:{key:value for key,value in result.items() if key!='output_hashes'}
                      for name,result in results.items()},sort_keys=True,indent=2))


if __name__=='__main__':
    main()
