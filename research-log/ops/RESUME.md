# Resume — repository delivery

Read `CLAUDE.md`, `ops/STATUS.md`, the REPO-FINAL registry entry, `docs/README.md` and `ops/reports/repo_final/REVIEW.md`. The user explicitly authorized public repository maintenance, pushes, integration, cleanup and metadata updates. No final paper PDF or live Google Doc changes are authorized by this overhaul.

Current research records remain at established paths. The latest accessible manuscript is `paper/final/manuscript.md`; its title follows the owner request. Root README is the canonical public summary. Do not use old manuscript build outputs or restart old experiments.

Verification uses `python3 scripts/reproduce_headline.py`, the 11 independent arithmetic tests, eight demo provenance tests and `scripts/check_artifact.py`. Full local implementation suite uses `scripts/test_offline.py` with the existing pinned starter environment and local-only pilot traces. Missing public inputs and genuine release-rights/privacy concerns are documented in `docs/REPRODUCING.md` and `docs/LIMITATIONS.md`.

A local pre-cleanup recovery bundle preserves all local refs at `/private/tmp/ccc-repository-overhaul/pre-overhaul.bundle`. It must not be pushed wholesale: it includes unpublished submission PDFs and template artifacts excluded by the owner. Existing public history was not rewritten. Final PDF placement instructions: `paper/README.md`.
