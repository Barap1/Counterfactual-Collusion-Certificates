# AMD-IMP-6a report: constructed controls (C4)

- Instances: 30 DEV (P 8, P-IB 2, N1 8, N2 8, N3 4). Predictions: supported 6, inconclusive 8, not supported 16.
- Oracle verifier: 30/30 K effects match the derivation, 30/30 N_v1.1 effects match, 18/18 N_m zero effects, 12/12 absent-placebo refusals.
- Derivation vs oracle: no mismatches.
- Exclusion helper: `assert_not_constructed(instances)` added; tested.
- Offline runner: 70 tests OK.
- Files touched: ccc/fixtures/constructed.py, tests/fixtures/test_constructed.py, docs/research/sci002/constructed_controls.md, docs/research/sci002/constructed_controls.json, ops/reports/AMD-IMP-B.md.
- No CCC, decision layer or baseline run. No commits.
