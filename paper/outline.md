# CCC paper outline (PUB-001 early, working skeleton)

**Status:** working skeleton from 2026-10-23. **No results exist yet.** Every quantitative or empirical slot is a labeled placeholder. Nothing here is a finding.
**Template:** this follows the official *Apart Research hackathon submission template* (Drive ID `[REDACTED-DOC-ID]…`). The prepared working copy is a verbatim instance of that template (see `ops/reports/PUB-001_early.md`).
**Authoritative inputs:** `docs/research/sci001/claim_review.md` (allowed and forbidden claims) and `source_ledger.md` (citable sources). Citation keys refer to `paper/references_draft.bib`.

### Placeholder grammar (to be removed before export)
- `[RESULT-PENDING: <task> <artifact/field>]`: a number, figure or table that can come only from frozen analysis output. These are filled by STAT-002 or VIS-001 and must trace to `ops/CLAIMS.md`.
- `[TODO(<task>): …]`: method details that depend on SCI-002, ENG-00x, FIX-001 or STAT-001 decisions.
- `[CONTRIB-PENDING]`: contribution wording that depends on what is actually implemented and tested. Delete any element we do not implement. The sham arm and the benign fixtures are the first at risk.
- `[OWNER]`: an owner-only decision (see `paper/author_checklist.md`).

### Hard requirements (official sprint page, rechecked 2026-10-23)
- The report is a PDF using the official template, **≤ 8 pages excluding references and appendices**. The template recommends 4 pages (Intro + Related Work 1p, Methods + Results 2.5p, Discussion 0.5p). Our target is **4–6 main pages**.
- Title, plus an **abstract of 150–250 words**, written last, after the results freeze.
- **Author names and affiliations** [OWNER].
- **Required appendix: "Limitations and Dual-Use / Ethical Considerations"**. It must cover what the result does and does not establish, and whether the setup or findings could make real-world collusion easier to carry out or harder to detect. *The template has no section for this. We must add it.*
- Prior work and preexisting code must be clearly identified. Undisclosed prior work can lead to disqualification. Fabricated results or references can disqualify.
- Optional: a public GitHub repo and a 3–5 minute video [OWNER approval for anything public].
- Deadline: **Sun 25 Oct 2026, 23:59 AoE = Mon 26 Oct 2026, 11:59 UTC.** A resubmission with the identical title replaces the earlier files.

---

## Title block

- **Title:** [OWNER] Working candidate from spec 01: *Counterfactual Collusion Certificates: Auditing Harmful Coordination Without Confusing It with Cooperation.* Revisit after the results: if the fallback claim (§3 of claim_review) becomes the headline, retitle toward that finding. Avoid "proves" and "detects collusion".
- **Authors / affiliations:** [OWNER]. Delete the unused template author cells. Keep or remove the "With Apart Research" box per owner.
- **Abstract (150–250 words, write LAST):** [RESULT-PENDING: STAT-002 frozen headline + REV-001 sign-off]. Required beats: problem (message-removal evidence can mislabel teamwork), approach (validity-gated fork/mask/sham audit with four verdict states), key results [RESULT-PENDING], takeaway with scope ("in this controlled setting…").

## 1. Introduction (~0.6 p)

**Problem (one concrete example).** Track 2.3 asks what should count as convincing evidence of collusion. A natural audit removes a suspicious message and checks whether the outcome changes. But useful teamwork is also communication-dependent. If one agent shares task costs or its availability, removing that message changes the outcome too. Knockout magnitude alone therefore cannot separate harmful coordination from legitimate cooperation. [TODO(FIX-001): use the actual benign fixture as the running example once it exists. Do not describe an example we do not run.]

**Why it matters.** Auditors of replayable multi-agent deployments need evidence that (a) survives a valid intervention, (b) is tied to a declared harm rather than to coalition advantage alone, and (c) abstains when the evidence is insufficient. Colosseum notes that "collusion is not always harmful" and that it "remains unclear which qualitative factors yield efficient yet non-collusive communication" [nakamura2026colosseum]. We target that gap at the level of individual exposures.

**Scope stated up front.** The method requires an executable, checkpointable simulator and a declared suspected exposure (a sender → receiver message). It does not apply to immutable production logs alone. Our "certificate" is an *evidence record* with explicit preconditions. It is not a proof, a legal finding or an intent detector. Define the term at first use.

