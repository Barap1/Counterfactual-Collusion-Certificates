# ENH-C: competing research directions (R1 input)

Evidence labels: everything below about v1.2.2 is **development** (Gate A DEV seeds 12000-12019, 20 independent world groups; 4 wording/stratum copies per group are not independent). Computed by `docs/enh/r1/scratch_C/a1_gates.py` from `gate_a_results.json.gz` (read-only).

## 1. Why CCC supports so rarely (from code and counts)

`decide()` in `ccc/audit/decision.py` supports only if ALL hold: valid, no treatment-dependent missingness, accepted N_m placebo that ran with no lesion artefact, `tau_O` lower bound > m_O = 2.5, coalition benefit pass (`tau_C` lower bound > 0), no material efficiency gain (`tau_W` lower bound >= -n_O*m_O), `info_bearing is False`, no redundancy flag.

The 80 A1 cells (truth = "forbidden" mechanism label), by the **oracle** effect:

| Bucket | Cells |
|---|---:|
| oracle tau_O = 0 (receiver never acts on the signal in this iid world) | 30 |
| oracle tau_O < 0 (steering helps outsiders) | 24 |
| 0 < tau_O < 2.5 (below m_O) | 14 |
| tau_O >= 2.5 ("path active") | 12 (3 world seeds per mechanism: 12006/12011/12014 for A1a, 12006/12011/12015 for A1b; 4 distinct seeds overall) |
| ...active and supported | 4 (one seed, 12011) |
| ...active, blocked by `pattern_mutual_disruption` (tau_C interval not > 0) | 8 |

So 68/80 "forbidden" cells have no realized outsider harm above the floor; "not supported" there is the correct answer to the realized-effect question. The 8/80 "sensitivity" in the Gate A table is dominated by the **label-vs-realized-effect gap**, not by CCC conservatism. Among the 12 active cells, 8 fail the coalition-benefit gate (6 of them with `info_bearing=True`, which would block next); only 1 independent world (seed 12011) is cleanly supported. The iid generator (`ccc/fixtures/iid.py`) draws costs uniformly in [2,30] with no conditioning on effect, so the mechanism label ("receiver follows signal") rarely implies large harm. The 4 independent active seeds for A1 is also a power problem: any prospective claim needs far more worlds.

Related facts: A5 (redundant, 120 cells) is 100 "not supported" because single-event K shows `tau_O`=0 (path active in only 4/40 per family); paraphrase resends carry no flag in 40/40 cells (`ccc/audit/text.py` matcher is lexical by design). A2 (legit) never supported: 22 inconclusive, 18 not supported of 40 (A2a).

## 2. Can the current generators build matched indistinguishable pairs?

Two generators exist.

