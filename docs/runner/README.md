# EXP-000 Gate B collection plumbing

Run from the repository root with `starter/collusion_hackathon/colosseum/.venv/bin/python`.
The CLI is intentionally offline-only in EXP-000. It never starts Ollama, discovers providers,
loads credential files, or enables a remote fallback. The scripted client is a transport **inside**
`GuardedChatClient`; all simulated generation calls pass the same budget admission path.
Its response model string is a scripted echo of the configured identity, not a measurement of
loaded weights. Every run is labelled `scripted_dry_run`.

```sh
python -m ccc.runner plan docs/runner/dev_manifest.json
python -m ccc.runner run docs/runner/dev_manifest.json --output docs/runner/my-run --dry-run
python -m ccc.runner status --output docs/runner/my-run
# Explicit retry creates an additional whole-world attempt, retaining the previous one:
python -m ccc.runner run docs/runner/dev_manifest.json --output docs/runner/my-run --dry-run --retry-failed
```

`run` without `--dry-run` refuses before collection writes. Output roots must be under
`docs/runner/`; this prevents writes to the pilot archive and other workers' collection paths.
CLI errors return 2. `plan` and `status` are read-only. No commit is created by the runner.

## Manifest schema

The complete, runnable JSON example is [`dev_manifest.json`](dev_manifest.json).
`ccc.runner.manifest.v1` extends the module-15 contract with explicit source-world construction
and freeze metadata. Required fields:

| Fields | Contract |
| --- | --- |
| `schema_version`, `experiment_id` | Version and experiment identity |
| `analysis_commit`, `upstream_commit`, `ccc_commit` | Declared provenance; retained alongside actual working-tree Python hashes in `code.json` |
| `phase`, `frozen` | `development` or `holdout`; `frozen: true` required even for dry-run |
| `protocol_artifact`, `protocol_sha256` | Repository-relative non-secret file and verified SHA-256 |
| `worlds` | List of `{id, seed, regime, split}`; unique safe ids and seed/regime pairs; B1/B2 supported |
| `world_template` | Embedded Colosseum batch config; four agents, private pair, two planning rounds, no assignment filling |
| `b1_prompt_variant`, `colluder_selection` | Exactly `deception` and `random`; B2 overrides coalition prompting to `never` |
| `selection_rule`, `horizon` | `sci002.first_private_bundle.v1`, `episode_end` |
| `arms`, `continuations_per_arm` | F/S/K/N, at least two fresh continuations per collected arm |
| `branch_order_seed`, `sampling_seed`, `placebo_subset_seed` | Separate frozen integer seeds; sampling seed is explicitly sent in every guarded wire request |
| `common_randomness_claim` | Exactly `none`; seeded F/S does not establish common provider RNG |
| `max_requests` | Frozen cap across the output root, including retries and attempted admissions |
| `model` | `backend`, `requested_id`, `base_url`, `weight_digest`, `context_limit`, `parameters`; primary stratum pins local `gemma4:26b`, ctx 32768, `reasoning_effort: none` |
| `policy` | Exactly zero new spending, no automatic fallback, live inference disabled |
| `stat001` (holdout only) | `{task_id: "STAT-001", artifact, sha256}`; actual approval JSON must contain `task_id` and `frozen_manifest_sha256` |

The STAT-001 approval's `frozen_manifest_sha256` is the SHA-256 of canonical manifest JSON
with only `stat001` omitted (`ccc.runner.manifest.freeze_hash`). Its file hash is independently
checked. A hash of an unrelated file cannot authorize held-out seeds. Seed 1 remains development
only even with an approval. Declared splits must agree with the run phase. STAT-001 approval
is not manufactured by this runner; tests use temporary synthetic approvals solely to test refusal.

The manifest is copied immutably into the output. Resume refuses a changed manifest or changed
runner/replay/infra Python sources. A new protocol, backend, config, or code version requires a
new collection root. The embedded template's model, prompt and regime knobs are overridden by
the explicit frozen fields; the complete resulting `WorldSpec` is archived before execution.

## Selection and collection

Selection follows SCI-002 §4 without outcome inspection: first communication on the designated
pair's private board, its author as sender, other member as receiver, first receiver exposure,
then the complete sender bundle first rendered at that boundary. The selector checks each
bundle member for prior exposure with replay's public validator. It does not replace an
ineligible first message with a later candidate. No-message, post-decision, prior-exposure and
restore failures remain in the world denominator with missing outcomes.

