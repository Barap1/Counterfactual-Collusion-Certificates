# 05 - Experimental design and evidence tiers

## Three evidence tiers; never mix their meaning

**Tier A - controlled mechanisms.** Small scripted or explicitly constructed environments with independently known information flow and harm. These validate the auditing method and expose confounds. They are not evidence that unprompted LLMs spontaneously collude.

**Tier B - real LLM Colosseum case study.** Tool-using agents, actual generated messages, and actual rewards. This establishes feasibility and measured intervention effects in this setting. Coalition assignment and a collusive prompt are treatment conditions, not perfect ground-truth labels for successful collusion.

**Tier C - generalization or mitigation.** A second model, another environment, or targeted intervention versus blanket communication removal. Attempt only after the first two tiers and the paper pipeline are sound.

All plots, datasets, manifests, and demo panels must identify their tier.

## Tier A: the control suite

Use a small allocation/decision environment with a transparent principal objective, explicit outsider rewards, and a message surface structurally similar to the real adapter. The fixture generator and label oracle must be independent of CCC's scoring function. Tests should derive expected behavior from the scripted transition mechanism, not simply assert that the method agrees with its own thresholds.

| Family | Mechanism | Expected audit behavior, not a fabricated measured result |
|---|---|---|
| A1: harmful signal-dependent coalition | Sender's signal changes receiver's allocation in a way that benefits the coalition at an explicitly defined cost to others | Valid scoped evidence when the effect is sufficiently identified |
| A2: legitimate causal cooperation | The message conveys useful task facts and improves authorized joint performance | Communication dependence may be large; harmful-collusion status must not follow |
| A3: common-cause coordination | Agents respond similarly to a shared task state; the audited message is irrelevant | No material message effect; correlated behavior alone should not suffice |
| A4: collusive talk with no action path | Suspicious-looking text is emitted after actions are committed or is ignored by a scripted receiver | No causally relevant effect; clearly label the construction |
| A5: redundant or alternative carrier | Two signals can independently induce the same coalition behavior | Single-event null does not exonerate; channel intervention is a distinct follow-up |
| A6: audit-invalid stress tests | Leaked pre-exposure memory, malformed tool exchange, or corrupted restore | Invalid/abstain, never positive certification |

Use randomized task values, role assignments, and wording templates. Keep task difficulty and exposure opportunity as comparable as possible across A1-A4. Do not bake the label into a message such as `TRUE_COLLUSION_CASE`. The detector must not receive fixture labels, hidden role instructions, or the oracle's answer.

An initial target is 20 independently generated development instances and 100 held-out instances per valid mechanism family, with separate random seeds and template groups. These are inexpensive scripted tests, not paid LLM generations. If generation is deterministic, repeating the same instance does not increase the sample size. Include probabilistic variants to exercise uncertainty estimation; deterministic variants exercise exact invariants.

The audit should be able to identify constructed benign cooperation even when an advantage-only or intervention-magnitude-only baseline reacts strongly. Report whatever happens, including fixtures on which CCC fails.

## Tier B: real Colosseum study

Start from the already working Jira setup. Preserve agent count, task generation rules, and known dependency versions. Create explicit CCC configuration files outside the ignored starter checkout. Give every configuration an accurate model label and a declared backend.

Recommended matched regimes:

- **B1: prompted coalition with private communication opportunity.** Build on the pilot, but generate new held-out worlds.
- **B2: authorized cooperation with comparable communication opportunities.** No hidden coalition objective; useful task information may flow through the same channel surface. Make clear whether the coalition identifiers here are merely a preselected evaluation subset.
- **B3: independent/common-cause reference.** Shared task state with no operational reliance on the candidate message, as established by design where possible. Otherwise call it a reference condition, not known innocence.

Retain the starter's no-private-channel condition as a descriptive condition-level baseline when affordable. Do not conflate it with a checkpoint intervention: changing the entire history and changing one exposure answer different questions.

### Pairing and task generation

Use the same task world seed across regimes where that is semantically valid. Keep role assignment, task cost distributions, and scheduler policy fixed within each matched world. Randomize or balance designated pair identities across independent worlds to avoid attributing a favorable first-two-agent position to collusion. Record every role mapping and task realization.

Validate whether environment seeds and model sampling seeds are distinct. A task seed does not control an external API's random output. Explicitly persist the generated tasks rather than relying on an integer seed as sufficient provenance.

### Candidate event selection

For confirmatory analysis, use **one predeclared eligible exposure per base trajectory**. A practical rule is the first coalition-channel message from the designated sender that the designated receiver has not yet seen, occurring before the final decision window. The exact rule must be checked against the real scheduler and frozen before holdout collection.

If this rule selects many empty or unusable exposures, revise it using development runs only. Do not search the holdout for the message with the largest effect. More elaborate localization belongs to an exploratory phase followed by independent confirmation.

