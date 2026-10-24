# CITE-CHECK handoff
**Task:** Verify every reference and claim-citation pair in paper/v2/draft_v2.md (20 refs).
**Status:** Complete.
**Artifacts:** paper/v2/references_v2.bib (20 verified entries, each noted "verified 2026-10-24"); paper/v2/CITATION_AUDIT.md (bibliographic table + claim table); this file.
**Validation:** arXiv abs pages for all 19 arXiv items; full text (PDF/HTML) for refs 1-7, 11, 12; AEA page for Calvano; web search for JAIR venue. All previously uncaptured authors resolved: [7] Zhang, Emu; [15] Shah; [16] Arslan; [18] Pona et al. Everitt and Ward author lists confirmed. Key results:
- MISREPRESENTED: sentence citing [19, 20]. Lopes de Moraes finds impulse responses do NOT identify punishment ("over-determined rather than selective").
- FIX: Ward/Everitt "depend on the observer's causal model" is overstated (Everitt says nothing on intent/observers). "[6, 8] argued informally for indistinguishability": only [6] says it; [8] names the boundary problem. [16] "disclosed deviations" not verified. Ref [7] title/author text needs updating.
- REMOVE or cite: [4] is never cited in the body.
- OK with quotes: Colosseum (Jira DCOP, "collusion is not always harmful"), Tran and Yu (shared seeds, A/A, placebo, positive control, exact "punisher" quote), 2607.26773, 2607.26385, 2608.18078, 2601.00360, 2609.18346, VLA.
**Limitations:** Refs 8-10, 13-18 checked against abstracts only; Calvano forced-deviation method not seen first-hand; Tran and Yu read to char 100k of 214k. Riemer abs page shows submission 29 May 2026 despite id 2608 (oddity, unresolved).
**Budget:** $0; about 35 web fetches/searches; no Firecrawl; model Sonnet 5.5. Temp PDFs only in /tmp/cc_txt.
**Next:** Director applies the FIX rewordings in draft_v2.md, drops the CITE-CHECK tags, and swaps the reference list for references_v2.bib.
