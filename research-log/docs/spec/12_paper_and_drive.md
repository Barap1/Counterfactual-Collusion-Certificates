# 12 - Paper, Google Docs destination, and submission workflow

## Required research artifact

Use the official submission template. The event requires a PDF of no more than eight main pages excluding references/appendices, a 150-250 word abstract, author information, and a Limitations and Dual-Use / Ethical Considerations appendix. Code and a 3-5 minute recording are optional. The written report is the central artifact. [S01](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25)

The owner's template copy recommends four pages; that is a recommendation, not a different hard cap. Aim for approximately four to six main pages of strong evidence; expand toward eight only when it improves the argument. Do not shrink fonts or crowd figures to rescue a sprawling report.

## The actual document target has already been prepared

The original template in the owner's Drive was found and copied during specification preparation. The original is left unchanged. The working copy remains template content; final research results have **not** yet been written into it.

Original owner template:

```text
ID: [REDACTED-DOC-ID]
[REDACTED-DOC-ID]
```

Prepared working destination:

```text
Title: CCC - Counterfactual Collusion Certificates - Submission Working Draft
ID: [REDACTED-DOC-ID]
[REDACTED-DOC-ID]
```

The copy was verified as not shared at preparation time. Do not change sharing or create repeated new copies. Store these identifiers in `ops/doc_target.local.json` for the local workflow. They are not credentials, but omit private working-document identifiers from a public release unless the owner approves their inclusion.

### Local access is a separate capability

The fact that this ChatGPT session accessed Drive does not mean Claude Code inherits that connector or authorization. BOOT-001 must discover an authenticated local Drive/Docs tool or permitted browser workflow. Use the exact known document ID; never search broadly through unrelated private files just to find a substitute.

If access is missing, continue producing `submission/paper.md`, figures, reference data, and an importable document package locally. Mark `DOC_SYNC_PENDING` and ask once for the necessary connection when the paper is ready for synchronization. Do not report a Google Doc update that did not happen. Do not put account passwords or OAuth tokens in the PRD or agent prompts.

## Paper outline and page economy

1. **Introduction:** one concrete false-positive/evidence problem, why it matters, and two or three actual contributions.
2. **Related work:** closest prior intervention/audit methods, explicit overlap, and the narrow gap tested here.
3. **Methods:** operational harm definition, checkpoint/exposure boundary, branch arms, validity checks, experimental tiers, sampling hierarchy, and analysis.
4. **Results:** actual measured findings with the smallest set of readable figures/tables needed to support them. Separate mechanism fixtures from real-agent case studies.
5. **Discussion and limitations:** where the audit helps, where it abstains, inaccessible state, information-loss confounds, model/sample limits, and feasibility costs.
6. **Conclusion:** the supported takeaway, not the original aspiration.
7. **Code/data, references, required ethics appendix, and LLM-use statement.**

Draft the methods and limitations early, but write the final abstract and conclusion after the results are frozen. Keep expected results out of the paper. Empty placeholders are acceptable in a working draft but forbidden in the final exported submission.

## Claims-to-prose pipeline

The publication worker consumes `ops/CLAIMS.md`, frozen aggregate outputs, figures, and verified source records. It must not infer a result from a worker's enthusiastic summary. Every quantitative sentence should point to a named table field, analysis version, and sample definition.

Use language such as "in this controlled setting," "under the tested intervention," "we observed," and "the estimate was inconclusive" where appropriate. Do not call prompted behavior spontaneous. Do not substitute "collusion" for every use of coalition advantage. State whether the method needs a known suspected pair and access to an executable simulator.

The final paper should clearly distinguish preexisting organizer code, the archived setup pilot, and new sprint contributions. Attribute upstream code and observe licenses. The source list must use actual author/title/year/version metadata and working links, not unresolved chat citation tokens.

## Authorship and human responsibility

Do not infer author names or affiliations from a filesystem username, Git profile, or unrelated memory. Prepare a concise owner confirmation checklist for names, affiliations, author order, team/contact fields, publication consent, and final submission approval. This is a finalization gate, not a reason to halt engineering.

The template includes an LLM Usage Statement and encourages the human team to take responsibility for the final writing. Describe the actual use of Claude/Codex for planning, implementation, analysis assistance, and drafting. Do not state "independently verified by humans" unless that review actually occurred. The owner should review the final claims, figures, and abstract before submission.

## Safe Google Docs editing

Only the publication worker writes the document. Read its latest content and revision before editing. Preserve the template's meaningful structure and formatting. Replace guidance placeholders with the approved content, remove unused author placeholders and instructional boxes, and insert figures with legible captions. Avoid deleting the whole document and rebuilding it as unformatted text.

Use revision-aware writes where supported. If the owner edited concurrently, re-read and reconcile instead of overwriting. Save a local text/export backup before major replacements. Do not use publicly hosted private figures solely to satisfy an image-insertion API if a local/connector upload route exists.

After synchronization, re-read the document and compare critical numeric values, references, headings, and figure captions with the approved local draft. Record the document ID, revision/time, analysis manifest hash, and final export hash.

## PDF quality assurance

Export the actual working Google Doc to PDF, then render and inspect every page. Verify main-body length, abstract word count, figure legibility, equation rendering, table breaks, reference links, required appendix, and absence of template instructions. A text-only extraction is not enough to catch clipped plots or bad pagination.

If the local tools cannot inspect the exported document, mark that step unverified and request the owner's visual review rather than claiming it passed. Keep the source draft, synchronized document, and submitted PDF version aligned.

## Submission handoff

Prepare `submission/SUBMIT_CHECKLIST.md` with the final PDF path/hash, exact title, abstract, track, author details awaiting confirmation, code/demo links if authorized, required declarations, and the deadline. Do not click final submit, publish a private repository, change Drive sharing, or agree to terms without the owner's explicit authorization for that action.

A local finished PDF is valuable even if Drive sync is blocked. A synced Google Doc is not a completed submission. Report those states separately.
