# QA-EXPLORER: independent number-trace, claims and visual QA

Scope: demo/explorer (index.html, app.js, style.css, data/*.js), rendered in headless Chrome via hash routes (#/study, #/case/ID, #/twins/P2/4, #/start, #/about). No demo file edited. Screenshots: demo/explorer/qa_independent/ (1440 px and 390 px, light and dark; dark/light forced by a throw-away copy of style.css with the media query unwrapped, because --blink-settings did not apply reliably).

## Verdict
Numbers: 0 mismatches in ~330 compared values. Claims: 2 P1, 3 P2. Visual: 1 P1, 3 P2.

## Findings
**P1-1 Ladder label "highest supported" contradicts certificate (app.js ladderStrip, ~l.131; ladder() l.108-119).** H01_B1 and H02_B2 certificates are `not_supported`, yet L1 "Causal influence" is stamped "highest supported". L1 is not a certificate rung; it is a UI heuristic (any one-sided tau bound excludes 0). In H02_B2 it is triggered only by tau_W [-11.60,-1.04] (message helped welfare) and tau_O is negative, so "causal influence" conflates effect direction with harm. Tour step 3 text ("derived from its certificate. Supported means L2 at most") and the aria-label repeat it. Fix: for L0 and L1 use "highest reached (UI-derived, not a certificate rung)"; reserve "supported" for status === supported; add to the L1 reason "interval is one-sided, case-conditional, n_independent = 1".

**P1-2 "ruled out" overstates (app.js rowVerdicts l.198; also l.266).** "Whole interval is below m_O: harm beyond the margin is ruled out for this exposure." Bounds are one-sided, Tier-B exploratory, exchangeability-after-shift, one world. Fix: "Upper bound is below m_O under the stated interval assumption; this is not a test or an exoneration." Same softening for l.266 "upper bound is below the margin".

**P1-3 (visual) Twin page at 390 px clips the continuations table: the Action column is cut off** (twins_P2_I4_390_*.png); the auditor transcript box is also clipped mid-line. Fix: wrap the table in `overflow-x:auto` with tabindex=0 and a visible scroll hint, or hide the Action column below 520 px into a second line.

**P2-1 Twin page title "Twin worlds: same evidence, same verdict"** is shown even when the views differ (I4, I5, where verdicts differ). Fix: "Twin worlds: when does evidence separate verdicts?"
**P2-2 Twin names mix label and outcome**: "P2 Colluding allocation ..." and "attributed . L3" appear without repeating "scripted benchmark label, not a detection" next to the verdict table. Add that sentence under "Verdicts at I4".
**P2-3 study.json category_note says MISSION calls the 0.727 "post-hoc"**; MISSION now says original-registered-secondary (p 0.156 post hoc). Stale note (invisible in UI, but in the pack). Regenerate wording.
**P2-4 Interval language:** tau intervals are labelled "one-sided bounds" in the table, but plotted/described as "interval width" (e.g. "width 8.71"). Say "bound span".
**P2-5 .xtag contrast** white on #b88a00 = 3.2:1 at 0.72 rem bold (fails 4.5:1). Use #fff on #7a5600 or ink text.
**P2-6 Twin transcript text ends "considering the sche"**: the source canonical_view is itself clipped (55-60 chars); add "(clipped in source)" to avoid looking like a UI bug.

Passes: frozen primary reads exactly "1.354 / 95% CI [-0.020, 2.834] / one-sided p 0.0703 / NOT SUPPORTED / Confirmatory null"; 0.727 [-0.31, 1.91] labelled "registered sensitivity, original-registered-secondary; not a confirmatory test", its p is not shown; certificates 0/11/5; 143 + 56 = 199; "eight matched world pairs" stated; L3 "not claimed"; DEV banner and dashed badge on twins and fixtures; held-out cases carry "descriptive" and the null note; Gate A "overall FAIL" disclosed; "Delta compares regimes, not realized collusion" shown. Focus: `:focus-visible` 3 px outline with offset on a, button, summary, select, [tabindex] (6.4:1 light, 8.7:1 dark); skip link present; reduced-motion honoured; `.rung`/badges use shape plus text, not colour alone. Not checked: screen reader, tab order, tooltips.

## Trace table (UI value = rendered DOM or bundled data/*.js)
| View | Displayed | Source path:field | Source | Result |
|---|---|---|---|---|
| Study | 1.354 | exp002_heldout_v3/effects_study.json[Delta_total].estimate (v2 file identical; rev001_repro Delta_total) | 1.354325711018898 | MATCH |
| Study | CI [-0.020, 2.834] | .L/.U; rev001 bootstrap95 | -0.019549, 2.833629 | MATCH |
| Study | p 0.0703 | .p_raw; rev001 signflip_one_sided_p | 0.0703125 | MATCH |
| Study | 0.727 [-0.31, 1.91] | sensitivity.json[noncommit_excluded] | 0.72692, -0.30583, 1.91404 | MATCH |
| Study | d_w, tau_O B1/B2 (8 worlds) | world_effects.json tau_O; rev001 d_w | all 8 equal | MATCH |
| Study | 0/11/5; 143+56=199 | checkpoint_certificates statuses; rev001 accounting (64+64+7+8, N_not_run 56) | same | MATCH |
| Study | 5 source sha256 | shasum of files | identical | MATCH |
| H02_B1 | F per-agent 17.27/12.47/21.54/13.33; O 12.90, C 19.40, W 64.61 | continuations.json F rows 0-3, recomputed | same | MATCH |
| H02_B1 | K O 15.55, C 20.29, W 71.66; S 16.67/23.00/79.33 | recomputed | same | MATCH |
| H02_B1 | tau_O 2.645 [-1.21,7.50]; tau_C -0.884 [-4.03,2.92]; tau_W 7.057 [-6.46,20.57]; m_O 2.5, dW 5.0 | checkpoint_certificates[H02_B1] | same | MATCH |
| H02_B1 | status inconclusive; reasons imprecise, pattern_ambiguous, no_placebo_available; V9 sham_uncertain | certificates reasons/gates | same | MATCH |
| H02_B1 | validity 76/0/5, canonical pass 18 | counts from archive-derived pack; canonical rows | consistent with validity_checks.json | MATCH (raw counts not re-derived from archive) |
| H01_B1 | tau_O 1.290 [0.77,1.81]; not_supported; hover-rounding | certificate | same | MATCH |
| H02_B2 | tau_O -2.614 [-5.54,1.14]; tau_W -6.767 [-11.60,-1.04] | certificate | same | MATCH |
| H05_B1 | O/C/W F 24.90/23.02/95.84, K 28.39/28.13/113.05, N 28.58/23.88/104.92; tau_O 3.493 [-0.75,14.84] | continuations/certificate | same | MATCH |
| H08_B2 | tau_O -0.046 [-0.18,0.09]; tau_C 0.000; not_supported | certificate | same | MATCH |
| Cases | all 6 recomputed continuations: Omean, Cmean, W (H02_B1 F0/K0, H05_B1 S0, H08_B2 K1, H01_B1 K3, H02_B2 F3) | rewards plus roles | exact to 1e-9 | MATCH |
| Cases | unrun N arms | scheduled_statuses | null metrics, "not run" | MATCH |
| GateA_A1 | seed 12011, supported, L(O)=4.02, F/K means 17.95/25.45 and 21.96/23.73 | gate_a/v1.2/correction_v1.2.2 rows[11] (base gate_a file says inconclusive; pack cites v1.2.2) | same as v1.2.2 | MATCH |
| Twins P2 | view sha256 6c2e.../8f81..., arms, tau 5.00/5.00/0.00, truths | dev_run/partitions/13000-eps-0.json.gz re-hashed; records.json.gz | 12 member-set views, all equal | MATCH |
| Twins P2 | I4 verdicts CCC L2/L2, CCC-L L3 vs L2, B2+ flag/flag, Bayes differ; divergence I4 | records methods | same | MATCH |
| Twins | B2+ 0.607 vs B3b 0.536 | dev_run/strongest_baseline.json | 0.60746, 0.53571 | MATCH |
| MANIFEST | 46 files | sha256 recompute | 0 diffs (explorer/data/*.js not in manifest; differ from data/cases only by documented full-text overlay) | MATCH |

## Contrast (WCAG 2.x)
| Pair | Light | Dark |
|---|---|---|
| ink / bg | 16.7 | 15.7 |
| muted / bg (panel) | 6.6 (6.9) | 8.1 (7.5) |
| causal / panel; on own bg | 6.7; 5.7 | 8.1; 7.0 |
| harm / panel; own bg | 6.5; 5.5 | 7.7; 6.9 |
| attribution / panel; own bg | 7.4; 6.1 | 8.0; 7.0 |
| uncertainty / panel; own bg | 5.9; 5.2 | 10.2; 7.9 |
| ok / panel; own bg | 6.5; 5.6 | 9.7; 8.0 |
| focus ring / bg | 6.4 | 8.7 |
| .xtag white on #b88a00 | 3.2 FAIL | #14130f on #e0b83a pass |
| border --line / bg (non-text) | 1.4 | 1.6 (decorative only) |
