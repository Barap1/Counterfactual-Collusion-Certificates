# Gate-B runner (EXP-000b)

Run commands from the repository root. This runner never starts Ollama, reads credentials,
loads local policy/secrets, or discovers remote providers. All generation calls, including
scripted tests, pass through `ccc.infra.budget_guard.GuardedChatClient`. Live execution is
explicit, local-only, single-call concurrency, with no fallback and no automatic retries.

## Operator command for EXP-001

With the INF-001 operator's already running, resident, attested local server:

```sh
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner run docs/runner/exp001_manifest.json --output docs/runner/exp001-live --live
```

The runner never starts Ollama or loads a model. The operator starts a dedicated local
server, then preloads the already-installed model (these commands make local model calls;
EXP-000c did not execute them):

```sh
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NO_CLOUD=1 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1 OLLAMA_CONTEXT_LENGTH=32768 OLLAMA_KEEP_ALIVE=-1 ollama serve
```

In another terminal:

```sh
curl --fail --silent --show-error http://127.0.0.1:11434/api/generate -H 'Content-Type: application/json' -d '{"model":"gemma4:26b","keep_alive":-1,"options":{"num_ctx":32768},"stream":false}'
```

Preflight uses OS `lsof` to reject wildcard/LAN listeners, verifies the exact digest in
`/api/tags` and `/api/ps`, resident context 32768, and at least six hours of residency.
Requests send `keep_alive: -1` and `options.num_ctx: 32768`; server configuration remains
necessary if the OpenAI adapter ignores these fields. Proxies and redirects are disabled.

The session fingerprint includes digest, size_vram, context_length, listener PIDs and
an unambiguous model runner subprocess PID under the listener (`ps -axo pid=,ppid=,command=`).
The dedicated single-model server requirement associates that subprocess with gemma4:26b.
A runner PID change means reload. `expires_at` is checked for valid residency but is
excluded from identity: Ollama refreshes it on requests even with infinite keep-alive.
Server version changes also fail closed. When process inspection is unavailable or
ambiguous, fingerprint plus canary is used. Attestation and session checks record the
selected detector and observed runner PID; the canary remains active with either detector.

Before and after each eligible checkpoint's branch set, a fixed prompt, seed 731921,
T=0.7, and max_tokens=16 probe passes through OllamaChatClient/GuardedChatClient.
UTF-8 output content must match byte for byte across this process's session; response IDs
are excluded. Canary requests/responses and guard attempts are retained in `canary/`,
counted in both ledgers and the frozen request cap. An additional canary is sent immediately
after each successful source run, including sources without an eligible checkpoint
(three extra calls for a completed eligible checkpoint).
Probe failure or mismatch invalidates every scheduled checkpoint branch as model_reload.
This detector follows INF-001's observed load-dependent stochastic behavior; it is not a
proof that every possible reload changes the canary. No real model calls were made for
EXP-000c; compatibility is verified against an in-process fake server with real-shaped ps.

The observed digest and initial residency are written into immutable `run_manifest.json`,
linked to the frozen input manifest hash. Each attempt retains all `/api/ps` observations
in `session_checks.json`, with explicit checkpoint before/after evidence. The runner checks
residency and listener PID before and after **every** generation call, too. Every call logs
its session ID, request bytes represented as JSON, seed and guard attempts. Live budget
records go to both `ops/budget_ledger.jsonl` and the attempt-local `budget.jsonl`; shared
HALTs are honored. No local policy file or secret is read.

A changed session, expired/lost residency, changed digest/context, or failed attestation
invalidates the entire checkpoint with reason `model_reload`. All scheduled branch
`result.json` files have invalid status and null outcomes; branch results are published
only after the final session check. Raw traces are retained. `invalidation.json` identifies
the checkpoint-wide scope. The run halts; it does not silently continue on a fresh model.
An explicit `--retry-failed` retains the prior attempt and regenerates the whole world.
The director may authorize the preregistered single reload retry; repeated reloads require
operator investigation. No process resumes an unfinished checkpoint's branch set.

## Manifest and schedule

`ccc.runner.manifest.v1` now requires a **map** `continuations_per_arm` and integer
`master_seed`; the old scalar continuation count and `sampling_seed` are refused.
The default map is `{F:4,K:4,S:2,N:4}`. Held-out checkpoint slots must be even: sort the
world/regime slot IDs, shuffle with Python `random.Random(placebo_subset_seed)`, take
exactly the first half for N, before source calls or outcomes exist. There is at most one
selected checkpoint per slot; ineligible slots are retained and never replaced to fill
N quotas. The realized eligible N fraction need not be 50%. The frozen `plan.json`
persists this selection. Development collects N on all slots.

