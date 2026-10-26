# PAPER-PDF-RELEASE

Task: add the owner-provided final PDF to the repository and push it. Authorized by the owner on October 26, 2026. No active competing lease was recorded for the release paths.

Artifacts: `paper/paper.pdf`, plus navigation updates in `README.md`, `paper/README.md`, and `CCC_START_HERE.md`. The supplied Google Docs PDF export was copied without editing or regeneration. Unrelated working-tree changes were excluded.

File evidence:

- Title: When Cooperation Looks Like Collusion: The Limits of Counterfactual Auditing in Multi-Agent AI
- 16 letter-size pages; 909,171 bytes; unencrypted; no PDF JavaScript.
- SHA-256: `ff54ae5dd431373ca1bc904c2f5f862f42f23803c86e197963d24716afd37039`
- Source and destination bytes compared equal.

Validation commands:

```sh
pdfinfo paper/paper.pdf
pdftoppm -f 1 -l 1 -r 100 -singlefile -png paper/paper.pdf /private/tmp/ccc-final-paper-first-page
python3 scripts/check_artifact.py
git diff --check
```

Results: source/destination equality, PDF parsing, first-page rendering and visual inspection passed. Artifact navigation checks passed for 15 pages, 118 local links/anchors, four SVG variants and the new README PDF link. Whitespace checks passed. No code changed, so no implementation regression tests were needed.

Limitations: this release does not constitute a new scientific audit or full pagination review. Frozen data and the live Google Doc were not changed. No experiments or new spending.

Next: publish the scoped commit with a normal fast-forward push; the final response records its actual SHA and push status.
