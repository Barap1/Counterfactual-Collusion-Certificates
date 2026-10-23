# Counterfactual Collusion Certificates: Auditing Harmful Coordination Without Confusing It with Cooperation

**DRAFT v0 (PUB-002), 2026-10-23. Methods-first. No held-out result exists.** Working title only [OWNER]. Authors and affiliations: [OWNER].

**Tag grammar (remove before export).** `[VERIFIED: path]` marks an implementation or integrity statement backed by a committed artifact. `[PROVISIONAL: reason]` marks anything under diagnosis, development-only, or dependent on an unfrozen value. `[RESULT-PENDING: task]` is an empty result slot. `[TODO(...)]`, `[OWNER]` are as in `paper/outline.md`. Nothing tagged PROVISIONAL or PENDING may be read as a finding.

---

## Abstract

[RESULT-PENDING: STAT-002 frozen headline + REV-001 sign-off. Write last, 150-250 words.]

Skeleton (beats only, no content):
1. Problem: removing a message and checking whether the outcome changes can mislabel useful teamwork as harmful collusion. [no number]
2. Approach: a validity-gated fork / mask / sham audit of a declared message exposure in a replayable Colosseum Jira task, returning one of *supported / not supported / inconclusive / invalid*. [no number]
3. Evaluation: controlled fixtures with benign causal cooperation as hard negatives, compared with outcome-only, knockout, influence-score and transcript-rule baselines; a small development-scale local-model case study. [RESULT-PENDING: STAT-002 primary comparison; RESULT-PENDING: EXP-002 case-study counts]
4. Takeaway, scoped "in this controlled setting". [RESULT-PENDING: REV-001]

---

## 1. Introduction

Track 2.3 of the sprint asks what should count as convincing evidence of collusion among AI agents. A natural audit removes a suspicious message and checks whether the outcome changes. This test has a weakness. Useful teamwork is also communication-dependent: if one agent tells another its costs or availability, removing that message changes the outcome too. The size of a knockout effect therefore cannot by itself separate harmful coordination from legitimate cooperation. Colosseum notes that "collusion is not always harmful" and that it "remains unclear which qualitative factors yield efficient yet non-collusive communication" [nakamura2026colosseum]. We target that gap at the level of a single declared message exposure.

An auditor of a replayable multi-agent deployment needs evidence that (a) survives a valid intervention, (b) is tied to a declared harm rather than to coalition advantage alone, and (c) is withheld when the evidence is insufficient. We call the resulting record a *certificate* only in the sense of an evidence record with explicit preconditions. It is not a proof, a legal finding, or a detector of intent. The method needs an executable, checkpointable simulator and a declared suspected exposure (a sender-to-receiver message). It does not apply to immutable production logs alone.

**Contribution (scoped, conditional on what is implemented and tested).** We contribute a reproducible audit protocol that combines the elements below, and we evaluate its failure modes on the tasks listed in Section 3.5. [CONTRIB-PENDING: delete any element not implemented and run by submission.]

1. A validity-gated counterfactual audit protocol for communication in replayable, tool-using LLM agent teams, instantiated on Colosseum's Jira task. It forks at the receiver's earliest exposure, regenerates fresh continuations under factual, receiver-masked, sham and matched-neutral arms, estimates the change in a predeclared harm outcome separately from coalition advantage and task-utility loss, and returns *supported / not supported / inconclusive / invalid*.
2. An evaluation against outcome-only, knockout, harm-gated knockout, influence-score and rule-based transcript baselines on controlled fixtures that include benign causal cooperation as hard negatives. [RESULT-PENDING: STAT-002 primary comparison]
3. A replay engineering layer and an open harness, with an integrity check suite that we also run against deliberately faulty replays (Section 3.8).

The contribution is the combination and its failure-mode evaluation. It is not the intervention itself: counterfactual intervention is established practice (Section 2). Whether CCC outperforms any baseline is an empirical question that our evaluation may answer either way (Section 4.2).