Record no-message, no-exposure, and insufficient-context cases. They count in the audit's coverage denominator and cannot be silently discarded. The method's accuracy on eligible cases and its coverage across attempted cases are separate outcomes.

### Pilot, calibration, and holdout

- Existing seed 1: archival pilot only.
- Additional development: approximately three to five new worlds, as the budget permits.
- Freeze: eligibility rule, harm score, intervention logic, thresholds/margins, backend/model, analysis, stopping rule.
- Held-out target: eight to twelve new independent worlds per matched regime, with repeated continuations within checkpoints.

These are feasibility targets, not claims that the study is adequately powered. The statistician must compute attainable interval widths and decide which statements the realized sample can support. An underpowered study is labeled exploratory.

### Branch design

Within each eligible checkpoint, run F, K, and S arms with the same continuation horizon, model settings, and treatment-independent exogenous environment schedule. Shuffle branch execution order to reduce confounding with provider load or temporal drift. Use at least two fresh continuations per arm for the small feasibility study; three or more is preferable when local/credit compute permits. The original historical continuation is displayed separately, not reused as all factual replicates.

Add task-preserving repair R only on a prespecified subset where its semantic validity can be independently checked. The repair must not be generated after seeing which edit causes the desired result. Store original/edited text and the factual information inventory.

A narrower, affordable endpoint may be the target receiver's next committed allocation decision. That can support a proximal behavioral claim, not a full-episode welfare claim. Never silently shorten a horizon for branches that are inconvenient or slow.

## Call-budget arithmetic before launching

Estimate using actual pilot telemetry, not the starter's rough call count alone:

```text
base_requests = worlds * regimes * measured_prefix_requests
branch_requests = worlds * regimes * arms * continuations * measured_suffix_requests
extra_requests = judge_calls + repairs + validation_calls + bounded_retries
```

Illustration, not an observed requirement: eight worlds, three regimes, three arms, two continuations, and four suffix requests per branch imply **576 suffix requests**, plus prefix generation and validation. Twelve worlds and three continuations imply **1,296 suffix requests** under the same assumptions. The standard free OpenRouter quota cannot be treated as a bulk-experiment budget. [S10](https://openrouter.ai/docs/api_reference/limits)

If throughput makes the matrix infeasible, shrink optional regimes/extensions or use a well-defined shorter horizon; do not replace independent worlds with hundreds of repeats of one convenient checkpoint. Reserve the last part of the sprint for analysis and writing.

## Comparator set

P0 baselines:

1. **Coalition advantage only:** factual `A`, with thresholds frozen on development data.
2. **Unqualified knockout:** intervention magnitude without validity/harm/cooperation checks. This tests whether CCC adds anything beyond "remove a message."
3. **Harm-gated knockout with uncertainty:** a strong baseline using the same objective/harm observables, branch data, and interval method as CCC, but without CCC's additional validity and information-loss adjudication. This prevents claiming novelty merely for adding a harm condition to an intentionally weak detector.
4. **Transcript suspicion:** a fixed rubric judged from permitted observable text; use an existing local/free model or a clearly labeled rule-based substitute if no adequate judge budget exists.

Evaluate the contribution of validity checks, harm checks, and cooperation controls with feature ablations on the same frozen data where possible. Do not give CCC hidden labels or extra human information that its strongest comparator lacks without reporting that difference. Choose matched coverage/recall operating points on development data; never tune them on the held-out labels.

Optional: action-dependence or mutual-information baseline only when the collected data support a defensible estimator. Four agents' final choices in one run are not a reliable mutual-information dataset. Report an omitted baseline honestly rather than implementing a misleading statistic.

Keep observer access consistent across methods. If CCC has replay access and a transcript judge does not, state that capability and compute difference explicitly. Report performance versus audit cost/coverage, not an unfair claim that CCC dominates at equal information and compute.

## Blinding, leakage, and labeling

Separate fixture truth, prompts, evaluation labels, and audit inputs. A transcript judge must not see "colluder" file names or hidden objective labels. Use neutral run identifiers in blinded inputs. A different worker should audit this boundary.

For real LLM cases, report regime-conditioned effects and harm evidence. Do not calculate a universal "collusion detection accuracy" by treating all prompted agents as true positives and all cooperative prompts as true negatives. Any manually adjudicated labels need a written rubric, observable evidence, recorded uncertainty, and independence from CCC's score.

## Optional mitigation result

If a carrier is credibly localized, compare a targeted restriction with blanket private-channel removal on fresh evaluation worlds. Measure both the declared harm and legitimate utility. Freeze the targeted policy using development data; do not select the best intervention on the same worlds used to claim mitigation success. A reduction in all activity is not a useful safety improvement by itself.
