# CCC Evidence Explorer

Offline research interface over the frozen evidence pack in `demo/data/`.

## Open
Double-click `index.html` (works from `file://`; no server, no network, no CDN, no framework, no vendored library).
Views: Start here (4-step tour), Study, Twin worlds (hidden unless `demo/data/twins.json` exists), Concepts & sources, and 21 cases (16 held-out EXP-002 checkpoints, 5 development fixtures) in the left list. Hash routes: `#/case/H02_B1`, `#/study`.

## Data provenance
`demo/data/*.json` is the single source of truth. `bundle_data.py` wraps it into `data/*.js` (`window.CCC_DATA`), loading one case file per selection via an injected `<script>`. The only transformation is overlaying untruncated message text from `demo/data/full/`. Never edit `data/*.js` by hand. Held-out data are descriptive; fixtures are development evidence. Effect conventions (tau_O = O_K - O_F, tau_C = C_F - C_K, tau_W = W_K - W_F) were verified against stored rows, and the case page shows a rows-vs-certificate reconciliation.

Rules the UI derives (stated in the UI too): evidence-ladder rung comes only from certificate fields (supported -> L2; invalid -> L0; not supported / inconclusive -> L1 if any tau interval excludes 0, else L0; L3 never claimed). Tour contrast = the world with the largest |tau_O(B1) - tau_O(B2)| (illustrative, not a selected positive result).

## Rebuild
`python3 -I demo/explorer/bundle_data.py` (rerun after any change to `demo/data/`; picks up `twins.json` automatically).

## QA
Screenshots in `qa/` (headless Chrome; 390 px shots use a 390 px iframe because headless windows are at least 500 px wide).
