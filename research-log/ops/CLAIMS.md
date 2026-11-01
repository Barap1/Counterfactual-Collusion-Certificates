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
| C-H08 | 199 scheduled branch records = 143 executed valid continuations + 56 unrun placebo (N) branches; 8 independent matched world pairs | VERIFIED | docs/review/rev001/CLAIMS_LEDGER.md C30 |
| C-H07 | Post-hoc sensitivity (excluding non-commit F runs H02_B1, H05_B1): Delta 0.727, CI [-0.31, 1.91], p 0.156 | VERIFIED, labelled POST HOC (not primary) | REV001.md F-2 |
| C-D01 | DEV Gate A v1.2.2: F/S 380/380, K scope 4180/4180, isolation 760/760, A2 never supported 80/80; 8/800 supported, all with oracle harm 4.015; 0 false supports; 0 estimand-level false negatives | VERIFIED (director recount) | docs/gate_a/v1.2/correction_v1.2.2/; docs/review/director_gateA_audit.md |
| C-D02 | A5 redundancy check 20/120 (16/68 amended) and A6 350/360 fail as stricter diagnostics | VERIFIED (limitation) | same |
| C-D03 | Tier-B placebo availability 0/8 on DEV real conversations | VERIFIED | docs/research/sci002/placebo_census_tierB_dev.md |
| C-X01 | "First causal/counterfactual audit of LLM collusion"; "novel message knockout" | **REJECTED** | docs/research/sci001/claim_review.md, close_read.md |
| Note | REV-001 ledger C24 says 3 `pattern_ambiguous`; frozen rows show 4 (H02_B1, H07_B1, H07_B2, H08_B1). The paper uses 4. | CORRECTED | ops/reports/PUB-007.md |

## D-048 platform and stratum claims (FIX-EPS)

| ID | Claim | Status | Evidence |
|---|---|---|---|
| C-E01 | Shared eps=0 units byte-identical 149/149; no method-output differences on 1458 records | descriptive archive audit; supports established eps=0 scope | docs/enh/r2/PLATFORM_DIVERGENCE.md; scripts/eps_platform_check.py |
| C-E02 | Shared eps=0.1 units differ 142/148; method outputs differ on 1160/1452 records | platform-dependent, not established; cause unresolved | docs/enh/r2/PLATFORM_DIVERGENCE.md |
| C-E03 | eps=0: RQ1/RQ2 pass, RQ3/RQ4/RQ5 fail, RQ4b pass, RQ6 descriptive | established new-prospective, scoped to frozen generator; RQ4b DEV-informed; RQ5 exploratory | docs/enh/r2/RESULTS_BY_STRATUM.json strata.0; run_par/RESULTS.json |
| C-E04 | Four aggregate predictions failed: RQ3/RQ4/RQ4b/RQ5; RQ1/RQ2 pass, RQ6 descriptive | unchanged pre-registered report.py verdicts | run_par/RESULTS.json rq; RESULTS_BY_STRATUM.json aggregate_verdicts |
| C-E05 | eps=0 RQ3 61/200; B2+ legitimate P2/P3 200/200 each, P6 0/200, benign 0/100 | established new-prospective | RESULTS_BY_STRATUM.json strata.0.rq.RQ3/RQ4; run_par/RESULTS.json tables.T5 |
| C-E06 | eps=0 RQ5 v1 2/84 cells, v0 5/84; 73 undefined gaps each; v1 pair attribution P2/I4 and P3/I5 200/200 each | exploratory-method; overall failure retained | RESULTS_BY_STRATUM.json strata.0.rq.RQ5 |
| C-E07 | Established-scope restriction was decided after outcomes were visible; no claim rests on eps=0.1; noisy DEV/prospective are not comparable | post-hoc decision, not new preregistration | ops/DECISIONS.md D-048; paper/v2/draft_v2.md §§5,7,B |
| C-E08 | eps=0 CCC I2 legitimate P2/P3 supported 200/200 each | new-prospective L2 exposure, not attribution | RESULTS_BY_STRATUM.json strata.0.rq.RQ6.rows |
