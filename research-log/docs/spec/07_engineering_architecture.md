# 07 - Engineering architecture and replay implementation

## Build a thin research layer, not a replacement platform

Reuse Colosseum's environment, tool semantics, and reward instrumentation where valid. Add a CCC adapter, recorder, branch executor, validity checks, and analysis interface. Keep the upstream checkout inspectable and pinned. Prefer new package code and small reproducible patches over a sprawling fork hidden inside an ignored directory.

Suggested layout, adapting to existing files rather than overwriting them:

```text
ApartSprint/
  CCC_START_HERE.md
  CCC_MASTER_SPEC.md
  CLAUDE.md                      # short routing and hard rules
  AGENTS.md                      # consistent Codex-facing rules
  docs/spec/                     # this specification, modular
  docs/research/                 # prior report and verified source notes
  ops/                           # durable coordination state
  configs/                       # explicit model and experiment settings
  src/ccc/
    adapters/colosseum.py
    state.py
    recorder.py
    interventions.py
    replay.py
    inference.py
    metrics.py
    certificates.py
    cli.py
  tests/                         # offline by default
  experiments/                   # protocols and frozen run manifests
  results/raw/                   # append-only, normally excluded from Git
  results/analysis/
  results/certificates/
  analysis/
  demo/                          # offline viewer, no keys
  submission/                    # paper, figures, final PDF, evidence manifest
  patches/upstream/              # minimal documented changes if required
  starter/collusion_hackathon/   # ignored upstream checkout
```

Do not build every file before proving replay. Begin with the recorder, one adapter boundary, and exact scripted tests. Use an ordinary Python package/CLI and JSONL or SQLite rather than a distributed service. SQLite WAL is reasonable for the single-machine run ledger; do not introduce a hosted database.

## Inspect before choosing hooks

The replay worker must inspect actual installed Terrarium objects and Colosseum execution paths. Identify:

- where agent prompts and message histories are stored;
- where blackboards are formatted for each receiver;
- where tool requests are executed and tool results appended;
- how task state, RNGs, scheduler order, and termination are represented;
- which client method transmits model requests;
- whether histories contain nonserializable clients, closures, or live tasks;
- whether any state is hidden in global variables or environment caches.

Document these with exact file/function references. Do not assume `resume.py` means arbitrary event-level branching is already supported. Do not blindly deep-copy an object containing clients, locks, or asyncio tasks.

## Two permitted replay strategies

### Strategy A: explicit state snapshots

Serialize only the state needed for continuation: environment data, per-agent histories, blackboard records, schedule/cursor, random state, and tool state. Recreate clients and immutable configuration separately. Make snapshots immutable and content-addressed. Restore into isolated branch instances with no shared mutable dictionaries or lists.

### Strategy B: deterministic prefix reconstruction

Rebuild from the initial world using recorded pre-boundary model responses and tool events. Intercept each expected request; require its canonical hash to match the recorded request. Execute each environment transition exactly once. Stop at the exposure boundary, validate state equivalence, then switch to fresh generation for all downstream behavior.

This strategy can be simpler than serializing complex live objects. It is valid only if prefix reconstruction is exact under the declared observable state and no unrecorded nondeterminism changes the boundary. Unexpected requests or mismatched tool events must stop the replay rather than silently continuing.

Use whichever passes the invariants with the least code. Record why the other was rejected. A controlled deterministic fixture must pass before consuming real inference quota.

## Snapshot content

At minimum record:

```text
schema_version; world_id; parent_run_id; task configuration;
upstream_commit; CCC_commit; dependency versions;
agent identities, roles, histories, tools, parameters;
environment tasks, costs, assignments, rewards state;
blackboards and receiver visibility rules;
scheduler state and logical turn counters;
Python/NumPy/other relevant RNG states;
request/response prefix index and canonical hashes;
first eligible exposure and treatment policy;
model/provider/backend/quantization identity;
context-window and truncation policy.
```

A hash over serialized state is useful only if the serialization includes all causal state. Add a separate coverage note listing inaccessible or reconstructed fields. Any unknown state that could affect continuation limits the claim.

## Model request recording

