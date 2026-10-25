# CCC Evidence Explorer

Offline research interface over the frozen evidence pack in `demo/data/`.

## Open
Double-click `index.html` (works from `file://`; no server, no network, no CDN, no framework, no vendored library).
Views: Start here (4-step tour), Study, Twin worlds (hidden unless `demo/data/twins.json` exists), Concepts & sources, and 21 cases (16 held-out EXP-002 checkpoints, 5 development fixtures) in the left list. Hash routes: `#/case/H02_B1`, `#/study`.

## Data provenance
`demo/data/*.json` is the single source of truth. `bundle_data.py` wraps it into `data/*.js` (`window.CCC_DATA`), loading one case file per selection via an injected `<script>`. The only transformation is overlaying untruncated message text from `demo/data/full/`. Never edit `data/*.js` by hand. Held-out data are descriptive; fixtures are development evidence. Effect conventions (tau_O = O_K - O_F, tau_C = C_F - C_K, tau_W = W_K - W_F) were verified against stored rows, and the case page shows a rows-vs-certificate reconciliation.

Rules the UI derives (stated in the UI too): evidence-ladder rung comes only from certificate fields (supported -> L2; invalid -> L0; not supported / inconclusive -> L1 if any tau interval excludes 0, else L0; L3 never claimed). Tour contrast = the world with the largest |tau_O(B1) - tau_O(B2)| (illustrative, not a selected positive result).

## Rebuild
Run `build_twins.py` when changing the selected benchmark source, then `python3 -I demo/build_data.py`, then `python3 -I demo/explorer/bundle_data.py`. The pack builder writes its manifest last; the bundler verifies generated file hashes before replacing the previous bundle. It embeds the exact manifest SHA-256 and copies the manifest's authentic generation base commit. That commit records HEAD at generation; source hashes identify the actual input and generator bytes, including uncommitted corrections.

## Twin worlds
`python3 -I demo/build_twins.py --run docs/enh/r2/run_par --label PROSPECTIVE --dev-run docs/enh/bench/dev_run` writes `demo/data/twins.json` from preserved outputs only (records, canonical per-seed partitions, separators, RESULTS.json); follow with `build_data.py`, then `bundle_data.py`. For development use `--run docs/enh/bench/dev_run --label DEV`. Deep link: `#/twins/P2/4`. Selection is the lowest seed per pair type at epsilon=0. The prospective view retains all frozen aggregate criterion decisions and discloses the post-hoc epsilon=0 scope and unresolved epsilon=0.1 divergence. Labels are scripted, not recovered real-agent intent.

## QA
Current interaction and desktop/mobile review notes are in [`ops/reports/repo_final/`](../../ops/reports/repo_final/). Older screenshot sets were redundant presentation evidence and are excluded from the reading path. Frozen numerical pack provenance remains in `demo/data/` and is checked by `tests/test_demo_data.py`.
