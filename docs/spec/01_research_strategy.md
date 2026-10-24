# 01 - Research strategy, contribution, and scope

## The project in one sentence

**Build an audit that can rewind a multi-agent decision, intervene on a precisely identified communication exposure, and produce an inspectable evidence record distinguishing harmful message-dependent coordination from legitimate cooperation, coincidental alignment, and unsupported suspicion.**

Suggested working paper title:

> **Counterfactual Collusion Certificates: Auditing Harmful Coordination Without Confusing It with Cooperation**

Suggested demo headline:

> **Same suspicious behavior. Different causal evidence.**

Do not use a sensational title that implies mathematical proof or that all real-world collusion has been solved. A memorable presentation is compatible with conservative claims.

## Why this is the best version of the idea

The attractive part is not merely deleting a message. It is making an audit *accountable*: the certificate states what was changed, which preconditions held, how much uncertainty remains, which legitimate-cooperation controls passed, and when the auditor refuses to conclude anything. A skeptical judge should be able to follow a headline number to a plot, an analysis record, a branch pair, and a raw model/tool trace.

The strongest result to seek is a **demonstrated false-positive trap**: a simple message-removal audit reacts strongly to useful teamwork, while CCC's validity and harm checks prevent that reaction from being mislabeled as harmful collusion. If the evidence also identifies a harmful coordination pathway in the real Colosseum run family, the project combines methodological criticism, a concrete repair, and an accessible demonstration.

This is a proposed contribution, not an established result. If the refined method does not outperform a simpler baseline, report that. A well-supported failure mode can still be the central finding.

## Verified competition alignment

Primary placement is **Track 2: Detection and Audit of Collusion**, particularly question **2.3** on convincing evidence. Track 3 is secondary only if an actual carrier intervention is evaluated. The rubric assesses innovation/impact, execution, and clarity. [S01](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25)

| Judging goal | Our design choice | Evidence required before claiming success |
|---|---|---|
| A useful original contribution | Reusable, validity-gated evidence records; benign causal cooperation as a hard negative | Prior-art comparison plus a working audit that adds information beyond a naked ablation |
| Strong execution | Branch invariants, independent controls, frozen analysis, uncertainty, honest nulls | Reproducible tests and raw-to-claim lineage |
| Clear presentation | One flagship contrast, two or three readable figures, offline replay | A reviewer can understand the claim without reading code |

Do not optimize for the number of tools, models, subagents, dashboards, or experiments. Optimize for one difficult question answered convincingly.

## Novelty boundary: what is already known

The source review found substantial overlap, not an empty field:

