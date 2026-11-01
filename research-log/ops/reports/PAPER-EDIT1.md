# PAPER-EDIT1 handoff

**Task** Apply CITATION_AUDIT fixes, update Methods/Results templates to frozen R2 protocol (D-040, D-041), build pipeline for paper v2.

**Status** Done. Prospective placeholders untouched except template updates.

**Artifacts** paper/v2/draft_v2.md (edited); paper/v2/make_v2.py (new; `--figdir`, default figures/enh/dev; `--figheight`, `--no-pdf`); paper/v2/build/{submission_v2.md,.html,.pdf,build_report.json}.

**Validation**
- Citations: all FIX/REMOVE verdicts applied ([19,20] reworded, Ward/Everitt, [6,8], [16], Zhang and Emu [7], [4] now cited, authors filled, venues added). Reference list regenerated from references_v2.bib only; 0 CITE-CHECK tags.
- Methods: CCC-L v1 (adds "L3 excluded", DEV-informed, v0 also reported); RQ2 method-independent; RQ4 verbatim plus RQ4b; RQ3 <25% with DEV 12/80 (Gate A), 12/50 (eps 0), 5/50 (eps 0.1); REV-R2 C2-C4 stated. {{RQ4b}} template added; RQ2/RQ3/RQ5 templates updated.
- Evidence tags all kept; [OWNER] placeholders kept (4 distinct).
- Pages (headless Chrome, letter, 1in margins, 11pt): total 18. Main text through Code and Data = about 7.8 pages (ends bottom of p8); References p9; appendix p9-18. Requires <=8: met, but with about 1 inch slack.

**Cuts to meet the limit** Moved to appendix: twin-pair table, seeds, metrics, stopping rule, full methods list (App E); RQ result templates (App E); S1-S3, sham, accounting, metadata repair (App F); 5.2 detail (F); extended related work (A). Frontier and risk figures moved to appendix (A9-A10). Figures capped at 1.9in. References set at 9pt.

**Limitations**
- Filling the seven RQ sentences adds roughly 0.4-0.5 page; expect overflow past 8 unless more is cut (candidates: Section 2, 5.1 secondaries, Intro). If references count toward 8, total is about 8.8 pages.
- Abstract/intro twin numbers (3.1) are still illustrative (editor comment retained in draft, not rendered).
- Rendered figures are DEV-labelled; rebuild with `--figdir figures/enh/<run>` after R2.
- Appendix planning sections G/H are not rendered.

**Budget** $0, offline, Claude Sonnet.

**Next** Fill {{...}} from frozen results, rebuild, recount pages, owner choice of title.
