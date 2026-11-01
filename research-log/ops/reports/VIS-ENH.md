# VIS-ENH handoff
**Task:** figure script for CCC paper v2 benchmark figures; DEV run rendered.
**Status:** done for DEV; fig_twins degraded (needs RESULTS.json field).
**Artifacts:** `figures/enh/make_enh_figures.py` (`--run DIR --out DIR --label {DEV|PROSPECTIVE}`); `figures/enh/dev/` has SVG + PDF (headless Chrome, vector) + sidecar JSON (all plotted numbers, source sha256, run label, caption) for fig_ladder, fig_twins, fig_frontier, fig_risk (axis M), fig_risk_E (axis E, supplementary), fig_overattribution, fig_prevalence, plus figures_manifest.json. DEV stamp "DEVELOPMENT DATA" top-right on every figure.
**Validation:** each figure rendered to PNG with headless Chrome and inspected; fixed row overlap, clipping, legend wrap, z-order. fig_twins layout tested with a synthetic RESULTS.json in /tmp (not shipped). Reads only frontiers/separators/scores/population (+symmetry, RESULTS if present). CP intervals come from scores.json (unit_cp95); prevalence per-case CP is computed in-script, labelled descriptive.
**Limitations / missing fields:**
- fig_twins: outcome bars (F/K/S/N), CCC v1.2.2 status text and I4 probe values are not in the allowed outputs. Expected: `RESULTS.json["twin_exhibit"] = {seed, members:{A|B:{outcomes:{F,K,S,N}, ccc_status, i4_probe:{before,after,metric,reading}}}}`. Pair rule: P2, eps 0, lowest seed (13000 in DEV). Without it, the bars are hatched and the missing fields are named on the figure and in the sidecar. Enumerated I0-I5 distinctness and "CCC output identical" come from frontiers/separators.
- CCC v1.2.2 emits no M or H output, so fig_risk (M) omits it (noted on figure); it appears in fig_risk_E. Over-attribution shows it on axis E as L2.
- Strongest baseline = lowest mean min-risk (c=0.5) over eps and sets on the plotted axis (B2 in DEV); rule recorded in sidecar.
- fig_frontier overlay is the share of seed units where outputs differ between twins, not Bayes accuracy (per-class accuracy is not in scores.json).
- No per-class breakdown of over-attribution (P2/P3/P6/benign pooled, as in scores.json).
**Budget:** $0; Claude Sonnet 5.5; no network, no git.
**Next:** director/RESULTS worker adds twin_exhibit; rerun with `--label PROSPECTIVE` after the R2 freeze.
