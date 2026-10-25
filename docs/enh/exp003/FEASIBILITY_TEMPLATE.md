# EXP-003 feasibility measurement record — unmeasured template

This template supplies no measurements and authorizes no GPU/model calls. ORCH
must run the separately authorized development spike and replace placeholders
with observed, DEV-valid evidence before final freeze. Synthetic test values are
software fixtures, never measurements. Record all failed and successful attempts.

Record spike date, raw sealed evidence paths/hashes, GPU type, CPU cores, memory
GiB, Ollama parallelism and scaledown seconds, server/model/load identities, model
configuration, continuation counts and validation results. One regime-world is
B1 or B2; one pair contains two regime-worlds. Include source generation and all
F/K/N/PF/PK/S work, request failures and identity canaries. Report both regimes,
variation, conservative upper bounds and the rationale for choosing them; a mean
alone is not a worst-case planning bound. Preserve request logs and GPU wall time.

Required measurements (all currently **UNMEASURED**):

| Parameter | Required observation |
| --- | --- |
| GPU type/configuration | Actual resource assignment and identity |
| Seconds per regime-world | Conservative bound covering source, branches, canaries and idle/request overhead |
| Calls per regime-world | Source + continuations; separately count canaries |
| Cost per regime-world with margin | Conservative dollar bound including CPU/memory/GPU and 20% margin |
| Startup seconds/cost/calls | Cold start, load, warm-up, identity checks; cost includes 20% margin |
| Prior usage/storage | Reconciled cumulative prior cost and conservative unledgered storage liability |
| Shutdown | 120 seconds reserved at the pinned resource rate with margin; actual teardown verification |

Use a public JSON measured-cost artifact, with no endpoint credentials. Its schema
is enforced by `ccc.exp003.feasibility.projection`:

```json
{
  "status": "placeholder",
  "measured_dev_valid": false,
  "workload_sha256": "UNMEASURED",
  "launch_config": {"gpu": null, "cpu": null, "mem_gib": null, "parallel": null, "scaledown": null},
  "safety_margin": 1.2,
  "seconds_per_regime_world": null,
  "cost_per_regime_world_usd": null,
  "calls_per_regime_world": null,
  "canary_calls_per_regime_world": null,
  "startup_seconds": null,
  "startup_cost_usd": null,
  "startup_calls": null
}
```

Only an attested successful DEV-valid spike may set status=measured and
measured_dev_valid=true. Compute workload_sha256 with
`ccc.exp003.feasibility.workload_sha256(manifest)`; it binds model parameters
(excluding endpoint), arms and continuation counts. Freeze the measured file's
path and SHA256 as feasibility_budget.measured_cost_artifact and
measured_cost_sha256 in ORCH's final freeze. The existing feasibility_budget
request/time fields must equal the measured file's corresponding parameters.
Document raw evidence provenance alongside this record; hash that record in the
final evidence inventory. Placeholder, missing, changed, zero per-world or
nonfinite parameters refuse admission.

For the unchanged 32 scheduled pairs, calculate:

- Active seconds = startup_seconds + 64 × seconds_per_regime_world.
- Request cap ≥ startup_calls + 64 × (calls_per_regime_world + canary_calls_per_regime_world).
- Projected cost = startup_cost_usd + 64 × cost_per_regime_world_usd + shutdown cost.
- Total liability = reconciled prior usage + storage + maximum of measured block
  projection and requested session lifetime reservation (including shutdown).

Frozen projected totals may conservatively exceed these calculations. They may
never understate them. Total liability must remain below $45 operating stop and
$51 absolute cap, and active lifetime plus shutdown must fit before 09:00 UTC.
The controller also checks current committed ledger exposure, applies the larger
of ledger and reconciled prior usage, and reserves before spawning. Collector
attachment requires the same frozen configuration and enough remaining reserved
lifetime for the entire block. The 7200-second server timeout ceiling also applies.

Compute an affordable pair ceiling from the measured time/cost/request bounds,
remaining time, prior usage and storage. **The planned pair target must be reduced
to what fits the $45 operating stop before any outcomes**, never by affordability
ceilings presented as measurements. This worker does not change the registered
32 scheduled / desired 24–32 / minimum 16 targets. If the measured ceiling is below
32, this protocol's current admission refuses: ORCH needs a prospective documented
amendment and independent review before changing the scheduled target. Never
shorten a block after seeing outcomes. A ceiling below 16 supports only explicitly
labelled feasibility/descriptive work; it cannot lower the confirmatory floor.

Final release remains blocked on real measurements, reconciled billing/storage,
audited seed artifacts, final approved freeze, verified teardown and release review.
