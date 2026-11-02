# Research process

This note explains the research as a safety study: what problem it addresses, what each claim requires, how the work guarded against fooling itself, and what went wrong. Dates and identifiers are quoted from the records in [`research-log/`](../research-log/README.md) and [`docs/stats/`](stats/); decision numbers (D-0xx) refer to [`research-log/ops/DECISIONS.md`](../research-log/ops/DECISIONS.md).

## Threat model

Deployments increasingly put several AI agents in one system, and oversight often relies on agents not coordinating against the overseer or against third parties. Surveys of multi-agent risk treat collusion as a distinct failure mode (Hammond et al., *Multi-Agent Risks from Advanced AI*, arXiv:2502.14143). Agents can hide coordination in ordinary-looking text (Motwani et al., *Secret Collusion among AI Agents: Multi-Agent Deception via Steganography*, arXiv:2402.07510), and AI control protocols that use one model to monitor another must reason about monitor and policy colluding (Gardner-Challis et al., *When can we trust untrusted monitoring? A safety case sketch across collusion strategies*, arXiv:2602.20628; Nguyen et al., *TraceGuard: Structured Multi-Dimensional Monitoring as a Collusion-Resistant Control Protocol*, arXiv:2604.03968). This project works in the Colosseum environment for auditing collusion in cooperative multi-agent systems (Nakamura et al., arXiv:2602.15198).

An auditor who finds a suspicious message usually wants to act: sanction an agent, roll back a deployment, or clear the system. A counterfactual test can show that a message changed behaviour. Influence measures of this counterfactual kind are well established in multi-agent learning (Jaques et al., *Social Influence as Intrinsic Motivation for Multi-Agent Deep Reinforcement Learning*, arXiv:1810.08647; Lowe et al., *On the Pitfalls of Measuring Emergent Communication*, arXiv:1903.05168). But an influence measure does not say whether the change violated a norm. Legitimate cooperation also changes behaviour, and it can also leave outsiders worse off. An audit that treats influence plus harm as collusion will accuse legitimate teams, and an audit that clears everything without a separating test will miss real coordination. Related work shows the same gap in markets: price-level audits can be blind to collusion by construction (Xu et al., *Collusion with Competitive Marginals: Price-Level Audits Are Blind by Construction*, arXiv:2607.26385). Auditing multi-agent systems therefore needs **attribution**: evidence that separates a prohibited policy from the legitimate policies that would produce the same observations.

## Research question and claim ladder

The question is: **what counterfactual evidence justifies which claim about collusion?** The project separates four claims, each requiring more than the last:

| Rung | Claim | Evidence required | Where it is implemented |
| --- | --- | --- | --- |
| Observation | A message was sent and looks suspicious | The transcript | Transcript rule B4; ladder rung L0 |
| Causal influence | The message changed what the receiver did | A valid controlled replay with a nonzero effect of removing it | Arms F and K; rung L1 |
| Harmful exposure | The message's effect disadvantaged outsiders | Outsider, coalition and welfare effects with valid sham and placebo controls and stated margins | `decide`; rung L2 |
| Attribution | The behaviour violated a declared policy | A declared policy and evidence that separates it from legitimate alternatives | Ladder rule L3 at evidence levels $I_3$ to $I_5$ |

The formal versions are in [MATH.md](MATH.md): evidence levels as information sets (section 1.4), the arms and what they identify (section 2), and the result that no rule restricted to evidence on which two policies coincide can label both correctly (section 3).

## Method: a constructed benchmark and a real-agent study

The two studies answer different questions and are never pooled.

* The **constructed benchmark** uses scripted policies with known labels, so identifiability can be computed exactly by enumerating every policy in a declared census. It can show, with certainty within its design, that particular evidence is insufficient and that particular additional evidence (a cost probe, an authorization record) is sufficient. Its weakness is that the generator defines the labels and the separators work by construction.
* The **real-agent study** (EXP-002) uses local language-model agents (`gemma4:26b`) in a task-allocation environment, comparing a deceptive-coordination prompt regime with authorized-cooperation prompts across eight matched world pairs. It tests whether the replay instrument detects a difference in realistic behaviour. Its weaknesses are a small sample, one model and one prompt variant, and no verified ground truth: a prompt is not proof of realized collusion.

