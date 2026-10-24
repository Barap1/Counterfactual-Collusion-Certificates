# CITATION AUDIT for paper/v2/draft_v2.md (CITE-CHECK, 2026-10-24)

Method: arXiv abs pages (WebFetch) for all 19 arXiv refs; full text (PDF via local pdftotext, or arXiv HTML) for refs 1, 2, 3, 4, 5, 6, 7, 11, 12; AEA page for 19; web search for 13 venue. ~35 web calls. Quotes are <=40 words, taken from opened text. "abs only" means the claim was checked against the abstract only.

## A. Bibliographic verification (all entries verified; draft reference-list fixes in bold)

| Draft # | bib key | Verified fields | Fix needed in draft reference list |
|---|---|---|---|
| 1 | nakamura2026colosseum | 8 authors, title, v1 2026-02-16, no venue | none |
| 2 | tran2026enforcing | Hieu Tran, Hong Yu; v1 2026-10-20; no venue | none |
| 3 | kaur2026vla | 6 authors, v1 2026-08-19 | none (drop "abstract-level": HTML passages read) |
| 4 | rose2026helios | 6 authors, v5 2026-10-15 | none; **not cited anywhere in the body** (only in list) |
| 5 | xu2026competitivemarginals | 6 authors, v1 2026-07-29 | none |
| 6 | riemer2026position | 7 authors; comments "ICML 2026" | optional: add venue ICML 2026 (position track). Note: abs page says submitted 29 May 2026 although id is 2608; flag oddity, keep year 2026 |
| 7 | zhang2026latentaudit | **Huixiang Zhang, Mahzabeen Emu** (resolved); title ends "...LLM Communication" (arXiv metadata truncates it) | **replace "[Author list not captured]" with Zhang, Emu; remove CITE-CHECK tag** |
| 8 | idowu2026anticollusion | 3 authors; also Knowledge-Based Systems 344:116067 (2026) per abs page | optional: add venue |
| 9 | lee2026faithful | Lee, Park; Findings of EMNLP 2026 (accepted) | optional: add venue |
| 10 | motwani2024secret | 7 authors, 2024 | none |
| 11 | everitt2021incentives | Everitt, Carey, Langlois, Ortega, Legg confirmed; AAAI 2021 | **remove CITE-CHECK; add AAAI 2021** |
| 12 | ward2024intention | Ward, MacDermott, Belardinelli, Toni, Everitt confirmed; comments AAMAS24 (publication not confirmed on page) | **remove CITE-CHECK** |
| 13 | chockler2004responsibility | Chockler, Halpern confirmed; JAIR 22:93-115, doi 10.1613/jair.1391 (web search; full text not read) | **replace "JAIR" with "JAIR 22, 93-115 (2004)"; remove CITE-CHECK** |
| 14 | li2026gcjr | Li, Song, Yao, Li | none |
| 15 | shah2026car | **Jaineet Shah (sole author)** | **fill author** |
| 16 | arslan2026audit | **Paul-Peter Arslan (sole author)** | **fill author** |
| 17 | geifman2017selective | Geifman, El-Yaniv; page states no venue (NIPS 2017 is from memory, not included) | remove CITE-CHECK |
| 18 | pona2026ctd | **Pona, Kazemi, Hosseini, Du, Watson, Simeone, Paoletti** | **fill authors** |
| 19 | calvano2020artificial | 4 authors, AER 110(10):3267-97 | none |
| 20 | lopesdemoraes2026deterrence | Kaue Lopes de Moraes, Rodrigo De-Losso; ICAIF '26 | optional: add venue |

## B. Claim-citation audit

