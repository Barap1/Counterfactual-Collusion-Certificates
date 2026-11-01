# AMD-FIX-2 commands and scope

Cwd for every command: `/Users/aarav/Documents/Projects/ApartSprint-wt-v12`.
Assignment: user owns AMD-FIX-2; ops/tasks.json contains no AMD-FIX-2 lease (stale registry); no other task ownership changed. Initial branch v1.2-impl, HEAD c8e3ad1, clean working tree. Only audit fixes, their regressions and versioned correction evidence are edited.

Read-only review input: `/Users/aarav/Documents/Projects/ApartSprint/ops/reports/codex_runs/REV-FIX1.stdout`. No live-checkout writes.

```sh
starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-FIX-2/run_suites.py audit contract
starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-FIX-2/run_suites.py runner replay fixtures review full
PYTHONPATH=. starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-FIX-2/evaluate_dev.py
PYTHONPATH=. starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-FIX-2/run_constructed.py
PYTHONPATH=. starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-FIX-2/report.py
```

Suite driver records every exact required offline_runner command, exit and count in tests.json. Evaluation and constructed drivers install the same audit guard. Historical census and pre-CCC predictions are read as immutable inputs, not regenerated or represented as preregistered anew. Prior hashes: prior_sha256.json. No model/API calls, network, Ollama, commits, thresholds, protocol edits, holdout or pilot/archive changes.

Final artifact checks:
```sh
PYTHONPATH=. starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-FIX-2/verify.py
 git diff --check
 git status --short
 git branch --show-current
 git rev-parse --short HEAD
```
