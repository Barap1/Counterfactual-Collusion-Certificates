Task: REL-ENH1 — local release hygiene.
Status: Complete; working-tree Doc identifiers/emails redacted, README corrected, scanner extended.
Artifacts (every file changed by this task):
- CCC_MASTER_SPEC.md
- docs/spec/12_paper_and_drive.md
- ops/reports/PUB-001_early.md
- paper/author_checklist.md
- paper/outline.md
- ops/RESUME.md
- ops/reports/BOOT-001.md
- scripts/secret_scan.py
- README.md
- ops/CLAIMS.md
- docs/release/CHECKLIST.md
- ops/reports/REL-ENH1.md
Validation: Python in-memory exact-ID search/replacement over `git ls-files -z`: three IDs, five files, no additional occurrences; targeted email-only substitutions. AST-loaded scanner rules over every tracked working file: 0 Doc-ID flags; synthetic positives and token-length checks pass. `git diff --check` passes. Headline numbers checked against CLAIMS_LEDGER.md C1–C3/C13/C20/C30/C31 and v3 CORRECTION.md. Clean temporary tracked-input extraction, `shasum -a 256 -c docs/runner/archives/exp002-live.tar.gz.sha256`, and `/usr/bin/python3 -I review/reproduce_headline/independent.py --input <temporary>/exp002-live`: PASS; Delta 1.354325711018899, p 0.0703125, 8 pairs. README puts the stdlib path first.
Scan: `/bin/zsh scripts/secret_scan.sh`: 3,595 blobs; 0 working-tree Doc-ID flags; exit 1 solely for three unchanged staged blobs (CCC_MASTER_SPEC.md, docs/spec/12_paper_and_drive.md, ops/reports/PUB-001_early.md), rules 6/7; no exact-credential matches. Host denied nice priority adjustment.
Limitations: Index/history untouched; concurrent ops/tasks.json changes are not mine. Full starter/venv reproduction not rerun. Visibility copied from SEC-001, not queried. No ignored targets edited, network, commits, staging, or model/API experiments.
Budget: $0 new spend; Codex GPT-6 agent, no external inference.
Next: Integration custodian reviews/stages redactions and reruns scanner; owner decides visibility, history, and release.
