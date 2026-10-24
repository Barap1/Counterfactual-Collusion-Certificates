# DEMO-TWINS handoff

**Task:** build demo/build_twins.py and the Twin worlds centrepiece in the explorer.
**Status:** Done on docs/enh/bench/dev_run with --label DEV.
**Artifacts:** demo/build_twins.py; demo/data/twins.json (151 KB); demo/explorer/{app.js,style.css,README.md,data/twins.js}; demo/build_data.py (binds twins.json and its sources into MANIFEST, adds TRACE rows); demo/data/{MANIFEST.json,TRACE.md}; qa/twins_P2_I2_desktop.png, twins_P2_I4_desktop.png, twins_P2_I4_mobile.png.
**Validation:**
- twins.json is built from records.json.gz, partitions/*.json.gz and separators.json only. No ccc imports and no model calls. Each canonical_view is re-hashed against view_sha256.
- Rule: lowest seed per pair type (13000), eps=0. relayed is a single case with no twin.
- First view difference matches the enumerated separators: P1 I3, P2 I4, P3 I5, P4 I1, P5 I0, P6 I1.
- Builder asserts identical view implies identical verdict.
- Strongest baseline by the PROTOCOL s5 rule is B2+ (balanced accuracy 0.600 vs B3b 0.543).
- tests.test_demo_data passes (8 tests) after the rebuild; the other pack files were byte-stable.
- UI: pair tabs, I0 to I5 slider and buttons, side-by-side twins with private labels, per-set arms/probe/authorization, verdict table, I0 to I5 divergence matrix, and the "Identical evidence → identical verdict; only new evidence (Ix) separates them" line. The DEV banner and badge come from the JSON. Desktop and 390 px screenshots were inspected.
**Findings shown, not hidden:** CCC v1.2.2 gives both P2 twins "supported · L2", with identical verdicts at every set. Only CCC-L and Bayes diverge, at I4. The explorer says L2 is not attribution.
**Limitations:**
- Single seed per type is illustrative.
- eps=0 only, so one continuation per arm.
- The filler text is truncated in the source.
- The 390 px tables scroll horizontally.
- Not run: PROSPECTIVE.
**Budget:** $0, no network, no git changes.
**Next:** Rerun the three commands once a prospective run exists.