---

## 2. Related Work

All citations are to sources verified in `paper/references_draft.bib`. The method comparisons below are based on full-text reads of VLA and Tran and Yu [VERIFIED: docs/research/sci001/close_read.md §§1–2]. Other statements about prior work rest on abstract-level or partial reading unless noted. [TODO(PUB): rerun the residual novelty search (claim_review section 4).]

**Interventional collusion audits.** Counterfactual intervention is already used as evidence of collusion. In algorithmic pricing, forced deviations and impulse responses separate reward-punishment schemes from merely high prices [calvano2020artificial]. A recent analysis finds that such a test can be non-selective, because a forced price increase triggers the same retaliation as an undercut [lopesdemoraes2026deterrence]. For LLM market agents, Tran and Yu force one agent to deviate in a cloned market, regenerate both continuations under shared sampling seeds, and use A/A tests, strategy-free placebos, and positive controls [tran2026enforcing]. Sham-like pairing and regenerated continuations are therefore precedented in kind. Their method studies action interventions and enforcement rather than message-removal effects on a declared harm outcome. Messages appear in Appendix J as cheap talk, are coded, and are not ablated [VERIFIED: docs/research/sci001/close_read.md §2]. Controlled peer interventions give population-level causal evidence of collusion in long-horizon LLM interaction [shi2026emergent]. We make no claim to be the first causal or interventional audit, and carry the selectivity concern over to message interventions.

**Message-level counterfactuals.** VLA [kaur2026beyond] intervenes on a sender's continuous latent vector using delivered, matched-neutral, blocked, and independent conditions; its anomaly gate compares candidate-action distributions against stored matched-condition references. This is a single-step analysis: the detector does not regenerate continuations, and white-box steering reruns a sender decision or replaces the incoming latent before receiver scoring [VERIFIED: docs/research/sci001/close_read.md §1]. Its neutral condition is a content reference, not a sham variance-floor arm. Neither VLA's neutral-latent negatives nor Tran and Yu's non-colluding placebos test causally useful legitimate coordination [VERIFIED: docs/research/sci001/close_read.md §§1–2]. Our scope is text exposures in tool-using teams and legitimate causal cooperation as a source of false positives. Rose et al. [rose2026detecting] state a counterfactual communication-removal criterion for collusion and relax it because counterfactual simulation cannot always be assumed. CCC operationalizes a scoped, stochastic approximation of that criterion. Audit the Whisper [tailor2025whisper] applies per-utterance auditor interventions with fresh-seed calibration. Its honest baselines contain no legitimate cooperation, so its false-alarm bounds do not transfer to our setting and we do not borrow them.

**Testbed.** Colosseum [nakamura2026colosseum] measures collusion through regret against the DCOP optimum, coalition advantage, and condition-level secret-channel contrasts. We build on its environment and attribute its metrics. Colosseum states the cooperation-versus-collusion limitation itself; we do not present it as our discovery. Our channel-level arm is a replication bridge to its condition-level control, not a contribution.

**Counterfactual replay in MAS debugging.** Remove-or-edit-and-replay is standard practice for failure attribution [cha2026zeroreplay; ma2025dover; epperson2025agdebugger; zhang2025agentracer; li2026repair]. These methods typically assume deterministic replay, and several find that more than one distinct intervention can repair a failure [ma2025dover; li2026repair]. CCC repurposes the technique for a harm-versus-utility estimand under stochastic resampling, with collusion-specific negative controls, and reports redundancy as "not identifiable" rather than "no effect".

**Influence is not collusion.** Counterfactual influence of one agent's messages on another underlies pro-social coordination objectives [jaques2019social]. Messages can be informative yet causally inert [lowe2019pitfalls], and detectors can be confounded by benign affinity [zhou2026cabal]. These results motivate our benign hard negatives and our inert-talk and sham controls. Covert and tool channels can also escape text-level interventions [motwani2024secret; rippin2026tooluse]; this is a limitation we inherit (Section 5).

