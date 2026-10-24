# PUB-001 (early phase) report

**Date:** 2026-10-23, about 17:15 UTC. **Scope:** read-only Drive check, template requirements, paper skeleton. No results exist. **Spend:** $0. The only network calls were free: the Google Drive connector (metadata and content reads), a WebFetch of the sprint page, the arXiv API and the Crossref API.

## 1. Google Docs working copy: FOUND, read-only access verified
Tool: the claude.ai Google Drive connector (`get_file_metadata` and `read_file_content` only). There were no writes, no sharing reads or changes, no new files and no broad searches; only exact IDs were queried.

| Field | Working copy | Official Apart template (S01 link) |
|---|---|---|
| Title | CCC - Counterfactual Collusion Certificates - Submission Working Draft | Apart Research hackathon submission template |
| ID | `1zsYXLll5dKl4MmCcXI0WwFp1ThiKDxkDKQsPDX3rSHM` (matches module 12) | `1Y5wd3VRbXU5N08BvAGiJUQTaWbMCSPjhzXsR-ozuehg` |
| Owner | aarav.patel280@gmail.com | kamil@apartresearch.com |
| Created / modified | 2026-10-23T15:31:23.120Z / **same, so unedited since copy** | 2026-09-21T14:50Z / 2026-10-22T13:37:56Z |
| Size | 8519 | 8519 (identical snippet) |
| Revision ID | not exposed by the connector. Use modifiedTime as the revision anchor before the first write. | — |

- The working copy is still pure template content: placeholder title, six author cells, the guidance box and the italic guidance under each section. No CCC content has been written yet.
- Template structure: title + authors + "With Apart Research" + Abstract (150–250 words) → info box (recommended length **4 pages** excl. refs/appendix; 1p Intro+RW, 2.5p Methods+Results, 0.5p Discussion; links the rubric https://apartresearch.notion.site/sprint-evaluation-rubric) → 1 Introduction (with a "Our main contributions are" list) → 2 Related Work → 3 Methods → 4 Results (figure tips) → 5 Discussion and Limitations (### Limitations, ### Future Work) → 6 Conclusion → Code and Data → Author Contributions (optional) → References → Appendix (optional) → LLM Usage Statement.
- The original owner template (`16N0Us…`) was not opened in this phase, as it was not needed.
- ⚠ The connector reports `readOnly:false` on the **official Apart template**, which means the owner account appears to have edit rights on it. It must never be written. This is flagged in the author checklist.
- `ops/doc_target.local.json` does not exist yet. Module 12 says to store the IDs there. That path is outside this phase's owned paths, so creating it is left to the director. It is git-ignored via `*.local.json`.
- Doc sync status: **access available; writes not yet approved (DOC_SYNC_PENDING owner approval + GATE-C).**

## 2. Official requirements (sprint page fetched 2026-10-23)
- **Deadline reconfirmed:** "Sunday, October 25 at 11:59 PM AoE" = **2026-10-26 11:59 UTC**. This matches STATUS.
- A PDF report using the official template; **max 8 pages excluding references and appendices**; title and an abstract of **150–250 words**; **author names and affiliations**.
- **Required appendix: "Limitations and Dual-Use / Ethical Considerations"**, covering what the work does and does not establish, and any way it could make collusion easier or harder to detect. **The template has no section for it, so we must add one.** The outline includes it as Appendix A.
- **LLM use:** the sprint page does not require a statement ("use AI tools however they help you"; the team is responsible for all content; fabricated results or references can disqualify). The template *does* include an LLM Usage Statement section and encourages the team to write the final version themselves.
- Optional: a public GitHub repo, a 3–5 minute video, slides and an image. Uploads are capped at 25 MB each.
- Preexisting work and code must be disclosed (in the README and the report). Resubmitting with the exact same title replaces the earlier files. A person can be on at most two projects.
- Rubric (1–5 each): Impact Potential & Innovation; Execution Quality; Presentation & Clarity. Track 2, Q2.3 ("What should count as convincing evidence of collusion?") is confirmed verbatim.

## 3. Files written
- `paper/outline.md`: template-ordered skeleton. It contains the narrowed contribution statement (claim_review §1), drafted related-work prose (verified sources only; V-meta sources used only at abstract level), Methods TODOs keyed to SCI-002/ENG/FIX/STAT tasks, labeled `[RESULT-PENDING: …]` result slots, the required appendix, and a pre-export checklist. **It contains no results.**
- `paper/author_checklist.md`: owner decisions (authorship, title/track, LLM disclosure wording, prior-work disclosure, Doc sync approval, public release, submission approval).
- `paper/references_draft.bib`: 43 entries, consisting of 40 arXiv + Calvano 2020 (AER, DOI) + the S01 sprint page + the S02 starter repo. Inclusion rule: ledger V-meta or V-text only. Full author names, titles and the latest versions were re-pulled from the arXiv API and Crossref. All surnames match the ledger. **Excluded:** R09 (UNVERIFIED), L25 (V-partial, author conflict), and L05 (V-meta, but the ledger says its author list has not been re-checked). Unconfirmed venues (P03 NeurIPS, R02 CHI, M01 ICML) are cited as arXiv only.
- All 18 citation keys used in the outline resolve to bib entries.

## 4. Notes for later PUB-001 phases
- Version updates found via the API: P02 is at **v5** (spec 18 cites v3), P05 at v2, P09 at v2, P06 at v2, P03 at v2, L01 at v3 and R01 at v3. The P01 title contains an API typo ("Co ordination"), which has been normalized.
- The residual novelty re-check (claim_review §4) is still owed before submission. P01 and P04 need full method-section reads before any quote is used.
- Before the first Doc write: re-read the doc, compare modifiedTime against 2026-10-23T15:31:23.120Z, and take a local export backup.
