# ENH-A novelty and competition review (r1)

Search date 2026-10-24. Queries (Firecrawl paper index, WebSearch, WebFetch; ~25 calls): counterfactual/interventional audit of multi-agent collusion; message ablation in MARL; identifiability of intent or collusion from behaviour; agent incentives and causal influence diagrams; tacit collusion and plus factors; Halpern-Pearl responsibility; selective prediction for safety monitors; abstention in collusion auditing; overdetermination in agent failure attribution; Apart collusion sprint. Tags: **V** = passages or full text opened; **V-abs** = abstract opened only (not read further). Not checked: legal "plus factors" primary law (only secondary mention in 2608.18078), journal versions, anything after 2026-10-24. This is a bounded search, not a survey; no "first" claim is supported.

## 1. Already demonstrated

- Forced-deviation counterfactual copies with A/A tests, placebos, positive controls for LLM markets; "Outcome measures cannot tell these cases apart; the audit can." Tran and Yu, arXiv:2610.28787, 2026, https://arxiv.org/abs/2610.28787 (V). They note the test "separates a punisher only poorly from a rival that merely best-responds" at cartel prices.
- Collusion audit in Jira/DCOP with regret, secret-channel probe; states "collusion is not always harmful". Nakamura et al., arXiv:2602.15198, 2026 (V).
- Latent-message intervention for collusion monitoring. Kaur et al., arXiv:2608.19161, 2026 (V-abs).
- Matched other-example message replacement as a control, with positive / negligible / inconclusive outcomes, paired sign-flip tests, presence vs content decomposition; not collusion-specific. arXiv:2607.26773, 2026, https://arxiv.org/abs/2607.26773 (V). Closest methodological neighbour found.
- Counterfactual replay for failure attribution; joint necessity versus alternative repairs. Li et al., arXiv:2608.29228 (V-abs); Causal Agent Replay, arXiv:2606.08275 (V-abs).
- Marginal-only audits are blind to coupled conduct; "lawful multi-identity operation and conspiracy are behaviourally indistinguishable here". Xu et al., arXiv:2607.26385, 2026 (V).
- Position: reasoning agents "collapse the legal evidentiary distinction between competition and collusion"; CoT cannot be relied on as evidence. Riemer et al., arXiv:2608.18078, 2026 (V).
- CoT monitoring dissociates from collusion. Lee and Park, arXiv:2609.18346 (V).
- Boundary problem named: "distinguishing beneficial cooperation from harmful collusion". Idowu et al., arXiv:2601.00360 (V).
- Steganographic channels evade monitoring; "perfectly-secure steganography limits the utility of this approach". Motwani et al., arXiv:2402.07510 (V).
- Auditors name innocents under upstream false alarms (34.4%, 62.6%); preregistered with disclosed deviations. arXiv:2609.07680 (V).
- Selective classification with reject option and risk control: Geifman and El-Yaniv, arXiv:1705.08500 (V-abs); delegation with guarantees for safety monitors, arXiv:2604.14251 (V-abs).
- Responsiveness differs from instrumental control; intent from behaviour needs a correct causal model. Everitt et al., arXiv:2102.01685 (V); intention paper arXiv:2402.07221 (V).
- Degree of responsibility/blame under overdetermination. Chockler and Halpern, arXiv:cs/0312038 (V-abs).
- Apart sprint (23-25 Oct 2026; Detection and Audit track asks "what should qualify as convincing evidence in logged trajectories"). https://www.createwith.com/event/new-york-ai-collusion-research-sprint-oct-2026 (V, listing page; judging criteria not stated there).

## 2. Ranked contribution memo

**C1. An explicit evidence ladder: influence, harm, attribution, identifiability are four separately gated claims.** Closest: 2102.01685 (response vs control incentive), 2608.18078 and 2601.00360 (boundary named, no protocol), 2602.15198. Delta: executable preconditions that map each rung to a verdict (supported / not supported / inconclusive / invalid), with the held-out null reported against them. Risk: "conceptual restatement of known caveats". Mitigation: ship it as code plus counterexample (C2), not prose.

**C2. Executable twin-world identifiability counterexample.** Two scripted policies with identical F/K/S/N outcome distributions on all declared arms, one harmful coordination, one legitimate transfer; CCC must return `inconclusive: pattern_ambiguous` and name the extra intervention that would split them. Closest: 2607.26385 (marginal tests), 2610.28787 (weak separation at cartel state), 2402.07221 (C-4 example). Delta: message-level, interventional, normative-label version with a witness intervention. Risk: "trivial by construction". Answer: triviality is the point; it exposes any knockout-plus-harm audit that outputs a binary.

**C3. Benign causal cooperation as hard negative for message knockout.** Closest: 2602.15198 (concedes), 2609.36855 (messages both help and hurt), policy-graph audits such as 2608.07098. Delta: LLM text-exposure fixtures where K effect is large yet harm-gated verdict is withheld. Risk: scripted, no model evidence; SCI-001 already noted precedent in spirit.

**C4. Placebo-plus-abstention verdict taxonomy with validity gates.** Closest: 2607.26773 (other-example control, three outcomes), 2610.28787 (placebos), 2606.08275. Delta: sender-matched non-informational placebo plus coalition/outsider harm gates and `invalid`. Risk: highest; do not claim novelty of placebo or three-way outcome.

