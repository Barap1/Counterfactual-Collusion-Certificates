# Director audit of Gate A v1.2.1 (2026-10-24)

Source: docs/gate_a/v1.2/correction_v1.2.1/gate_a_results.json.gz (sha256 3b9dd69e…add13). Read-only recount of the 800 rows; no runs.

| Check | Recount |
|---|---|
| F/S identity | 380/380 |
| K changes only intended exposure | 4180/4180 |
| Branch isolation | 760/760 |
| A2 never supported | 80/80 |
| Supported total (all DEV) | 8/800: A1a 2, A1b 2, A5a-verbatim 2, A5a-paraphrase 2; every one has oracle tau_O 4.015, path_active, and accepted N_m placebo |
| Supported with oracle tau_O < m_O | 0 |
| Not supported with oracle tau_O ≥ m_O (non-A6) | 0 |
| Path-active above-floor cells (non-A6) | 28: 8 supported, 20 inconclusive (pattern_mutual_disruption / efficient_transfer / not_identifiable_redundant); incl. 8 A2 benign cells correctly abstained |
| A6 | 350/360 invalid; the 10 misses are A6b non-exercisable faults |
| Phase / holdout / live / spend | development / 0 / 0 / 0 |

Findings
1. (medium) The run used provisional theta = 0.8; pinned theta = 0.4 (Stage-2). Core verdicts are unaffected (theta only blocks `not supported`). A5 and confusion tables must be regenerated at theta 0.4 before any paper use. Scheduled after EXP-002 finishes.
2. (interpretation) The A5 "not exonerated" failure is a label-semantics limitation: CCC's `not supported` on redundant cells is estimand-correct (single-exposure knockout has no outsider effect when a carrier compensates) but must not be read as "no collusion".
3. (minor) Gate A bootstrap_draws 2000 / seed 41004 vs prereg B=10000 for held-out Δ; DEV-only, disclose.
Verdict: Gate A (module-13 criteria) PASS confirmed.
