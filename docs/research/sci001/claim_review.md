# SCI-001 Claim Review

**Date:** 2026-10-23. Evidence: `novelty_matrix.md` and `source_ledger.md`. This review supersedes the novelty framing in `docs/research/CCC_Updated_Deep_Research_Report.md` wherever the two conflict.

## 1. Narrowed contribution statement (what we can honestly claim, *if implemented and tested*)

> We contribute a validity-gated counterfactual audit protocol for communication in replayable, tool-using LLM agent teams (instantiated on Colosseum).
>
> For a declared message exposure, it forks the trajectory at the receiver's earliest exposure. It then regenerates fresh continuations under factual, receiver-masked and sham arms, and estimates the change in a predeclared harm outcome separately from coalition advantage and task-utility loss. It issues *supported / not supported / inconclusive / invalid* records rather than a score.
>
> We evaluate it against harm-gated knockout baselines on controlled fixtures that include **benign causal cooperation as hard negatives**. Our aim is to measure whether message-removal evidence mislabels useful teamwork as harmful collusion, and whether validity and harm checks prevent that.

The contribution is the **combination and its failure-mode evaluation**, specifically the legitimate-cooperation hard-negative test. It is not the intervention. The permitted template from spec 01 still applies: "We contribute a reproducible audit protocol that combines [features actually implemented] and evaluate its failure modes on [tasks actually tested]." Delete any element we do not actually implement. The sham arm and benign fixtures are the first to be at risk.

### How to position it against the closest work (draft related-work sentences)

- **Kaur et al. (VLA)** already block or neutralize a single private exposure and measure the receiver's action shift for collusion monitoring. CCC differs in three ways. It intervenes on text exposures in tool-using teams. It regenerates multi-step continuations in every arm. Its evaluation targets legitimate causal cooperation as a false-positive source. *We should say we extend this line, not that we open it.*
- **Rose et al.** state a counterfactual communication-removal criterion. They relax it because counterfactual simulation cannot always be assumed, and their footnote notes that NarcBench-Core could support it. CCC runs a scoped, stochastic approximation of that criterion. *Wording: "operationalizes", never "the first to test".*
- **Colosseum** runs condition-level secret-channel contrasts and notes that it "remains unclear which qualitative factors yield efficient yet non-collusive communication". CCC directly targets that open question at the exposure level.
- **Tran & Yu** and **Calvano et al.** use counterfactual deviation copies to separate enforced collusion from look-alike outcomes. **Lopes de Moraes & De-Losso** show that such tests can be non-selective. CCC carries the selectivity concern over to message interventions.
- **MAS debugging** (DoVer, AGDebugger, AgenTracer, GCJR, Cha et al.) establishes remove/edit-and-replay as standard practice for failure attribution. CCC repurposes it for a harm-versus-utility estimand under stochastic resampling, with collusion-specific negative controls.

## 2. Claims we must NOT make

| Forbidden claim | Why (falsifying source) |
|---|---|
| "First causal / counterfactual / interventional audit of multi-agent (LLM) collusion" | Falsified by P01 (VLA, matched-neutral counterfactual), P04 (counterfactual-copy audit, 20 Oct 2026), P05 (causal peer interventions) and P08 (impulse response, 2020). |
| "First to implement Rose et al.'s causal criterion" / "Rose et al. could not run counterfactuals" | P02 v5's footnote says counterfactuals are runnable in NarcBench-Core, and P01 runs per-decision channel counterfactuals. Use "an executable, scoped approximation", not "first". |
| "Novel message-knockout / replay / rewind technique" | P07 calls counterfactual replay "the standard tool". R01–R04 edit or remove messages and re-run. LOC1 already ships checkpoint branching in the sprint starter. |
| "Interventions reveal what outcome statistics cannot" (as *our* insight) | Stated almost verbatim by P04 ("Outcome measures cannot tell these cases apart; the audit can"). Cite it as a shared premise. |
| "We discovered that naive intervention tests produce false positives" (as a general insight) | P09 (forced price increase triggers the same retaliation), M02 (informative-but-ineffective messages) and L01 (benign-affinity confounds) cover this. Only the *specific* finding on LLM message knockouts with benign cooperation could be ours, and only if we show it. |
| "Partner/coalition specificity proven" | See spec 04. It is not identifiable when outsiders never had channel access. |
| "Certificate" in a proof or legal sense; "proves collusion"; "detects intent"; "guarantees low FPR"; "generalizes to frontier agents"; "causal necessity" of a single historical event | See spec 01/04. Note that L25 already uses "certification" in a policy sense, so define our term early. |
| Any FP bound borrowed from Audit the Whisper | P06's null contains no legitimate cooperation, so its 10k-run bound does not transfer. |
| "Colosseum does not distinguish cooperation from collusion" stated as a flaw we discovered | Colosseum states the limitation itself (§5.4, §6). Credit them for it. |