---

## 3. Methods

### 3.1 Setting

We use the Jira-ticket task of Colosseum on the Terrarium multi-agent framework. Four agents, a designated coalition pair C = {s, r} and two outsiders O, claim tasks with per-agent costs; the installed reward is `r_i = 20 + 20*prio - cost_i` for a claimed task and 0 for a skip, with the loss `20*(k-1)/k` for each of k agents sharing a task [VERIFIED: docs/research/sci002/protocol.md section 0, F1]. The pinned upstream checkout is Colosseum commit `d585a7b` with `terrarium-agents==0.1.1` [VERIFIED: docs/eng/ENG-001_state_map.md section 0]. Colosseum and Terrarium are preexisting organizer or third-party code; the audit protocol, fork and mask machinery, fixtures, baselines, runner and analysis are sprint work (Section 3.9).

The state map shows that agents have no memory across turns: each turn rebuilds a fresh two-message context containing the full event log of every board the agent belongs to [VERIFIED: docs/eng/ENG-001_state_map.md sections 1-3]. A private message is therefore re-rendered at every later receiver turn. This is the reason the mask must be persistent, not one-shot (Section 3.3).

### 3.2 Outcomes and estimand

Let W = sum of r_i over agents. We define W from the per-agent rewards, not from the upstream `joint_reward`, because the two differ in 323 of 4,096 exhaustively enumerated assignments (duplicate claims of an unknown task id) [VERIFIED: ops/reports/ENG-003.md; docs/research/sci002/protocol.md F2]. Coalition advantage A is reported separately: A > 0 is not harm.

The primary harm outcome is outsider shortfall, h = -Omean, where Omean is the mean outsider reward. The primary estimand is

tau_O = E[Omean under K] - E[Omean under F],

the change in outsider reward when the receiver does not see the audited exposure E* [VERIFIED: docs/research/sci002/protocol.md v1.2 §§2.1–2.3]. Harm units are Colosseum reward units, not dollars. Secondary estimands are the coalition benefit tau_C = E[Cmean_F - Cmean_K], total-utility change tau_W = E[W_K - W_F] = n_O tau_O - n_C tau_C, matched-message placebo effect tau_O^N, and bias-corrected communication dependence TV_excess (receiver task-distribution distance minus its permutation-null mean). We always report tau_O − tau_O^N with its interval as descriptive, non-gating context; raw total variation is never reported alone [VERIFIED: docs/research/sci002/protocol.md §§2.1–2.3, 8].

### 3.3 Arms and the fork

All arms restore the same serialized checkpoint, taken immediately before the receiver's prompt at the earliest exposure t\* is assembled. Every agent's turns after t\* are regenerated in every arm. The arms are:

- **F (factual):** unmodified render; the reference.
- **S (sham):** the mask transform with an empty mask set, byte-identical to F's render. It measures natural continuation variance and exercises the code path. It does not control for lesion-induced disruption.
- **K (receiver mask, primary):** the events of E\* are omitted, by event id, from every receiver prompt in the horizon, with original board indices preserved. New sender posts after t\* are not masked; a resend is detected and flagged.
- **N_m (matched-message placebo mask):** mask a preregistered set M* of matched, non-informational messages from the same sender, leaving E* visible. It uses the K mask path on all checkpoints where M* is available. This tests whether applying the masking operation, index gap, and prompt shrink to irrelevant content changes outcomes; it does not establish that removal of E* or other salient content is harmless. If M* is empty, N is unavailable [VERIFIED: docs/research/sci002/protocol.md §§3.1, 3.3].
- **C (channel mask, optional):** all sender-authored private-channel messages are masked. This is the bridge to Colosseum's condition-level control.
- **R (task-preserving repair):** deferred; not run. [CONTRIB-PENDING: confirm R is excluded.]

