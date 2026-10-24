# FIX-001 commands and evidence

All commands run from the repository root. No network, model inference, git mutation,
or extraction was performed. `PYTHONDONTWRITEBYTECODE=1` prevents import cache writes.
The interpreter is the repository's existing Colosseum virtual environment.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest tests.test_fix001_validity_mapping > docs/enh/fix/regression_before.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest tests.test_fix001_validity_mapping > docs/enh/fix/regression_after.log 2>&1
PYTHONDONTWRITEBYTECODE=1 python3 docs/enh/fix/check_archive.py
PYTHONDONTWRITEBYTECODE=1 starter/collusion_hackathon/colosseum/.venv/bin/python docs/enh/fix/run_analysis.py > docs/enh/fix/analysis.log 2>&1
PYTHONDONTWRITEBYTECODE=1 starter/collusion_hackathon/colosseum/.venv/bin/python docs/analysis/exp002_heldout_v3/verify_correction_v3.py > docs/enh/fix/verification.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python docs/enh/fix/run_tests.py > docs/enh/fix/tests.log 2>&1
```

The initial six-test regression run produced seven assertion failures (including
subtests), before production edits; two additional unknown/NA tests were added
for final validation. An initial synthetic fixture omitted the required F4/K4/S1/N4
manifest map; it was corrected before capturing the failing regression evidence.

The standard release sitecustomize guard forbids all held-out reads. An initial
standard-guard analysis invocation was rejected before reading the manifest. The
saved run_analysis.py uses the existing replay guard (network and secrets blocked)
for this explicitly authorized held-out rerun. Its pipeline arguments are exactly:
`run('docs/runner/exp002-live', 'docs/analysis/exp002_heldout_v3', watchdog_dir='docs/runner/exp002-live.watchdog')`.

Full-suite discovery is the release command `python -m tests.replay.offline_runner
-s tests -t .`, executed via run_tests.py. The wrapper redirects only the suite's
persistent coverage_simulation.json write to docs/enh/fix/coverage_simulation.json,
so the existing readiness artifact is not overwritten. Production code is not patched.
The release guard skips its real held-out manifest test; the authorized analysis
rerun separately exercises the real manifest contract.

Read-only inspection also used cat, sed, rg, ls, tar -tzf, git diff -- scoped source
paths, git status --short, and git show HEAD:ccc/analysis/study.py. Archive data was
streamed with tarfile in memory, and matching existing files were read for comparison.
No member was extracted. AppleDouble metadata was excluded from the regular-file
comparison. The requested external extraction directory is outside sandbox writable
roots, and was unnecessary because all regular files already matched the archive.
