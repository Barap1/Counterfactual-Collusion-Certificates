# RESUME packet (2026-10-24 ~09:30 UTC)

Read CCC_START_HERE.md, ops/STATUS.md, docs/release/CHECKLIST.md, and ops/DECISIONS.md D-028..D-035. All science is complete and frozen. Do NOT rerun experiments or change analysis numbers.

Rules in force: $0; owner is sole commit author with no AI trailers (D-027); push, Google Doc writes, publication and submission only on explicit owner approval; conservative models.

Remaining work is owner-driven:
1. Fill [OWNER] placeholders in paper/draft.md (authors, LLM statement approval, human-verification sentence, dual-use review, public-release line), then `python3 paper/build/make_submission.py` and render the PDF with headless Chrome (see paper/build_pdf.sh; Chrome must run outside the Codex sandbox).
2. If approved: sync to the Google Doc working copy (ops/doc_target.local.json; check baseline_modified_utc first; never write the official template).
3. If approved: push main to origin (private).
4. Owner submits on the Apart sprint page before 2026-10-26 11:59 UTC.
