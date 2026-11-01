# EXP-001 pilot report

Status: PILOT HALTED after one live call with `model_reload`. Pilot did NOT complete a checkpoint. Full run NOT launched. No retry made. Ollama server left running (PID 57827).

## Watchdog (Step 1)

- Code: `ccc/runner/watchdog.py` (stdlib only); tests: `tests/runner/test_watchdog.py` (20 watchdog tests, fakes only).
- Suite, command `starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner.offline unittest discover -s tests/runner -t .`:

```
Ran 61 tests in 28.702s
OK
```

- Ledger-line rule (a) is applied to `attempt_end` lines for cost (`api_cost_usd`, `new_out_of_pocket_usd` must be present and 0), and to any new line's `backend` and `model_requested`/`model_resolved`.
- Ollama PID for rule (e) is read from `runs/exp001/ollama.pid` (optional `--ollama-pid` override). Unreadable probes fail closed.

## Pilot run (Step 2)

- Ledger line count before launch: 252 (`runs/exp001/pilot_ledger_start_lines.txt`).
- Pilot start: 2026-10-23T21:49:20Z. Pilot PID 64572 (caffeinate parent of the runner), watchdog PID 64659 (`runs/exp001/watchdog.pid`).
- Command: `caffeinate -dimsu ... -m ccc.runner run docs/runner/exp001_manifest.json --output docs/runner/exp001-pilot --live --max-checkpoints 1`.
- Runner log (`docs/runner/exp001-pilot.log`), final lines:

```
Can't get LLM response: model_reload: model-load session changed
ccc.runner.live.ModelReload: model_reload: model-load session changed
runner refused: world attempt failed; evidence retained at .../docs/runner/exp001-pilot/worlds/dev02_B1/attempt_0001
```

- Attempt result (`worlds/dev02_B1/attempt_0001/result.json`): `"status":"failed","error":"ModelReload: model_reload: model-load session changed","outcomes":null`.
- Watchdog log (`docs/runner/exp001-pilot.watchdog.log`):

```
2026-10-23T21:49:23.460002+00:00 watchdog started run_pid=64572 ollama_pid=57827 ledger_offset=117749 initial_size_vram=17398172220
2026-10-23T21:49:53.477489+00:00 run pid exited on its own
```

- `WATCHDOG_EXIT.json`: `exited_utc 2026-10-23T21:49:53.476908+00:00`. No `WATCHDOG_STOP.json`, so no watchdog trigger.

### Ledger delta (`ops/budget_ledger.jsonl`, lines 253-256)

```
run_open     ts 2026-10-23T21:49:20.756970Z  max_calls 2470
attempt_begin  call_index 1, backend ollama_local, model_requested gemma4:26b
attempt_end  status ok, http 200, finish_reason tool_calls, latency_ms 5980.6,
             prompt_tokens 1063, completion_tokens 111, api_cost_usd 0.0, new_out_of_pocket_usd 0.0
run_close    ts 2026-10-23T21:49:26.975650Z  calls_started 1
```

Cost total of ledger delta: `api_cost_usd` 0.0, `new_out_of_pocket_usd` 0.0.

### Session evidence (`attempt_0001/session_checks.json`)

Three `/api/ps` snapshots. Only `expires_at` differs:

```
2026-10-23T21:49:20.754876+00:00  expires_at 2319-02-02T16:27:52.743589807-05:00  size_vram 17398172220  digest 5571076f...
2026-10-23T21:49:20.773755+00:00  expires_at 2319-02-02T16:27:52.743589807-05:00  (same)
2026-10-23T21:49:26.839828+00:00  expires_at 2319-02-02T16:36:43.691220807-05:00  (size_vram, digest, context unchanged)
```

Follow-up reads with no requests, 10 s apart, both return `2319-02-02T16:36:43.691220807-05:00`, so the value is now stable. The llama-server child (PID 58015, `--model sha256-7121...`) has the same process since 17:40 (elapsed 09:55 at check time), so no process reload is visible. Listener PID 57827 is unchanged.

## Pilot metrics

| Metric | Value |
|---|---|
| Wall time (run_open to run_close) | 6.2 s (process exit observed by watchdog at 21:49:53Z) |
| Live calls | 1 (source agent, world dev02_B1, B1, seed 2) |
| Canary calls | 0 (canary probe never reached: halted at the session check after the first call) |
| Calls/min | not meaningful (n=1) |
| s/call | 5.98 (ledger latency_ms 5980.6); llama-server log reports 5.67 s total for 1,174 tokens |
| Branches complete / invalid / failed | 0 / 0 / 0 scheduled branches reached; world attempt failed |
| Failure reason | `model_reload` (session fingerprint changed) |
| model_reload count | 1 |
| Tool-call validity | not evaluated; the one call returned `finish_reason: tool_calls` |
| Ledger cost | 0.0 (api and out-of-pocket) |
| Watchdog triggers | none |

## Full-run projection (Step 3)

Not established. Only one call was measured and no checkpoint completed, so per-checkpoint time is unknown. Illustration only, not an estimate: 2,352 planned calls at about 6 s each is about 3.9 h of serial model time, before tool overhead, canaries, and multi-call trajectories. Time from pilot start (21:50Z) to the hard stop (2026-10-24T09:00Z) is about 11.2 h. That margin cannot be claimed until a full checkpoint completes without a model_reload.

## Anomalies

