# CCC submission: owner decisions checklist

Prepared by PUB-001 (early) on 2026-10-23. Agents **must not** infer or decide any item below (spec 12, "Authorship and human responsibility"). None of this blocks engineering. These are finalization gates.

Deadline: **Sun 25 Oct 2026, 23:59 AoE = Mon 26 Oct 2026, 11:59 UTC**. Owner review package target: 26 Oct 01:00 UTC (ops/STATUS.md).

## A. Authorship (required by the sprint page: names + affiliations)
- [ ] Author full names, as they should appear. *Not inferred from the Git profile, filesystem or email.*
- [ ] Affiliation for each author, or "Independent".
- [ ] Author order.
- [ ] Team name / contact fields for the submission form.
- [ ] Keep or remove the template's "With Apart Research" box.
- [ ] Optional Author Contributions paragraph: include it, and who did what.
- [ ] Confirm that no listed person is on more than two sprint projects (sprint rule).
- [ ] Consent to publication from every listed author.

## B. Title and track
- [ ] Final title. Working candidate: *Counterfactual Collusion Certificates: Auditing Harmful Coordination Without Confusing It with Cooperation* (may be revised to match the realized finding). Note that a resubmission must use the **exact same title** to replace the earlier one.
- [ ] Track: Track 2 (Detection and Audit), Q2.3 primary. Confirm with the owner.

## C. LLM-use disclosure (template "LLM Usage Statement")
The sprint page requires no AI-use statement, but the template includes one, and the team is responsible for everything in the report. Choose or approve the wording:
- [ ] Which tools to name: Claude Code (Claude models, used for planning, orchestration, implementation, analysis assistance and drafting); Codex (only if it was actually used; currently unused per STATUS); any others.
- [ ] Which parts the humans wrote or rewrote. The template strongly encourages the final version to be primarily written by the team.
- [ ] The extent of human review. **Do not** state "independently verified by humans" unless that review actually happened. Suggested neutral draft for the owner to edit:
  > "We used Claude (via Claude Code) to help plan the study, implement and test the audit harness, run analyses and draft sections of this report. [Owner: describe the actual human review and rewriting here.] The authors take responsibility for all claims, figures and references."
- [ ] Disclose that the tested agents use LLMs (model IDs per the final run config). This is separate from authoring assistance.

## D. Prior-work disclosure (sprint rule: undisclosed prior work can lead to disqualification)
- [ ] Confirm which code and materials predate the sprint (organizer starter, the archived seed-1 pilot, the spec/PRD and the Deep Research report) and how they are labeled in the report and README.

## E. Google Doc sync (working copy `CCC - Counterfactual Collusion Certificates - Submission Working Draft`)
- [ ] **Approve PUB-001 writing to the working copy** once the claims are frozen. Writes are revision-aware, a local backup is taken first, and the template structure is preserved.
- [ ] Confirm no sharing changes. The working copy currently has the owner as its only listed owner. Sharing was not inspected or changed in this phase.
- [ ] Note: the connected Drive account also reports **edit** access to the *official* Apart template (`1Y5wd3VR…`, owned by apartresearch.com). Agents will never write to it. Please be aware of this as well.
- [ ] Approve or deny including private Doc IDs in any public artifact (default: omit).

## F. Public release and optional artifacts
- [ ] Public GitHub repo: yes or no, and when (optional per the sprint page).
- [ ] 3–5 minute video demo: yes or no, and who records it (optional).
- [ ] Optional slides and project image.

## G. Final review and submission (owner only)
- [ ] Review the final claims, figures, abstract and limitations/dual-use appendix.
- [ ] Visually inspect the exported PDF, or accept the agent's page-by-page render check.
- [ ] **Explicit approval to submit.** Agents will not click submit, agree to terms or upload anything.
- [ ] Accept the submission form terms (owner only).
