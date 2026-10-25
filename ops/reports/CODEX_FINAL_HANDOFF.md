# CCC final owner handoff — 2026-10-25

**READY FOR OWNER FINALIZATION.** No machine-verifiable P0 build/freshness blocker remains. This is not submission or release authorization. Proceed to wording/graphics/template polish while retaining all scientific limitations and completing the human decisions below.

## Git and exact changes

Branch: `codex/final-submission-audit`. Baseline: `4811eaf24b3bdc9e73bb96c1cbf3cf7288c429ac` (main and local origin/main agreed). Final local delivery commit SHA and branch are recorded verbatim in `ops/reports/final_audit/FINAL_COMMIT.json` after the commit, avoiding a self-referential commit hash inside its own tree. Resolve directly with `git rev-parse HEAD`. No push occurred.

Every changed/added delivery path is listed in `ops/reports/final_audit/modified-files.txt`; file hashes/sizes and final artifact inventory are in `docs/release/FINAL_ARTIFACTS.json`. Original frozen evidence and source/build snapshots are preserved. Initial tracked tree was clean; pre-existing untracked `ops/reports/codex_runs/` logs were not staged or overwritten. The other worktree was untouched. Commits use the existing owner-only identity under D-027, with no AI co-author trailer.

## Final candidate

- PDF: `paper/v2/build/submission_v2.pdf`.
- SHA-256: `8bec47060d6b27d638217ef9c52676a463af4f5d8bccd6cc99c0d75094382498`.
-23pages total: main text1–8 (through Code and Data), references9 (all20entries), appendices10–23 (LLM statement on23).
- Abstract207words. Title retained: *Same Evidence, Different Verdicts: Evidence Standards for AI Collusion Attribution*.
- Current editable text/build source, HTML, bibliography, final figures and exact commands: `paper/v2/TEMPLATE_TRANSFER.md`.
- Current hash receipt: `paper/v2/build/build_report.json`; `make_v2.py --check` returned true after the last build.
- Historical `FIX-EPS-validation.json` is preserved unchanged as an earlier blocked-build record, not current validation. `FINAL_AUDIT_VALIDATION.json` and the build manifest identify the new candidate.

The actual current official template was read anonymously, without editing/syncing it. Its font, size, margins/title treatment and sections were checked. The local candidate is an explicit adaptation: body single spacing/4pt paragraph gaps differ from template examples using1.15 spacing. Owner approval or native-template transfer is required; exact differences and the full transfer package are documented. The present candidate meets the numerical page/abstract limits; recheck after owner edits. Guidelines deadline:2026-10-26 11:59UTC; upload limit25MB.

## Executed test matrix

| Classification | Check | Result / exact evidence |
|---|---|---|
| EXECUTED | Final complete guarded pytest discovery/run |500passed,4skipped,351subtests passed in346.53s; `final_audit/tests/pytest_final.log` and XML. Subtests are not counted as additional independent tests |
| EXECUTED | Initial unittest run |460reported tests:452passed,4skips,4import errors because pytest missing. Preserved `tests/unittest.log`; not mislabeled pass |
| EXECUTED | Missing-dependency supplement |43pytest-style tests passed in89.11s after offline cached pytest staging; `pytest_supplement.log` |
| EXECUTED | Initial full pytest from stdin |499passed/1harness failure/4skips: multiprocessing could not reload `<stdin>`. Preserved `pytest_stdin_attempt.log/.xml`; corrected real-file runner used for final full run |
| EXECUTED | New builder regressions |5passed: cleanup preserves science, Figure3 location, stale candidate invalidation/preservation, hash tampering, failed renderer publication |
| EXECUTED | Stdlib independent headline unit tests |11passed; `tests/independent_unit.log` |
| EXECUTED | Final text-only About wording change |8demo tests passed after the full suite; four fresh final provenance screenshots show current manifest and corrected formal/diagnostic Gate A wording |
| EXECUTED | EXP002 raw archive/headline |Raw archive checksum;8pair contrasts; exact p18/256. Reduction differs from frozen Delta by1.1102230246251565e-15 only |
| EXECUTED | Independent frozen-seed bootstrap |PCG64(20261025),10,000world-cluster draws; interval differs from frozen by≤4.5e-16 |
| EXECUTED | Frozen evidence and raw archive hashes |16,992protected files unchanged; both tar sidecars match;27pilot manifest entries match preserved copies |
| EXECUTED | R2 receipt/report checks |34frozen source hashes;2,100worker receipts;8,400artifact hashes;40-seed post-run comparison; five-seed selfcheck; three stratum outputs byte-identical |
| EXECUTED | Independent existing R2 record reconstruction |42,000records; numerical comparison differences=[] at1e-12; `science/independent_current/comparison.json`. No simulation/new worlds |
| EXECUTED | v2→v3 correction verification |39files;33,292literal numeric tokens identical;222categorical changes;16validity fields/5reason arrays;0status changes |
| EXECUTED | Final PDF/HTML checks |23fresh150DPIpages; all pages inspected; no blank page/text outside safe page box; figure/caption/category checks; exact source/output hashes |
| EXECUTED | Explorer |16held-out+5DEV cases;6lowest-seed eps0twins;21selectors/143transcript options/147section anchors/123detail toggles/36twin states; keyboard, links, tour;8demo tests and corruption guards |
| EXECUTED | Release scan |Baseline tracked tree/history/raw archives scanned without secret-file reads; no strict-format credential hits; private-reference/history and licensing limits below |
| REVIEWED RECORD ONLY | Historical399/415test counts, old QA/build claims, old scientific reviews |Not current test results; corrections reconciled against current code/evidence |
| NOT VERIFIED | Fresh starter install, remote CI runner, full DEV reproduction script rerun, current cloud jobs/spend, actual document sharing/access, upstream permissions |Local alternatives supplied; no claim that these passed |