**C5. Reporting standard from an honest confirmatory null.** Closest: 2609.07680 (preregistration with disclosed deviations). Delta: certificate accounting (0/11/5), loader-artifact disclosure, order-sensitivity of the bootstrap bound, MDE_80 about 2.2 against 8 worlds. Risk: nulls are not contributions; framed as a standard it is.

## 3. Interesting beyond Colosseum

(a) The twin-world principle applies to any replayable agent team (code review, procurement). (b) Persistent masking by event id, since re-rendered history leaks exposures. (c) Sham and placebo distinguish "removal operation" from "removed content". (d) Redundancy reported as "not identifiable" rather than "no effect" (cf. overdetermination, 2608.29228). (e) The `not supported` meaning "declared margin, declared exposure only". (f) Coverage-versus-error reporting for auditors (risk-coverage as in 1705.08500).

## 4. Cheap experiments (scripted, no paid compute; label development or new-prospective under r2 freeze)

1. **Twin-world suite**: 10 pairs, vary payoffs; confirm identical certificates, then show a norm-intervention (swap the receiver's private objective) separates them. Output: the memorable figure.
2. **Risk-coverage curve** for CCC vs knockout-only vs harm-gated on existing fixtures: coverage against false-support on benign cooperation (development evidence only).
3. **Redundancy sweep**: m = 1..6 redundant carriers x detector recall; show false "not supported" rate rises with m, quantifying the blind spot.
4. **Power curve** by simulation (paired SD 2.23): worlds needed for the registered rule at several true Delta; one table for "what the next study must be".
5. **Margin-sensitivity map**: verdict as function of declared m_O and delta_W, showing evidence is conditional on the declared norm.

## 5. Skeptical-expert criticisms

1. n = 8 worlds, CI includes 0; the "contribution" is a null.
2. Fixtures are scripted with oracle labels; results are circular and cannot estimate false-positive rates.
3. Twin-world impossibility is true by construction; reviewers will say any outcome-equivalence limit is known (Everitt/Halpern-Pearl style).
4. Carrier extractor is `weak_detector` (Youden J 0.49, no paraphrase detected), so "not supported" may overclaim.
5. Masking removes information, not intent; `info_bearing` unresolved, so K conflates loss of cooperation with loss of collusion.
6. Placebo available on 2/16 checkpoints; support was structurally near-unreachable on real agents.
7. B1 versus B2 compares prompt regimes, not realized collusion; one model, one prompt variant.
8. Post-hoc corrections (labels, non-commit exclusion 0.727, loader artifact) invite forking-paths suspicion despite disclosure.
9. Needs replay access; useless for deployed logs, the actual regulatory setting.
10. Crowded area: 2607.26773, 2610.28787, 2608.19161 overlap on mechanism; 2607.26385 and 2608.18078 already argue indistinguishability.

## 6. What judges will remember

- **Figure**: "One evidence, two verdicts": two worlds, identical F/K/S/N bars, two opposite norm labels, both stamped INCONCLUSIVE with the witness intervention listed beneath.
- **Principle**: "A knockout measures what a message did, not what it should have done."
- **Executable counterexample**: a single command that builds both twin worlds and prints identical certificates. Pair with the null: "our own preregistered test failed, and the certificate told us why it could not have said more."

## 7. Prior identifiability / indistinguishability statements (quoted)

- Xu et al. 2607.26385 (V): "Since lawful multi-identity operation and conspiracy are behaviourally indistinguishable here, we argue that the tractable regulatory target is not detection but counting." Also: "Every such test has power exactly alpha" for price-level tests against their construction, and "A universal impossibility claim would also be false, since Chassang et al. (2022) construct observational screens with real power." Scope: single-agent marginal tests, observational data.
- Riemer et al. 2608.18078 (V): reasoning agents are "compressing the evidentiary gap between lawful parallelism and unlawful coordination to the point of indistinguishability"; "a structural failure of attribution". Scope: position paper, pricing, CoT.
- Tran and Yu 2610.28787 (V): at cartel prices "the deviation's gain separates a punisher only poorly from a rival that merely best-responds". Scope: forced price deviations.
- Ward et al. 2402.07221 (V; author list from memory, not shown in opened text): "assessing intentions requires that the causal model that we use (as observers of the system) corresponds to the agent's subjective causal model"; their C-4 example admits two readings under the same intervention. Scope: intent definitions, not collusion.
- Idowu et al. 2601.00360 (V): the boundary between harmful collusion and beneficial coordination "is context-dependent and requires a level of nuance that current detection algorithms struggle to provide" (their attribution to Ghaemi 2025, not checked). Position text only.
- Rose et al. 2604.01151 (V partial): "no known universally most powerful test for this setting". A detector-power remark, not an identifiability theorem.
- Hartline-style audits (2501.09740, V-abs): algorithms "can pass the audit by pretending to have higher costs".

I found no theorem stating that message-level interventional evidence on (influence, harm, utility) cannot separate harmful coordination from legitimate cooperation. Absence in a bounded search is not proof. Safe wording: "we state and demonstrate a scoped outcome-equivalence limit for declared-arm evidence; related indistinguishability claims exist for marginal price tests [Xu] and are argued informally [Riemer, Idowu]."
