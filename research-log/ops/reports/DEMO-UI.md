# DEMO-UI handoff

**Task:** Build the offline CCC Evidence Explorer in demo/explorer/.
**Status:** Done, verified in headless Chrome (desktop 1440 and 390 px, dark mode).
**Artifacts:** demo/explorer/{index.html, app.js, style.css, bundle_data.py, README.md, data/*.js (generated), qa/*.png}; this file.
**Validation:**
- Renders from file://, no network requests, vanilla JS.
- 21 cases load lazily via script tags.
- Rows-vs-certificate reconciliation (tau_O/C/W) shows "reconciles" on checked cases (H02_B1, GateA_A1).
- Screenshots reviewed: start, tour step 2, H02_B1, GateA_A1 (desktop); start, H02_B1, study, A6 (390 px). A table-body bug and a sidebar label wrap were found and fixed.
- Covers case select with provenance badges, interaction with exposure highlight, F/K/S/N compare with explicit "not run: no eligible placebo", interval plot vs m_O and delta_W, validity counts, gate trace, raw evidence with sha256 and MANIFEST link, study panel with strip plot, concept chips, ladder strip, tour. Twin worlds is hidden and renders the JSON as received only if data/twins.js exists.
**Limitations:**
- Twins schema is TBD, so rendering is generic.
- Validity meanings for V-echo, V-model, V6, V1_static are not documented in the pack and say so.
- Ladder L1 rule is mine: any tau interval excluding 0. It is stated in the UI.
- No screen reader or keyboard test beyond semantic markup, focus styles and skip link. Contrast was not audited with a tool.
- The sidebar claims nothing beyond pack fields.
- A6 and the other 390 px views were only partly inspected.
**Budget:** $0, no model calls, no network.
**Next:** Owner review of the tour wording. Rebuild after twins.json lands. Optional axe or keyboard pass.
