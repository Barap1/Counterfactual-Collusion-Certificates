# CCC agent rules (Codex and other agents; keep consistent with CLAUDE.md)

Read `CLAUDE.md` in this directory - the same rules apply to you. Key points:
- Work only on the task ID and owned paths you were given; check `ops/tasks.json` leases.
- Load only the `docs/spec/` modules named in your brief; never the master spec.
- No model/API calls for experiments, no secrets read or printed (`.env`, `compute.env`, `*.local.json`), no network unless your brief allows it.
- No git push/force/reset/clean. Write evidence to disk; return a short handoff with exact paths and commands run.

## Cursor Cloud specific instructions

The image install prepares a gitignored Colosseum checkout and restores release copies. It does not create or source `compute.env`.

- Starter: `starter/collusion_hackathon` at `d585a7b3be50366cc2bdf5789bf8add5890b2abd`, paths `colosseum/` and `util/` only, with `colosseum/external/CoLLAB` present. Interpreter: `starter/collusion_hackathon/colosseum/.venv/bin/python` after `uv sync --locked` on `/usr/bin/python3` (3.12; the lockfile admits this version).
- `results/baselines` is copied from `docs/release/pilot_archive` only when `results/baselines` is absent. Leave an existing archive unchanged.
- `docs/runner/exp001-pilot3` is copied from `docs/release/pilot3_input` only when that path is absent.

Offline checks from the repo root:

```sh
export CCC_STARTER_ROOT="$PWD/starter/collusion_hackathon"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PWD/scripts/offline_guard:$PWD"
starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests -t .
/bin/zsh scripts/reproduce_offline.sh
```

`PYTHONPATH` includes `scripts/offline_guard` so discovery skips the held-out EXP-002 manifest test. The public tree contains 9 of the 27 seed-1 pilot files named in `ops/pilot_manifest.sha256`. `tests.test_offline_adapter` then errors on the three checks that read the missing run traces (`final_summary.json` and the interrupted-run prompts). Leave those bytes unrestored. `docs/release/exp001_dev_input` is present for the offline analysis driver.
