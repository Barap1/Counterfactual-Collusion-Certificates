"""Reproduce GA-DIAG's full native DEV rerun with hard offline audit guards."""
import gzip
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tests.replay.offline_runner import guard
os.environ['CCC_STARTER_ROOT'] = str(ROOT / 'starter/collusion_hackathon')
sys.addaudithook(guard)
from ccc.audit.gate_a import main
out = Path(__file__).resolve().parent
main(out=out)
p = out / 'gate_a_results.json'
with gzip.open(str(p)+'.gz', 'wb') as stream:
    stream.write(p.read_bytes())
p.unlink()
