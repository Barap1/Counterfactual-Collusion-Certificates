# STAT-002a handoff

Task: offline frozen-candidate analysis, owned paths only.
Status: core `run` package implemented and offline-tested; statistical/specification limitations below remain. Registry inspected: no STAT-002a lease entry; direct assignment followed. No shared registry changes.

Artifacts: `ccc/analysis/{loaders,shift_perm,statistics,status,study,pinning,pipeline,__init__,__main__}.py`; `tests/analysis/{test_analysis.py,vectors.json,__init__.py}`; documentation/evidence under `docs/analysis/` (exact inventory: `docs/analysis/files_touched.txt`). CSV/JSON pairs include retained attempts, API events, missing/scheduled statuses, continuation metrics, certificates, world/study estimates, sensitivities, validity, coverage, throughput, crosschecks and figure data. Legacy N is `N_v1.1_deprecated`. DEV exports no claim candidates.

Validation: **28 tests passed** (16 required families + 12 regression methods). All four frozen interval vectors and six minimum-p vectors pass, including an independent scalar reference comparison. Gaussian lower-bound coverage: **1908/2000 = 0.954**. Finished pilot3: 14 complete attempts, one inconclusive checkpoint, seven unrun planned worlds. Scripted dry-run-v2: eight complete attempts, one inconclusive checkpoint. Both DEV/pilot runs exit 0 and rerun byte-identically. These are status/implementation checks, not findings.

Commands run (from repository root):

```sh
starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests/analysis -t .
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.analysis run --input docs/runner/exp001-pilot3 --out docs/analysis/pilot3
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.analysis run --input docs/runner/dry-run-dev02-v2 --out docs/analysis/dry-run-v2
starter/collusion_hackathon/colosseum/.venv/bin/python docs/analysis/check_end_to_end.py
```

Limitations / Next: TV CI algorithm unspecified: null interval with reason. Eligibility difference uses a labelled conservative exact-binomial rectangle; review required. Fixture evaluation and full Stage 2/pin CLI remain unimplemented (F/S-blind threshold helper supplied). Stage 2 absent: holdout fails closed; no held-out validation claimed. Detailed limits: `docs/analysis/README.md`.

Budget: $0; no live/model/API/network calls; no commits. No edits to protected code or reads of `docs/runner/exp001-live/`.