For each replicate, independently shuffle the still-active arms using
`sha256(canonical_json([branch_order_seed, world_id, replicate]))` as the shuffle seed.
This interleaves unequal arm counts without assuming S has as many replicates as F/K.

Every generation seed is the first 31 bits of SHA-256 of canonical JSON:

```text
["ccc.runner.seed.v1", master_seed, protocol_sha256,
 world_regime_checkpoint_slot_id, arm, replicate, turn_index, call_k, agent]
```

Here `canonical_json` sorts object keys, uses compact separators and UTF-8; `call_k`
is the zero-based call counter within that agent's continuation client. Source calls use
arm `source`, replicate 0. The slot ID identifies the selected checkpoint before it exists.
The schedule's `seed` is the same derivation with turn=-1, call_k=0, agent=""; the actual
per-call seed is recorded separately as `seed_sent`. S and F have different derivation
inputs, as do replicates, turns and tool-loop calls. This deliberately extends the
compute-plan seed tuple with a master seed, domain version and agent; STAT-001 must include
this documented derivation in its freeze. `common_randomness_claim` remains `none`.

Held-out execution, even a dry run, requires `frozen: true`, a verified `stat001` approval
JSON (`task_id`, `frozen_manifest_sha256`) and `stat001_hash` equal to its SHA-256.
The approval binds the exact canonical manifest excluding only `stat001` and
`stat001_hash`. Seed 1 is archival development only. The protocol artifact hash is verified
on every invocation. A changed protocol requires a new reviewed manifest hash.

`exp001_manifest.json` follows the STAT-001 development matrix: seeds 2,3,4,5, B1 then B2
within each seed; B1 deception with a random designated pair, B2 coalition prompting
`never`, the same seed/pair, private-channel access and legitimate task. Counts are
F4/S4/K4/N2, eight base trajectories, at most 112 branch continuations. The request cap
is 2,470 (the planning 2,352 calls plus 5%, rounded up); it is a cap, not a result.
The hard stop is `2026-10-24T09:00:00Z`: do not start another world after that time,
and recheck before launching a checkpoint's branches after its source trajectory.
An already launched checkpoint can finish after the deadline. Unstarted slots remain
visible with no attempt; a source that crosses the cutoff is retained as
`stopped_hard_stop`. There is no outcome-dependent stopping or reordering.

Provenance fields preserve declared commits alongside actual Python hashes in `code.json`.
Outputs are exclusive, hashed, sealed, and restricted to `docs/runner/`; existing output
cannot resume under changed manifest/code. No runner command makes a commit.

## Offline verification and inspection

```sh
starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests/runner -t .
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner plan docs/runner/exp001_manifest.json
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner.offline ccc.runner run docs/runner/dev_manifest.json --output docs/runner/my-offline-run --dry-run
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner status --output docs/runner/exp001-live
```

The Python socket/DNS audit guard remains intact. The sandbox rejects localhost bind, so
the fake Ollama HTTP server uses in-memory streams with the real stdlib HTTP handler and
response parser; only the opener and listener inspection are substituted. It accepts only
its localhost fixture origin. Tests exercise successful guarded collection and a reload
in the middle of a branch set, digest/context/lease/identity refusal, nonlocal listeners,
seeds, unequal schedules, held-out gating, and time cutoffs. Synthetic responses are test
evidence only. The Python guard is not OS-level isolation for arbitrary native code.
Earlier EXP-000 dry-run artifacts and logs remain unchanged historical evidence.

## Halt and restart

On exceptions and normal halt, the collector releases its OS advisory lock in `finally`.
The empty `.collector.lock` file remains intentionally: deleting a locked inode can allow
concurrent collectors to bypass each other. Its presence does not mean a collector is active;
process exit also releases the OS lock. Do not delete it while a collector may be running.
`status --output <directory>` reports failed/invalid/interrupted attempts as halted and
accepts the watchdog's raw JSON sidecars while still checking collector evidence hashes.

Preserve halted evidence. With unchanged code and manifest, an explicitly authorized
`run <manifest> --output <same-directory> --live --retry-failed` starts a new whole-world
attempt, subject to the single reload retry, request cap and deadline. After code changes
(including EXP-000d), use a fresh output directory and a reviewed manifest version; the
old code hashes deliberately prevent resuming the pilot in place. No failed branch set
is resumed. These instructions do not authorize a live retry.
