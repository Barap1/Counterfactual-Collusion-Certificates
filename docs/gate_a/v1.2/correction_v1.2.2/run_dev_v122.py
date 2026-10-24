# Run from repo root: PYTHONPATH=. python -I docs/gate_a/v1.2/correction_v1.2.2/run_dev_v122.py
import sys, os; sys.path.insert(0, os.getcwd())
import os, sys, json, gzip
from pathlib import Path
from tests.replay.offline_runner import guard
ROOT = Path.cwd(); OUT = ROOT/'docs/gate_a/v1.2/correction_v1.2.2'
os.environ['CCC_STARTER_ROOT'] = str(ROOT/'starter/collusion_hackathon')
sys.addaudithook(guard)
from ccc.audit.gate_a import main, resolve_parameters
(OUT/'placebo_manifests.jsonl').write_text('')
main(OUT, params=resolve_parameters(theta=0.4, bootstrap_draws=10000))
p = OUT/'gate_a_results.json'
e = json.loads(p.read_text()); e['evidence_version'] = '1.2.2'; e['correction_task'] = 'v1.2.2 theta pin + DEV bootstrap'
with gzip.GzipFile(filename=str(OUT/'gate_a_results.json.gz'), mode='wb', mtime=0) as f:
    f.write((json.dumps(e, indent=2)+'\n').encode())
p.unlink()
print('DONE', e['parameters'])