| Prior work | Existing contribution relevant here | What CCC must not claim | Plausible incremental contribution to test |
|---|---|---|---|
| Colosseum [S03](https://arxiv.org/abs/2602.15198) | Coalition metrics, private-channel experiments, and disagreement between communication and actions | Inventing channel ablations or coalition advantage | A reusable checkpoint-level audit and explicit checks against benign information loss |
| HELIOS/NARCBench [S04](https://arxiv.org/html/2604.01151v3) | Discusses a counterfactual causal criterion but relaxes it when counterfactual simulation cannot be assumed | Inventing the causal definition of collusion | An executable, narrowly scoped approximation in a replayable sandbox |
| Long-horizon peer-intervention work [S05](https://arxiv.org/html/2609.24967v1) | Controlled peer changes provide causal evidence of interaction effects | The first causal study of multi-agent collusion | Case-level audit artifacts, failure states, and calibrated control families |
| Audit the Whisper / ColludeBench [S06](https://arxiv.org/html/2510.04303v1) | Black-box detection, channel transformations, and calibration | The first calibrated intervention-based audit | Explicit replay-validity gates and a focused harmful-versus-benign causal-coordination benchmark |

The source lead must inspect the closest methods, not just abstracts. Search for event-level replay, counterfactual auditing, mediation, interventional collusion detection, and benign-cooperation confounds. Look for earlier work using the same methodological package. Record dates, versions, exact overlaps, and contradictory evidence. Stop the novelty search after a bounded first pass and one adversarial follow-up; an endless literature crawl is not the project.

**Permitted novelty language:** "We contribute a reproducible audit protocol that combines [features actually implemented] and evaluate its failure modes on [tasks actually tested]."

**Forbidden until independently supported:** "first," "proves collusion," "solves collusion detection," "detects intent," "guarantees low false positives," "generalizes to frontier agents," or "causal necessity" as an individual historical fact.

## Falsifiable hypotheses and the bar for a strong contribution

**H1 - specificity without trivial abstention.** On held-out controlled mechanisms, a validity- and harm-aware audit reduces erroneous harmful-collusion findings on legitimate causal cooperation and audit-corruption cases, compared with prespecified ablation baselines, while retaining useful coverage and sensitivity on harmful mechanisms. Thresholds and the coverage operating point are chosen on development data, not the holdout. A method that abstains on every case does not satisfy this hypothesis.

**H2 - real-agent applicability.** In new Colosseum worlds, some prespecified communication exposures have measurable effects on the declared harmful-outcome distribution after the replay and information-loss checks. This may fail even though the archived pilot has positive coalition advantage. Failure is reported rather than repaired by selecting favorable messages.

**H3 - added value beyond a strong baseline.** CCC's extra validity/control machinery adds interpretable evidence or prevents demonstrable errors beyond a harm-gated knockout with the same data and comparable uncertainty estimation. If the simpler method performs equally well, report that and narrow the contribution to the protocol, implementation, or identified limitations.

Before holdout collection, the science lead designates one primary hypothesis/comparison and freezes its operating point. Do not present all three as independently confirmed because one worked. A compelling submission needs a concrete lesson a skeptical evaluator could use, not a favorable comparison against an intentionally weak detector.

## Theory of change

1. Audit a controlled agent deployment before relying on it.
2. Determine which suspicions survive a valid intervention and which are explained by useful information transfer or replay artifacts.
3. Use the audit to improve monitoring criteria or choose a narrowly targeted mitigation.
4. Preserve legitimate task utility rather than indiscriminately removing all communication.

The intended users are multi-agent safety evaluators, developers of replayable agent services, and researchers comparing evidence standards. Immutable production logs alone are not enough for this method. This limitation belongs near the first presentation of the method, not hidden in an appendix.

## Deliverable tiers

### P0: indispensable

- Reliable, tested replay or a clearly labeled narrower intervention harness.
- Controlled fixtures with independently known mechanisms, including benign causal cooperation.
- A real Colosseum case study with a pinned model/backend and honest uncertainty.
- A transparent certificate format with invalid/inconclusive states.
- A frozen analysis and complete evidence lineage.
- A template-compliant paper, readable figures, and an offline reproduction path.

### P1: high-value only after P0 gates pass

- Task-preserving message repair on validated examples.
- A second independently collected model/backend stratum.
- Receiver/channel localization with meaningful controls.
- A polished offline replay viewer and short recorded demonstration.
- A limited mitigation-versus-utility comparison.

### P2: explicitly expendable

- Multi-environment generalization, token-level attribution, covert-channel search, activation probes, training new models, a hosted public application, a comprehensive detector leaderboard, or a large orchestration platform.

Remove P2 first. Remove second-model replication and interactive UI complexity before removing negative controls or paper QA. Do not pivot into the separate red-teaming challenge simply because its model is free to run.

## A useful result even when the preferred hypothesis fails

A credible fallback paper can show that message knockouts systematically overstate evidence because they damage ordinary coordination, and that a stricter certificate must abstain on the available real-agent cases. Another can demonstrate that replay integrity is a practical precondition absent from common audit recipes. These are not licenses to relabel an engineering failure as a scientific discovery: quantify the failure mechanism, test it with independent fixtures, and clearly delimit empirical versus implementation limitations.
