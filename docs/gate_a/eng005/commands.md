# ENG-005 commands and evidence

Run from `/Users/aarav/Documents/Projects/ApartSprint` with no live clients or network.

```sh
starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests/audit -t . > docs/gate_a/eng005/tests_audit.txt 2>&1
starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests/fixtures -t . > docs/gate_a/eng005/tests_fixtures.txt 2>&1
starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests -t . > docs/gate_a/eng005/tests_full.txt 2>&1
starter/collusion_hackathon/colosseum/.venv/bin/python -m docs.gate_a.eng005.evaluate_dev > docs/gate_a/eng005/evaluation_stdout.txt 2>&1
starter/collusion_hackathon/colosseum/.venv/bin/python -m docs.gate_a.eng005.verify_old_regressions > docs/gate_a/eng005/old_regression_commands.txt 2>&1
git diff --check
```

The DEV evaluation wrapper installs `tests.replay.offline_runner.guard` before importing the evaluator (secret opens, DNS, socket connect/send denied). The evaluator additionally refuses non-DEV seeds before generation and uses scripted clients only. `progress.jsonl` records first-pass cell decisions; final study-qualified decisions are in `gate_a_results.json.gz`.

Old-code regression reproduction uses a temporary tree under `/private/tmp`, `git show HEAD:<owned source>` for the pre-ENG-005 audit/fixture code, current tests, and read-only symlinks for other modules. It never checks out or overwrites repository sources. Real failures are in `old_tests_audit.txt` and `old_test_precondition.txt`; missing new study helpers are expected errors in the old implementation. C3 and A6 gating also produce behavioral assertion failures; V07 provenance and A6b precondition produce missing-evidence errors. Every new regression fails against that old source. The old tree path and process exit codes are retained in `old_regression_commands.txt`.

The first full-suite run is retained as `tests_full_initial.txt`; the final run includes all added regressions. Read-only discovery used `cat`, `sed`, `rg`, `git status --short`, `git diff`, and `git show`; edits used Python file writes and shell heredocs in owned paths. A process-list diagnostic (`ps`/`pgrep`) was denied by the sandbox and made no changes. No git commits, pushes, resets, cleans, secrets, live experiments, or protocol edits.

Final whole-dataset requalification (one-sided V10 study lower bound per `docs/stats/analysis_spec.md`, no branch/baseline/check changes):

```sh
starter/collusion_hackathon/colosseum/.venv/bin/python -m docs.gate_a.eng005.requalify > docs/gate_a/eng005/qualification_stdout.txt 2>&1
```

A prior qualification is retained in `qualification_prior.json.gz`. Requalification always starts from that archive, preserves branch/baseline/check hashes, and updates all 800 decisions and tables. The final full-suite run includes the one-sided-bound regression; its predecessor is `tests_full_pre_bound_correction.txt`.