Both are needed. The benchmark establishes limits that the real-agent study cannot (it has no labels to enumerate), and the real-agent study tests whether the instrument works on behaviour the experimenters did not script.

## Rigor practices

**Preregistration before held-out data.** The real-agent study was governed by a statistical preregistration ([`stats/prereg.md`](stats/prereg.md)), an analysis specification and protocol v1.2, whose hashes are listed in the freeze record ([`stats/FREEZE.md`](stats/FREEZE.md)). Thresholds were pinned on development data only: the outsider-harm margin $m_O = 2.5$, welfare tolerance 5 and sham margin 2.5 (D-030). A change to the call cap was derived from development call counts and frozen before any held-out data existed (D-030). An independent freeze review approved the record, and the held-out run launched on 2026-10-24 at 02:42 UTC (D-031). The preregistered decision required both a positive bootstrap lower bound and an exact sign-flip $p \le 0.05$.

**Freezing the benchmark before generating any world.** The prospective benchmark protocol was frozen on 2026-10-24 at 19:57:02 UTC with protocol SHA-256 `334a4539d2dc6976879c50c8244905a735a13ce32f5a4e8046715e31b250dcb6` after an independent review (D-041; [`enh/r2/FREEZE.json`](enh/r2/FREEZE.json)). The freeze binds the hashes of all benchmark, audit, baseline and fixture source files. Seeds were drawn only afterwards, as a deterministic function of the protocol hash, excluding the development and Gate A seed blocks, every seed found in earlier records, and 0 to 99,999 (seed-list SHA-256 `1720ba12cd131f9d914ea01bf0a14e72f4f7923fd060ca6d5802a2839e829e7c`). The block was run once, with no interim looks (D-041).

**Separate development and evaluation data.** The seed-1 positive-control pilot predates the sprint and is development data only; its 27 files are archived locally with hashes (D-002). Benchmark development used seeds 13000 to 13049. Changes informed by development results were made before the freeze and labelled as such: the revised attribution rule v1, a method-independent frontier criterion and a refined baseline prediction (D-040). The original predictions and rule v0 are still reported beside them.

**Hash-pinned archives.** The real-agent raw archive is verified by SHA-256 before any reproduction extracts it ([`runner/archives/`](runner/archives/)). Every evaluation record cited in [RESULTS.md](RESULTS.md) is a file in the frozen tree.

**Independent reproduction.** The held-out result was reproduced from raw data twice, by a standard-library script that imports no project code and by an independent review (REV-001), before it was accepted (D-034, D-035). The bootstrap interval was reproduced by a separate script.

**Recorded corrections, not rewrites.** Corrections appear as new decisions and new versioned outputs, with the originals kept:

* An analysis label hard-coded the primary result as exploratory; the governing protocol text made it preregistered. The labels were corrected with no change to any number or threshold (D-034; output `exp002_heldout_v2`).
* A certificate-validity mapping was repaired in `exp002_heldout_v3`, changing 16 validity fields and five reason arrays while preserving every estimate and status ([`enh/fix/`](enh/fix/); paper Appendix B).
* A review ledger counted three `pattern_ambiguous` cases; the frozen rows show four, and the paper uses four ([`research-log/ops/CLAIMS.md`](../research-log/ops/CLAIMS.md)).
* An extractor file changed in a reviewed correction after its freeze hash was written; it was re-frozen at the new hash before any held-out data and disclosed (D-030).
* The development placebo census ran before its inputs were hash-committed, so it was reclassified as exploratory (deviation DEV-002 in [`stats/deviation_log.md`](stats/deviation_log.md)).
* Early documents called the primary result a "confirmatory null". The current wording is that the preregistered directional hypothesis was not supported, which does not establish a null effect ([RESULTS.md](RESULTS.md)).

