# STAT-002c handoff

Owner is the sole author; no AI co-author lines.

Task/status: analysis readiness completed against synthetic runner metadata; real outcomes remain unseen. The task registry lacks STAT-002c; direct assignment governs owned paths and no lease/control files were edited.

Fixes: new `ccc/analysis/runner_input.py` reads terminal v1.2 runner metadata and validates the real frozen design/approval without inference. `loaders.py` routes runner output separately from legacy DEV/flat ledgers. `pipeline.py` handles skipped/null N, explicit unavailable placebo contrasts, final whole-world retries and operational missingness. `study.py` reports unobserved eligibility. Thresholds are read from the frozen markdown addendum, not re-pinned. Failures/caps stay undefined; absent N is not scheduled/missing. Missing case info_bearing remains explicitly conservative; no inferred validity pass.

Artifacts: `docs/analysis/readiness/READINESS.md` gives the exact post-completion command, all 39 outputs, limitations and reproduction commands. `tests/analysis/readiness_fixture.py`, `tests/analysis/test_readiness.py`, `docs/analysis/readiness/synthetic_input/`, `synthetic_analysis/`, `tests.log`, `analysis.log`, `generate.log`, `verification.json`, `coverage_simulation.json` hold reproducible evidence.

Commands run (repository root; also listed verbatim in READINESS.md):

```sh
nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.analysis.readiness_fixture --out docs/analysis/readiness/synthetic_input
nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.analysis run --input docs/analysis/readiness/synthetic_input --out docs/analysis/readiness/synthetic_analysis
nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests/analysis -t .
```

Validation: 50 tests pass. Independent bootstrap/sign-flip, conditional Delta, eligibility, Holm, V9 S1 TOST, skipped-N statuses, failure/cap accounting, active guard and retry isolation pass. The real frozen manifest validates in a temporary empty terminal fixture, without loading outcomes. Synthetic Delta=22/7, p=0.015625 is test evidence only. Lightweight `cat`, `rg`, `sed`, `tail`, scoped `git diff`, and Python file-edit/summary commands were also used; one early protocol-locating `rg --files docs | rg` search was broader than allowed and could traverse protected paths; only protocol filenames were returned and no protected output contents were opened. Subsequent searches were scoped.

Limitations/budget/next: $0; no live calls, network, secrets, held-out outcome contents, shared ledger, commits or delegation. Host denied nice priority adjustment; logs retain the warning. Tier B remains exploratory under protocol v1.2/DEV-001. TV interval has no frozen algorithm; runner info_bearing unavailable, conservatively true. Controller must confirm terminal completion before the documented real analysis command is run.