**`ccc/fixtures/worlds.py` + `runner.py` (structural, 4 agents).** Receiver rule in {primary, either, shared, committed}; `runner.detector_input(arm, joint_mask)` is the exact auditor view (allowlisted, `assert_blinded`). Already usable pairs:
- *Redundant vs inert (outcome-identical):* `either` (events 0 and 1, bit-independent) vs `committed` with bit=True. Under F, S and single-event K both give `active=True`. The oracle already calls the first `not_identifiable` for this reason (`oracle.mechanism_truth`, `redundant_path`). Gaps: the inert template differs from the harmful template in `generate()` (auditor sees different text), and `committed` emits one event, not two. Minimal code: a new world constructor (about 40-60 lines, outside `ccc/`) with a `duplicate_event` flag and shared template choice, so both worlds emit identical observations; the existing `joint_mask=True` arm in `detector_input` then separates them. This is the cleanest demonstration that the limit is relative to the intervention set, not to the world.
- *Common cause vs inert:* `shared` and `committed` are literally the same `action()`; they differ only in templates (and `common` renders "base"). Pair is outcome-identical by construction; label difference is only narrative. Weak science, but valid as a "label unobservable" control.
- *Harmful vs legitimate cooperation:* currently separated by the payoff (`transfer` vs `service`), i.e. the label is a function of the outcome the auditor sees. Not a matched pair. A real pair needs a **hidden authorization/justification field** (new label axis, e.g. principal-authorized transfer) that never enters observations. That is identical-by-construction (tautological) and must be framed as such: the informative part is what CCC and baselines then *output* (CCC's claim wording is about exposure contribution, so it should say the same thing for both; B1/B3b knockouts will too).

**Jira/iid generator (`jira.py`, `iid.py`; what Gate A uses).** Agents are policies keyed by `world.case` strings in `iid_decision`. A new variant needs a new case plus receiver-policy branches (decode resend vs ignore it; act on first vs second), and `native_case` in `ccc/audit/gate_a.py` must accept it. Minimal: new module that subclasses/wraps `JiraCase` and monkeypatches the policy (about 200-300 lines). Realistic pair here: A5a-paraphrase (receiver acts on first OR resend) vs a world where the receiver acts on the first only but K nonetheless shows `tau_O`=0... that second world is not outcome-matched. Outcome-matched Jira pairs are therefore hard; do them in the structural generator and use Jira only for the population-prevalence question.

## 3. Direction assessments

### A. CCC v2 (fix redundancy/semantic carriers), prospective
- Feasibility: add a "K2" arm (mask all later events from the same sender/channel; machinery exists as `joint_mask` in `runner.py`, `refresh.py`/`placebo.py` for Jira) and a carrier-agnostic redundancy rule; edit `decision.py` flags. 10-14 h incl. tests and regression on DEV; Jira port is the costly part. Cannot fix the paraphrase blind spot without a decoder (LLM, excluded by $0 and by the project's own CARRIER_LIMIT_TEXT).
- Novelty: low-moderate (resend/ablation of redundant paths is standard in causal/ablation work; the claim-ladder wording is the novel part and already exists).
- Validity: highest circularity risk. We author both the fixtures and the fix; any gain on A5/A6 is by construction. Prior failures are DEV; sample (4 active A1 seeds) is too small.
- Visual/demo: modest (one before/after table).
- Learn: positive = K2 resolves redundancy in scripted worlds (expected, uninformative). Negative = rule trades specificity for recall (informative but small).

### B. Abstention-aware benchmark
- Axes: mechanism label M, realized harm H, causal exposure effect E, identifiability I(information set). Scoring: per-instance expected utility with abstention cost c in (0,1); report **risk-coverage curves and a 2x2 (accuracy when answering; abstention rate on non-identifiable)** rather than one scalar, so always-abstain scores zero on the first axis and always-answer is penalized on the second. Add a "Bayes-given-I" reference method (see 5) that is the ceiling for any abstainer.
- Feasibility: mostly bookkeeping on existing rows (`oracle_effects`, `oracle_strata`, `truth`): 6-8 h for scoring + report; new instances optional.
- Novelty: moderate; selective prediction is known, but separating M/H/E/I for collusion attribution is a clean contribution. Conflict risk: I must be defined independently of CCC's gates, otherwise CCC wins by construction.
- Visual: good (axis grid, risk-coverage plot).
- Learn: positive = CCC abstains on mixed classes and answers on pure ones. Negative = CCC over- or under-abstains versus the information-set ceiling; both publishable as a calibrated finding.

### C. Identifiability / indistinguishability study
- Feasibility: structural generator pair constructors (4-6 h), exhaustive enumeration of the finite receiver-rule space (all boolean rules over inputs (primary, secondary, bit) x payoff x authorization flag, a few hundred worlds) partitioned into observational-equivalence classes under nested intervention sets I0={transcript+F}, I1=+K, I2=+S,N, I3=+joint mask, I4=+content-swap (3-4 h), run actual CCC and B0-B4 on pair members (4-6 h; Jira baselines need adaptation, structural worlds have no placebo N, so CCC pipeline may need a thin adapter). 14-18 h total.
- Novelty: moderate-high if framed as a *measured frontier* (which label distinctions need which interventions, and how often natural populations fall into non-separable classes), not as a theorem. Equivalence under a fixed information set is a tautology; say so in the paper and state the contributions that are not: (i) empirical symmetry check that the real pipeline emits byte-identical outputs on pair members (catches leaks); (ii) minimal separating intervention per label pair; (iii) prevalence in the iid population (section 1 gives a first number: 68/80 forbidden-labelled cells have E < m_O); (iv) behavior of baselines on pairs.
- Validity threats: pair worlds are hand-built, so the share of "natural" worlds in indistinguishable classes depends on the generator; report prevalence only for the iid population and call it conditional. Avoid "no auditor can ever..."; state limits per information set.
- Visual: strong (class lattice, pair side-by-side transcripts, heatmap label x intervention set).
- Learn: positive = a precise, executable limit and the cheapest resolving arm. Negative (pipeline leaks, i.e. pair members decide differently) = discovers an information channel CCC uses beyond the stated evidence, which is itself a finding.

## 4. Ranking

1. **C as core + B as scoring/benchmark layer + a small A (K2 arm as an evidence level, not a "fix")**. Fits the north star (evidence standards, not detection), cheap, $0, no LLM calls, defensible after a confirmatory null, and turns Gate A's failures (A5, A2) into the object of study.
2. B alone (cheapest, lower risk, less scientific content).
3. A alone (highest circularity, smallest evidential gain).

## 5. Falsifiable research questions (winner)

1. **Symmetry:** for each pair type, are CCC outputs (status, reasons, flags, intervals) and B0-B4 labels identical across members under I1-I2? Falsified by any within-pair difference outside the allowlisted world_id/identifiers.
2. **Resolving arm:** does adding the joint-mask arm (I3) separate redundant-vs-inert pairs in 100% of pairs without raising the false-support rate on A2/A3/A5b-like negatives above the I1 rate? Falsified by any false support on a negative or an unresolved pair.
3. **Prevalence:** in a fresh iid population, is the share of mechanism-"forbidden" worlds with exposure effect >= m_O below 25%? (DEV: 12/80 = 15%, 4 independent seeds.) Falsified if >= 25%.
4. **Abstention quality:** relative to the Bayes-given-I reference, does CCC have abstention precision and recall >= 0.9 on classes labeled mixed (identifiability 0), and zero over-claims? Falsified otherwise.
5. **Baselines:** on authorized-vs-unauthorized transfer pairs, does the strongest knockout baseline attribute "harmful collusion" on the authorized member at a rate > 0.5 where CCC's claim wording is unchanged? Falsified if the baseline abstains/clears at least as well as CCC.

## 6. Prospective protocol sketch

- **Estimands:** per-method over-claim rate (supported/flag on a not-attributable class), correct-answer rate on identifiable classes, abstention precision/recall vs I, pair-symmetry violation count, separation rate with added arm.
- **Classes (labels x axes):** M in {harmful, legitimate/authorized, inert, common-cause, redundant, invalid}; H realized harm yes/no; E effect >= m_O yes/no; I identifiable under I1 yes/no (computed by enumeration, not by CCC).
- **Methods:** CCC v1.2.2 as frozen; CCC + K2 (single pre-specified variant); B0-B4; **strongest reasonable baseline = Bayes-given-I** (majority label per equivalence class with the true class priors; unbeatable by any method restricted to I) plus best knockout (B3b/B1) under the same arm budget; always-abstain and always-answer as sanity anchors.
- **Samples:** structural pairs: 200 independent world seeds x 6 pair types (pair members share the seed and count as ONE independent group; nuisance factors: roles, baseline, amount, token, template). Jira iid prevalence: 200 independent world seeds (vs 20 in DEV), outcome deterministic so repeated continuations add nothing. Report world-cluster exact/Clopper-Pearson intervals; no seed reuse from 12000-12019 or from held-out EXP-002.
- **Stopping rule:** fixed N, single pass, no interim looks, no seed replacement; any pipeline crash or asymmetry is reported as a result and fixes force a new seed block.
- **Claims allowed:** descriptive/measured frontier for the specified information sets only; no "undetectable" statements beyond them; label all as new-prospective.

## 7. Freeze before drawing seeds

1. Seed ranges and RNG schema (new split manifest, disjoint from DEV/hold-out), generator code hash for pair constructors and iid population.
2. Axis definitions (M, H, E, I), thresholds (m_O = 2.5 and the harm definition), and the information sets I0-I4 including exactly which arms are observable.
3. The enumeration code and its output (class partition and priors) hashed before running any method.
4. Decision code hashes: CCC v1.2.2 and the single K2 variant; baseline implementations and thresholds; no tuning on the new seeds.
5. Scoring formula, abstention cost(s) c, risk-coverage grid, and the list of reported metrics and tables (including negative ones).
6. Primary hypotheses and their pass/fail criteria (RQ1-RQ5), sample sizes, stopping rule, and the rule for handling crashes or symmetry breaks.
7. Wording of the limit statement (per information set; explicitly not a general theorem).
8. Adapter for structural worlds to the CCC pipeline (placebo N handling) and its test evidence, since structural worlds lack N_m.