**Reporting negative results.** None of the four aggregate predictions written down before the benchmark ran was confirmed (label-effect prevalence, the original baseline prediction, the refined baseline profile in aggregate, and ladder utility), and each is reported exactly as it came out. The real-agent primary hypothesis was not supported ($\hat\Delta = 1.354$, 95% interval about $-0.020$ to $2.834$, $p = 0.0703125$), and no exploratory case-level certificate was supported. The restriction of established benchmark findings to the deterministic condition was decided after outcomes were visible, and it is labelled post hoc wherever it appears (D-048).

## What went wrong and what was learned

* **The first audit protocol could never say "supported".** The development gate failed. Independent review found that under protocol v1.1 the placebo's filler removed the same content as the knockout, so the placebo effect equalled the removal effect in 390 of 390 cells and the placebo veto always fired (D-018). Thresholds were not changed to pass the gate (D-015). Protocol v1.2 replaced the filler with a matched inert message, and the paper discloses that the amendment was motivated by the development result (D-021, D-023). Lesson: a control that shares the treatment's content is not a control, and a gate that cannot pass is not evidence about the method.
* **"Harmful" labels did not imply harmful effects.** In 68 of 80 development fixtures labelled as harmful dependence, the oracle outsider-harm effect was below the margin (D-017). This turned into a research question: the prospective benchmark measured how often a "forbidden" label comes with an exposure effect, and its point prediction failed (61 of 200).
* **Real conversations rarely contain an eligible placebo.** No development checkpoint had one (D-030), so case-level `supported` was unavailable by rule for real agents, and the held-out placebo ran at two of sixteen checkpoints. The study-level estimand does not need the placebo and remained the confirmatory target.
* **Fail-closed checks fired on false alarms.** A model-residency check halted the first pilot because a refreshed expiry timestamp was part of the fingerprint (D-019), and a collection-wide call budget was mistaken for a per-world cap (D-029, D-030). Both stopped the run rather than continuing silently; both were fixed outcome-blind before held-out data.
* **The noisy benchmark stratum depends on the platform.** Deterministic outputs agree byte for byte across macOS and Linux, but noisy outputs differ substantively, including decisions. The independent results review did not catch this; a later check did (D-048). Established findings were restricted to the deterministic stratum, after outcomes were visible, and both strata remain published. Lesson: a freeze that binds code and seeds but not the platform does not fully determine floating-point and random-number behaviour.
* **A follow-on study was stopped.** A second real-agent study (EXP-003) missed its freeze deadline and was recorded as not completed; it supplies no result and is not claimed (D-047a).

## Open problems and next steps

Each follows from a stated limitation ([LIMITATIONS.md](LIMITATIONS.md)):

* **Independent cases and labels.** The benchmark's labels and separators come from its own generator. The next test is whether additional evidence reduces false accusations on independently generated trajectories with policy-conditioned labels from verified authorization and separately checked behaviour, not from prompts.
* **End-to-end sensitivity.** Positive-control recovery of complete certificates is unestablished. The exposure instrument needs validation separately from attribution before a detection comparison means anything.
* **Better placebos.** The real-agent placebo is not matched in surface or prompt position and is often unavailable. A control matched on both would make the content-specific effect identifiable under weaker assumptions ([MATH.md](MATH.md), section 2).
* **Platform-determined execution.** The cause of the noisy-stratum divergence is unresolved; a future freeze should pin the platform and check self-determinism before running.
* **Precision.** Eight pairs, one model and one prompt variant leave real-agent sensitivity unestablished.
* **Adversarial robustness.** Probe responses can be gamed and records forged; publishing ambiguous cases could help a coalition design behaviour that survives a narrow audit. None of this provides operational assurance against an adaptive coalition.

A six-to-eight-week continuation with proposed success criteria is outlined in [STUDIO_RESEARCH_PLAN.md](STUDIO_RESEARCH_PLAN.md). It is a proposal, not a new preregistration.
