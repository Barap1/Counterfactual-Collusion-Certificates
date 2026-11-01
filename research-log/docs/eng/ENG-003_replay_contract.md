# ENG-003 replay hardening

SCI-002 freeze-candidate v1 is the scientific authority. This is offline engineering evidence,
not an inference experiment or an independently reviewed scientific protocol freeze.

## Compatibility and intervention boundary

Existing `ReplayFixture`, `run_fixture`, `record_source_run`, `candidate_exposures`,
`make_checkpoint`, `run_branch` and `audit` call signatures remain valid. `audit` defaults to
F/S/K; opt in with `arms=("F", "S", "K", "N", "C")`. It shuffles arm execution and logs the
actual order. `audit_replicates` shuffles the full arm × replicate schedule and checks response
IDs across all attempts. `select_protocol_exposure` adds SCI-002's one-confirmatory-exposure
selection/bundling without changing the exploratory `candidate_exposures` API.

K removes only declared pre-fork communication event IDs; original indices stay fixed.
N substitutes exactly matched character lengths using the five frozen development phrases in
`ccc/replay/neutral.py`, keeping sender/index/metadata. C removes E* plus sender communications
on P, including new posts. Actions and assignments are retained. The hook is run at prefetch
and again before every submitted request, including later tool-loop calls, against the frozen
turn-start view. This matches upstream's fixed user prompt within each turn.

`prompt_diff.py` independently derives permitted byte edits from raw event IDs and full upstream
renders. It imports no intervention or rendering helpers; only the neutral vocabulary is shared
as configuration data. Every submitted system/user prompt is checked against a same-state F
render. The actual F and K boundary prompts are also paired. Later F/K states may diverge, so
later prompts are compared against their own state's factual rendering rather than against a
different trajectory. Existing check IDs remain; independent `V3` and protocol `V6` are added.
The legacy `V-model` ID remains available to consumers.

## V07 decision and full-horizon coverage

Per protocol §§3,7,9, a fresh sender post after t* has a new event ID and passes through K,
even when verbatim. This is a valid coarse event intervention with `resend_detected` and
`post_fork_carrier`, rather than an invalid branch. C is the follow-up intervention. Provenance
requires an exact event/payload match in the underlying raw turn-start board: finding the same
text somewhere else does not exempt the rest of the request. Public relays, preexisting copies,
action traces and CURRENT ASSIGNMENTS receive the applicable redundancy/carrier flags.
An original masked ID or an unattributed re-render in memory/summary/tool text fails V07;
an injected summary also fails independent V3. Receiver-generated assistant/tool arguments
are fresh post-fork carriers, not passive re-renders. Tool results are independently checked for
board echoes. Raw receiver requests are scanned throughout the declared horizon, across all
boards, context/megaboard records, structured message content, memory/summaries, tool results
and CURRENT ASSIGNMENTS. First turn, surface, match kind, carriers and flags are retained.

The development detector uses normalized exact text, three-word shingle Jaccard ≥0.5, or
matching task/commitment targets. Its vocabulary is independent of fixture policy code and
has no fixture imports. This is a deliberately limited lexical extractor; agent attribution and
arbitrary semantic/encoded carriers are not resolved. θ and the extractor need scientific
freeze/review. No negative certificate can treat its silence as proof of absent communication.

## State, outcomes and model identity

Dynamic schema v2 captures every local game RNG: env, run selection/order and a world-local
copy of Python global RNG (including client retry jitter), plus the entire local Megaboard,
logical event clock, protocol log and cursor. Global RNG use is scoped per serial world and
the caller's RNG is restored. Prefix response records retain post-call RNG state, allowing
prefix reconstruction even when a scripted client consumes Python randomness. No real MCP
server is used on this upstream path: the in-process Megaboard is the complete channel store.
Static tasks/costs/roles/order/config/params are reconstructed and hash checked. Provider-side
RNG/cache/routing remains inaccessible. Arbitrary client-owned RNGs require their own state
adapter; parallel worlds in one process are unsupported. Legacy dynamic v1 snapshots are
rejected instead of being silently upgraded.