**Our main contributions are** [CONTRIB-PENDING. Use the permitted form: "We contribute a reproducible audit protocol that combines [features actually implemented] and evaluate its failure modes on [tasks actually tested]."]:
1. A validity-gated counterfactual audit protocol for communication in replayable, tool-using LLM agent teams, instantiated on Colosseum. It forks at the receiver's earliest exposure and regenerates fresh continuations under factual, receiver-masked and sham arms. It estimates the change in a predeclared harm outcome separately from coalition advantage and task-utility loss, and issues *supported / not supported / inconclusive / invalid* records. [CONTRIB-PENDING: delete any arm or check not implemented]
2. An evaluation against harm-gated knockout and single-step-influence baselines on controlled fixtures that include **benign causal cooperation as hard negatives**. [RESULT-PENDING: STAT-002, primary comparison]
3. [CONTRIB-PENDING: choose one, according to the evidence] (a) a quantified replay-validity failure taxonomy for naive knockouts in Colosseum; or (b) an abstention reason distribution on real Colosseum cases; or (c) the released harness alone (the weakest option, but honest).

Do not use "first", "novel technique", "proves", "detects intent", "guarantees low FPR" or "generalizes to frontier agents" (claim_review §2).

## 2. Related Work (~0.5 p)

*Draft prose. Every sentence is drawn from `claim_review.md` §1 and uses only ledger-verified sources. V-meta sources support abstract-level statements only.*

**Interventional collusion audits.** Counterfactual intervention is already established as evidence of collusion. In algorithmic pricing, forced deviations and impulse responses separate reward-punishment schemes from merely high prices [calvano2020artificial]. Recent work shows that this test can be non-selective, because a forced price *increase* triggers the same retaliation as an undercut [lopesdemoraes2026deterrence]. Counterfactual-copy audits for LLM market agents force one agent to deviate in a cloned market [tran2026enforcing]. They argue that outcome measures cannot distinguish enforced collusion from look-alikes, but an intervention can. That work intervenes on *actions*, not messages. Controlled peer interventions give population-level causal evidence of collusion in long-horizon LLM interaction [shi2026emergent]. We therefore make no claim to be the first causal or interventional audit. We carry the selectivity concern over to message interventions.

**Message-level counterfactuals for collusion.** The closest work, VLA [kaur2026beyond], blocks or neutralizes a single private latent exposure with a matched neutral counterfactual and measures the shift in the receiver's action distribution. CCC extends this line in three ways. It intervenes on *text* exposures in tool-using teams. It regenerates multi-step continuations in every arm. Its evaluation targets legitimate causal cooperation as a source of false positives. Rose et al. [rose2026detecting] state a counterfactual communication-removal criterion for collusion and relax it because counterfactual simulation cannot always be assumed. They note that NarcBench-Core could in principle support it. CCC *operationalizes* a scoped, stochastic approximation of that criterion. Audit the Whisper [tailor2025whisper] applies per-utterance auditor interventions with fresh-seed calibration. Its honest baselines contain no legitimate cooperation, so its false-alarm results do not transfer to our setting.