| Ref | Claim sentence (short) | Supporting quote | Verdict | Suggested rewording |
|---|---|---|---|---|
| [2] | Tran and Yu clone markets, regenerate continuations under shared seeds, A/A tests, placebos, positive controls (Sec. Related) | "the copies share every sampling seed, so they differ only through the deviation"; "In A/A tests without a deviation"; "Agents that cannot collude show what an outcome looks like without strategy"; "The audit must catch agents known to punish" | OK | none ("regenerate continuations" is our paraphrase) |
| [2] | deviation "separates a punisher only poorly from a rival that merely best-responds" | "At cartel prices the deviation's gain separates a punisher only poorly from a rival that merely best-responds" (Limitations/App. H) | OK | quote is exact; cite Limitations/Appendix H |
| [2,7] | counterfactual interventions, sham/placebo controls, three-way outcomes "established" | [2]: placebos above. [7]: "paired inference with positive, negligible-effect, and inconclusive outcomes" | OK | none |
| [1] | Colosseum audits collusion in a Jira-style DCOP with regret and secret-channel contrasts | "software Jira ticket allocation and hospital patient transfers" (new DCOP environments); "actions (regret metrics)"; secret channel vs "no-secret-channel control" | OK | none |
| [1] | states that collusion is not always harmful | "collusion is not always harmful: when the nominal objective encodes an unsafe or unethical task, coordinated deviation may be desirable rather than adversarial." (Limitations) | OK | add "in its limitations" |
| [3] | VLA intervenes on latent messages for single-step action scores | "the runtime replaces only the incoming suspect latent before scoring the receiver's action distribution"; unit is "one scheduled sender-receiver interaction joined to one receiver bid event" | OK | note it is bid-level, whitebox recovery is "a sanity check by construction" |
| [7] | replaces message with matched other-example message; positive/negligible/inconclusive; paired sign-flip; presence-vs-content | "paired inference with positive, negligible-effect, and inconclusive outcomes"; "We report paired bootstrap confidence intervals together with sign-flip or exact paired tests"; other-example message "approximately length-matched" | OK | "sign-flip or exact paired tests" (not only sign-flip); "matched" = length/compute matched. Authors now known: Zhang, Emu |
| [7] | not collusion-specific | no collusion content in the text (keyword search negative) | OK | none |
| [5] | price-level audits vs competitive marginals have power exactly alpha | "every such test has power exactly alpha, its own size. This is not low power that more data would fix." | OK | domain is auction bids (incl. Ethereum block-building), say "price or bid-level" |
| [5] | lawful multi-identity operation and conspiracy behaviourally indistinguishable | "Since lawful multi-identity operation and conspiracy are behaviourally indistinguishable here" | OK | keep "here" scope |
| [5] | universal impossibility claim would be false; observational screens can have real power | "A universal impossibility claim would also be false, since Chassang et al. (2022) construct observational screens with real power against noncompetitive bidding" | OK | none |
| [6] | reasoning agents compress evidentiary gap lawful parallelism vs coordination to indistinguishability | "compressing the evidentiary gap between lawful parallelism and unlawful coordination to the point of indistinguishability" | OK | none |
| [6] | chain-of-thought cannot serve as evidence | "chain-of-thought reasoning agents are incapable of providing any meaningful level of algorithmic interpretability that can be relied on as evidence of collusion" | OK | position paper, DeepSeek-R1 Bertrand experiments only |
| [8] | Idowu et al. name the boundary between beneficial cooperation and harmful collusion without a protocol (abs only) | "the boundary problem (distinguishing beneficial cooperation from harmful collusion)" listed as open challenge | OK (abs only) | "flag as an open challenge" is safer than "without a protocol" since they propose per-mechanism approaches |
| [6,8] (Intro) | indistinguishability "informally argued" for reasoning agents [6, 8] | [6] verbatim above; [8] only names boundary problem, no indistinguishability claim | FIX | "argued for reasoning agents [6]; the cooperation/collusion boundary is named as open in [8]" |
| [9] | CoT monitoring dissociates from collusion | "dissociate along both dimensions"; "CoT monitoring alone cannot serve as a standalone safeguard against algorithmic collusion" (abs) | OK (abs only) | none |
| [12, 11] | Ward et al. and Everitt et al. "show that intent and incentive claims depend on the causal model used by the observer" | [12]: "assumptions that the observers and the agent have a shared SCIM representation of the environment". [11]: "Only Figure 5a gets this right" (incentives depend on whether the diagram is causally correct) | FIX (overstated) | "Ward et al. define intent relative to a structural causal model and infer it from interventions under an assumed shared model [12]; Everitt et al. show incentive criteria are properties of the assumed causal influence diagram [11]." [11] says nothing on intent or observers |
| [14, 15] | counterfactual replay for failure attribution and minimal repair families | [14] abs: "pointwise attribution cannot identify jointly necessary repairs, and single-event replay misses them"; [15] abs: intervenes on a step and "re-executes the trajectory" | OK (abs only) | none; [14] directly supports the redundancy motivation |
| [13] | structural responsibility under overdetermination | abstract: degrees of responsibility; "voters in 11-0 win less responsible than in 6-5" (redundant contributions); word "overdetermination" not on abstract | OK-weak (abs only) | "degrees of responsibility under redundant contributions [13]" |
| [17] | selective classification with reject option and risk-coverage | "a user to set a desired risk level... rejects instances as needed"; coverage trade-off | OK (abs only) | none |
| [18] | delegation with risk guarantees for safety monitors | "finite-sample guarantees on either computation cost or safety performance" | OK (abs only) | "cost or safety-performance guarantees" (not purely risk) |
| [16] | preregistration with disclosed deviations has precedent in audit work finding auditors naming innocents | abs: auditors "name an innocent party in 34.4% and 62.6% of clean episodes where an agent raised a false alarm"; preregistered hypothesis "is not supported"; no deviation disclosure seen | FIX | "preregistered audit study whose preregistered hypothesis was not supported [16]"; drop "disclosed deviations" unless OSF record checked |
| [10] | steganographic/covert channels can evade text-level intervention | abs: steganography makes coordination "hard to detect"; limited capabilities except GPT-4 jump | OK (abs only) | none |
| [19,20] | "Forced deviations and impulse responses separate reward-punishment schemes from high prices in algorithmic pricing" | [20]: impulse-response pattern "does not by itself identify a punishment mechanism"; return is "over-determined rather than selective" (abs/summary). [19] abs: "finite phase of punishment"; method not on page | MISREPRESENTED | "Impulse responses after forced deviations were used to infer punishment in Q-learning pricing [19]; later work shows that pattern does not by itself identify a punishment mechanism [20]." This also supports the paper's own point |
| [4] | (not cited in body) | n/a | REMOVE or cite | cite where HELIOS/NARCBench is discussed, or drop from list. Rose et al. say counterfactual simulation "cannot always be assumed", so use weaker observable criterion |
| draft para "Closest methodological neighbour" | "(arXiv:2607.26773; abstract and passages read, author list not captured)" | authors now resolved | FIX | replace with "Zhang and Emu [7]"; delete "author list not captured" and [CITE-CHECK authors] tags |

## C. Items not checked
- Whether Calvano et al. (2020) full text describes forced deviations (page shows only abstract; second-hand via [20]).
- Full text of refs 8, 9, 10, 13-18 (abstract only). Chassang et al. (2022) cited inside [5] is not in the draft.
- Tran and Yu: only first 100k of 214k characters read; Appendix H wording read as quoted in Limitations.
- Self-claims about our own contribution (e.g., "we reuse its environment" for [1]) are outside scope.
