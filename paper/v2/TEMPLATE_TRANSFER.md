# Owner template and artifact handoff

The current Apart Guidelines and the actual linked official template were inspected on 2026-10-25. The template was opened anonymously, read-only, and exported for inspection; it was never edited, copied into the owner's Drive or synchronized. Access receipt, format properties and source hash: `ops/reports/final_audit/paper/official_template_export.json`. Screenshot: `official-template.png` in that directory.

Guidelines source: https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25 (Guidelines → official template). Follow that link for the current template rather than an old email. Deadline: October 25 at 23:59 AoE, equivalent to October 26 at 11:59 UTC. PDF upload maximum: 25 MB.

## Requirements and current status

| Item | Official requirement or observed template | Local candidate / owner task |
|---|---|---|
| Format | PDF using linked template; section structure adaptable | Local adaptation uses the inspected font, title treatment and margins; owner template approval or transfer remains required |
| Length | At most eight pages excluding references/appendices | Main text pages 1–8; references page 9; appendices start page 10; rerun checks after owner edits |
| Abstract | 150–250 words | 207 whitespace-delimited words |
| Title block | Centered 20pt bold Old Standard TT; author/affiliation fields; With Apart Research; sprint note | Title preserved; author/affiliation remain `[OWNER]`. Do not infer them from Git metadata |
| Body | Observed Old Standard TT 11pt; 468pt content width; 72pt margins; template body examples use 1.15 line spacing | Same font/size/width/margins; local body uses single spacing and 4pt paragraph gaps, a documented adaptation requiring owner approval |
| Headings | Observed section 14pt, subsection 13pt; consistent numbered sections | Matched; methods/evidence standard and discussion/limitations separated where useful |
| Figures/tables | Numbered; descriptive captions; near first reference; legible | Main figures 1–3 have readable versions; original and detailed appendix figures remain. Dense appendix matrices/curves are owner graphics-polish items |
| References | Consistent style; authors/year/title/venue/URL or DOI | Twenty numbered entries regenerated from BibTeX. Citation review limits are in audit report |
| Ethics appendix | Guidelines require Limitations and Dual-Use / Ethical Considerations, despite generic template's optional appendix heading | Appendix A retained; dual-use/release sign-off requires owner |
| LLM use | Describe actual assistance; claims remain team's responsibility | Statement retained with approval tag; human verification has not been invented |

## Clean transfer package

- Text with numbered references and final figure captions: `paper/v2/build/submission_v2.md`.
- Self-contained figure HTML with local fonts: `paper/v2/build/submission_v2.html` (keep `paper/v2/fonts/` relative to it).
- Editable manuscript: `paper/v2/draft_v2.md`. Its internal H figure-plan section is deliberately omitted by the builder; never transfer that editorial section.
- Bibliography: `paper/v2/references_v2.bib`; numbering in `make_v2.py:REF_ORDER`.
- Main figures: `paper/v2/figures/fig_ladder_audit.svg`, `fig_twins_audit.svg`, `fig_heldout_delta_audit.svg`, each with provenance JSON.
- Corrected appendix annotations: `fig_gateA_integrity_audit.svg`, `fig_prevalence_audit.svg` in the same directory. Original SVGs and all plotted data are preserved.
- Other appendix figures: original paths listed in `make_v2.py:FIGS`; full source hashes are in `build/build_report.json`.
- Font files: unmodified Old Standard TT faces and full OFL 1.1 license in `paper/v2/fonts/`.
- Candidate PDF: `paper/v2/build/submission_v2.pdf`. Source freshness is verified by hashes, not the file's mere presence.

## Exact local build

From repository root, with existing Chrome installed:

```sh
python3 paper/v2/prepare_audit_figures.py
python3 paper/v2/make_v2.py --figdir figures/enh/prospective
python3 paper/v2/make_v2.py --check
pdfinfo paper/v2/build/submission_v2.pdf
pdftotext -layout paper/v2/build/submission_v2.pdf /tmp/ccc-submission.txt
pdftoppm -r 150 -png paper/v2/build/submission_v2.pdf /tmp/ccc-page
```

Chrome required an execution context permitting macOS browser processes in this audit; the restrictive tool sandbox caused SIGABRT even with an isolated profile. The successful build used the same command outside that sandbox, a fresh temporary profile, existing Chrome and no installation. `--chrome /path/to/existing/chromium` selects another existing executable. The browser log is retained in `build/renderer.log`.

A failed build removes the candidate PDF, preserves the previous file under content-addressed `build/history/`, writes `pdf_current:false` and leaves Markdown/HTML available. `--no-pdf` also invalidates the candidate; it cannot bless an old PDF. Run `--check` again after any source, font or figure change. This validates freshness, not final human visual approval.

Owner: transfer into a personal copy of the official template if exact native-template formatting is desired. Remove owner approval tags only after completing those decisions. Recheck the eight-page boundary and all figures after transfer. Never overwrite the official template.