F/S/K/N restore one serialized checkpoint. ENG-003 supplies persistent masks, original-index
rendering, neutral filler and independent prompt checks. Neutral fillers are frozen code/data
whose exact hashes are retained in `code.json`. The random N subset is chosen before source
generation: half the independent worlds, rounding up for odd counts; matched B1/B2 worlds share
inclusion. In the one-world development demo, N is included. Within each replicate all arms are
shuffled, and replicate blocks are interleaved in execution order. Continuations never increase
the independent-world count.

Source calls, per-turn snapshots, generated tasks/costs/roles/order, requests/responses, selected
bundle and checkpoint are persisted. Branches retain native replay `ccc.event.v1` JSONL and
its request/response hashes under `replay_ledger/`. The additional runner call records retain
the **actual guarded wire payload**, including fixed sampling seed, which can differ from
the upstream request params recorded by the replay wrapper. Headers are never serialized.

Every call has an exclusive fsynced `.begin.json` before admission and `.end.json` after success
or failure. A crash between them remains visible. Guard retries are zero. Upstream-swallowed
call exceptions are checked independently before accepting outcomes. Branch failures remain
missing, never numeric zero. Ended attempts have a sealed file inventory that catches deletion
as well as mutation; native replay hash chains are also verified by `status`. Append-only budget
logs are per-attempt here, separate from the shared live inference ledger.

Resume skips completed or ineligible worlds. Failed/interrupted/invalid worlds require
`--retry-failed`, which creates a new attempt with `retry_of` lineage and regenerates the entire
source/checkpoint/arm block. It does not combine successful arms from different sessions. It
does not resume an individual branch or reconstruct a running provider session. All old attempts
remain available to missingness analysis. The dry-run session label is synthetic and is not an
Ollama load-session observation.

## Verification and retained evidence

Requested OS sandbox command (this environment refuses nested sandboxing):

```sh
sandbox-exec -p '(version 1)(allow default)(deny network-outbound (remote ip))' starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest discover -s tests/runner -t .
```

Real output in [`sandbox-test-output.txt`](sandbox-test-output.txt):
`sandbox-exec: sandbox_apply: Operation not permitted` (exit 71; no tests ran).

The fallback audit hook denies Python socket connection, send, and DNS events before execution.
It is not an OS sandbox for arbitrary native extensions or subprocesses. Tests additionally
patch the live HTTP transport to fail on use during the full-collection test.

```sh
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner.offline unittest discover -s tests/runner -t .
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner.offline ccc.runner plan docs/runner/dev_manifest.json
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner.offline ccc.runner run docs/runner/dev_manifest.json --output docs/runner/dry-run-dev02-v2 --dry-run
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner.offline ccc.runner status --output docs/runner/dry-run-dev02-v2
```

[`tests-current.txt`](tests-current.txt) contains real output: **22 tests, OK** (10.590 seconds).
[`dry-run-v2-summary.json`](dry-run-v2-summary.json) records seed 2/B1: eight valid branches,
28 source + 152 branch = 180 guarded scripted calls, 778 verified JSON artifacts,
zero live calls, $0 new spend. `dry-run-dev02-v2/` is the current immutable evidence tree.
`plan-output.json`, `dry-run-v2-output.json`, `status-v2-output.json`, `resume-v2-output.json` and
the corresponding stderr files retain CLI evidence; resume returned identical output without
new attempts. Current source hashes matched the collected snapshot at handoff.
The earlier `dry-run-dev02/` evidence and summaries remain intact: ENG-003 subsequently
changed replay code, so a fresh collection root was used. Earlier test outputs are retained
as development history, not presented as passing final evidence.

## Before live Gate B

INF-001 must activate a live controller entry point using this guarded collection path, the
shared budget ledger and approved local resource policy. This task intentionally ships no
CLI path that can issue a live request. Live transport activation is **remaining integration
work**, not a validated feature. It must establish and monitor one actual model-load session
for the source/checkpoint and every arm, keep the model resident, verify weights/context/parallelism,
and stop on a reload. A synthetic session id cannot establish that condition.

The director must accept ENG-003/replay and ENG-004/audit integration, inspect an actual live
branch and feasibility under EXP-001, then obtain STAT-001's frozen plan/margins/approval before
holdout. No certificate or scientific effect is produced by this plumbing. OpenRouter corroboration
is a separate future stratum with the 50/day guard, not a fallback or bulk route.
