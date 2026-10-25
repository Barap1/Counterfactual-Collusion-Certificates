# REPO-FINAL-ENG — independent engineering and hygiene audit

2026-10-25. Read-only source audit plus limited offline execution. No network, model, cloud, paid call, secret-file read, code modification, or experiment. Other workers own implementation. This report is the only file owned by this task.

## Verified checks

- `python3 scripts/reproduce_headline.py`: PASS under Python 3.14.7. Archive SHA-256 `83bf451dad54c773afbc3e775acc13e08bd97fbe92dee4d1a21307cc60625831`; eight paired contrasts; independently recomputed Delta `1.354325711018899`; exact sign-flip 18/256 = `0.0703125`. Frozen analysis Delta differs by approximately 1e-15 due to reduction order. Script explicitly states directional hypothesis NOT supported.
- `python3 -m unittest discover -s review/reproduce_headline/tests -v`: PASS, 11 tests in 0.085 seconds. Tests reject corrupt hashes, bad rewards, incomplete attempts and incorrect summaries; preserve retry/nonexecution distinctions.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_demo_data -v`: PASS, 8 tests in 1.887 seconds. Checks 21 case records against source certificates, primary interval and p, 143 valid/56 not-run branches, eight per-world contrasts, raw archive sample hashes and transcripts, fixture rows, gate traces, complete pack hashes and source hashes.
- The local starter interpreter exists: Python 3.14.7, NumPy 2.2.6, SciPy 1.17.0, PyYAML 6.0.3, terrarium-agents 0.1.1. Pytest is absent from that environment. `/tmp/ccc-final-audit-pytest` exists from the prior offline cache staging. These are local facts, not a fresh-install verification.
- All 27 pilot-manifest files exist locally and match SHA-256 in `docs/release/pilot_archive/`; **only nine are tracked**. All 27 also exist in local ignored `results/baselines/`. Mapping is the same as `tests/test_offline_adapter.py`: date 20261023-111229 uses interrupted pilot folder, 20261023-111625 uses completed pilot folder. Two initial counting attempts used the wrong manifest base; corrected mapping gave 27/27 matches.

## Findings requiring implementation or careful documentation

1. **Legacy scanner reads secrets.** `scripts/secret_scan.py` loads `.env` with `dotenv_values` before scanning. Do not execute under this task's no-secret-read boundary. Remove exact-value secret-file access or use an independent path/strict-pattern scanner. The previous final audit also avoided this script. Current pattern scan does not establish historical removal or complete privacy clearance.
2. **Full public-checkout pilot reproduction is incomplete.** PR #1's missing-file caveat is accurate. A copy from the tracked `docs/release/pilot_archive/` restores nine of the 27 exact pilot files. Local success using all 27 does not validate fresh-checkout tests. Keep missing-file and licensing limits explicit unless separately resolved; do not fabricate, regenerate or silently replace frozen pilot traces.
3. **Legacy full reproduction is zsh-specific.** `scripts/reproduce_offline.sh` uses `${0:A:h:h}`, `[[ ]]` and `print`; `/bin/zsh` is not universal on Linux. The standard-library headline is cross-platform and should remain primary. If maintaining the full driver, a Python wrapper or POSIX shell is preferable.
4. **Legacy full test command misses pytest functions.** `reproduce_offline.sh` invokes unittest discovery, so it does not run all pytest-style tests. Prior complete audit used a guarded real-file pytest runner; its 500-pass/4-skip result belongs to that prior run. The prior handoff explicitly says the complete DEV reproduction script was reviewed, not rerun.
5. **Full analysis has external requirements.** `ccc/analysis/` imports NumPy/SciPy; replay/fixtures depend on the excluded upstream starter and CoLLAB. No root Python package/dependency manifest supplies a tested fresh install. Document this separately from the working zero-install headline.
6. **Secret-manifest fallback exists.** `ccc/paths.py` attempts `ops/environment.local.json` unless `CCC_STARTER_ROOT` is set. Safe full commands must set it and install audit guard before importing production modules.
7. **PDF exclusion affects old build records.** Historical reports and tests refer to generated paper PDFs, and `tests/test_paper_v2_build.py` tests PDF freshness/failure handling. Retain source/provenance and identify historical records as historical. Do not run final manuscript regeneration for this overhaul.

## Exact full-suite command available locally

The existing prior audit runner `ops/reports/final_audit/run_pytest.py` sets the starter path and `PYTEST_DISABLE_PLUGIN_AUTOLOAD`, installs network/secret audit protection and provides a real `__main__` path for multiprocessing workers. With the existing cache:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="/tmp/ccc-final-audit-pytest:$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/final_audit/run_pytest.py -q tests --junitxml=ops/reports/repo_final/pytest.xml
```

