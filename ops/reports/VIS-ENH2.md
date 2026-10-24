# VIS-ENH2 handoff
**Task:** update figures/enh/make_enh_figures.py to the updated benchmark schema (r2-results-1).
**Status:** done; DEV re-run into figures/enh/dev/ (SVG, PDF, sidecar JSON per figure, figures_manifest.json), all renders inspected.
**Changes:**
1. Strongest baseline is read from RESULTS.json `dev_derived.strongest_baseline` (fallback `strongest_baseline.json`); missing gives SystemExit. My min-risk rule is removed. DEV: B2+. fig_overattribution also aborts if T5/T5b method differs from it.
2. fig_overattribution: per class (P2, P3, P6, benign cooperation) x eps from T5/T5b, I1, CP95 over units, 0.5 line, 0.05 line (P6/benign), RQ4/RQ4b class pass flags, CCC v1.2.2 L2 rate as separate red diamond. No pooling.
3. fig_twins: uses `twin_exhibit` (checks P2, eps 0, lowest seed = rule seed, else abort); hatched path removed; also shows PF/PK probe bars and I4 action before/after.
4. fig_risk, fig_risk_E, fig_frontier add CCC-L v1 (labelled "DEV-informed method version") beside v0.
5. fig_frontier Bayes number = T3 pair accuracy (RQ2); P5 has no T3 row, shown n/a. Other methods remain share-of-units-with-different-output from separators.json (T3 has no per-method pair accuracy), so the cell mixes two quantities; the legend says which.
6. fig_prevalence now uses RESULTS RQ3/T4 strata (eps 0: 12/50; eps 0.1: 5/50), both with CP95 and the 25% line.
**Validation:** rendered with headless Chrome. Script needs RESULTS.json plus frontiers, separators, scores, population in the run dir; set `--label PROSPECTIVE` on `docs/enh/r2/run/` with the same schema. Prospective run not tested (none exists).
**Limitations:** CCC v1.2.2 has no M output (absent from fig_risk, present in fig_risk_E). In risk panels v1/v0 curves are often hidden under coincident curves (noted on figure). Twin-exhibit CCC status was recorded at I5.
**Budget:** $0, Claude Sonnet 5.5; no git, no network.
