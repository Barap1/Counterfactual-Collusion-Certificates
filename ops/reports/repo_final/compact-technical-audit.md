# Compact README graphics — independent technical review

2026-10-25. Read-only review of the owner-requested compact README revision. Owned output: this report only. No experiment, inference, secret-file read, source edit, or full-suite repetition. Root owns browser inspection, integration and publication.

## Result

No blocking technical finding in the reviewed revision. The README now uses explicitly sized HTML images at width 600. The original editable allocation graphic is 640×536 and the evidence map is 640×246. Both retain nonempty descriptive alternative text, SVG title/description, live editable text and viewBox. Their compact captions retain the generator-defined policy boundary and the distinction between replay influence and attribution.

Every numerical label in the allocation SVG agrees with `paper/v2/figures/fig_twins_audit.json` → `plotted_values.members`: both F14/K19, permitted PF29, prohibited PF14. The values describe mean outsider task reward. Neither diagram embeds external references, scripts or foreignObject content.

`docs/assets/generate.py` regenerates **byte-identical** SVGs when executed in an isolated temporary working directory. No tracked source was overwritten for this check:

- `allocation-twins.svg`: SHA-256 `ae3a3661d227e65a3dc20b0342ed45273459b957f4c589c1e4ae951ce830135d`.
- `evidence-steps.svg`: SHA-256 `affe7b3a1ecc7ccda9fccb7e24dede7af681772bdaa595c9626ad41848fb9755`.

## Navigation and automation

Executed `python3 scripts/check_artifact.py`: **PASS**, 15 maintained reading-path pages, 109 local links/anchors and two editable SVGs; no root README paper-PDF link. The updated HTMLParser includes HTML `img src` and `a href` alongside Markdown links and rejects images lacking nonempty alt text. README dimensions therefore do not bypass image-path checks.

Executed `git diff --check`: PASS. Static review of `.github/workflows/offline-artifact.yml` confirms read-only `contents` permission, Python 3.12/3.14 public-file jobs, no dependency installation, no secrets, no model runner and no experiment command. The unchanged quickstart runs recorded-output arithmetic. The standalone `scripts/test_offline.py` now explicitly installs the release guard through `runpy`, fixing the earlier discrepancy between its documented and actual skip policy.

Public guides retain the full-suite dependency and missing 18/27 pilot-trace limitation. The later PDF location remains `paper/paper.pdf`; no placeholder or active link was introduced. Rights/privacy boundaries remain visible.

## Read-only GitHub state observed

Connector checks during this review confirm:

- Repository `Barap1/Counterfactual-Collusion-Certificates` is public; default branch is `main`.
- Remote branch search returns only `main`.
- Open-PR search returns none.
- Local HEAD and tracking `origin/main` both initially identify `dbd734c16334daacd1a2b3600c5e6f893b530bd1`; compact edits were still uncommitted when those refs were inspected.

The connector workflow-run lookup is limited to PR-triggered runs and cannot establish a main-push CI result by itself. Final pushed commit and push-triggered CI need the root's post-publication check or a follow-up exact run lookup. No claim of final-CI success is made in this pre-push report.

## Validation limits

This review checks source consistency, structural accessibility, numerical labels, navigation and automation configuration. Root performs actual desktop/mobile/GitHub visual inspection. The implementation suite was not repeated for this README/SVG-only change; prior executed software results remain separate from this pass.
