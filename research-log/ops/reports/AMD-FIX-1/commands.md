# AMD-FIX-1 / Gate A reproduction

Working directory for every command: `/Users/aarav/Documents/Projects/ApartSprint-wt-v12` (branch `v1.2-impl`).
No commits, network, live inference, Ollama operations, secrets or main-checkout writes.

```
python3 ops/reports/AMD-FIX-1/run_suites.py
python3 ops/reports/AMD-FIX-1/run_suites.py audit full
PYTHONPATH=. starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-FIX-1/run_census.py
PYTHONPATH=. starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-FIX-1/run_census.py fx2
PYTHONPATH=. starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-FIX-1/evaluate_dev.py
PYTHONPATH=. starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-FIX-1/run_constructed.py
PYTHONPATH=. starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-FIX-1/report.py
git diff --check
git status --short
```

`run_suites.py` records the exact requested offline-runner commands, counts and exits in `tests.json`.
Initial audit failures and corrected reruns are preserved as `audit_initial.log`, `audit_second.log` and `audit_final.log`.
The first two-census invocation completed fx1, then encountered an Objective-C-after-fork macOS crash before fx2; the actual failed output is `docs/gate_a/v1.2/census_stdout.log`. The retry runs only fx2 in a fresh process. Reproduction should prefer separate `run_census.py fx1` and `run_census.py fx2` commands to avoid this host issue.

The full-suite errors are exactly the missing isolated-worktree pilot archive files; see `full.log`. No archive was copied or test skipped to hide them.
The attempted read-only `ps -o ...` process inspection was denied by the host sandbox; it produced no process data.

The final Gate A command used a separate fresh staging directory after reverting the extra singular-cost pattern:

```
PYTHONPATH=. starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-FIX-1/evaluate_dev.py ops/reports/AMD-FIX-1/final_gate_run
```

Its completed files were copied byte-for-byte to `docs/gate_a/v1.2/`. `final_verification.json` checks 800 fx2 cells, all 740 manifests, all actual arm counts and every N_m provenance record. The driver now explicitly truncates its selection manifest before execution to make repeated invocations reproducible.

The superseded extra-quantity run was interrupted (exit 130); its 241 completed case rows and diagnostics are under `superseded-extra-quantity/`, never used in final tables. A superseded historical comparator using one deterministic legacy result repeated as rows is under `superseded-single-legacy-comparator/`; the final constructed driver executes four actual legacy continuations per control, with unique response IDs, and supersedes it completely. The process-list-based cancellation attempts (`pkill`, `lsof`) returned no process data; the own-session interrupt completed cancellation.
