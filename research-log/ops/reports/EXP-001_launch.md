# EXP-001 launch report

Status: NOT LAUNCHED. Launch attempt refused by the runner before any model call. Operator stopped per protocol; no code, manifest, or seeds were changed.

## Preflight
- Before start: no `ollama` process running; no listener on 127.0.0.1:11434 (no desktop app server to stop).
- Our server started detached, local-only:
  - Server PID: 57827 (`ollama serve`, listener 127.0.0.1:11434, pidfile runs/exp001/ollama.pid)
  - Log: runs/exp001/ollama_serve.log
  - Version 0.32.5, up after ~2 s.
- Preload `gemma4:26b` with keep_alive -1, num_ctx 32768: succeeded (done_reason "load").
- `/api/ps`: gemma4:26b, digest 5571076f3d70050487b26b341705799e0ab29b808164f90d20d4cf84f699d251, context_length 32768, size_vram 17398172220, expires_at far future (infinite keep-alive).
- `/api/tags` digest for gemma4:26b matches the required digest.

## Plan
- `ccc.runner plan docs/runner/exp001_manifest.json` exit 0; saved to runs/exp001/plan.txt.
- 8 base trajectories, 112 continuations, 4 independent worlds.

## Smoke test
- Skipped: `ccc.runner run --help` exposes only `--dry-run`, `--live`, `--retry-failed`. No limit flag exists.
- Per step 3, the first checkpoint would have been watched during the full run. That did not happen, because the run never started.

## Launch
- Launch attempt time: 2026-10-23T21:40:44Z (runs/exp001/launch_time_utc.txt).
- Command: `caffeinate -dimsu ... ccc.runner run docs/runner/exp001_manifest.json --output runs/exp001/live --live`
- Run PID: 58427 (runs/exp001/run.pid). The process exited immediately.
- runs/exp001/run.log:
  `runner refused: hard_stop_utc must be UTC`
- Cause (read-only inspection): ccc/runner/manifest.py:138 raises this in `parse_time`. The manifest value is `"2026-10-24T09:00:00Z"` (docs/runner/exp001_manifest.json:166). The same manifest passed `plan`, so the `run` path appears to validate it differently. Not investigated further, because that requires a code change.

## Progress
- None. Zero live model calls. No budget ledger entries were written by this run.

## Monitoring / stop
- Ollama server: `curl -s http://127.0.0.1:11434/api/ps`; stop with `kill 57827`. It is still resident and holds about 17 GB VRAM until stopped.
- Relaunch only after the runner refusal is fixed by the director: rerun the command in step 4 of the operator brief.

## Anomalies
- Runner refused a manifest it had already accepted in `plan`.
- Runner has no limit flag, so the smoke test could not be run as designed.
- The README says outputs are restricted to docs/runner/; the requested `--output runs/exp001/live` was not reached, so this is still unverified.
