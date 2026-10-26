# CCC Evidence Explorer

An editorial research companion to *When Cooperation Looks Like Collusion: The Limits of Counterfactual Auditing in Multi-Agent AI*.

Open `index.html` from a downloaded checkout, keeping adjacent assets and `demo/data/` together. The site uses vanilla JavaScript, embedded local fonts, relative assets, and hash routes; it needs no server, inference, tracking, API key, or external font service. Light is the default; theme preference is stored locally. Reduced motion disables animation and smooth scrolling.

## Reading and inspection

- **Start** (`#/start`): the P2 allocation counterexample, a cost-probe transition, evidence progression, findings, and research continuation.
- **Study** (`#/study`): all eight independent matched-pair differences, mean, whole-pair uncertainty interval, exact sign-flip result, registered sensitivity, and sources.
- **Twin worlds** (`#/twins/P2/2`, `#/twins/P2/4`, `#/twins/P3/5`): six pair families and cumulative information sets I0–I5, including controls, cost probes, authorization, exact recorded verdicts, and hashes.
- **Case inspector** (`#/case/H02_B1`): a compact selector for 16 held-out checkpoints and 5 development fixtures; original messages, F/K/S/N comparisons, uncertainty, validity, certificates, transcripts, and raw evidence. H02_B1 illustrates the largest absolute matched-world contrast; it is not a selected positive finding.
- **Concepts & sources** (`#/about`): effect definitions, provenance categories, raw downloads, limitations, and redistribution notices.

The initial labels in the counterexample are benchmark-supplied programmed labels. The deterministic scope is post hoc; the noisy condition has unresolved cross-platform discrepancies. The four unmet aggregate benchmark criteria, 2/84 v1 utility result (5/84 v0), and inconclusive real-agent direction remain disclosed. Constructed evidence is never presented as real-agent attribution or deployment accuracy.

## Evidence architecture

`demo/data/` remains the frozen source of truth. `bundle_data.py` wraps it into `data/*.js` (`window.CCC_DATA`), loading cases on demand and overlaying untruncated text from `demo/data/full/`. Never edit the generated bundle by hand. This redesign leaves all original pack and bundle bytes unchanged.

`build_research_context.py` creates the small additional `research-context.js` from frozen `docs/enh/r2/run_par/RESULTS.json`. It copies aggregate decisions and computes the displayed utility counts from stored criterion rows, with a source hash. It does not modify research records.

L0/L1 case ladder displays are UI-derived heuristics; only recorded supported certificates reach L2. L3 is never claimed for held-out cases. The case table reconciles stored replicate arithmetic against the authoritative certificate.

Rebuild the original pack only when intentionally regenerating artifacts from frozen source records:

```sh
python3 -I demo/build_data.py
python3 -I demo/explorer/bundle_data.py
python3 -I demo/explorer/build_research_context.py
```

Twin-source changes require the existing `demo/build_twins.py` step first. Pack generation records the current generation HEAD and hashes the actual inputs. Reproduction QA writes to a temporary output rather than replacing the frozen public pack.

## Design and fonts

The live Apart Research website was inspected for its actual CSS tokens: paper `#f8f5f1`, ink `#193025`, forest `#194b37`, and warm rules `#e3dfda`. These inform this independent site's palette; it does not use the Apart logo or imply endorsement. Old Standard TT is embedded as unmodified font bytes in `fonts/fonts.css` for offline compatibility. Its SIL OFL 1.1 license and source hashes are included in `fonts/`. Controls and metadata use the system sans-serif stack.

## Verification

```sh
python3 -m unittest tests.test_demo_data tests.test_explorer_context -v
python3 scripts/reproduce_headline.py
python3 scripts/check_artifact.py
node --check demo/explorer/app.js
python3 -m http.server 8765 --bind 127.0.0.1 --directory demo
# In another terminal, with Playwright installed for development:
node demo/explorer/qa_browser.cjs http://127.0.0.1:8765/explorer/ ops/reports/explorer_redesign/browser
```

The QA runner accepts HTTP(S) previews only. It covers 1440/768/390/320px, both themes, reduced motion, persistence, all cases, all twin states, keyboard controls, contrast tokens, errors, asset failures, and unexpected external requests. Full-page and viewport screenshots are written locally; selected screenshots and the report are retained with the handoff. Direct `file://` navigation was blocked by the browser tool's URL policy and is not claimed as an executed browser test. The static offline dependency audit and HTTP runtime tests are recorded separately.

## Deployment

`.github/workflows/deploy-demo.yml` verifies evidence, stages only public demo files with `prepare_pages.py`, and deploys through GitHub Pages. Existing root hash links are preserved by a small redirect to `demo/explorer/`. The staged pack includes raw JSON and the numerical trace, so disclosures keep working publicly. Repository files, local settings, and operational reports are outside the staged site.

Upstream scenario/trace redistribution rights remain unresolved in `NOTICE.md` and `docs/release/LICENSES.md`. The restricted public-data pattern scan is not exhaustive privacy or licensing clearance. No new model outputs or experimental records were added.
