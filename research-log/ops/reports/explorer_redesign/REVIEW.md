# CCC Evidence Explorer redesign — implementation and verification

Task: EXPLORER-REDESIGN. Scope authorized by the owner: `demo/explorer/`, supporting tests, this evidence report, and GitHub Pages deployment. Task registry inspected; no live agents or conflicting explorer lease existed. Existing edits to `ops/tasks.json`, `ops/reports/graphics_redesign/`, and `paper/graphics_redesign/` were preserved and excluded from staging. Network use was limited to the requested references and GitHub delivery; no inference, experiments, new outputs, or spend.

## Result

The dashboard has become an editorial research companion: Old Standard TT, warm paper and forest accents, thin rules, a short opening, an interactive P2 counterexample, a single evidence progression, restrained findings, and a concrete research continuation. Light is the default; dark preference persists locally. All animation respects reduced motion; entry effects never gate visibility.

The counterexample reads the authentic P2 twin records. Both initial worlds show outsider reward 14→19 under message removal, coalition 24→19, and welfare 76→76. After lowering outsider costs by 10, the permitted factual probe changes to base (outsider29, coalition19, welfare96), while the prohibited factual probe retains route (outsider14, coalition24, welfare76). Both probe knockouts give outsider29. Labels are benchmark-supplied, and the text distinguishes the recorded exposure certificate, CCC-L v0 attribution/abstention, and Bayes reference.

Dedicated Study, Twin Worlds, Case Inspector, and Concepts & Sources routes remain. The inspector uses a compact selector, transcripts and gate traces use disclosures, source hashes remain accessible, and raw JSON/full-text overlays have direct links. Development fixtures remain explicitly separate from held-out cases. A compact source-derived context bundle retains all aggregate benchmark outcomes and utility counts without changing the original pack.

The study plot retains every pair, the mean, whole-pair interval, zero reference, exact sign-flip p, and numeric captions. It lays out at the actual mobile reading width. Case plots preserve label size in labeled keyboard-scrollable viewports.

## Reference inspection

- Live `https://apartresearch.com/`, inspected through Chrome: actual CSS `--color-paper #f8f5f1`, `--color-ink #193025`, `--color-forest #194b37`, `--color-line #e3dfda`; the site uses Instrument Sans and generous spacing. CCC borrows palette restraint, does not copy the logo, and explicitly states independence.
- The supplied Google Doc was read through the Drive connector for named typography. Its title style names Old Standard TT. No live document was edited.
- The repository's Old Standard fonts are embedded unmodified under SIL OFL1.1; license and SHA-256 source records are in `demo/explorer/fonts/`. System sans-serif is used for controls/metadata.
- Firecrawl connector was unavailable; live Chrome and the official public page were used instead.

## Validation executed

- `python3 -m unittest tests.test_demo_data tests.test_explorer_context -v`: 10 passed. Exact statistics, source certificates, fixtures, archive hashes, generated context, and safe Pages staging.
- `python3 -m unittest discover -s review/reproduce_headline/tests -v`: 11 passed. Independent arithmetic retained.
- `python3 scripts/reproduce_headline.py`: mean1.354325711018899, exact sign-flip18/256=.0703125, matches frozen arithmetic within floating-point precision; directional hypothesis not established.
- `python3 scripts/check_artifact.py`: 15 reading-path pages,114 local links/anchors,4 SVG variants passed.
- `python3 demo/explorer/bundle_data.py`: original JS bundle reproduced byte-for-byte. SHA-256 comparison: all70 original pack/bundle files unchanged.
- Imported `demo/build_data.py`, redirected only its output to a fresh `/private/tmp/ccc-explorer-reproduction-*` directory, and ran `build()`: all46 non-manifest pack files reproduced byte-for-byte; manifest matches except current generation HEAD. Original records/pack were never overwritten by this check.
- `node --check` on app, theme, and both QA runners; Python compilation of the two new build/staging scripts; `git diff --check`: passed.
- `qa_browser.cjs` against loopback preview: 48 route/width/theme combinations plus functional suite passed, 49 full-page screenshots and48 viewport screenshots. Widths1440/768/390/320, light/dark, persisted preference, reduced motion,8 pair marks,36 twin states,21 cases, selector, keyboard disclosure/section/skip links, invalid-case recovery, and probe/reset tested. No page errors, HTTP asset failures, or external content requests. Text-token contrast on the actual paper background: minimum5.53:1 light,7.42:1 dark.
- `qa_pages.cjs` against a separately served exact staged artifact: root hash links redirect correctly, all six source/license downloads return200, raw case JSON agrees,21 selectors exist, P3/I5 authorization works, probe values agree, and390px dark study renders without overflow or errors.
- Actual viewport and full-page screenshots inspected. Selected evidence is in `screenshots/`; full generated screenshot sets remain local under ignored QA image paths. The final case charts use720px minimum width with13–14px source labels; the responsive study figure preserves13px labels without horizontal scrolling on phones.
- Separate read-only reviewer identified two scientific wording errors and two UI issues. All were corrected. Independent report is retained. No replacement certificates or scientific data were written.

## Offline, privacy, and deployment limits

Static offline dependency audit passes: every stylesheet/script/icon is local, fonts are embedded, all21 dynamic case files exist, no runtime content API is used. HTTP runtime tests block unexpected external requests. Direct `file://` browser navigation was rejected by the browser tool's URL policy; no alternative browser surface or workaround was used. Actual double-click offline browser execution is therefore not claimed as verified.

The public-data scan read only already-public frozen JSON and JS, checked four restricted credential patterns, and found none. It did not inspect secret files and does not establish exhaustive privacy or licensing clearance. Existing upstream scenario/trace redistribution rights remain unresolved in repository notices; no new trace content was published.

Remote `main` advanced during work by one deployment-workflow commit (`ae564dde`). Local main was fast-forwarded without altering existing edits. The redesign updates that existing workflow rather than adding a competing deployment. Only public demo assets and frozen JSON are staged. Existing root hash links are preserved by an external-script redirect to `demo/explorer/`. GitHub Pages is configured for Actions, repository write permission is available, and main is not branch-protected. Push/deployment verification is performed after the single implementation commit; the resulting receipt is saved locally to ignored `delivery.json` and `public-pages/` so it does not require a second commit.
