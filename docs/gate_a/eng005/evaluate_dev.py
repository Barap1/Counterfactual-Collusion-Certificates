"""ENG-005 full DEV rerun with the same hard guard as the authorized tests."""
import gzip
import os
from pathlib import Path
import sys
from tests.replay.offline_runner import guard

ROOT=Path(__file__).resolve().parents[3]
os.environ['CCC_STARTER_ROOT']=str(ROOT/'starter/collusion_hackathon')
sys.addaudithook(guard)
from ccc.audit.gate_a import main
out=ROOT/'docs/gate_a/eng005'
main(out)
raw=out/'gate_a_results.json'
with gzip.open(out/'gate_a_results.json.gz','wb') as stream:
    stream.write(raw.read_bytes())
raw.unlink()
# The v1.1-fixed report above is the current report; avoid a stale legacy narrative.
(out/'GATE_A_REPORT.md').unlink()