W is now `sum(agent_rewards.values())`, retaining upstream joint reward and its difference as
separate diagnostics. Exhaustive 4,096 assignments over skip/six tasks/unknown test the exact
identity; 323 duplicate-unknown assignments differ, with `joint_reward-W = 20*(k-1)` for k
unknown claimants. Unknown single claims and legal task collisions agree up to float roundoff.
Each call retains provider response model ID, usage, finish reason, latency, unknown cost as
null and context-overflow flag. Requested/reported model or parameter drift fails V6.

## Disk evidence and external integration fixes

`run_branch(..., ledger_dir=...)` creates an immutable attempt directory with `events.jsonl`,
request/response artifacts, checkpoint/snapshot, full prompt audits, branch status/outcomes,
SHA-256 manifest and hash-linked events. Invalid/failed attempts are retained. Exclusive writes
and unique attempt paths prevent accidental overwrite; a repeated replicate ID is an attempt,
not a new independent sample. `verify_branch` checks relative paths, artifact hashes and chain.
Without `ledger_dir`, artifacts live in scratch and are removed at process exit; scientific
collection must explicitly select durable storage. Hashes detect drift, not a malicious rewrite
of every artifact and its external anchor. Consumers must retain the manifest hash.

Two changes outside ENG-003 ownership are provided only as unapplied patches:

- `patches/ENG-003_optional_registry.patch`: BOOT-001's `environment_names()` calls the full
  Terrarium registry, importing optional `personal_assistant` and failing on `problem_layer`.
  Query the dcops lazy export names instead. The actual Jira import stays targeted.
- `patches/ENG-003_stale_fixture_assertion.patch`: FIX-001's verbatim-resend test explicitly
  expects the old invalidation. Change it to require valid replay plus the resend flag.

The starter venv, archived baselines and other workers' source paths were not edited.

The concurrently appearing ENG-004 full suite also exposed
`tests.audit.test_native.NativeIntegration.test_tool_fault_invalid` →
`ccc/audit/gate_a.py` baseline-record construction → `estimate()` → `KeyError: Omean`.
That code labels any truthy diagnostic outcome dictionary `complete`, even when it contains
only an incomplete status/final-summary. The integration owner should pass the actual branch
status and admit only outcome dictionaries containing complete finite Omean/Cmean/A/W; invalid
or infrastructure-missing branches remain missing. ENG-003 does not edit those paths or turn
incomplete diagnostics into zero rewards to make the test pass.

During this task the shared `protocol.md` advanced to **v1.1**. ENG-003 is scoped to v1;
checkpoint metadata now pins the preserved `protocol_v1.md` (SHA-256
`7893ba8dd077d2318d7ea2464b30420fe8b2077e9f4aed8af1ad5f21ef26bf84`). If that archive is
absent it accepts `protocol.md` only when its status is still exactly v1. The v1.1 per-call
seed/load-session and statistical changes need their own integration/revalidation. The
concurrent runner's example manifests can fail their current-protocol hash check after that
protocol edit; ENG-003 does not refresh another owner's frozen manifests.

The registry error in the earlier guarded development run is retained in
`ENG-003_baseline_guarded.txt`. A later standalone adapter run passed 4 tests in the shared
checkout (`ENG-003_adapter_tests.txt`); no ENG-003 code changed the adapter or starter venv.
The optional registry patch remains a portable proposed fix, not a claim of an applied change.

Retained ledger attempts under `ENG-003_ledger_evidence/` are versioned evidence, not independent
replicates. The v3 probe/verification supersedes earlier development observations for this task.
A retained attempt includes world spec, static state, prefix request/response records, and the
source-hash artifact alongside the snapshot and post-fork events. `run.json` implements the
module-15 run-manifest shape; unknown backend/weights/quantization/context fields remain null or
unclassified and cannot authorize a live run. Default scratch ledgers are intentionally ephemeral.
