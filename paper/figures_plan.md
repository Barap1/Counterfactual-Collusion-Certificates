# CCC paper: figures and tables plan (PUB-002)

Status 2026-10-23. All numbers are placeholders until the owning task delivers frozen output. Each item must cite an `ops/CLAIMS.md` ID, table field and analysis version before export.

| ID | Item | Content | Source data path | Owning task | Status |
|---|---|---|---|---|---|
| Fig 1 | Arm schematic and fork | Timeline: shared checkpoint at t*, arms F/S/K/N (C optional), mask by event id with preserved indices, fresh continuations, verdict states | `docs/research/sci002/protocol.md` sections 3-4 (diagram only, no data) | VIS-001 | not started |
| Fig 2 | Flagship contrast: same knockout magnitude, different verdicts (A1 vs A2) | Per-instance tau_O vs verdict, by family | [RESULT-PENDING] STAT-002 fixture table; interim: `docs/gate_a/gate_a_results.json` (dev only) | VIS-001 / STAT-002 | blocked on Gate A diagnosis |
| Tab 1 | Gate A integrity table | Check, pass/total (F=S, K scope, isolation, A6 invalid detection, fault activation) | `docs/gate_a/GATE_A_REPORT.md`, `docs/gate_a/gate_a_results.json`; diagnosis in `docs/gate_a/diag/` (uncommitted) | ENG-004 / GA-DIAG | integrity rows final; A6/A5 rows provisional |
| Tab 2 | CCC vs baselines confusion by fixture family | TP/FN/FP/TN for CCC, B0, B1, B2, B2+, B3a, B3b, B4-rule; abstain/invalid column; per family A1-A6, strata by oracle path activity | `docs/gate_a/gate_a_results.json` (dev); held-out: STAT-002 output [RESULT-PENDING] | STAT-002 | dev numbers provisional; held-out pending |
| Tab 3 | CCC sensitivity loss vs B2, cell by cell | B2 flags without CCC support per stratum | `docs/gate_a/GATE_A_REPORT.md` (appendix table) | STAT-002 | provisional |
| Tab 4 | Replay validity failure taxonomy | Rate of leakage, protocol corruption, non-regenerated continuations in naive knockout vs gated | [RESULT-PENDING] EXP-001/EXP-002 branch records `runs/exp001/` | EXP-001 / STAT-002 | pending |
| Tab 5 | Real-trajectory case study status counts | eligible / ineligible / invalid / inconclusive / supported / not supported; abstention reasons; worlds vs branches vs failures separate | [RESULT-PENDING] STAT-002 T2 | STAT-002 | pending |
| Tab 6 | Dev-pilot validity and throughput | Calls/hour, tool-error rate, missingness per arm, overflow, reload events | `ops/reports/INF-001.md` (benchmark, verified); EXP-001 run logs `runs/exp001/` [RESULT-PENDING] | EXP-001 / INF-001 | benchmark done; pilot pending |
| Tab 7 | Robustness | Sensitivity to m_O and delta_W; interval method check | [RESULT-PENDING] STAT-002 | STAT-002 | pending |
| Tab 8 (appendix) | Baseline definitions and fairness rules | B0-B5 table | `docs/research/sci002/baselines.md` | PUB-002 / SCI-002 | draftable now |
| Tab 9 (appendix) | Fixture families A1-A6 | Mechanism, truth label, predicted verdicts | `docs/research/sci002/fixture_spec.md` | FIX-001 | draftable now |

Constraints: main text allows 4-6 pages, so keep Fig 1, Fig 2, Tab 1, Tab 2, Tab 5 in the body and move the rest to the appendix. Dev-only numbers must carry a "development, not held-out" caption. No figure may imply a result not yet frozen.