Four skips (`final_audit/tests/skips.json`):

1. `ReadinessTests.test_real_frozen_manifest_contract_without_outcomes`: legacy REL-001a restriction hard-coded into the test. Current independent raw/headline/hash checks cover held-out evidence separately; the skipped contract test itself was not run.
2. `PositiveControls.test_PC2_current_assignments_row`: historical specification ambiguity about CURRENT ASSIGNMENTS row syntax.
3. `SpecRulesBeyondControls.test_attribution_maps_to_claim`: historical specification ambiguity about attribution surface form.
4. `SpecRulesBeyondControls.test_registered_alias_gives_tuple`: historical specification ambiguity about alias mapping/DEV-pinned contents.

The three ambiguity skips remain disclosed rather than changing a frozen protocol to obtain a green count.

## Exact verification commands

Run from repository root. Full tests used the existing starter environment; cached pytest was staged in/tmp, with no download or project-environment mutation:

```sh
uv pip install --offline --python starter/collusion_hackathon/colosseum/.venv/bin/python --target /tmp/ccc-final-audit-pytest pytest
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="/tmp/ccc-final-audit-pytest:$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/final_audit/run_pytest.py -q tests --junitxml=ops/reports/final_audit/tests/pytest_final.xml
python3 -m unittest tests.test_paper_v2_build -v
python3 -m unittest discover -s review/reproduce_headline/tests -v
python3 scripts/reproduce_headline.py
starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/final_audit/verify_bootstrap.py
python3 ops/reports/final_audit/science/verify_receipts.py
python3 ops/reports/final_audit/science/verify_v2_v3.py
python3 scripts/eps_platform_check.py --out ops/reports/final_audit/science
python3 ops/reports/final_audit/science/rerun_independent_r3.py
python3 ops/reports/final_audit/verify_final.py
shasum -a 256 -c docs/runner/archives/exp001-live.tar.gz.sha256 docs/runner/archives/exp002-live.tar.gz.sha256
python3 paper/v2/prepare_audit_figures.py
python3 paper/v2/make_v2.py --figdir figures/enh/prospective
python3 paper/v2/make_v2.py --check
pdfinfo paper/v2/build/submission_v2.pdf
pdftotext -layout paper/v2/build/submission_v2.pdf /tmp/ccc-submission.txt
pdftoppm -r 150 -png paper/v2/build/submission_v2.pdf /tmp/ccc-page
python3 ops/reports/final_audit/cold/verify_cold.py
python3 ops/reports/final_audit/cold/verify_final_pdf.py
```

