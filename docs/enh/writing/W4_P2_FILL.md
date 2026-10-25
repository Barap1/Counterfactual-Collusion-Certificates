# W4-P2 fill ledger

Sources below are key paths within `docs/enh/r2/run_par/RESULTS.json`; [NP] means new-prospective, [DEV] development. Conditional alternatives were selected by reported status, then inactive alternatives removed.

| Placeholder | Value | Source key path |
|---|---|---|
| ABSTRACT_PROSPECTIVE; INTRO_PROSPECTIVE; DISCUSSION_PROSPECTIVE; CONCLUSION_PROSPECTIVE | Consistency passes; failures retained | `rq.*.status`; `tables.RQ6` |
| RQ1; N_cells; k; ub | pass; 364 eligible cells; 0/200; 0.01827534 [NP] | `rq.RQ1`; `tables.T2.violations[*].rate` (eligible count) |
| RQ2; n | pass by construction; separating sets and denominators [NP] | `rq.RQ2`; `tables.T3[*]` |
| RQ3; k/n/p/lo/hi | FAIL; eps-0 61/200, 0.305, [0.242,0.374]; eps-0.1 41/200, 0.205, [0.151,0.268] [NP] | `rq.RQ3.by_epsilon` |
| RQ4; baseline_id; classes/other/rate | FAIL; B2+; class rates/intervals [NP] | `rq.RQ4`; `tables.T5[*].over_attribution` |
| RQ4b; which/rate/eps | FAIL; noisy P2/P3 0/200 [NP] | `tables.T5b[*]` |
| RQ5; gap/overclaims/precision/recall/pair_attr | FAIL both versions; undefined retained; cell-specific quantities [NP] | `rq.RQ5`; `tables.T8[*]`; `tables.T8_v0[*]` |
| RQ6; k/n/class/interval | descriptive; legitimate P2/P3 under I2 [NP] | `tables.RQ6[*].supported_on_legitimate` |
| T2–T9; FIG_FRONTIER; FIG_RISK | Populated source index; selected numerical summaries; rendering pending | `tables.*`; `figures.frontier_heat_map`; `figures.risk_coverage` |
| R2_RUN_HASHES | Input and seed-list SHA-256 values | `inputs`; `tables.T1.seed_disjointness.seed_list_sha256` |
| EXP003_RESULTS | Removed; not completed | User instruction, D-047a |

Unresolved numeric placeholders: none. Inactive templates were not imputed. Existing DEV comparisons remain [DEV]. Six OWNER slots remain. Positive-control recovery remains unverified.
