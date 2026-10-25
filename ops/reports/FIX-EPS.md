## Task
FIX-EPS — implement D-048 platform disclosure and deterministic-stratum reporting.

## Status
Content and numerical checks complete. Current PDF rebuild/page-limit verification blocked: headless Chrome SIGABRT; UI fallback denied Chrome access.

## Artifacts
- `scripts/eps_platform_check.py`; `docs/enh/r2/PLATFORM_DIVERGENCE.md`; `docs/enh/r2/RESULTS_BY_STRATUM.md` and `.json`.
- Updated `paper/v2/draft_v2.md`, `docs/enh/JUDGE_SUMMARY.md`, `DEMO_SCRIPT.md`, `FINAL_REVIEW.md`, `README.md`, `ops/CLAIMS.md`.
- `figures/enh/make_enh_figures.py` adds `--platform-dependent-eps01`; regenerated `figures/enh/prospective/` SVGs/JSON captions.
- Rebuilt `paper/v2/build/submission_v2.md` and `.html`; validation, numeric trace and exact commands: `paper/v2/build/FIX-EPS-validation.json`, `FIX-EPS-validate.py`, `FIX-EPS-commands.txt`.

## Validation
Shared eps=0: 149/149 units byte-identical; 0/1458 records differ. Shared eps=0.1: 142/148 units differ; 1160/1452 records have differing method outputs. Every method×kind×set count and per-seed hashes are recorded. Every copied RQ row matches frozen RESULTS.json; revised headlines trace to stratum JSON. All four aggregate failures remain. EXP-002 §5.4 is byte-identical. Abstract: **207 words**.

Commands run: assigned Python on `scripts/eps_platform_check.py`, figure builder with `--platform-dependent-eps01`, and `paper/v2/build/FIX-EPS-validate.py`; `python3 paper/v2/make_v2.py --figdir figures/enh/prospective` (failed PDF), then `--no-pdf` (passed). Exact invocations, Chrome fallback and Swift command are in the command log.

## Limitations
**Current page count unavailable; ≤8 main pages unverified.** Swift counted only the stale pre-revision PDF: 15 total, References on page 7. Old PDFs are preserved as `.pre-FIX-EPS.pdf`; current SVGs carry labels. Both run directories remain untouched. Cause of platform divergence unresolved.

## Budget
$0; GPT-6 Codex session; no network, git, experiments or delegated agents.

## Next
Run the logged PDF build and Swift page check in a Chrome-capable environment before release.