The persisted logs/worker reports contain exact output redirections and initial failed attempts. Chrome succeeded outside the restrictive macOS tool sandbox using a fresh temporary profile; that environment requirement is recorded. PDF extraction/render commands used audit-owned destinations in the executed run. `paper_qa.py` ran with the bundled Python3.12 runtime containing Pillow/pdfplumber; it is a QA dependency, not required for the headline script. The existing full DEV `reproduce_offline.py` received only a truthful diagnostic-status message correction; it was reviewed, not rerun in full. No claim of a clean remote install or complete reproduction via that legacy script is made.

## Preserved values and corrections

Frozen EXP002: Delta1.354325711018898, CI[-.01954964911635066,2.8336288730243204], p.0703125,8independent pairs,16worlds,143executed valid/56unrun,0failed/invalid,0/11/5certificates; all unchanged. Non-commit estimate.7269157197310299 remains registered secondary; reported p.156 remains post hoc. Full held-out manuscript section is byte-identical to baseline.

R2 aggregate RQ1/RQ2PASS by construction; RQ3/RQ4/RQ4b/RQ5FAIL; RQ6descriptive. Deterministic RQ3 is61/200=.305, CP95[.242,.374] including.25. RQ4 legitimate P2/P3 is200/200each, P6=0/200, benign=0/100; deterministic RQ4b pass does not rescue aggregate FAIL. RQ5v1=2/84,v0=5/84 at eps0 with73undefined gaps each. No result changed. All stratum/report fields reproduced; exact provenance tables are in the scientific report.

Corrected derived annotations only: prevalence n50→200; percentage labels30→30.5and20→20.5; reading footer below→at-or-above mO; formal Gate A accepted narrowly versus A6diagnostic350/360failure; held-out outlines PH case inspection versus separate ORS sensitivity. Figure sidecars and demo `field-differences-v3.json` give exact field differences and preserved-original hashes. No plotted numerical mark changed to improve results.

## Visual and explorer evidence

Current final page PNGs: `final_audit/paper/final-annotation-pages/page-01.png` through23; contact sheets `final-annotation-contact-1.jpg` through6. `paper/page_geometry.json` binds every page to PDF SHA8bec4706…; prior24-page and23-page attempts remain separately named. Only pages13/15 changed between the last reviewed legible version and final annotation correction; they were reinspected. All other final pixels match inspected pages. Owner graphics polish is still needed for dense appendix A5/A8–A10; main figures/tables are readable.

Open `demo/explorer/index.html#/twins/P2/2`; compare I2/I4, then Study. No server is required for ordinary local opening. Real-browser QA used an owned127.0.0.1static server with external requests blocked; browser/server were closed afterward. Build order is twins→data→bundle, never bundle before the pack manifest. Authentic manifest SHA: `bdb66f194e5ba4abf1e6b18f20ee4ec6ff44b954ad0adbb19f3685a31cddb687`; generation base commit4811eaf2is genuine, and source hashes bind working inputs.

36fresh functional/view screenshots plus four current final About/provenance shots cover1440×1000and390×844, light/dark. The final source-pack category-note fix left rendered Study data byte-identical. Root's last About-only wording correction has its exact diff, eight targeted tests and four new shots in `explorer_release/final-provenance-screens/QA.json`. The existing explorer/color system was retained.

## Release safety, limitations and owner tasks

Repository visibility was independently confirmed PUBLIC. The bounded scan found no strict-format credentials/current private Doc matches, but history remains reachable with two potentially private owner-document references and one official public-template reference. Actual IDs/secret values are not printed. Existing personal Git emails and OS-username paths remain. No history rewrite, sharing change or visibility change occurred. Legacy secret scan was reviewed rather than executed because it reads local secrets; independent scans honored the no-secret-read boundary.

Original CCC MIT is retained; the README contradiction is fixed. New font faces are unmodified OFL1.1 with full notice. Colosseum/poseidon/CoLLAB adaptations, copied patch context and derived scenario/trace rights remain unverified. This is an owner release decision, not assumed permission. No release ZIP or new upstream/model redistribution was created.

Owner must finalize author/affiliation, title approval, truthful LLM usage/actual human verification, dual-use and release authorization, template adaptation or transfer, appendix graphics/final PDF visual approval, public history/private-document access and upstream rights decisions, any later push/sync and final submission. EXP003 was not completed; full support-level positive-control recovery/useful real-agent sensitivity are unestablished. Retain these limitations. The owner can proceed to the final visual and wording pass; no further research run is needed for the honest scoped submission.
