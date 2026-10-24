# RESUME packet for a fresh Opus director session (2026-10-24 15:00 UTC)

Paste to start:
> Resume CCC as research director. Read CCC_START_HERE.md, ops/STATUS.md, this file, docs/release/CHECKLIST.md (section "Owner decisions required"), and ops/DECISIONS.md D-026..D-036 only. Science is frozen; do not rerun experiments or change numbers. Wait for the owner's decisions below before acting on them.

## Standing rules (owner instructions)
- $0 out-of-pocket; no paid fallback.
- The owner (Aarav Patel, [REDACTED-EMAIL] git identity) is the SOLE commit author; never add Claude/Codex Co-Authored-By trailers (D-027).
- Be stingy with subagents: Codex gpt-6.1-sol medium or low, gpt-6-luna for easy work; Claude Sonnet or Haiku; no Opus or gpt-6-astra without a stated reason. Prefer Codex when credits allow (Codex cannot write .git or run headless Chrome; the director commits).
- Push, Google Doc writes, sharing/visibility changes, publication and submission require explicit owner approval each time.
- Keep about 40 commits per push; squash local unpushed history with git commit-tree (trees identical, backup branch) if asked.

## Key paths
- Paper (tagged audit copy): paper/draft.md. Submission: paper/build/submission.{md,html}; PDF paper/build/CCC_submission_draft.pdf (+ .sha256). Rebuild: `python3 paper/build/make_submission.py`, then `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer --print-to-pdf=paper/build/CCC_submission_draft.pdf file://$PWD/paper/build/submission.html`. Page QA: `swift paper/build/pdf_pages.swift <pdf> <outdir>` (PDFKit: page count, section-per-page, PNG per page).
- Results: docs/analysis/exp002_heldout_v2/ (+CORRECTION.md); DEV docs/analysis/exp001_dev_v2/; review docs/review/rev001/, docs/review/REV_FREEZE.md, docs/review/director_gateA_audit.md, docs/review/cold_read.md.
- Protocol/prereg: docs/research/sci002/protocol.md (v1.2), docs/stats/prereg.md, docs/stats/stage2/STAGE2_ADDENDUM.md, docs/stats/deviation_log.md, docs/stats/FREEZE.md.
- Raw traces: docs/runner/archives/exp00{1,2}-live.tar.gz (+.sha256); live dirs are gitignored.
- Reproduce: `/bin/zsh scripts/reproduce_offline.sh` (verified exit 0 on 2026-10-24).
- Google Doc target: ops/doc_target.local.json (gitignored; check baseline_modified_utc before any write; never write the official template).

## Next actions (owner-gated)
1. Owner decides repo visibility; if private is approved, run the gh command in STATUS.md.
2. Owner provides author line, LLM-statement approval and dual-use sign-off; edit the [OWNER] tags in paper/draft.md; rebuild; QA the PDF (main text must stay ≤ 8 pages).
3. If approved: sync to the Google Doc; push main; optionally scrub Doc IDs before any intentional public release.
4. The owner submits on the Apart sprint page before the deadline.