This review did not run the full suite. It normally takes several minutes. If the report folder is reorganized, promote the runner into `scripts/` and correct its root calculation. Prior four skips: one historical held-out-manifest guard; three specification ambiguities in extractor/alias/attribution fixtures. Preserve and explain them.

## Explorer

`demo/explorer/index.html` loads only local CSS, `data/index.js`, `app.js` and injected local case/twins bundles. CSP blocks connections. `#/twins/P2/2` and `#/twins/P2/4` are supported by router lines 843–851; `#/study` and `#/case/H02_B1` also exist. The HTML file entry works from file URLs by design; this audit verified static wiring and numerical pack tests, not browser rendering. Desktop/mobile browser interaction remains root verification work.

Builder order is `demo/build_twins.py` → `demo/build_data.py` → `demo/explorer/bundle_data.py`. The bundler fails on stale manifest/source hashes before deleting the old bundle. Do not hand-edit generated JS. A normal builder run updates provenance metadata; preserve frozen research records.

## Recommended CI and organization

Use dependency-free GitHub Actions on Python 3.12 and 3.14 for headline, 11 independent tests, eight demo tests, README link checks and SVG source checks. Grant only `contents: read`; never use model/environment regeneration, secrets or the excluded starter. Do not label these checks full reproduction.

Keep `ccc/`, `tests/`, `scripts/`, `demo/`, canonical evidence paths, notices and one manuscript source navigation. Move or remove redundant presentation renders and obsolete launch/package stubs only after inventory/recovery; avoid moving 16,992 protected records or generator-hashed paths merely for cosmetic uniformity. Replace competing “final” navigation with a single source index and a concise evidence map. Audit screenshots/logs can remain supporting, not prominent README links.

Licensing remains unresolved for Colosseum/poseidon/CoLLAB adaptations and derived scenarios/traces. Original CCC MIT and bundled font OFL do not grant those rights. Historical public document references and commit metadata remain publicly recoverable; a current-tree cleanup must not claim otherwise. No outgoing contact or visibility/history change is authorized by this subtask.

## Fresh post-implementation review

Reviewed the rewritten `README.md`, current `docs/README.md`, `RESULTS.md`, `REPRODUCING.md`, `LIMITATIONS.md`, `docs/assets/README.md`, `paper/README.md`, maintained checker and test runner, scanner change, and `.github/workflows/offline-artifact.yml`. No tests were repeated. Root reports current full suite 500 passed / four skips / 351 subtests, and 19 public tests passed; this reviewer does not relabel those root executions as independent runs.

The main reading path now accurately separates recorded-output arithmetic, bootstrap verification and environment-dependent full analysis. The pilot missing-input limitation is explicit. CI has read-only permissions, Python 3.12/3.14, no package installs or experiment commands, and public-data checks only. The headline command and expected output match the earlier independent execution. The scanner no longer reads `.env` and prints paths/rule numbers without matched content.

Findings sent to root before finalization:

- `scripts/test_offline.py` initially installed the network/secret guard but not the `scripts/offline_guard/sitecustomize.py` held-out skip. The documented standalone command therefore did not reproduce the documented skip policy without caller-supplied `PYTHONPATH`. Remedy: explicitly install the guard/skip in the runner, or document exact environment setup.
- `paper/final/FIGURE_EVIDENCE_MAP.md` initially claimed retained PDF/PNG figure exports and old README banner/evidence-flow SVG locations, although only original paper SVGs were consolidated and new README SVGs replaced those assets. Remedy: correct retained formats and link new `docs/assets/README.md`.
- `demo/explorer/README.md` initially pointed to removed `qa/` screenshots. Remedy: link current review evidence or label the historical captures as removed.
- `docs/release/CHECKLIST.md` initially retained stale “current” PDF build/freshness, no-CI, unapproved publication and presentation-finalization language after the overhaul. It is not frozen scientific evidence; replace it with current release facts and link historical audits as historical. Retain unresolved rights, public-history exposure and owner submission decisions.

These are fixable documentation/runner consistency issues, not scientific result discrepancies. All checks above refer to the state inspected during this pass; root owns final fixes and validation.
