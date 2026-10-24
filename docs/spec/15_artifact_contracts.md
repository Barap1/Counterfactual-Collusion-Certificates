# 15 - Artifact schemas and interfaces

These are design contracts to implement and validate. They do not imply that the current starter already exposes these objects. Use versioned Pydantic/dataclass/JSON Schema definitions or an equivalent lightweight approach. Keep schemas stable after collection begins; migrations must preserve originals.

## Run manifest

```yaml
schema_version: ccc.run.v1
experiment_id: REQUIRED
protocol_sha256: REQUIRED
analysis_commit: REQUIRED
upstream_commit: REQUIRED
ccc_commit: REQUIRED
phase: development # or holdout; never silently changed
world_ids: []
regimes: []
model:
  requested_id: REQUIRED
  resolved_id: null
  provider: REQUIRED
  endpoint_kind: local # local, openrouter, or explicit_modal
  weight_digest: null
  quantization: null
  parameters: {}
  context_limit: null
intervention:
  selection_rule_version: REQUIRED
  eligible_surface: REQUIRED
  arms: [factual, sham, receiver_mask]
  continuation_horizon: REQUIRED
  repeated_exposure_policy: REQUIRED
sampling:
  world_seed_manifest: REQUIRED
  continuations_per_arm: REQUIRED
  branch_order_seed: REQUIRED
  common_randomness_claim: none
policy:
  new_out_of_pocket_usd: 0
  automatic_model_fallback: false
  live_inference_enabled: false
  max_requests: REQUIRED
```

`REQUIRED` is a placeholder for implementation, not a value accepted by a validator. Missing model identity, protocol, or budget policy blocks a live run.

## Event record

```json
{
  "schema_version": "ccc.event.v1",
  "run_id": "<actual id>",
  "branch_id": "<actual id>",
  "replicate_id": "<actual id>",
  "logical_turn": 0,
  "event_type": "model_response",
  "agent_id": "<neutral agent id>",
  "request_id": "<provider/local request id>",
  "request_sha256": "<hash>",
  "response_artifact": "<relative path>",
  "cache_mode": "fresh",
  "model_resolved": "<actual model>",
  "finish_reason": "<actual reason>",
  "status": "complete",
  "api_cost_usd": null,
  "latency_ms": null
}
```

Raw request/response payloads live in referenced artifacts. They must not contain authorization headers. If provider usage is missing, null remains null. Do not infer zero cost from a missing field.

## Checkpoint manifest

Include the source run/world, snapshot hash, prefix request hashes, environment state schema, agent history hashes, blackboard/visibility schema, scheduler cursor, RNG records, exposure boundary, code versions, model/backend, and a state-coverage note. Include a `restore_validation` object with test IDs and pass/fail/unknown states.

A checkpoint must be immutable once used in analysis. Any correction creates a new hash/version and invalidates downstream analyses that depended on the old one until rerun.

## Certificate example shape

```json
{
  "schema_version": "ccc.certificate.v1",
  "certificate_id": "<content-addressed id>",
  "evidence_tier": "real_llm_case_study",
  "scope": {
    "checkpoint_id": "<id>",
    "sender": "<id>",
    "receiver": "<id>",
    "event": "<id>",
    "horizon": "<declared horizon>"
  },
  "status": "inconclusive",
  "status_reasons": ["<actual reason>"],
  "harm_definition_id": "<frozen definition>",
  "effects": {
    "primary": {"estimate": null, "interval": null, "units": "<units>"},
    "coalition_advantage": null,
    "outsider_recovery": null,
    "principal_utility_change": null
  },
  "sample": {"independent_worlds": 0, "fresh_continuations_by_arm": {}},
  "validity_checks": {},
  "specificity": {"status": "not_identifiable", "reason": "<actual reason>"},
  "controls": {},
  "limitations": [],
  "provenance": {
    "run_manifest_sha256": "<hash>",
    "analysis_version": "<version>",
    "artifact_paths": []
  }
}
```

The nulls and zeros above are illustrative empty fields, **not measured results**. A supported certificate cannot contain missing required evidence. The schema validator and scientific validator are separate: valid JSON can still describe invalid science.

## Task record and ownership lease

```yaml
task_id: ENG-002
parent_id: DIRECTOR
attempt: 1
status: queued
owner_role: replay_engineer
runtime: discover_at_launch
model: discover_at_launch
depends_on: [BOOT-001, SCI-002]
read_modules: [04, 07, 10, 15]
write_paths: [src/ccc/replay.py, tests/test_replay.py]
worktree: null
allowed_live_calls: 0
max_children: 2
depth: 2
acceptance_tests: [V01, V02, V03, V04]
reviewer_task: REV-REPLAY-001
artifact_paths: []
lease_expires_at: null
```

A lease expiration alone does not permit two workers to write simultaneously. Confirm process/parent state before reclaiming. Keep parent-child lineage explicit so the director can cancel a subtree and account for its resource use.

## Source ledger

Each source record includes source ID, stable URL, title, authors/organization, version/date, access date, relevant section/location, exact supported claim, limitations, verification status, and any superseding version. A reference mentioned by the prior report but not checked is `unverified`, not automatically eligible for the paper.

## Data-to-paper manifest

`submission/evidence_manifest.json` links every figure/table/quantitative claim to input artifact hashes, analysis code commit, parameters, output hashes, sample units, and reviewer status. Include the final PDF hash and Google Doc revision after export. Keep private connector/account identifiers in the local version only.

## Schema invariants

- Every completed branch belongs to one world, regime, arm, and fresh replicate.
- A duplicate record cannot increase sample size.
- Invalid/failed branches cannot silently become zero outcomes.
- Model/backend changes split groups or invalidate a matched comparison.
- Every claimed effect names the intervention and its horizon.
- Every artifact path resolves within approved roots; no arbitrary path traversal.
- Raw data are append-only; corrections are new versions with lineage.
- The viewer and paper consume the same frozen aggregate outputs.