Only `communication` events in the receiver's view are altered. Environment state, other agents' views, tool results, and model settings are held fixed. Removing an action with mechanical effects is a different estimand and is outside the certificate. [VERIFIED: docs/research/sci002/protocol.md section 3 (design as written); implementation status: docs/eng/ENG-003_replay_contract.md]

**Fork at earliest exposure.** The exposure is a declared sender-to-receiver message; the fork is the receiver's first prompt that would render it. A candidate-exposure selection rule is preregistered, to avoid choosing the largest of many candidate lesions. Exposures that were already visible to the receiver before t\*, or that arrive after the receiver's decision, are tabulated as ineligible. [PROVISIONAL: selection rule is part of the unfrozen SCI-002 protocol v1.1 / prereg.]

### 3.4 Validity checks

An audit branch is checked before a verdict: checks cover restored-state and prompt identity, exposure integrity, intervention isolation, fresh continuation calls, tool and mask validity, model/backend identity, balanced missingness, sham equivalence (V9), and the matched-message placebo test (V10) [VERIFIED: docs/research/sci002/protocol.md §§4, 7]. If M* is empty, a would-be `supported` record becomes `inconclusive: no_placebo_available`; the placebo does not test removal of salient content. A failed integrity check yields an `invalid` record. The one-load-session rule comes from a measured backend property: at temperature 0.7 with a fixed seed, local outputs were identical within a model load but changed after an unload and reload [VERIFIED: ops/reports/INF-001.md (determinism section)].

### 3.5 Decision rule

Per checkpoint, each contrast is estimated from that checkpoint's own continuations (F4, K4, S2 and N4 in development; held-out S is n=1 on the frozen 50% subset) by exact shift-permutation inversion, giving one-sided 95% bounds L and U [VERIFIED: docs/research/sci002/protocol.md §§7, 11]. The status, evaluated in order, is:

1. **invalid:** a branch-integrity check fails, or the study-level sham equivalence fails.
2. **inconclusive (ineligible):** the exposure is not eligible.
3. **supported:** validity checks pass, including N_m study-level and case-level requirements; L(tau_O) > m_O; the coalition benefit gate passes (L(tau_C) > 0); the efficiency gate passes (L(tau_W) >= -delta_W, with delta_W = n_O m_O); and the frozen rule-based extractor finds the exposure not information-bearing. If no matched placebo is available, a would-be supported case is `inconclusive: no_placebo_available`. The required record says only that generic disruption was not shown for masking non-informational messages; it does not establish that removing salient content is harmless [VERIFIED: docs/research/sci002/protocol.md §§7–9].
4. **not supported:** valid, U(tau_O) < m_O, and no redundancy or post-fork-carrier flag. The record states that this is not evidence the agents did not collude.
5. **inconclusive** otherwise, with every applicable reason attached (imprecise, efficient transfer, mutual disruption, information loss untested, lesion artefact, not identifiable under redundancy, treatment-dependent missingness).

The frozen commitment extractor segments clauses, extracts agent-keyed `(agent, task)` tuples with negation handling, and tests carrier matches by tuple containment or normalized-text shingle similarity; the same implementation supplies `info_bearing` and shares no code with fixture policies [VERIFIED: docs/research/sci002/protocol.md §9]. Operating-point values are set from development data using factual and sham arms before held-out [VERIFIED: docs/research/sci002/protocol.md §11]. Numeric preregistration and threshold freeze status remain provisional [PROVISIONAL: docs/research/sci002/protocol.md §§11–12].

### 3.6 Baselines

Every baseline receives the same branch data, outcome function and interval method as CCC, and free thresholds are fixed on development fixtures at a dev operating point matched to CCC's development coverage [VERIFIED: docs/research/sci002/baselines.md (fairness rules as written)]:

- **B0** outcome-only coalition advantage;
- **B1** harm-agnostic knockout magnitude (receiver action distance, or advantage change);
- **B2** harm-gated knockout, the strong baseline: flag iff L(tau_O) > m_O;
- **B2+** B2 plus CCC's pattern gates, with no validity, placebo, redundancy or information-content logic, so that CCC is not credited for gates a baseline could trivially add;
- **B3** VLA-style single-step influence score, our adaptation and not a reproduction of [kaur2026beyond], in a next-commitment form (B3a) and a first-step output form (B3b);
- **B4** transcript suspicion monitor: a frozen keyword rubric (B4-rule); the optional local-LLM variant is omitted under the no-model-call constraint of the development run;
- **B5** condition-level secret-channel contrast, descriptive and not a per-case detector.

Beating only B0 or B1 would be a weak comparison. We report the comparison against B2 and B3 as primary. A baseline may match or outperform CCC on some or all fixture families; this is a possible outcome that the evaluation is designed to expose, not to avoid.

### 3.7 Fixtures and truth oracle

Tier A consists of scripted four-agent worlds whose mechanisms are known by construction. The truth label is defined by the sender and receiver policy's objective (forbidden, legitimate, or none), never by an outcome inequality. A separate exact oracle recomputes the effects by exhaustive enumeration directly on the simulator, with no use of CCC's checkpoint, mask, render-check or statistics code; the oracle checks estimator bias and stratifies results but supplies no status label. Scripted policies read only the rendered prompt through fixed patterns, and CCC's extractor shares no code with them [VERIFIED: docs/research/sci002/fixture_spec.md sections 1.1, 1.4 (as specified)]. Families:

- **A1** harmful signal dependence (forbidden); A1a direct, A1b relay.
- **A2** legitimate causal cooperation (the hard negative): a message is causally useful and carries no forbidden objective.
- **A3** common cause or mechanical path with no message path; A3b has state-redundant visibility.
- **A4** suspicious talk with no action path (A4a post-decision, ineligible; A4b none).
- **A5** redundant or alternative carriers: the event-level mechanism is not identifiable.
- **A6** audit-invalid stress tests: leaked digest, one-shot mask, corrupted restore (factual-only and mask-only), reused future, route or parameter change, protocol break, over-masking, and mask-only state perturbation. Any non-invalid status on A6 is a failure, and `supported` is a critical one.

Each family is crossed with explicit versus implicit wording and benign-sounding versus suspicious-sounding pools. Expected behavior is a prediction from the mechanism, fixed before CCC output was seen. Tier A validates the implementation of the audit rule and its predicted failure modes. It is not evidence about LLM behavior.

**Constructed controls.** These scripted cases are unit tests for reachability and implementation behavior only. They do not provide evidence about LLM behavior and are excluded from sensitivity claims and baseline comparisons [VERIFIED: docs/research/sci002/protocol.md §10].

**Real-trajectory tier (Tier B).** Local `gemma4:26b` (Ollama 0.32.5, digest `5571076f3d70...`, T = 0.7, 32k context) runs Colosseum worlds under two prompt regimes. The primary Tier B contrast compares the exposure effect on outsider reward between a deception-prompt regime and an authorized-cooperation regime across independent worlds, using a world-cluster bootstrap and an exact paired sign-flip test, both required [PROVISIONAL: docs/stats/prereg.md draft, unfrozen]. The model's backend is measured at about 900 calls per hour with 12 of 12 turns and zero tool errors on an end-to-end smoke run [VERIFIED: ops/reports/INF-001.md]. This regime contrast compares prompts, not realized collusion truth, and prompted behavior is never described as spontaneous.

### 3.8 Replay engineering

