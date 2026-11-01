# 06 - Preregistration, statistical analysis, and claim discipline

## Freeze a small analysis contract

Before confirmatory collection, write `experiments/preregistered_protocol.md` and a machine-readable manifest. Include the research question, primary outcome, independent unit, target sample, arms, model/backend, candidate-selection rule, excluded cases, missing-data handling, practical-effect margin, thresholds, and the exact analysis commit. Hash both files. A timestamped repository commit is a reproducibility record, not a claim of an external preregistration registry.

The scientific question is not "Can we get a significant result?" It is whether the audit separates a declared harmful mechanism from important alternatives while respecting its own limits.

## Unit of analysis

The primary independent unit is the **generated task world / base trajectory group**, not a tool call, token, message, agent, branch, or seed repeated with cached output. Branch continuations are nested within a checkpoint. Matched regimes sharing a task world are also related observations.

For world `w`, average fresh outcomes within each arm before computing its arm contrast. Aggregate matched contrasts across independent worlds. Use a cluster bootstrap at the world level, keeping all paired regimes and branch observations together. If nested resampling is used, specify its target and justify the sampling hierarchy; do not mix world uncertainty and model-sampling uncertainty without labeling them.

For an individual checkpoint's certificate, uncertainty is conditional on that checkpoint and depends on the number of genuinely fresh continuations. A dataset-level confidence interval cannot be pasted onto every case. With only two or three continuations, case-level evidence will often be inconclusive. That is acceptable.

## Primary and secondary outcomes

Select **one primary harm score** after the reward-code audit and development phase. Report the interpretable vector `tau_A`, `tau_C`, `tau_O`, and `tau_W` regardless of whether it supports the desired narrative. Distinguish confirmatory from exploratory outcomes in the tables.

A useful primary analysis is a difference in harm-specific intervention effects between the harmful-intent and legitimate-cooperation regimes, with the caveat that prompts specify intent conditions rather than realized collusion truth. Test the actual operational claim; do not quietly substitute a statement about intentions or all models.

The science/statistics worker must decide whether a difference-in-differences contrast is meaningful for the chosen scalar. If scores are on incompatible scales or the controls differ substantially in task difficulty, prefer within-regime paired effects and a descriptive comparison.

## Practical margins and certificate rules

Choose a minimum effect worth acting on in environment units or using a verified fixed normalization. A convenient rule such as `effect > 0` is not sufficient when tiny stochastic fluctuations are common. Choose margins on development data and task semantics, not after observing holdout confidence intervals.

A certificate is supported only when:

- the declared harm evidence is present;
- mandatory validity checks pass;
- the relevant effect estimate and uncertainty clear the frozen practical margin;
- confound controls do not provide an adequate alternative explanation.

Specify a matched sham equivalence tolerance. Failure to reject a difference between F and S is not evidence that they are equivalent. With insufficient precision, label the validation uncertain. Deterministic replay invariants can be checked exactly; stochastic outcomes require a distinct inferential check.

Do not force a binary decision when evidence is weak. Report the proportion supported, not-supported, inconclusive, invalid, and ineligible. Abstention is part of the method, so report both conditional accuracy and overall coverage on labeled fixtures.

## Comparisons and multiple testing

Designate one primary comparison. Use a prespecified multiplicity adjustment, such as Holm, for a small family of confirmatory secondary tests, or clearly mark those comparisons exploratory. Do not conduct an unbounded search over events, masks, models, prompts, and thresholds and then present the best p-value as a planned test.

Use held-out fixture labels for a confusion matrix, sensitivity, specificity, and false-positive rate. AUROC is optional and meaningful only when the score and labels are justified. A three- or four-state certificate is not automatically a scalar classifier; report a risk-versus-coverage view or separate abstention-aware metrics when appropriate.

When zero false positives occur among `n` independent negative cases, write "0/n observed" and report an interval. The one-sided 95% binomial upper bound for zero events is `1 - 0.05**(1/n)`. For example, zero observed errors among 10 independent negatives still permits an upper bound around 26%. This calculation is not valid if 10 observations are correlated copies of the same world.

## Missingness, failures, and stopping

Every scheduled run receives a status. Distinguish model refusal, malformed tool output, timeout, rate limit, context overflow, crash, invalid restore, and intentional cancellation. These are not zero-harm outcomes. Summarize failure rates by arm and backend. If failures depend on treatment, a complete-case analysis can be biased; report the missingness and use a conservative sensitivity analysis where possible.

Set a bounded retry policy before collection. Record every attempt and its quota/cost. Do not repeatedly rerun only unfavorable or failed treatment cases until they succeed. Infrastructure retries must not change model, prompt, or sampling settings within a purportedly matched comparison.

Stop at the registered sample or a declared external resource/deadline limit. Do not peek at the effect after each batch and stop as soon as it looks impressive. If adaptive sampling is necessary, explicitly redesign and label the analysis exploratory; do not invoke statistical guarantees not implemented.

## Cost and throughput analysis

Report calls, tokens where available, inference latency, total experiment wall time, local model/backend, and actual credit use separately from environment costs. Null or unavailable provider cost telemetry is `unknown`, not zero. Prices inferred from a free catalog are an estimate/provenance fact, not a measured invoice.

Use the pilot to measure suffix length and request latency. Predict remaining runtime conservatively using upper latency quantiles and the actual concurrency limit. An idle model process is not a successful batch. Build progress indicators based on completed branch records rather than a spinner with no checkpointing.

## Claim ledger

Every paper claim must have an ID and an evidence chain:

```text
CLAIM-07
Text: exact proposed sentence
Type: measured | derived | prior work | hypothesis | limitation
Scope: fixture family / environment / model / sample
Evidence: raw manifest -> analysis version -> figure/table cell
Uncertainty: interval and independent sample count
Reviewer: task ID, date, outcome
Status: proposed | verified | narrowed | rejected
```

Examples of unacceptable shortcuts:
- "The private channel caused collusion" from a positive coalition advantage alone.
- "Zero API cost" from Colosseum's `total_cost` field.
- "No collusion" from an underpowered null intervention.
- "Independent replication" from two agents analyzing the same CSV.
- "50 independent trials" from 50 continuations of one checkpoint.
- "Generalizable across models" after silently changing providers halfway through a batch.

## Analysis deliverables

Produce `analysis/analysis_plan.md`, executable analysis code, `results/analysis/aggregate.json`, a tidy effect table, uncertainty outputs, missingness tables, and figure source data. Re-running analysis from the frozen artifacts must not make model/API calls. Unit-test metric direction, grouping, normalization, confidence-interval behavior, and empty-data handling. Keep effect values signed; do not take absolute values merely to make bars positive.

The final report must include a limitation statement that matches the realized evidence tier and sample size, not the ambition of the original plan.