**Testbed.** Colosseum [nakamura2026colosseum] measures collusion via regret against the DCOP optimum, coalition advantage and condition-level secret-channel contrasts. We build on its environment and metrics and attribute them. Our channel-level arm, if run, is a replication bridge, not a contribution. [TODO(SCI-002): confirm whether arm C is just Colosseum's existing control]

**Counterfactual replay in MAS debugging.** Remove/edit-and-replay is standard practice for failure attribution [cha2026zeroreplay; ma2025dover; epperson2025agdebugger; zhang2025agentracer; li2026repair]. These methods typically assume deterministic replay, and several find that more than one distinct intervention can repair a failure [ma2025dover; li2026repair]. CCC repurposes the technique for a harm-versus-utility estimand under *stochastic* resampling, with collusion-specific negative controls. It treats redundancy as "not identifiable" rather than "no effect".

**Influence ≠ collusion.** Counterfactual influence of one agent's messages on another is the basis of *pro-social* coordination objectives [jaques2019social]. Messages can be informative yet causally inert [lowe2019pitfalls]. Detectors can also be confounded by benign affinity [zhou2026cabal]. These results motivate our benign hard negatives and inert-talk/sham controls.

*Optional single sentence if space allows, abstract-level only:* covert and tool channels can escape text-level interventions [motwani2024secret; rippin2026tooluse]. This is a limitation we inherit (see §5).

[TODO(PUB, pre-submit): run the residual novelty check in claim_review §4 (an arXiv `collusion AND counterfactual` search from 23 Oct onward). Before any quote is finalized, someone must read the P01 and P04 method sections in full.]

## 3. Methods (~1.2 p)

### 3.1 Operational harm definition
[TODO(SCI-002): freeze **one** primary harm outcome h before the holdout. Candidates: (a) outsider loss conditional on coalition gain; (b) a drop in system utility versus a task-matched cooperative reference. State its units (Colosseum task-cost units, not dollars; see C-P03). Coalition advantage A is reported separately: A > 0 is not harm.]

### 3.2 Exposure, checkpoint and branch arms
- The exposure is a declared sender → receiver message, forked at the receiver's earliest exposure. [TODO(ENG-001/ENG-002): document the exact hooks, inaccessible state and how re-rendered copies (blackboard, memory, summaries) are handled]
- Arms: **F** factual regenerated · **M** receiver-masked · **S** sham/matched-harmless message (same sender and receiver, content-neutral, comparable length) · [optional **C** channel-level replication bridge] · [P1 **R** task-preserving repair]. [CONTRIB-PENDING: delete arms not run]
- Single-exposure versus persistent withholding: [TODO(SCI-002)]. Removing an informational exposure must be kept separate from removing an action with mechanical effects.

### 3.3 Validity gates
[TODO(ENG-002/SCI-002): deterministic F = S identity where applicable; the knockout changes only the declared exposure; isolation between branches; exposure-leakage check; protocol-corruption check; continuations are actually regenerated. Gate A is defined in `ops/STATUS.md`.] An invalid branch yields an **invalid** record, never a verdict.

### 3.4 Verdict rule
[TODO(STAT-001): the mapping from effect on h (with interval), the sham/variance floor, the utility-loss gate τ_W and validity status to *supported / not supported / inconclusive / invalid*. The operating point is chosen on development data only.]

### 3.5 Fixtures and real-agent case study
- Controlled fixtures with independently known mechanisms. At minimum: a benign causal-cooperation hard negative, a harmful mechanism with matched effect size, common-cause, inert-talk and invalid-replay controls. [TODO(FIX-001): labels must not be derived from CCC outputs]
- Real Colosseum worlds: [TODO(EXP-001/EXP-002): model ID and backend pinned, world seeds, candidate-exposure selection rule pre-registered]
- **Preexisting versus sprint work** (sprint rule): organizer code (Colosseum / `collusion_hackathon` @ [TODO(ENG): local revision]) is preexisting. The archived seed-1 pilot is a *prompted positive control used as development data only* and is not holdout evidence (C-P04 rejected). Everything else is new sprint work [TODO: enumerate].

### 3.6 Baselines
Ungated message knockout · harm-gated knockout (same data and uncertainty method) · VLA-style single-step influence score (KL between the receiver's next-action distributions with and without the message), following [kaur2026beyond]. [TODO(SCI-002/STAT-001): confirm the final baseline set. Beating only the ungated knockout is a weak comparison (H3).]

### 3.7 Sampling and analysis
The unit is the checkpoint/exposure, with continuations nested inside it, clustered by run and world seed. We use cluster-aware intervals and never count continuations as independent cases. [TODO(STAT-001): number of continuations per arm under the $0 budget; interval method; primary hypothesis designated before holdout collection]

## 4. Results (~1.3 p; mechanism fixtures and the real-agent case study kept in separate subsections)

### 4.1 Replay validity
[RESULT-PENDING: GATE-A/ENG-002 validity table: pass/fail counts per gate, leakage and corruption rates]

### 4.2 Controlled fixtures: the benign-cooperation trap
- **Figure 1** (flagship contrast: same knockout magnitude, different verdicts): [RESULT-PENDING: VIS-001 Fig 1 from STAT-002 fixture table]
- **Table 1** (verdicts by fixture × method: CCC versus the ungated, harm-gated and VLA-style baselines; erroneous harmful-collusion findings on benign cases; coverage and sensitivity on harmful mechanisms): [RESULT-PENDING: STAT-002 table T1]
- Primary-comparison sentence (H1 or H3, whichever STAT-001 designated): [RESULT-PENDING: STAT-002 primary estimate + interval + n independent fixtures]

### 4.3 Real Colosseum case study
- [RESULT-PENDING: STAT-002 table T2: eligible / ineligible / invalid / inconclusive / supported / not supported counts, with independent worlds, branch repeats and failures counted separately]
- [RESULT-PENDING: STAT-002: abstention reason distribution, if abstention dominates]

### 4.4 Robustness and cost
[RESULT-PENDING: STAT-002 sensitivity to margin and τ_W; resource usage reconciled separately from environment task cost]

*Language rule:* use "in this controlled setting", "under the tested intervention", "we observed", "the estimate was inconclusive". Never call prompted behavior spontaneous. Every number must cite a `ops/CLAIMS.md` ID, table field and analysis version.

## 5. Discussion and Limitations (~0.5 p)

- Discussion: where the audit helps and where it abstains. [RESULT-PENDING: depends on §4]
- **Limitations** (draft early; the template asks for assumptions explicitly): the method requires an executable simulator and a known suspected pair. State identification is limited by inaccessible state [TODO(ENG-001)]. There are information-loss confounds. Partner/coalition specificity is not identifiable when outsiders never had channel access. Redundant signals mean a single-exposure null is "not identifiable", not "no collusion". Steganographic, tool and side channels escape text masking [motwani2024secret; rippin2026tooluse]. Model and backend are limited to [TODO: pinned model], with a small sample. Fixtures are constructed. The prompted positive control is not spontaneous collusion.
- **Future work:** [TODO: P1 items not done, e.g. repair arm R, second model stratum]

## 6. Conclusion (1–2 paragraphs, write LAST)
[RESULT-PENDING: the supported takeaway after STAT-002 freeze and REV-001, not the original aspiration]

## Code and Data
- Code repository: [OWNER: public release approved? Remove private Drive IDs from any public artifact]
- Data: [TODO(REL-001): reproduction bundle, frozen manifests]
- Other artifacts: [OWNER: video/demo, optional]
- Preexisting code statement: [TODO(ENG): upstream commit, patches, license]

## Author Contributions (optional)
[OWNER]

## References
Generated from `paper/references_draft.bib` (verified-only). Use a consistent format: authors, year, title, venue/publisher, URL or DOI. Cite arXiv versions as read (e.g. rose2026detecting **v5**, not the v3 named in the spec).

## Appendix

### A. Limitations and Dual-Use / Ethical Considerations — **REQUIRED by the sprint page (not in the template; add it)**
- What the result does and does not establish: [RESULT-PENDING: mirrors the §4 scope]
- Dual use: could a validity-gated audit help colluders learn which messages evade detection, for example by routing through redundant or covert channels the audit labels "not identifiable"? Could the released fixtures serve as collusion recipes? [TODO(PUB/REV-001): assess and state the mitigations]
- Does the method make real-world collusion harder to detect? Risk of false reassurance from "not supported" verdicts. [TODO]
- Use of prompted collusive agents in sandboxed environments only. No real markets or users.

### B. Additional material (optional)
Prompts, the certificate schema, extra figures and the fixture specs. [TODO]

### LLM Usage Statement
[OWNER: approve the final wording; see `paper/author_checklist.md`.] Describe the actual use of Claude (Claude Code) and, if used, Codex for planning, implementation, analysis assistance and drafting. **Do not** copy the template example "All results and claims were independently verified" unless that human review actually happened. The template notes that the final version should primarily be written by the team.

---
### Pre-export checklist (from spec 12/17)
- [ ] No `[RESULT-PENDING]`, `[TODO]`, `[CONTRIB-PENDING]` or `[OWNER]` markers remain. Template guidance boxes and unused author cells are deleted.
- [ ] Main body ≤ 8 pages (target 4–6). The abstract has 150–250 words.
- [ ] Every quantitative sentence maps to a CLAIMS.md ID, table field and analysis version.
- [ ] Only verified references are used. The residual novelty check has been re-run.
- [ ] Every page of the exported PDF has been rendered and inspected, or the owner's visual review is flagged.
