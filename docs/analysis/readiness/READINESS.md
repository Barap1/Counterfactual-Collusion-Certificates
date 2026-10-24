# STAT-002c analysis readiness

Owner is the sole author. No AI co-author attribution is authorized.

Validated with synthetic metadata only, on 2026-10-24. No held-out outcome contents, shared budget ledger, model service, credentials, or network were accessed. Scope deviation: an early `rg --files docs | rg` filename search to locate the protocol was broader than allowed and could traverse protected paths; only protocol filenames were returned. No protected output contents were opened, and later searches were scoped. The explicitly authorized `docs/runner/exp002_manifest.json` was read as a design contract only. The task registry has no STAT-002c entry; ownership follows the direct task assignment and no registry/lease was changed.

The command accepts terminal v1.2 runner output directly. It verifies the frozen manifest against its STAT-001 approval and protocol, reads the pinned Stage-2 addendum (m_O 2.5, delta_W 5, delta_S 2.5, theta 0.4, weak_detector true), verifies metadata envelopes, and records input/code hashes. It does not need a hand-created flat analysis ledger or a nonexistent `docs/stats/stage2_addendum.json`. Active/incomplete collection remains refused by the existing terminal-marker/collector-lock guard. Never run this command against the ongoing experiment.

After the controller confirms completion, set `EXP002_OUTPUT` to the controller-supplied terminal output directory. Do not discover it by listing experiment directories. From the repository root, run exactly:

```sh
nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.analysis run --input "${EXP002_OUTPUT:?set to the completed runner output directory}" --out docs/analysis/readiness/heldout_analysis
```

The output must be separate from the input. Exit 0 means analysis completed; exit 2 writes `validation_report.json` explaining input rejection. Use a fresh output directory to avoid stale files from an earlier analysis.

Successful execution produces exactly these 39 files. Each of the following 13 stems produces both `.csv` and `.json`:

| Stem | Contents |
| --- | --- |
| `events_accounting` | Attempt-local call accounting; never the shared budget ledger |
| `attempts` | All recorded branch attempts, including prior world attempts |
| `scheduled_statuses` | Every world attempt, failed/cap reasons, skipped N records, unrun worlds |
| `continuations` | Final-world-attempt branches and explicitly unrecorded missing slots |
| `checkpoint_certificates` | Case status/reasons, tau vector/intervals, placebo availability, lexical detector limits, TV_excess |
| `world_effects` | World/regime effects, definition flags, operational status, observed eligibility |
| `effects_study` | Primary Delta, Delta_conditional, eligibility rates/difference, within-regime effects, Holm S1–S3 |
| `sensitivity` | Missing-data bounds, noncommit exclusion, S pooling, eligibility sensitivity, leave-one-world-out |
| `missingness` | Scheduled/completed/missing counts, status subtypes, retries and intervals per arm/regime |
| `validity_checks` | V8, V9 TOST with attained 90%/95% intervals, V10, recorded checkpoint checks |
| `status_crosscheck` | Analysis/audit disagreements when an audit decision exists; empty otherwise |
| `coverage` | All attempted cases by status/regime and determinate coverage |
| `cost_throughput` | Recorded calls/tokens/latencies/costs and unknown-cost counts |

Each of these five stems also produces both `.csv` and `.json`:

- `figure_data/fig_delta_by_world`
- `figure_data/fig_tau_vector`
- `figure_data/fig_status_stack`
- `figure_data/fig_sham_noise`
- `figure_data/fig_missingness`

The remaining files are `aggregate.json` (hashes, thresholds, counts, limitations), `validation_report.json` (validation/warnings), and `claims_candidates.jsonl` (unverified exploratory candidates; may be empty). No images, paper claims, or verified claims are generated.

The primary interval resamples complete matched world pairs with PCG64, B=10000, seed=20261025; its test enumerates paired signs exactly. Delta_conditional is descriptive. Eligibility difference uses the existing conservative Bonferroni exact binomial rectangle. Floors and Holm are retained. Protocol v1.2 / DEV-001 keeps Tier B exploratory even when sample floors pass; this readiness work does not restore a confirmatory claim label.

N `not_run/no_placebo_available` records are retained in scheduling accounting and excluded from scheduled continuation/missingness denominators. Without N, `tau_O_minus_tau_O_N` and its bounds are null, with explicit `unavailable:no_placebo_available`; they are never zero-filled. F/K harm cases can report `inconclusive` with `no_placebo_available`. A source failure or cap before an exposure remains undefined in Delta, with its actual operational reason (`world_attempt_failed`, `request_cap`); it is not invented as a restore failure or a no-op. Such worlds remain in attempted denominators; eligibility tables explicitly count unobserved eligibility. True `no_exposure/post_decision` has effect zero as preregistered. Unstarted worlds are listed as unrun and excluded from attempted denominators.

Whole-world retries retain all recorded attempts, use only the final attempt for estimation, and never recycle earlier branches to fill gaps. Session changes within that final checkpoint invalidate it. Skipped N is not an infrastructure failure. S is n=1 only at the frozen hash-selected checkpoint IDs, so V9 pools checkpoint/world sham differences; it never tries to construct a within-checkpoint S interval from one draw.

Runner metadata does not contain the frozen case `info_bearing` output. The adapter explicitly records that absence and conservatively sets it true; missing validity checks are never inferred to pass. This cannot create support, and does not affect F/K study estimates. Model identity comes from the configured stratum checked against recorded local event metadata. TV interval remains unavailable because no frozen interval algorithm is specified; raw TV, null correction, TV_excess, and the reason are reported. These limits are not silently repaired with new science or live calls.

Reproduce the synthetic proof (all paths are owned by this task):

```sh
nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.analysis.readiness_fixture --out docs/analysis/readiness/synthetic_input
nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.analysis run --input docs/analysis/readiness/synthetic_input --out docs/analysis/readiness/synthetic_analysis
nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests/analysis -t .
```

`synthetic_input/` is fixture-generated runner-shaped, hash-enveloped metadata labelled `synthetic_readiness`, live disabled, with 16 worlds / 8 pairs, F4/K4, hashed S1, absent N on every eligible checkpoint, one source failure, one request-cap stop, and one additional no-exposure case. Its synthetic phase is accepted only by this explicit adapter path and is recorded in output provenance. No collector or model calls are needed. `tests.log`, `generate.log`, `analysis.log`, `coverage_simulation.json`, `verification.json`, and the 39 files under `synthetic_analysis/` are retained evidence.

All 50 analysis tests pass under the required offline runner; all 39 synthetic analysis files are byte-identical on repeat execution. Tests independently enumerate the sign-flip, reconstruct the bootstrap draws, verify Holm and eligibility accounting, exercise V9 pass/uncertain/invalid with S1, and check active-input rejection and retry isolation. Synthetic primary Delta=22/7, CI [1.5714285714285714, 4.857142857142857], exact p=0.015625; Delta_conditional=2.5 over 6 pairs. These are synthetic test values only. The host rejected the requested `nice` priority change (`setpriority: Operation not permitted`); commands still completed successfully. No commits or spending.