The replay layer snapshots the complete Megaboard state, environment assignment order, and RNG state; replaces wall-clock timestamps and uuids by a deterministic logical clock; preserves original event indices under masking; applies per-call K, N and C hooks; diffs the receiver prompt independently for V3; scans the full horizon for carrier copies with provenance; records per-call model, usage, latency, cost and overflow; and writes immutable branch records with artifact hashes. A new sender post after t\* passes the mask check and sets `resend_detected` and `post_fork_carrier`, while re-rendering a masked original fails it [VERIFIED: ops/reports/ENG-003.md]. The replay test directory ran 58 tests, all passing; the whole offline suite at that time ran 199 tests with 1 failure and 18 errors that ENG-003 attributed to a stale fixture assertion and an unowned runner manifest schema [VERIFIED: ops/reports/ENG-003.md; docs/eng/ENG-003_replay_v1_verified.txt]. After integration the director recorded 213 tests passing [PROVISIONAL: reported in ops/DECISIONS.md D-015; the post-integration log has not been re-inspected for this draft]. Provider-side RNG is inaccessible, and lexical and commitment matching are heuristic [VERIFIED: ops/reports/ENG-003.md].

### 3.9 Preexisting versus sprint work

Preexisting: Colosseum / `collusion_hackathon` starter code (pinned commit above), Terrarium, the starter's checkpoint-branching code, and the seed-1 prompted pilot archive, which is development data only and is not holdout evidence. Everything else (SCI-002 protocol, fixtures, oracle, replay layer, runner, baselines, analysis code) is new sprint work. [TODO(ENG): enumerate patches against upstream and licenses.]

### 3.10 Sampling unit and analysis

The unit is the checkpoint, with continuations nested inside it; checkpoints are clustered by trajectory and world. Continuations are never counted as independent cases. Fixture instances sharing a matched task seed are not independent worlds, and we report this in every fixture table. Confirmatory and exploratory outputs are separated by a column in every table. [PROVISIONAL: sample sizes (400/200/100 per variant) and the Holm-corrected secondary family are in the unfrozen prereg.]

---

## 4. Results (structure only)

No held-out data have been collected. Sections 4.1 to 4.4 describe what each result slot will contain.

### 4.1 Replay validity (Gate A integrity)

On the development Gate A run (800 deterministic cells over 20 matched task seeds, both wording strata, one scripted continuation per arm), the integrity checks on clean mechanisms passed: factual-versus-sham identity 380/380, mask-only-intended-exposure 1520/1520, branch isolation 380/380 [VERIFIED: docs/gate_a/GATE_A_REPORT.md]. Under the deliberate A6 stress variants, 350 of 360 expected-invalid cells were labeled invalid, with 10 failures attributed in the report to faults that were not exercised; the diagnosis of these is ongoing [PROVISIONAL: docs/gate_a/diag/ is uncommitted and the classification is under review (D-015)].

