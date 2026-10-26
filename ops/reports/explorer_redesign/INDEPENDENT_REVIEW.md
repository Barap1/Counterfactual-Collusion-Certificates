# Independent explorer review

Task: EXPLORER-REDESIGN / independent read-only scientific and software review.

Reviewer scope: `demo/explorer/app.js`, `index.html`, `style.css`, `theme.js`, `build_research_context.py`, generated context, frozen twin/study/case data, and `docs/RESULTS.md`. Implementation and scientific records were not edited. This report is the reviewer's only written artifact. No network, experiments, model inference, secrets, or Git mutations were used.

Status: final static/data spot review passed; all four original findings are resolved in the inspected implementation. Lead browser and screenshot verification is recorded separately. The initial findings below are retained as review history; their resolution is recorded after validation. Line references can move after fixes.

## Findings

1. **High — cost-probe prose contradicts the stored CCC-L v0 verdict.** `app.js:728` says “CCC-L v0 does not attribute either at I4.” In `demo/data/twins.json`, the prohibited P2 member's `by_set.I4.verdicts.ccc_l` is `status=attributed`, `rung=L3`, `M=true`; the permitted member is insufficient/L2 with `M=null`. Correct the prose to distinguish attribution of the prohibited member from abstention on the permitted one. The Bayes-given-S reference distinguishes both labels. The existing full twin table already reflects the stored verdict correctly, so the new narrative currently contradicts its own inspectable evidence.

2. **Medium — RQ3 is given the wrong estimand label.** `app.js:646` calls RQ3 “Attribution coverage.” Frozen `RESULTS.json.tables.T4.estimand` is the share of forbidden worlds with oracle outsider-loss harm above the stated threshold; the harm definition uses joint-knockout minus factual outsider reward. The 61/200 = .305 figure is a generated-population harm-prevalence statistic, not auditor attribution coverage. Relabel it and state what the numerator measures beside the value.

3. **Medium — case figure labels still shrink below readable size on phones.** `intervalPlot` (`app.js:157–206`) and `barPlot` (`app.js:422–433`) use a 720-unit viewBox with 11–15-unit text. They are inserted directly into fluid-width containers. The CSS minimum-width/scroll treatment applies to study plots, not these case plots. At a 320px viewport, 11-unit labels would render at about 4px. Use a focusable horizontal figure viewport with a readable minimum width, or a mobile-specific plotting layout. This is a static sizing finding; screenshots were not independently captured here.

4. **Medium — selecting twin evidence levels jumps away from the controls.** Twin pair/evidence buttons change the hash (`app.js:875,882`); `route()` scrolls every non-case view to the top (`app.js:972`), and the hashchange listener focuses `main`. This interrupts repeated evidence-level exploration and keyboard operation. Preserve scroll and restore the selected control's focus for updates within the twin view, while retaining hash deep links.

## Independent validation

- `python3 -m unittest tests.test_demo_data -v`: **8 tests passed**, 1.862 seconds. Includes exact primary statistics, case certificates, fixture distinctions, archive hashes, message preservation, numerical reductions, and manifest completeness.
- `node --check demo/explorer/app.js`: passed.
- `node --check demo/explorer/theme.js`: passed.
- Python read-only comparison of the generated `research-context.js` payload against `build_research_context.build()`: exact match. Utility v1 2/84, v0 5/84; each has 73 undefined gaps.
- SHA-256 comparison against `frozen-before.json`: all **70** original pack/bundle files unchanged.
- All 21 compact-case and full-text-overlay links resolve to existing local files.
- H02_B1 maps to world 551864267, the largest absolute matched-world difference; the selection explanation is accurate.
- Eight pair values, whole-pair confidence interval, mean, and exact p-value are sourced from the frozen study. No null-equivalence claim was found.
- All stored equal-view twin cells have equal verdict objects. P2/I2, P2/I4, and P3/I5 remain available through their hash routes in the implementation.

## Limits and follow-up

This is independent static/data validation, not a browser, deployment, contrast, or screenshot sign-off. The lead must run the requested responsive/theme/offline/public browser checks and resolve the findings before the final commit. The existing README still describes the removed four-step tour/sidebar at review time and should be updated. No additional concern was found in the evidence separation, registered sensitivity wording, missingness counts, programmed-label distinction, or retained aggregate failure disclosures.

## Fix verification

A second independent read of the updated implementation verified:

- **Finding 1 resolved:** the P2 disclosure now says CCC-L v0 attributes the prohibited twin and abstains on the permitted twin at I4, while Bayes-given-S distinguishes both labels. This agrees with the frozen member verdicts.
- **Finding 2 resolved:** RQ3 is labeled harm prevalence among forbidden policies. Its paragraph explains that 61/200 measures oracle outsider harm above the 2.5 margin, retaining the unmet <0.25 criterion.
- **Finding 3 structurally mitigated:** case interval and outcome-bar figures now use `chartScroll`, a focusable, labeled horizontal viewport. The shared CSS minimum width is 580px, however; an 11-unit label in a 720-unit case viewBox still becomes approximately 8.9px at that minimum. Increase the case figure minimum width or source-label size if screenshots show small text. The matched-pair plot's 600px minimum similarly scales 13-unit text in an 820-unit viewBox to about 9.5px. Final visual readability is not independently established by this static review.
- **Finding 4 resolved statically:** pair and information buttons now call `updateTwin`; it changes the deep-link hash via `history.replaceState`, rerenders, restores scrollY, and focuses the selected button with `preventScroll`. It does not trigger the route-level scroll/focus reset. Browser execution remains a lead check.

Re-run checks after the fixes: `node --check demo/explorer/app.js` passed; SHA-256 comparison still finds all 70 original evidence files unchanged. No remaining scientific finding was identified. No implementation file was edited by the reviewer.

## Final pre-commit spot review

Reviewed the final responsive matched-pair layout, case chart sizing, condensed twin-scope disclosure, `prepare_pages.py`, and `.github/workflows/deploy-demo.yml`. No new scientific, JavaScript, or deployment blocker was found. The matched-pair plot now lays out at the available 280–820-unit width with 13-unit pair labels, while case figures retain a 720px minimum and larger source labels. This resolves the remaining static chart-sizing concern. Aggregate outcomes, post-hoc deterministic scope, and the noisy cross-platform limitation remain inspectable in the condensed scope disclosure.

The Pages staging script copies the public explorer asset tree and frozen data pack, retains relative `demo/explorer/` and `demo/data/` paths, excludes QA directories and Python source, and preserves root hash routes through an external local redirect script. The deployment job verifies provenance/context and deterministic rebundling before staging. No secret or environment-file path was introduced in the staging logic.

All four original findings are resolved. Independent sign-off is limited to the inspected code/data; the lead separately owns the reported responsive browser matrix, screenshot inspection, offline/runtime checks, public deployment verification, commit, and push. No further test expansion was performed for this spot review.
