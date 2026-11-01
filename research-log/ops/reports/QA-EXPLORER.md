# QA-EXPLORER handoff
Task: independent number-trace, claims and visual QA of demo/explorer.
Status: complete. No demo file edited; no git, network, spend or sub-agents.
Artifacts: docs/enh/qa/QA_EXPLORER.md (findings, trace table, contrast table); screenshots in demo/explorer/qa_independent/ (22 PNGs: 1440 and 390 px, light and dark; start, study, H01_B1, H02_B1, GateA_A1, twins P2 I4, about).
Validation: ~330 displayed values traced to v3 certificates/continuations/world_effects/sensitivity, v2 effects_study (identical), rev001_repro, Gate A v1.2.2 rows, and dev_run partitions/records (views re-hashed). 0 mismatches. Outsider mean, coalition mean and W recomputed from raw rewards for 6 continuations plus arm means: exact. Frozen primary reads 1.354 / [-0.020, 2.834] / p 0.0703 / not supported; 0.727 labelled registered sensitivity. MANIFEST hashes: 0 diffs.
Findings: P1 (3): (1) ladder shows "highest supported" at L1 for not_supported certificates (H01_B1, H02_B2; H02_B2 triggered by a negative tau_W), a UI heuristic not a certificate rung; (2) "harm ... ruled out" wording from one-sided case-conditional bounds; (3) twin page clips the continuations Action column at 390 px. P2 (6): twin page title says "same verdict" when verdicts differ; DEV-label caveat near twin verdicts; stale post-hoc note in study.json; "interval width" vs one-sided bounds; .xtag contrast 3.2:1; clipped source text "sche". Exact fixes in the report.
Limitations: dark mode forced via a temporary CSS copy (deleted); raw validity counts not re-derived from the archive; no screen reader or hover testing; headless 390 px via iframe.
Budget: $0, Sonnet.
Next: owner/builder applies P1 text and CSS fixes, rebuilds bundle, rerun QA.
