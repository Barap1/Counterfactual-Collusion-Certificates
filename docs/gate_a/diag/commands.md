# GA-DIAG commands and provenance

Working directory: `/Users/aarav/Documents/Projects/ApartSprint`.

Final regression command actually run (stdout/stderr captured verbatim):
```sh
starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests/audit -t . > docs/gate_a/diag/test_output.txt 2>&1
```

The full evaluation was actually launched with the following inline Python,
redirecting stdout/stderr to `docs/gate_a/diag/evaluation_output.txt`. The equivalent
standalone reproduction script is `docs/gate_a/diag/run_evaluation.py`.
```sh
starter/collusion_hackathon/colosseum/.venv/bin/python - <<'PY' > docs/gate_a/diag/evaluation_output.txt 2>&1
import sys,os
from pathlib import Path
from tests.replay.offline_runner import guard
os.environ['CCC_STARTER_ROOT']=str(Path.cwd()/'starter/collusion_hackathon')
sys.addaudithook(guard)
from ccc.audit.gate_a import main
main(out='docs/gate_a/diag')
import gzip
p=Path('docs/gate_a/diag/gate_a_results.json')
with gzip.open(str(p)+'.gz','wb') as f: f.write(p.read_bytes())
p.unlink()
PY
```

Descriptive analysis command/output:
```sh
PYTHONPATH=. starter/collusion_hackathon/colosseum/.venv/bin/python docs/gate_a/diag/analyze.py > docs/gate_a/diag/analysis_output.txt
```

Inspection used `cat`, `sed`, `rg`, `git status --short`, and offline Python over
archived JSON. No model calls, Ollama startup, network access, secrets, commits,
fixture writes, replay writes, protocol edits or held-out generation occurred.
The registry was checked: it still lists ENG-004, without a GA-DIAG lease entry;
the director's explicit GA-DIAG ownership in the task message governs this work.