1. `model_reload` after the first call looks like a false positive. The only changed fingerprint field is `expires_at` (`16:27:52.74` to `16:36:43.69`), changed once around the generation request. Digest, size_vram, context_length, listener PID, and llama-server process were unchanged. `docs/runner/README.md` says infinite keep-alive keeps `expires_at` constant; this run does not support that on Ollama 0.32.5 via `/v1/chat/completions`. Not confirmed as a real reload. Per the owner's rule, I did not retry, change code, or change the manifest.
2. `ccc.runner status --output docs/runner/exp001-pilot` refused with `runner refused: 'sha256'` (a KeyError; the halted output has no seal yet). Output in `runs/exp001/pilot_status.txt`.
3. `.collector.lock` remains in `docs/runner/exp001-pilot/` from the halted run.
4. Commit `7e1f098` ("EXP-001 pilot running") was made by another actor and is inaccurate now that the pilot halted.
5. The earlier launch refusal (`hard_stop_utc must be UTC`, `ops/reports/EXP-001_launch.md`) did not recur. The manifest was accepted and the run progressed to live calls.

## Recommended director decision

Do not relaunch until the expires_at question is resolved. The director must decide whether the fingerprint should exclude `expires_at` (or compare only its constancy after the first call) and whether the runner needs a code fix. Any such change requires owner approval because it touches `ccc/`.

## Files

- `docs/runner/exp001-pilot/` (runner output, halted), `docs/runner/exp001-pilot.log`, `docs/runner/exp001-pilot.watchdog.log`
- `runs/exp001/pilot_status.txt`, `runs/exp001/pilot_start_utc.txt`, `runs/exp001/pilot.pid`, `runs/exp001/watchdog.pid`
- `ccc/runner/watchdog.py`, `tests/runner/test_watchdog.py`

## Pilot 2 (EXP-000d detector, fresh output docs/runner/exp001-pilot2)

Status: HALTED. Checkpoint dev02_B1 ran to completion, but the attempt was invalid (V09 fresh_continuation on 12 of 14 branches). No model_reload. Full run NOT launched. Ollama PID 57827 still running; resident digest unchanged (5571076f3d70...). No commits.

Launch: pilot PID 73552 (caffeinate parent), watchdog PID 73699, `--max-checkpoints 1`, ledger start 256 lines (`runs/exp001/pilot2_ledger_start_lines.txt`). Offline suite before launch: `Ran 62 tests in 25.684s / OK`.

### Metrics (from `ops/budget_ledger.jsonl` lines 257-852 and the attempt's own files)

| Metric | Value |
|---|---|
| Wall time | 21:56:08.54Z to 22:16:50.17Z (last ledger line) = 1,241.6 s (20.7 min); runner exit observed by watchdog at 22:17:12.67Z |
| Live calls | 297 total: 294 generation + 3 reload canaries (`before`, `source_after`, `after`); all 297 `attempt_end` status ok |
| Mean / p95 s per call | 3.876 s / 6.808 s (p95 nearest-rank); median 3.631 s, min 0.57 s, max 9.37 s; sum of latencies 1,151.3 s |
| Calls/min | 14.3 (297 calls over 20.7 min wall) |
| Tokens | prompt 623,593; completion 25,688 |
| Branch statuses | 14 scheduled (F4/S4/K4/N2): 2 valid (N rep 0, S rep 1), 12 invalid. Reason on all 12: `V09 fresh_continuation failed` |
| V09 problem detail | "duplicate response ids within branch", "N response(s) reused from the source run", "N response(s) shared with another branch/replicate". Response IDs look like `chatcmpl-NN` and recur across branches (e.g. `chatcmpl-25` appears 3 times). |
| Attempt status | invalid, world dev02_B1 attempt_0001; other 7 world slots have no attempt (runner refused to continue) |
| Reload detector | `fingerprint+runner_pid+canary` (EXP-000d). 597 session checks, runner_pid 58015 in every check. |
| model_reload count | 0 |
| Canary | 3 probes sent (before, source_after, after); no canary mismatch raised |
| Cost | api_cost_usd 0.0; new_out_of_pocket_usd 0.0 (sum over 297 attempt_end lines) |
| Watchdog | no trigger; `WATCHDOG_EXIT.json` at 22:17:12.67Z (run_pid 73552); no `WATCHDOG_STOP.json` |

Runner refusal (`docs/runner/exp001-pilot2.log`): `runner refused: world attempt invalid; evidence retained at .../docs/runner/exp001-pilot2/worlds/dev02_B1/attempt_0001`

### Projection (not a go decision)

Measured throughput is 14.3 calls/min. The full plan is 8 checkpoints x 294 generation calls = 2,352 planned, plus 3 canaries each = 2,376 live calls. At 14.3 calls/min that is about 166 min (2.8 h) of wall time, against about 10.7 h remaining to the 2026-10-24T09:00:00Z hard stop from 22:18Z. Margin would be about 8 h, but this projection assumes every checkpoint is valid. Here 12 of 14 branches were invalid, and the runner halts on an invalid attempt, so the full run cannot finish without a fix to V09 (or the response-ID scheme) and a clean checkpoint.

### Anomaly and recommended director decision

V09 is failing on response IDs, not on content or reloads. The IDs repeat across branches and across the source run, which the V09 fresh-continuation rule reads as reuse. Whether that is a validator bug or an Ollama OpenAI-adapter ID scheme is not established. No code, manifest, or protocol was changed. The director should decide how to handle it. Any change under `ccc/` needs owner approval.
