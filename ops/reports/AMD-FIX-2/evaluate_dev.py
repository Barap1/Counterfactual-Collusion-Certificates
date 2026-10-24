"""AMD-FIX-2 fresh DEV evaluation; historical census and predictions are immutable inputs."""
import gzip,json,os,sys
from pathlib import Path
from tests.replay.offline_runner import guard
ROOT=Path.cwd(); OUT=ROOT/'docs/gate_a/v1.2/correction_v1.2.1'
os.environ['CCC_STARTER_ROOT']=str(ROOT/'starter/collusion_hackathon')
sys.addaudithook(guard)
from ccc.audit.gate_a import main
(OUT/'placebo_manifests.jsonl').write_text('')
main(OUT)
p=OUT/'gate_a_results.json'
e=json.loads(p.read_text());e['evidence_version']='1.2.1';e['correction_task']='AMD-FIX-2'
with gzip.GzipFile(filename=str(OUT/'gate_a_results.json.gz'),mode='wb',mtime=0) as f:
    f.write((json.dumps(e,indent=2)+'\n').encode())
p.unlink()
