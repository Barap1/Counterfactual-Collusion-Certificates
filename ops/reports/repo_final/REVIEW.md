# Final repository verification

Task REPO-FINAL. No experiments, inference, new spend, credential-file reads, final paper generation or live Google Doc edits. The owner's repository-publication authority supersedes older no-push instructions for this task. Original frozen science is unchanged.

## Scientific pass

Independent reviewer: `science_review.md`. All displayed benchmark counts and eight-pair primary quantities match frozen sources. Corrected the utility citation to include `T8_v0`, observation-equivalence citation to T3/frontiers, and control wording to acknowledge imperfect placebo matching. Policy labels are generator-defined, utility counts are evaluation settings, deterministic narrowing is post hoc, four aggregate prospective failures remain visible, and the real-agent hypothesis was not supported. No general detector/sensitivity claim is made. A frozen protocol's obsolete wording is superseded in `docs/RESULTS.md` without changing its hash.

## Editorial pass

Rebuilt README from a problem-first outline. The opening explains influence versus attribution before technical terms. A concrete shared-message allocation example leads into the extra cost probe. The two studies are separate, negative results appear in the main reading path, and detailed provenance sits behind short navigation links. Removed the final-PDF call to action and duplicated publication directions. Updated three misleading explorer null-effect sentences after inspecting the live study/case views.

## Design pass

Original editable SVGs: `docs/assets/allocation-twins.svg`, `evidence-steps.svg`, source `generate.py`. Rendered in Chrome through the browser tool and visually inspected. Desktop native SVG and 390px README-scale reviews showed readable labels, high contrast, complete arrows and no visible clipping. Phone README images render at 358px inside a 390px viewport; document scrollWidth equals clientWidth (390). Explorer mobile case view also has no page overflow; a fresh mobile entry collapses its case menu. The local README preview approximated GitHub typography. After push, the live GitHub README and both loaded SVG images were inspected; image dimensions were 640×1180 and 640×578.

## Engineering pass

Independent review: `engineering_review.md`. Exact commands executed from repository root:

```sh
python3 scripts/reproduce_headline.py
python3 -m unittest discover -s review/reproduce_headline/tests -v
python3 -m unittest tests.test_demo_data -v
python3 scripts/check_artifact.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="/private/tmp/ccc-final-audit-pytest:$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python scripts/test_offline.py -q tests --junitxml=ops/reports/repo_final/pytest.xml
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/ccc-final-audit-pytest starter/collusion_hackathon/colosseum/.venv/bin/python scripts/test_offline.py -q tests/analysis/test_readiness.py tests/test_demo_data.py
PYTHONDONTWRITEBYTECODE=1 starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/final_audit/verify_bootstrap.py
```

Results: headline Delta `1.354325711018899`, p `18/256 = .0703125`, eight pairs; 11 independent tests pass; eight demo tests pass; full suite 500 passed, four documented skips, 351 subtests in 370.26 seconds. After making the maintained runner install its own release guard, standalone regression: 13 passed, one expected held-out-manifest skip in 2.42 seconds. Bootstrap independently matches the frozen interval. Public reading-path check: 15 pages, 109 local links/anchors, two SVGs; no README PDF link.

Full-suite skips are the existing held-out manifest scope restriction and three unresolved syntax/specification ambiguities, retained in the prior audit's `tests/skips.json`. Complete local pilot traces were used; 18 of 27 are not public. This is not a fresh-install full-suite claim.

Browser checks: local HTTP entry, Twin worlds → P2 → I2 (identical auditor views), I4 (different cost-probe outcomes), Study primary/uncertainty, loaded world-case links, H02_B1 case and mobile case navigation. Console error/warning query returned none during the initial checks. Browser policy forbids `file://` access, so current direct file-URL execution was not verified; no policy workaround was attempted. The app uses local script bundles and `connect-src 'none'`. Its existing documented file entry is retained, with loopback interaction as this session's executed browser test.

## Hygiene and release boundaries

`INVENTORY.md`, `tree_before.json.gz` and `cleanup.json` record the inspection and dispositions. The retained prior `final_audit/frozen_before.json` supports the final byte-comparison receipt. Useful source work from local audit/publication branches is consolidated from a new main-based branch, excluding all unpublished final paper PDFs, DOCX/template exports and rendering QA. Baseline public build PDFs were removed from the current tree. A private local recovery bundle predates cleanup. No force/history rewrite or new public recovery ref is used.

The local JUnit XML was excluded because it contains machine/fixture metadata and a document-ID-pattern match; console summaries and test logs are retained. The scanner was repaired to never open `.env`; the maintained pattern scan excludes credentials/local manifests and prints paths/rule numbers, never matching contents. A pattern scan is limited evidence, not privacy clearance. Public history still retains document references. Upstream rights and missing public pilot inputs remain clearly unresolved. No third-party source or missing private trace is newly distributed.

Final preservation check: all 16,992 protected records are byte-identical. Targeted history inspection found three commits with document-reference changes; matching document IDs/contents were never emitted, and no history rewrite was attempted.

Clean staged-tree export to `/private/tmp/ccc-repository-overhaul/public-checkout` independently passed the headline, all 19 public-file tests, and all 109 link/anchor checks with no starter, credential files or private pilot inputs. No `paper/*.pdf` or DOCX is present in the staged public tree. The scanner checked 376 changed working/staged blobs with zero flags; two broad scans of unchanged compressed mirrors were interrupted and are not reported as complete full-tree scans. Old JUnit exports with document-ID-shaped fixture identifiers were also excluded. Hash verification protects the unchanged scientific bytes.

Published research-content commit: `89572d99e4042f04a387a80e7e093dca86421341`. GitHub CI passed on Python 3.12 and 3.14. PR #1 was closed as superseded; `cursor/cloud-agent-env-235e` was deleted after verifying its only proposed unique work was the setup notes consolidated here. The sole remote branch is `main`; no issues or milestones needed closure. Description, topics and homepage were updated. Details are recorded in `delivery.json`. No claim of final paper submission or third-party legal clearance is made.