Capture request ID, experiment/branch/replicate IDs, timestamps, exact submitted model and parameters, messages, tool schema, tool choice, response/tool calls, usage, provider identity if returned, finish reason, errors, and latency. Never log authorization headers or environment dumps. Keep private reasoning fields separate; do not require or publish model-private reasoning for the audit. The method must work from authorized observable inputs, outputs, and tools.

Store raw payloads privately where necessary and sanitized release payloads with a mapping/hashing scheme. Redaction must not destroy information essential to reproducing the reported intervention; document the tradeoff.

## Cache rules

Prefix replay caching and experimental sampling are different operations.

- Prefix responses may be replayed to reconstruct the same observed history.
- Fresh continuations must not reuse a cached sample as a new replicate.
- Request identity includes full messages/tools, model/backend, parameters, branch and replicate identity, plus the code/protocol version where behavior depends on it.
- Returning to the same prompt does not create independent evidence if the response is reused.
- Once a branch diverges, do not feed it the original future actions or outcomes. That would freeze away the very effect being measured.

Log `cache_mode: prefix_replay | fresh | analysis_only`; a validator must reject accidental mixtures.

## Interventions as pure transformations

Define interventions as typed, testable functions on the receiver observation view. Each returns the modified view plus a machine-readable diff and validity notes. Preserve tool-call IDs and required message structure. Do not edit the raw source trace in place.

For persistent masking, filter every declared subsequent rendering of the event to that receiver within the chosen horizon. Test alternate exposure paths, quoting, summaries, and tool echoes. Do not claim that absence of the original string alone proves absence of its information.

Store exact treatment eligibility and the mask/repair version. A free-form LLM rewrite is not a validated semantics-preserving intervention by default. Prefer a known structured representation or independently checked fact inventory for repair arms.

## Scheduler and randomness

Use a reproducible agent schedule within a comparison. If the upstream system is asynchronous, capture a logical order or use a declared serial scheduling mode for the audit. A serial audit changes the evaluated system; document this rather than pretending it is identical to the original concurrent deployment.

Separate world-generation RNG, scheduling RNG, and continuation sampling. For controlled local randomness, key independent streams by logical event IDs so branch-specific extra calls do not shift every later random draw. Do not claim common random numbers for an API that does not guarantee them. A supplied API seed is metadata, not proof of determinism.

## Target CLI contract

These are commands to implement, **not existing starter commands**:

```text
uv run ccc doctor --offline
uv run ccc validate-pilot --path <archived-run>
uv run ccc fixtures --config <fixture-config>
uv run ccc plan --manifest <run-manifest> --dry-run
uv run ccc collect --manifest <run-manifest>
uv run ccc audit --manifest <frozen-audit-manifest>
uv run ccc analyze --manifest <completed-manifest> --offline
uv run ccc certificate validate --path <certificate.json>
uv run ccc demo --manifest <public-demo-manifest> --offline
uv run ccc reproduce --bundle <release-bundle> --offline
```

Live commands must require an explicit live-inference enablement and policy check. Tests, analysis, viewer startup, and paper generation default to no network model calls. Each command exits nonzero for invalid inputs and writes structured status suitable for resuming.

## Failure containment and logging

Persist a branch record before requesting inference and atomically mark it complete after artifacts are flushed. A timeout or interrupted process leaves a resumable failed/pending entry, not a fabricated zero outcome. Bounded retries need unique attempt IDs and share the same global budget ledger.

Show progress by world, arm, continuation, and request count. Capture a heartbeat, but do not print all prompts to the coordinator. A 30-second quiet interval is not proof of a hung process. Use measured/request-configured timeouts and explicit watchdogs.

## Upstream modifications and reproducibility

If the adapter needs a small upstream hook, save the patch under `patches/upstream/`, record the exact base SHA, and add an application/check script. Test applying it to a clean matching checkout. Never rely solely on uncommitted changes inside `starter/`, because that directory is excluded from the owner's project repository.

A clean reproduction should be able to fetch the pinned upstream revision, apply the minimal patch, install locked dependencies, and reproduce analysis from included traces without spending money. Regenerating model outputs is a separate optional command with its own resource policy.
