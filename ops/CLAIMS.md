# Claim-to-evidence index

| ID | Claim | Status | Evidence |
|---|---|---|---|
| C-P01 | Seed-1 positive-control pilot completed with the 16 values in module 02 | machine-verified (values match) | `results/baselines/colosseum_positive_control_seed1/.../summary.json`, `final_summary.json`; `ops/pilot_manifest.sha256` |
| C-P02 | Pilot `coverage` = tasks_done / min(n_agents, n_tasks) = 3/4 (not 3 of 8 tasks) | machine-verified | `ops/reports/pilot_metric_audit.md`; `tests/test_offline_adapter.py::test_pilot_metrics_recompute` |
| C-P03 | Pilot `total_cost` (22.27) is task-cost units, not API dollars | verified in code | installed `envs/dcops/jira_ticket/jira_ticket_env.py` |
| C-P04 | Pilot shows causal collusion | **REJECTED** (pilot is prompted positive control, development data only) | module 02 |
| C-P05 | Pilot model was GPT-4o-mini | **REJECTED** (stale label; recorded model cohere/north-mini-code:free) | `run_config.json` |

## Final claims (2026-10-24; authoritative ledger: docs/review/rev001/CLAIMS_LEDGER.md)

| ID | Claim | Status | Evidence |
|---|---|---|---|
| C-H01 | Held-out primary Delta = 1.354 reward units, world-cluster 95% CI [-0.020, 2.834], exact one-sided sign-flip p = 0.0703, n = 8 pairs | VERIFIED (reproduced twice: independent script and REV-001) | docs/analysis/exp002_heldout_v2/effects_study.json; review/reproduce_headline/exp002_independent.json; docs/review/rev001/ |
| C-H02 | Preregistered decision: Delta > 0 NOT SUPPORTED (confirmatory null) | VERIFIED | D-034/D-035; exp002_heldout_v2 |
| C-H03 | Holm S1–S3 adjusted p 0.164 / 0.4375 / 0.164: none significant | VERIFIED | REV001.md §3 |
| C-H04 | Case certificates 0 supported / 11 not supported / 5 inconclusive; max case CI_lower 0.77 < m_O 2.5; N_m ran on 2/16 | VERIFIED | checkpoint_certificates.json; REV001.md §4 |
| C-H05 | "Not supported" means no collusion | **REJECTED** (estimand-level statement only) | paper Discussion/Conclusion |
| C-H06 | Integrity: 143/143 executed branches pass V3/V6/V05b/V08/V09/V-echo; 0 failed/invalid; one model digest; $0 | VERIFIED | REV001.md §5; docs/runner/archives/exp002-live.tar.gz(.sha256) |
| C-H07 | Post-hoc sensitivity (excluding non-commit F runs H02_B1, H05_B1): Delta 0.727, CI [-0.31, 1.91], p 0.156 | VERIFIED, labelled POST HOC (not primary) | REV001.md F-2 |
| C-D01 | DEV Gate A v1.2.2: F/S 380/380, K scope 4180/4180, isolation 760/760, A2 never supported 80/80; 8/800 supported, all with oracle harm 4.015; 0 false supports; 0 estimand-level false negatives | VERIFIED (director recount) | docs/gate_a/v1.2/correction_v1.2.2/; docs/review/director_gateA_audit.md |
| C-D02 | A5 redundancy check 20/120 (16/68 amended) and A6 350/360 fail as stricter diagnostics | VERIFIED (limitation) | same |
| C-D03 | Tier-B placebo availability 0/8 on DEV real conversations | VERIFIED | docs/research/sci002/placebo_census_tierB_dev.md |
| C-X01 | "First causal/counterfactual audit of LLM collusion"; "novel message knockout" | **REJECTED** | docs/research/sci001/claim_review.md, close_read.md |
| Note | REV-001 ledger C24 says 3 `pattern_ambiguous`; frozen rows show 4 (H02_B1, H07_B1, H07_B2, H08_B1). The paper uses 4. | CORRECTED | ops/reports/PUB-007.md |
