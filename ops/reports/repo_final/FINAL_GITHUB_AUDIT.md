# Final GitHub technical and visual audit

Repository: https://github.com/Barap1/Counterfactual-Collusion-Certificates

The owner requested a progress update, smaller README graphics, further text refinement, and a final technical/visual GitHub audit. This pass follows the initial overhaul review in `REVIEW.md`.

## Outcome

The README now uses compact diagrams rather than full-height posters. Both are capped at 600px wide. Allocation SVG: 640×536, down from 640×1180. Evidence SVG: 640×246, down from 640×578. Combined desktop display height is about 734px rather than 1758px, a 58% reduction. Primary diagram text is at least 24 SVG units for phone readability. Scientific values and conclusions are unchanged.

The prose was tightened from approximately 920 to 852 words, excluding alternative text/markup. It preserves all required negative findings, the distinction between scripted policies and real agents, the post-hoc deterministic restriction and unresolved noisy-condition disagreement. The introductory example still explains why message removal is insufficient and why the cost probe separates this specific pair.

## Live visual audit

Inspected the actual public GitHub README in Chrome, not only a local approximation:

- Desktop viewport 1280×900: both images loaded at 600×503 and 600×231; complete shared evidence, probe arrows, policy responses, numeric labels and takeaway visible without clipping.
- Phone viewport 390×844: GitHub's content column renders images at 324×271 and 324×125; document scrollWidth equals viewport width (390), with no horizontal page overflow. The 24-unit minimum text refinement was inspected at the same image size before publication; the final publication check uses these same dimensions.
- Text carries policy meaning alongside color. SVGs retain live editable text, accessible title/description and descriptive README alternative text. Light figure panels retain high contrast on GitHub's dark background.
- The results table, methods transition, reproduction block and navigation remain readable in the phone column. No decorative badges, fake paper control or final PDF link was added.

The browser's file-URL restriction remains a tooling limit; no workaround was attempted. The existing explorer was verified over a local-only HTTP server during the initial audit, including P2 I2/I4, Study, a real-agent case and phone layout.

## Technical audit

Independent report: `compact-technical-audit.md`. Scientific review and resolution: `compact-science-audit.md`.

- Public default branch `main` independently matched compact content commit `2c6a78d527ea935beeee556bdac0a36a65edbff0`. Both Python 3.12/3.14 jobs passed in [CI run 40239473489](https://github.com/Barap1/Counterfactual-Collusion-Certificates/actions/runs/40239473489). The final small font/checker/receipt follow-up is validated locally and its latest CI is checked before owner handoff.
- `python3 scripts/check_artifact.py`: 15 public reading-path pages, 109 links/anchors and both SVGs pass. It now checks HTML image paths and meaningful alternative text as well as Markdown links.
- Headline reproduction still returns Delta `1.354325711018899`, eight pairs and exact sign-flip p `18/256 = .0703125`.
- The 11 independent arithmetic tests and eight explorer source/hash tests pass again. No full-suite repeat is needed for this documentation/SVG refinement; the initial 500-pass/4-skip/351-subtest guarded run remains recorded.
- Both SVGs regenerate from their authoring source. Final checks compare all 16,992 protected scientific files byte-for-byte with the retained preservation map; no changes.
- No paper PDF or DOCX exists in the current public tree. No final PDF was generated, copied, added or uploaded.
- Fixed a future maintenance defect found in audit: the link checker now permits a PDF link after the owner supplies the real target, while still rejecting missing targets. Mocked existence checks covered both paths without creating any PDF. The owner only needs to add `paper/paper.pdf` and the documented README link.

## Repository hygiene

Only remote branch `main` remains. PR #1 was closed as superseded after its useful setup/missing-input notes were consolidated. No open issues, milestones or PRs require cleanup. Description, topics and homepage match the research artifact. No protections were weakened and no public history was rewritten.

Earlier manuscript drafts, frozen negative results, preregistration, correction notes and necessary figure sources remain recoverable. Redundant submission renders were removed from the public tree; root planning material was moved to `docs/archive/planning/`. Unpublished local final PDFs/template exports were excluded from the consolidation history. Recovery bundle: `/private/tmp/ccc-repository-overhaul/pre-overhaul.bundle` (local only; do not push wholesale).

## Boundaries that remain

Upstream adaptation/scenario/trace redistribution permissions and historically exposed document access still require owner attention. A current-tree pattern scan is not historical privacy clearance. The public tree lacks 18 legacy pilot traces and the excluded pinned upstream environment; complete fresh-install/model regeneration is not claimed. Final PDF and paper submission remain owner actions. These are retained limitations, not hidden or marked resolved by repository cleanup.
