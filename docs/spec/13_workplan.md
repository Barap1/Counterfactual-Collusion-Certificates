# 13 - Work packages, gates, and deadline strategy

## Dependency graph

```text
BOOT-001 workspace/delegation/budget audit
  + SCI-001 closest-prior-art and claim review
  + ENG-001 recorder/state inspection
             |
             v
SCI-002 causal/metric contract <--> ENG-002 minimal replay prototype
             |
             v
GATE A: deterministic integrity and benign-cooperation tests
             |
             v
INF-001 backend benchmark --> EXP-001 small real pilot
             |
             v
GATE B: valid real branch and feasible collection plan
             |
             v
STAT-001 freeze protocol + independent review
             |
             v
EXP-002 held-out collection --> STAT-002 frozen analysis
             |                         |
             +--> VIS-001 offline viewer skeleton
                                       |
                                       v
GATE C: claim audit + reproduction --> PUB-001 paper/figures/Drive
                                       |
                                       v
GATE D: final PDF, ethics, provenance, owner approval
```

The paper outline and source ledger start early. The fancy demo does not start before a valid audit exists. A viewer skeleton may use explicitly labeled fixtures, but must never present placeholder values as collected results.

## Work package contracts

| ID | Owner | Output | Acceptance/dependency |
|---|---|---|---|
| BOOT-001 | Bootstrap Lead | Environment/delegation/policy manifests; preserved pilot | Module 08 checks pass; no large inference batch |
| SCI-001 | Source worker + skeptical reviewer | Novelty matrix; verified source ledger; narrowed contribution | At least the closest four methods inspected; no unsupported first claim |
| SCI-002 | Causal-design worker | Harm definition, intervention scope, control plan | Independent design reviewer approves or explicitly narrows |
| ENG-001 | Replay engineer | State/observation map and prototype strategy | Exact hooks and inaccessible state documented |
| ENG-002 | Replay engineer + test worker | Snapshot/reconstruction, F/K/S execution | Offline invariants and corruption tests pass |
| INF-001 | Inference controller | Realistic backend benchmark and cost reservation | Tool-loop compatibility and zero-new-spend guards demonstrated |
| FIX-001 | Fixture worker | Independent mechanism/control generator | Labels not derived from CCC; hidden labels not leaked |
| EXP-001 | Experiment controller | Small development pilot; throughput and failure report | Real branch validity inspected; all attempted cases retained |
| STAT-001 | Statistician + cold reviewer | Frozen protocol, thresholds, sample/compute plan | World-level analysis; realistic uncertainty; holdout untouched |
| EXP-002 | Experiment controller | Immutable held-out traces and manifests | No unregistered model/prompt switch or selective reruns |
| STAT-002 | Statistician | Effect tables, intervals, missingness, claim candidates | Offline rerun agrees; claims follow realized evidence |
| REV-001 | Independent reviewer | Scientific and code audit findings | Reproduces key metric and challenges strongest claim |
| VIS-001 | Visualization worker | Publication figures and offline replay | Data lineage, readable design, no hidden live calls |
| PUB-001 | Publication worker | Paper, references, required appendix, working Doc sync | Numeric/source audit and template preservation |
| REL-001 | Integration/release reviewer | Reproduction bundle, final PDF, owner checklist | All mandatory gates pass or limitations explicitly narrow release |

Every package may create bounded children under module 03. Do not create a separate management agent for every small file.

## Phase budgets, not promises

Use these as planning envelopes for a roughly 48-hour effort, adjusting to the actual launch time and progress:

- **Foundation / early hours:** bootstrap, reward audit, source/claim review, exact replay strategy.
- **First major engineering block:** deterministic fixtures, recorder, state/exposure invariants, one real branch.
- **Next block:** backend benchmark, development cases, frozen causal/statistical protocol.
- **Central collection block:** controlled and real held-out data, checkpointed/resumable; writing methods in parallel.
- **Final substantial block:** analysis, independent review, readable figures, paper, export/QA, optional recording.

The director must reserve a meaningful finalization window rather than allowing experiments to consume the entire sprint. An experiment that cannot finish with time to analyze and explain it should not be launched merely because credits remain.

## Go/no-go gates

### Gate A - Replay is real

Require a scripted deterministic case where factual and sham are identical, the declared knockout changes only the intended exposure, and branch state is isolated. Require a benign causal-cooperation case that the method does not mislabel. If these fail, stop live experimentation and fix the method.

If exact event replay remains unreliable after a bounded engineering attempt, narrow to a documented **condition-level/channel intervention** or a transparent smaller harness. Change the title/claims accordingly. Do not keep saying "trajectory-level certificate" while only comparing unrelated complete episodes.

### Gate B - One meaningful real audit

Require a complete factual/sham/intervention sequence with preserved request traces, validated state/exposure, accurate model IDs, and interpretable metrics. The effect need not be positive. Also require a throughput/call forecast that fits approved resources.

If real branching works but outcomes are too noisy, select a more precisely defined proximal endpoint or reduce optional conditions using development data. Do not select successful seeds as the new dataset.

### Gate C - Evidence earns the claim

Require frozen analysis, all attempted run statuses, independent sample counts, control results, and an independently checked headline metric. If uncertainty is large, narrow the claim to feasibility, a measured confound, or a negative result. Do not add rhetorical certainty.

### Gate D - Submission is ready

Require an inspected final PDF, source checks, reproducibility bundle, correct author/approval status, and no operational jobs left consuming credits. A beautiful demo cannot compensate for a missing required paper.

## Deadline and buffer

The official cutoff is **October 25, 2026 at 23:59 Anywhere on Earth (UTC-12)**. This converts to **October 26, 2026 at 11:59 UTC / 07:59 America/New_York (EDT)**. [S01](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25) Reconfirm official changes at launch; compute local conversion from the recorded timezone rather than assuming the date remains Sunday locally.

Recommended internal targets are a science/code freeze by Sunday October 25 at 18:00 Eastern and an owner-reviewable submission package by 21:00 Eastern. These are project buffers, not organizer requirements or promises of completion. If launch/progress makes them unrealistic, protect at least a final review/export buffer and cut scope explicitly.

After the science freeze, allow fixes to correctness, reproducibility, text, or figures. New hypotheses and major model sweeps are postponed. A bug that changes results requires regenerating affected artifacts and re-auditing claims, not hiding the fix as cosmetic.

## Fallback ladder

1. Drop second-model and mitigation extensions.
2. Drop interactive UI complexity; keep a high-quality static figure and recorded replay.
3. Reduce exploratory event localization to one prespecified exposure/channel.
4. Use a shorter justified decision horizon; narrow welfare claims.
5. If only small real data exist, report a method/feasibility study with strong controlled tests.
6. If causal validity fails, report the demonstrated failure and do not issue causal certificates.

Never drop provenance, negative controls, budget guards, or honest labeling to save time.