## 3. Fallback claims, ordered by robustness

1. **Methodological negative result (most robust).** On controlled fixtures, harm-agnostic message knockouts produce large effects on benign causal cooperation, so knockout magnitude alone mislabels teamwork. This needs only the fixtures and a baseline. It is precedented in spirit (P09, M02), but no paper I read tests it for LLM text-message interventions.
2. **Replay-validity as a precondition.** Exposure leakage (the same message re-rendered on a blackboard, or repeated in memory or a summary), protocol corruption, and non-regenerated continuations invalidate naive knockouts. Quantify how often each happens in Colosseum. The MAS-debugging literature assumes deterministic oracles (P07 §12), so stochastic validity is less covered.
3. **Abstention as a finding.** On the available real Colosseum cases, a strict protocol must return *inconclusive*. Report the reason distribution: information loss untested, effect within the margin, fresh-F instability.
4. **Engineering contribution only.** A reusable, open fork-and-mask harness for Colosseum, with evidence records and lineage. This is the weakest claim to novelty, but an honest one.

## 4. Open questions and risks for SCI-002

**Harm metric**
- Colosseum's native quantities are regret against the DCOP optimum, Δ-collusion against a nominal reference, and coalition advantage. Spec 04 warns that A>0 ≠ harm, and Colosseum §6 concedes "collusion is not always harmful". Pick **one** primary h *after* auditing `metrics.py` and the Jira reward. Candidates: (a) outsider loss conditional on coalition gain, or (b) a drop in system utility against a task-matched cooperative reference. Freeze h before the holdout.
- Incompetence also raises regret. Decide how fresh-F instability and baseline regret enter the margin.

**Intervention scope**
- Choose between single exposure and persistent withholding, and decide how re-rendered blackboard copies are handled. GCJR and DoVer (R04, R01) show that joint and redundant repairs exist, so a null single-exposure effect must be labelled "not identifiable under redundancy", not "no collusion".
- Separate removing an informational exposure from removing an action that has mechanical effects (spec 04).
- Is the secret-channel-level knockout (arm C) just Colosseum's existing control? If so, present arm C as a replication bridge, not a contribution.

**Sampling unit**
- The checkpoint/exposure is the unit, with continuations nested inside it. Exposures within a run, and runs within a world seed, are clustered. Use cluster-aware intervals and don't count continuations as independent cases.
- Pre-register the candidate-exposure selection rule (spec 04 warns about picking the largest of many lesions). Decide the number of fresh continuations per arm against the $0 budget. The free-tier model's throughput may set a hard ceiling.
- Prior art uses deterministic replay (P07). We need fresh stochastic samples, so the sham arm must establish the natural variance floor.

**Legitimate-cooperation controls (the load-bearing piece)**
- Define at least one fixture where a message is *causally useful* (for example, sharing task costs or availability) and carries no forbidden objective. This is the hard negative. A second fixture should hold the same effect size with a forbidden objective.
- Adopt a **matched harmless message** control, in the spirit of VLA's matched-neutral latent and P09's benign-direction perturbation, as the selectivity check. The same sender and receiver should get a content-neutral message of comparable length.
- Decide how τ_W (utility loss under masking) gates a "supported" status, and whether an R arm (task-preserving repair) is P0 or P1.
- Ground truth for the fixtures must be independent of CCC's own outputs, to avoid circularity.

**Baselines (to satisfy H3 honestly)**
- These must include a harm-gated knockout and a **VLA-style single-step influence score**, meaning the KL between the receiver's next-action distributions with and without the message. Beating only an ungated knockout would be a weak comparison.

**Residual novelty risks**
- I did not search past Apart sprint submissions, the NeurIPS 2026 proceedings, or the citation graphs of P01, P02 and P04. A same-week preprint could appear: P04 was posted on 20 Oct 2026. Re-run a short arXiv check (`collusion AND counterfactual`) before submission.
- P01 and P04 were read only partly (by the child verifier, through truncated WebFetch). Before related-work quotes are finalized, someone should read their method sections in full.
- L25's author list is unresolved, and R09 is unverified. Do not cite either until resolved.
