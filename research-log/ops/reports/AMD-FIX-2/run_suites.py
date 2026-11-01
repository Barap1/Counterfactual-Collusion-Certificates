"""Record exact offline commands, exit codes and unittest counts."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PYTHON = "starter/collusion_hackathon/colosseum/.venv/bin/python"
CASES = [(s, f"tests/{s}") for s in ("audit", "runner", "replay", "fixtures", "review")]
CASES += [("contract", "tests/audit"), ("full", "tests")]
if sys.argv[1:]:
    CASES = [(n,d) for n,d in CASES if n in sys.argv[1:]]
previous = OUT / "tests.json"
results = [r for r in json.loads(previous.read_text()) if r['suite'] not in {n for n,_ in CASES}] if previous.exists() else []
for name, directory in CASES:
    cmd = [PYTHON, "-m", "tests.replay.offline_runner", "-s", directory, "-t", "."]
    if name == "contract":
        cmd += ["-p", "test_commitments_contract.py"]
    start = datetime.now(timezone.utc).isoformat()
    with (OUT / f"{name}.log").open("w") as stream:
        proc = subprocess.run(cmd, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    content = (OUT / f"{name}.log").read_text()
    ran = re.search(r"Ran (\d+) tests? in ([\d.]+)s", content)
    skip = re.search(r"skipped=(\d+)", content)
    row = {"suite": name, "command": " ".join(cmd), "cwd": str(ROOT),
           "started_utc": start, "exit_code": proc.returncode,
           "run": int(ran[1]) if ran else None, "skipped": int(skip[1]) if skip else 0}
    row["errors"] = int(re.search(r"errors=(\d+)", content)[1]) if re.search(r"errors=(\d+)", content) else 0
    row["failures"] = int(re.search(r"failures=(\d+)", content)[1]) if re.search(r"failures=(\d+)", content) else 0
    row["passed"] = row["run"] - row["skipped"] - row["errors"] - row["failures"] if row["run"] is not None else None
    results.append(row)
    (OUT / "tests.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(row), flush=True)
sys.exit(any(r["exit_code"] for r in results))
