## Task
W1-MODAL: execution-only Modal CPU driver for frozen R2.

## Status
Implemented; DEV byte equality passes. Cloud determinism gate NOT RUN (worker prohibition). Full execution requires GATE PASS.

## Artifacts
- `scripts/bench_modal_run.py`
- `tests/test_bench_modal.py`
- `docs/enh/r2/PARALLEL_EXECUTION.md`
- Reused `scripts/bench_parallel_run.py` unchanged.

## Validation
5 tests passed in 72.90s: two DEV seeds, serial versus mapped callable, all final artifacts byte-identical; resume/corruption, identity refusal, gate bytes and frozen-tail AST checks.

Exact passing command:
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD:/opt/homebrew/Caskroom/miniforge/base/lib/python3.14/site-packages" starter/collusion_hackathon/colosseum/.venv/bin/python -m pytest tests/test_bench_modal.py -q
```
Both dry-run commands passed with the documented offline prefix: `-m scripts.bench_modal_run --dry-run --gate 40` and `--dry-run`. Plans: 40/2100 seed blocks, respectively. Initial venv-only pytest and system-only pytest invocations failed due to missing dependencies; no installation.

## Limitations
No Modal commands, cloud calls, prospective worlds, git commands, or serial-directory writes. SDK authentication, image build/Python availability, and cross-platform gzip equality await ORCH. Population/report tail runs locally. Resume attempts are capped at three; only infrastructure retries are permitted. Serial inventory: 297 unit files; gate compares 80 units plus 80 partitions for the required 40 seeds.

## Budget
$0; Codex GPT-6 (session model; exact variant unavailable).

## Next
ORCH, from repository root, run gate then full run; same commands resume infrastructure interruptions:
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m scripts.bench_modal_run --gate 40 --containers 3
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m scripts.bench_modal_run --containers 3
```
Do not apply the offline guard to cloud commands. Gate writes `docs/enh/r2/run_par/GATE.json` and prints PASS/FAIL.