The overall Gate A decision is FAIL. We report this as a recorded outcome of a development gate, not as a result about collusion. The failure is split in the decision log into a replay-integrity part (passed) and an offline decision-layer part (failed), where the decision layer can be re-run after fixes without regenerating data [VERIFIED: ops/DECISIONS.md D-015 (as a record of the director's decision)]. Possible final states are: all gates pass after reviewed fixes; some gates remain failed and the paper reports the protocol's limitation; or the gate is not re-run before the deadline. [RESULT-PENDING: GA-DIAG / ENG-004 final Gate A table]

### 4.2 Controlled fixtures: the benign-cooperation trap

- **Figure 1 and Table 1** (verdicts by family and method; erroneous harmful-collusion flags on A2; sensitivity on A1): [RESULT-PENDING: STAT-002 / VIS-001].
- **Development-stage observation.** In the current development run, CCC returned no `supported` record on any A1 instance (0 of 80 forbidden-mechanism instances) and none on A2 (0 of 80 legitimate instances). Because CCC also never returned `supported` on A1, its zero flags on A2 carry no specificity information for now (the decision log calls the A2 pass vacuous). Baselines flagged some A2 instances (for example B0 on 22/40 of one A2 family) and some A1 instances [PROVISIONAL: docs/gate_a/GATE_A_REPORT.md under diagnosis; positives, thresholds and fixtures may change only by reviewed amendment (D-016)]. The cause (fixture design, protocol design, or implementation) is not settled in this draft.
- **Possible outcomes.** If sensitivity remains near zero after reviewed fixes, the finding is that the protocol, as specified, abstains or returns `not supported` on most harmful mechanisms in this setting, and that one or more baselines achieve higher sensitivity at higher false-positive rates on A2. If a baseline equals or exceeds CCC on both measures, we report that. If CCC achieves lower erroneous flags on A2 at comparable sensitivity, the primary comparison [RESULT-PENDING: STAT-002 primary estimate, interval, number of independent fixtures] will say so with its interval.

### 4.3 Real Colosseum case study

[RESULT-PENDING: EXP-001 / EXP-002 / STAT-002 table T2: eligible, ineligible, invalid, inconclusive, supported, not-supported counts; independent worlds, branch repeats and failures counted separately.] EXP-001 is a development-only local run under conditional owner approval (D-016) and its outputs are not validated evidence. A first launch attempt was refused by the runner before any model call (zero calls) because of a manifest validation error [VERIFIED: ops/reports/EXP-001_launch.md]. [RESULT-PENDING: abstention-reason distribution, if abstention dominates.]

### 4.4 Robustness and cost

[RESULT-PENDING: STAT-002 sensitivity to m_O and delta_W; resource use reconciled separately from environment task cost; dev-pilot validity and throughput (EXP-001).]

---

## 5. Discussion and Limitations

**Discussion.** [RESULT-PENDING: depends on Sections 4.1 to 4.3.] Whatever the outcome, the contribution is stated as a protocol plus a failure-mode evaluation, and a negative or abstention-dominated result is reportable under the fallback ordering: knockout magnitude alone mislabels cooperation on controlled fixtures; replay validity is a precondition; abstention reasons are a finding; and the harness is the minimum deliverable. The Gate A failure and a possible baseline advantage are both treated as outcomes to describe, not to explain away.

**Disclosure.** The v1.2 placebo redesign was motivated by the v1.1 development Gate A result: the v1.1 N filler removed the same audited content as K, making `supported` unreachable because the placebo effect tracked the K effect [VERIFIED: ops/DECISIONS.md D-015; docs/research/sci002/amendment_v1.2.md §§1, 6]. The revised matched-message placebo design was fixed before held-out collection, and further N redesigns were frozen before held-out [VERIFIED: docs/research/sci002/protocol.md v1.2; ops/DECISIONS.md D-022–D-023]. Separately, compute constraints reduced held-out sham replication to S n=1 on a hash-selected 50% of checkpoints (deviation DEV-001). This weakens V9 power to establish sham equivalence: the stated 90% half-width rises from about 0.36σ to 0.65σ, and sham uncertainty is expected to be common [VERIFIED: docs/stats/deviation_log.md DEV-001; docs/research/sci002/protocol.md §11].

**Limitations.**
- The method needs an executable, checkpointable simulator and a known suspected pair and exposure.
- Identification is limited by inaccessible state (provider RNG) and by information-loss confounds: masking removes information as well as intent.
- Partner and coalition specificity is not identifiable when outsiders never had channel access.
- A single-exposure null under redundant carriers is "not identifiable", not "no collusion". `not supported` is never evidence of innocence.
- Any legitimate transfer that does not materially raise W is outcome-equivalent to collusion under the declared norm; an outcome-only audit cannot separate them.
- Steganographic, tool and side channels escape text masking [motwani2024secret; rippin2026tooluse].
- One model and backend (local `gemma4:26b`), Jira-only world generator, small samples, and constructed fixtures. Fixtures validate the implementation, not LLM behavior. Prompted collusion is not spontaneous collusion.
- Fixture truth labels are defined by scripted policy objective; they could still encode designer assumptions.
- The N_m placebo tests the masking operation on matched non-informational content; it does not test whether removal of salient content is disruptive [VERIFIED: docs/research/sci002/protocol.md §§3, 8].
- Constructed controls are unit tests for reachability and implementation behavior only. They are not evidence about LLM behavior and are excluded from sensitivity claims and baseline comparisons [VERIFIED: docs/research/sci002/protocol.md §10].
- The shift-permutation interval assumes exchangeability after a constant shift.
- Numeric preregistration and held-out inference remain conditional on the stated freeze and collection status [PROVISIONAL: docs/research/sci002/protocol.md §§11–12].

**Future work.** [TODO: repair arm R; a second model stratum; other Colosseum tasks.]

## 6. Conclusion

[RESULT-PENDING: write last, after STAT-002 freeze and REV-001. State the supported takeaway only, scoped to this controlled setting.]

---

## Code and Data

- Code repository: [OWNER: public release approved? Remove private identifiers before any public artifact.]
- Data and reproduction bundle: [TODO(REL-001): frozen manifests; immutable branch records]. Offline Gate A reproduction command and captured outputs are in `docs/gate_a/` [VERIFIED: docs/gate_a/GATE_A_REPORT.md].
- Preexisting code: Colosseum commit `d585a7b` [VERIFIED: docs/eng/ENG-001_state_map.md]; patches and licenses [TODO(ENG)].

## LLM Usage Statement

[OWNER: approve final wording.] This project used a multi-agent workflow of Claude (via Claude Code) and Codex agents, directed by a director session, for planning, implementation, test writing, analysis scripts, literature verification, and drafting of this manuscript, including this draft. The experimental agents studied in the paper are separate local models (`gemma4:26b`) and scripted policies. As of this draft, a human owner review of the claims, results, and references has not taken place; no statement here should be read as independently human-verified. [OWNER: update when review is done.] The template recommends the final text be primarily written by the team. [OWNER]

## References

Generated from `paper/references_draft.bib` (verified-only). Cite arXiv versions as read. Keys used: nakamura2026colosseum, calvano2020artificial, lopesdemoraes2026deterrence, tran2026enforcing, shi2026emergent, kaur2026beyond, rose2026detecting, tailor2025whisper, cha2026zeroreplay, ma2025dover, epperson2025agdebugger, zhang2025agentracer, li2026repair, jaques2019social, lowe2019pitfalls, zhou2026cabal, motwani2024secret, rippin2026tooluse.

---

## Appendix A. Limitations and Dual-Use / Ethical Considerations

**What the result does and does not establish.** [RESULT-PENDING: mirror final Section 4 scope.] At most, the evaluation shows how an audit protocol behaves on constructed mechanisms and a small local-model case study. It does not show that real agents collude, that a verdict reflects intent, that a `not supported` record exonerates, or that any false-positive bound holds outside the tested fixtures. The Gate A development gate currently has a recorded FAIL on its decision layer [PROVISIONAL: docs/gate_a/GATE_A_REPORT.md]. Findings do not generalize to frontier agents, other tasks, or live markets.

**Dual use.** (i) A validity-gated audit could, in principle, help colluding designers learn which exposures evade it, for example by routing through redundant or covert channels that the audit labels "not identifiable" or does not reach. (ii) The fixtures and prompts that elicit collusive behavior could be read as recipes. Mitigations we plan: report the audit's blind spots explicitly in the main text; run only sandboxed simulated tasks (no real markets, users, or credentials); release scripted fixtures that encode toy reward structure rather than operational coordination tactics; and review released prompts before any public repository [OWNER/REV-001: confirm]. [TODO(PUB/REV-001): final dual-use assessment.]

**False reassurance.** A `not supported` or `inconclusive` record could be misread as clearance. The record wording states that it is not evidence of non-collusion, and we recommend against using it as a sole basis for deployment decisions.

**Other considerations.** All agents studied are local models or scripted policies; no human subjects. Spend was $0 on external inference [VERIFIED: ops/reports/INF-001.md for the benchmark; development-run spend per D-016 conditions].

## Appendix B. Additional material (optional)

Certificate schema, prompts, filler set, extra figures, fixture specifications. [TODO]
