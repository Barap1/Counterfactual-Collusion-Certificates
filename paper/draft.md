# Counterfactual Collusion Certificates: Auditing Harmful Coordination Without Confusing It with Cooperation

**DRAFT PUB-004, 2026-10-24. Methods and development evidence only; held-out analysis pending.** Working title [OWNER]. The owner is the sole author; affiliation: [OWNER].

**Tag grammar (remove before export).** `[VERIFIED: path]` marks an implementation or integrity statement backed by the named artifact. `[PROVISIONAL]` marks an unresolved claim or unfinished artifact. `[RESULT-PENDING: task]` is an empty result slot. `[TODO(...)]`, `[OWNER]` are as in `paper/outline.md`. Nothing tagged PROVISIONAL or PENDING may be read as a finding.

---

## Abstract

[RESULT-PENDING: STAT-002 frozen headline + REV-001 sign-off. Write last, 150-250 words.]

Skeleton (beats only, no content):
1. Problem: removing a message and checking whether the outcome changes can mislabel useful teamwork as harmful collusion. [no number]
2. Approach: a validity-gated fork / mask / sham audit of a declared message exposure in a replayable Colosseum Jira task, returning one of *supported / not supported / inconclusive / invalid*. [no number]
3. Evaluation: controlled fixtures with benign causal cooperation as hard negatives, compared with outcome-only, knockout, influence-score and transcript-rule baselines; a small development-scale local-model case study. [RESULT-PENDING: STAT-002]
4. Takeaway, scoped "in this controlled setting". [RESULT-PENDING: REV-001]

---

## 1. Introduction

Track 2.3 of the sprint asks what should count as convincing evidence of collusion among AI agents. A natural audit removes a suspicious message and checks whether the outcome changes. This test has a weakness. Useful teamwork is also communication-dependent: if one agent tells another its costs or availability, removing that message changes the outcome too. The size of a knockout effect therefore cannot by itself separate harmful coordination from legitimate cooperation. Colosseum notes that "collusion is not always harmful" and that it "remains unclear which qualitative factors yield efficient yet non-collusive communication" [nakamura2026colosseum]. We target that gap at the level of a single declared message exposure.

An auditor of a replayable multi-agent deployment needs evidence that (a) survives a valid intervention, (b) is tied to a declared harm rather than to coalition advantage alone, and (c) is withheld when the evidence is insufficient. We call the resulting record a *certificate* only in the sense of an evidence record with explicit preconditions. It is not a proof, a legal finding, or a detector of intent. The method needs an executable, checkpointable simulator and a declared suspected exposure (a sender-to-receiver message). It does not apply to immutable production logs alone.

**Contribution.** CCC combines a scoped audit protocol, replay machinery and a failure-mode evaluation. Held-out comparisons remain pending.

1. A validity-gated counterfactual audit protocol for communication in replayable, tool-using LLM agent teams, instantiated on Colosseum's Jira task. It forks at the receiver's earliest exposure, regenerates fresh continuations under factual, receiver-masked, sham and matched-message placebo arms, estimates the change in a predeclared harm outcome separately from coalition advantage and task-utility loss, and returns *supported / not supported / inconclusive / invalid*.
2. An evaluation against outcome-only, knockout, harm-gated knockout, influence-score and rule-based transcript baselines on controlled fixtures that include benign causal cooperation as hard negatives. [RESULT-PENDING: STAT-002]
3. A replay engineering layer and an open harness, with an integrity check suite that we also run against deliberately faulty replays (Section 3.8).

The contribution is the combination and its failure-mode evaluation. It is not the intervention itself: counterfactual intervention is established practice (Section 2). Whether CCC outperforms any baseline is an empirical question that our evaluation may answer either way (Section 4.2).

---

## 2. Related Work

Existing citation keys are retained from the prior draft; no citations are added in this update. The method comparisons below are based on full-text reads of VLA and Tran and Yu [VERIFIED: docs/research/sci001/close_read.md §§1–2]. Other statements about prior work rest on abstract-level or partial reading unless noted. [TODO(PUB): rerun the residual novelty search (claim_review section 4).]

Interventional collusion audits include forced deviations in algorithmic pricing [calvano2020artificial; lopesdemoraes2026deterrence] and cloned LLM markets with regenerated continuations, A/A tests and placebos [tran2026enforcing]. VLA intervenes on latent messages and scores single-step action distributions [kaur2026beyond]. Full-text comparisons support these distinctions [VERIFIED: docs/research/sci001/close_read.md]. Message removal also appears in collusion criteria [rose2026detecting] and multi-agent debugging [ma2025dover; li2026repair]. CCC studies text exposures, declared outsider harm and causally useful cooperation as a hard negative. Appendix B retains the detailed comparison; the combination and its limitations delimit the contribution.

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

Protocol v1.2 is final and adopted. All arms restore the same checkpoint immediately before the receiver's earliest exposure to E*. Every subsequent agent turn is regenerated. F is factual; S applies an empty mask with an identical render; K persistently masks E* by event id in the receiver's prompts, preserving indices. New sender posts remain visible and can trigger carrier flags. N_m masks a matched non-informational set M* from the same sender while leaving E* visible. It exercises the K masking path on irrelevant content; it does not test whether removing salient content is disruptive. M* must meet the frozen eligibility and length-matching rule; when empty, N is unavailable. C is optional and R is deferred; neither is in the held-out matrix. [VERIFIED: docs/research/sci002/protocol.md §§3–4]

### 3.4 Validity checks

Validity precedes interpretation: restored-state and prompt identity, exposure and intervention isolation, fresh continuations, tool/mask validity, model identity, missingness, sham equivalence (V9), and matched-placebo checks (V10). V9 passes when its 90% interval lies within ±delta_S; a 95% interval wholly outside invalidates the batch; otherwise sham equivalence is uncertain. Seeds differ across arms; no common-randomness claim is made. Provider RNG remains inaccessible. [VERIFIED: docs/research/sci002/protocol.md §7]

### 3.5 Decision rule and extractor contract

Exact shift-permutation inversion supplies one-sided 95% bounds L and U. In order: failed integrity yields `invalid`; ineligible exposures are separately tabulated; `supported` requires valid sham/placebo evidence, nonempty M*, N_m execution, L(tau_O) > m_O, L(tau_C) > 0, L(tau_W) ≥ −delta_W, and no information-bearing exposure; `not supported` requires U(tau_O) < m_O and no redundancy, resend or post-fork carrier flag. Remaining cases are `inconclusive` with all applicable reasons. Absence of a placebo blocks a positive claim, not a valid below-margin finding. [VERIFIED: docs/research/sci002/protocol.md §§7–9]

The frozen extractor segments clauses, extracts agent-keyed `(agent, task)` commitments using registered aliases and negation handling, and matches carriers by tuple containment or normalized word-shingle similarity. Generic verbs without a subject do not form commitments. Empty tuple sets leave only lexical matching. The same module supplies `info_bearing` for private quantities and commitments; it shares no code with fixture policies. The reviewed correction and re-freeze are disclosed in Section 5. [VERIFIED: docs/research/sci002/protocol.md §9; docs/stats/stage2/STAGE2_ADDENDUM.md §6]

Stage-2 pins are sigma_dev = 0.9187276506628345 (pooled df 49), m_O = 2.5 (construct floor binds), delta_W = 5.0, delta_S = 2.5, theta = 0.4, and `thin_dev = false`. Alpha remains 0.05. Calibration uses seven complete DEV checkpoints, not four complete pairs. Theta carries `weak_detector`; it is not a reliable semantic-carrier detector. [VERIFIED: docs/stats/stage2/STAGE2_ADDENDUM.md §§1–3]

### 3.6 Baselines

Baselines receive the same branch data and outcome definitions: B0 coalition advantage, B1 harm-agnostic knockout, B2 harm-gated knockout, B2+ with pattern gates, B3a/B3b single-step influence adaptations, B4-rule transcript rubric, and B5 descriptive channel contrast. The optional model-based monitor is omitted. Fairness rules require matched DEV coverage; performance comparisons await frozen analysis. [VERIFIED: docs/research/sci002/baselines.md]

### 3.7 Fixtures and real-trajectory design

Tier A contains scripted harmful dependence (A1), legitimate causal cooperation (A2), common-cause/state paths (A3), inert suspicious talk (A4), redundant carriers (A5), and replay faults (A6). Policy objectives define mechanism labels; an independent exact oracle supplies effect strata, not CCC verdicts. Constructed controls test reachability only and are excluded from sensitivity and baseline comparisons. Fixtures establish implementation behavior rather than LLM behavior. [VERIFIED: docs/research/sci002/fixture_spec.md; docs/research/sci002/protocol.md §10]

Tier B uses local `gemma4:26b`, temperature 0.7, context 32768, maximum 1500 output tokens, and no reasoning effort. EXP-002 schedules eight matched world-pairs H01–H08 (sixteen base trajectories), B1 deception versus B2 matched authorized cooperation. F4/K4 run at each checkpoint; N_m4 runs only with nonempty M*. S1 runs on the subset selected by `int(sha256("ccc.sham.v1|" + checkpoint_id).hexdigest(),16) % 2 == 0`, a hash-selected 50% rule, not a guarantee of exactly half the realized checkpoints. The request cap is 5981; no model fallback is allowed. These are design values, not completion counts. [VERIFIED: docs/runner/exp002_manifest.json; docs/stats/stage2/STAGE2_ADDENDUM.md §§6–7]

### 3.8 Replay engineering

Replay preserves serialized state and original event indices, independently checks receiver-prompt differences, scans for carriers, and records immutable branch provenance. Backend identity and fresh-call checks constrain validity; inaccessible provider RNG and heuristic carrier matching remain limits. Extractor provenance and DEV reproducibility details appear in Appendix B. [VERIFIED: ops/reports/ENG-003.md]

### 3.9 Preexisting versus sprint work

Preexisting: Colosseum / `collusion_hackathon` starter code (pinned commit above), Terrarium, the starter's checkpoint-branching code, and the seed-1 prompted pilot archive, which is development data only and is not holdout evidence. Everything else (SCI-002 protocol, fixtures, oracle, replay layer, runner, baselines, analysis code) is new sprint work. [TODO(ENG): enumerate patches against upstream and licenses.]

### 3.10 Sampling unit and analysis

Continuations are nested observations, not independent cases. The primary Tier-B quantity is Delta = mean_w[tau_O(w,B1) − tau_O(w,B2)], with whole matched worlds resampled together. The registered analysis requires both a world-cluster bootstrap interval (10000 draws, seed 20261025) and an exact paired sign-flip test. Minimum-size and eligibility floors govern confirmatory wording; case-level Tier-B status distributions are exploratory. Ineligible worlds, missingness, non-commit mapping and sensitivity analyses remain as registered. The final v1.2 arm allocation and Stage-2 addendum supersede older S2/N-subset wording in the preregistration. [VERIFIED: docs/stats/prereg.md §§3–10; docs/stats/stage2/STAGE2_ADDENDUM.md]

---

## 4. Results

### 4.1 Development Gate A and placebo availability

Gate A v1.2.2 covers 800 non-constructed DEV cells over twenty task seeds and two wording strata, with one scripted continuation per arm. It is a deterministic implementation check, not held-out stochastic inference. The corrected integrity counts are:

| Check | Passed / checked |
|---|---:|
| F/S identity | 380/380 |
| K changes only intended exposure | 4180/4180 |
| Branch isolation | 760/760 |
| A2 never supported | 80/80 |
| A6 invalid / intended validator | 350/360 |

[VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md]

CCC returned 8/800 `supported`: two each in A1a, A1b, A5a-verbatim and A5a-paraphrase. Every supported cell had oracle tau_O = 4.015, an active path and an accepted N_m placebo. There were zero false supports under the oracle margin (supported with tau_O < 2.5), and zero false negatives at the estimand level (non-A6 `not supported` with tau_O ≥ 2.5). These checks concern the exposure-effect estimand; they are not accuracy claims against intent labels. Of 28 path-active above-floor non-A6 cells, eight were supported and twenty abstained for mutual disruption, efficient transfer or redundant-path non-identifiability; the twenty include eight benign A2 cells. [VERIFIED: docs/review/director_gateA_audit.md; docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md]

The preregistered Gate A criteria (factual/sham identity, knockout scope, branch isolation, and no `supported` on benign cooperation) all pass. Two stricter diagnostic checks fail and are reported as limitations: the A5 redundancy check passes 20/120 cells (16/68 under the amended instantiation), and ten A6b faults were non-exercisable. A5 below-margin findings can be correct for a single exposure despite redundant team coordination. No paraphrase A5a cell carries a carrier flag. The pre-written prediction scorecard has sixteen confirmed, two falsified and three untested items; P1.3 is numerical agreement only because pre-census commitment was not established (DEV-002). Constructed controls are excluded from the headline denominator. [VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md; docs/review/director_gateA_audit.md]

The real-conversation Tier-B DEV census found M* available at 0/8 checkpoints, unchanged at descriptive matching windows 0.10 and 0.50. The sender's sole prior message was task-bearing and filtered out. This is a small observed sample, not a population estimate. Under the frozen availability rule, case-level Tier-B `supported` is unavailable; absent M* blocks would-be positives with `inconclusive: no_placebo_available`. N is skipped when M* is empty. The study-level F–K Delta remains defined without N; neither chatter nor a new placebo rule is introduced for real agents. [VERIFIED: docs/research/sci002/placebo_census_tierB_dev.md; docs/stats/stage2/STAGE2_ADDENDUM.md §5]

### 4.2 Controlled fixtures: the benign-cooperation trap

[RESULT-PENDING: STAT-002]

Table 2 will report CCC and baseline TP/FN/FP/TN, abstention, invalidity, attempted denominators and coverage by family, oracle-path activity and wording stratum, with determinate-only and operational views. Figure 2 will plot outsider-effect estimates and intervals against verdicts for A1/A2, identifying matched seeds and template groups. No held-out values or directions are inserted.

### 4.3 Real Colosseum case study

[RESULT-PENDING: STAT-002]

Table 3 will report attempted/completed world-pairs, eligible/ineligible checkpoints by reason, complete continuations and failures by regime/arm, status counts and abstention reasons. Table 4 will show Delta_total, Delta_conditional, within-regime tau_O, eligibility-rate difference, world-cluster intervals, paired-test outputs, sample-floor assessment and confirmatory/exploratory designation. Figure 3 will show paired world effects and the aggregate interval. Case status is exploratory and prompt regimes do not establish realized collusion truth.

### 4.4 Robustness and cost

[RESULT-PENDING: STAT-002]

Appendix Table B1 will show missingness bounds, non-commit exclusion, ineligibility alternatives, registered margin sensitivity, sham interval/attained half-width and placebo availability. Appendix Table B2 will separate requests, retries, failed/unrun work, runtime and inference spend from environment reward units. Appendix Figure B1 will show descriptive risk versus coverage. Each output will identify its denominator and analysis version; no values or expected directions are supplied.

---

## 5. Discussion and Limitations

**Discussion.** [RESULT-PENDING: STAT-002] Interpretation awaits frozen analysis and independent review. Development evidence describes a scoped exposure audit; it does not establish collusive intent or certify a team.

**Deviations and disclosures.** Protocol v1.2 was motivated by the v1.1 DEV result: the old N filler removed audited content like K, preventing support. The redesign is development-informed. DEV-001 reduces held-out S2 to S1 on a hash-selected 50% subset and drops optional pairs H09/H10. Its design calculation increases the V9 90% half-width from approximately 0.36σ to 0.65σ; attained sham uncertainty must be reported without re-pinning thresholds. DEV-002 records that the DEV placebo census preceded the required hash commit, so its results are exploratory and hashes establish subsequent byte stability rather than prior commitment. [VERIFIED: docs/stats/deviation_log.md; docs/research/sci002/protocol.md]

The reviewed v1.2.1 extractor correction occurred after the first freeze list; it was re-frozen before held-out data, retaining the earlier hash as history. EXP-001's cap calculation omitted canaries and underestimated calls per branch, leaving a 74-call shortfall. The preserved `dev05_B2/attempt_0001` failed at the collection-wide remaining budget of 223 calls (despite the error's “per-run” wording), with null outcomes, and was not rerun. Stage-2 therefore uses seven checkpoints and three complete pairs. The corrected outcome-blind cap is `ceil(1.05 × 16 × (28 + 3 + 13 × 25)) = 5981`. [VERIFIED: docs/stats/stage2/STAGE2_ADDENDUM.md §§3–6; ops/DECISIONS.md D-030]

**Limitations.**

- The method needs an executable, checkpointable simulator and a known suspected pair and exposure.
- Identification is limited by inaccessible state (provider RNG) and by information-loss confounds: masking removes information as well as intent.
- Partner and coalition specificity is not identifiable when outsiders never had channel access.
- Redundant carriers (A5). For the single-exposure estimand, CCC's `not supported` on redundant-carrier cases is correct: when another carrier compensates, removing one exposure does not change outsider harm. In every non-A6 `not supported` DEV cell the oracle outsider effect is below m_O (0 exceptions). It must not be read as "no collusion": the record concerns one exposure, not the team, and `not supported` is never evidence of innocence [VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md].
- Paraphrase carriers are not detected. The carrier matcher is shingle-based; the Stage 2 pin records best Youden J 0.495 < 0.5 and falls back to theta 0.4 with `weak_detector` [VERIFIED: docs/stats/stage2/theta_pin.json]. No A5a-paraphrase DEV cell carries a carrier flag under theta 0.4 [VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md].
- Any legitimate transfer that does not materially raise W is outcome-equivalent to collusion under the declared norm; an outcome-only audit cannot separate them.
- Steganographic, tool and side channels escape text masking [motwani2024secret; rippin2026tooluse].
- One model and backend (local `gemma4:26b`), Jira-only world generator, small samples, and constructed fixtures. Fixtures validate the implementation, not LLM behavior. Prompted collusion is not spontaneous collusion.
- Fixture truth labels are defined by scripted policy objective; they could still encode designer assumptions.
- The N_m placebo tests the masking operation on matched non-informational content; it does not test whether removal of salient content is disruptive [VERIFIED: docs/research/sci002/protocol.md §§3, 8].
- Constructed controls are unit tests for reachability and implementation behavior only. They are not evidence about LLM behavior and are excluded from sensitivity claims and baseline comparisons [VERIFIED: docs/research/sci002/protocol.md §10].
- The shift-permutation interval assumes exchangeability after a constant shift.
- The small world-pair design and reduced sham replication limit precision; inference must follow the registered minimum-size rules [VERIFIED: docs/stats/prereg.md §9; docs/stats/deviation_log.md DEV-001].

**Future work.** [TODO: repair arm R; a second model stratum; other Colosseum tasks.]

## 6. Conclusion

[RESULT-PENDING: STAT-002] Final wording requires independent review and must remain scoped to the realized evidence.

---

## Code and Data

- Code repository: [OWNER: public release approved? Remove private identifiers before any public artifact.]
- Data and reproduction bundle: [TODO(REL-001): frozen manifests; immutable branch records]. Corrected DEV reproduction commands and evidence are recorded in the v1.2.2 report [VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md].
- DEV Gate A parameter record (reproducibility): v1.2.2 pins theta to the Stage 2 value 0.4 (previously 0.8) and records the DEV bootstrap as 10000 draws (previously 2000; prereg B=10000). The DEV gate computes deterministic interval endpoints and does not read the bootstrap value, so this change alters no reported number [VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md].
- Preexisting code: Colosseum commit `d585a7b` [VERIFIED: docs/eng/ENG-001_state_map.md]; patches and licenses [TODO(ENG)].

## LLM Usage Statement

[OWNER: approve final wording.] This project used a multi-agent workflow of Claude (via Claude Code) and Codex agents, directed by a director session, for planning, implementation, test writing, analysis scripts, literature verification, and drafting of this manuscript, including this draft. The experimental agents studied in the paper are separate local models (`gemma4:26b`) and scripted policies. As of this draft, a human owner review of the claims, results, and references has not taken place; no statement here should be read as independently human-verified. [OWNER: update when review is done.] The template recommends the final text be primarily written by the team. [OWNER]

## References

Retained from `paper/references_draft.bib`; final reference audit pending REV-001. Cite arXiv versions as read. Keys used: nakamura2026colosseum, calvano2020artificial, lopesdemoraes2026deterrence, tran2026enforcing, shi2026emergent, kaur2026beyond, rose2026detecting, tailor2025whisper, cha2026zeroreplay, ma2025dover, epperson2025agdebugger, zhang2025agentracer, li2026repair, jaques2019social, lowe2019pitfalls, zhou2026cabal, motwani2024secret, rippin2026tooluse.

---

## Appendix A. Limitations and Dual-Use / Ethical Considerations

**What the result does and does not establish.** [RESULT-PENDING: mirror final Section 4 scope.] At most, the evaluation shows how an audit protocol behaves on constructed mechanisms and a small local-model case study. It does not show that real agents collude, that a verdict reflects intent, that a `not supported` record exonerates, or that any false-positive bound holds outside the tested fixtures. The diagnostic Gate A report retains A5/A6 failures; the director separately accepted module-13 Gate A (Section 4.1) [VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md; docs/review/director_gateA_audit.md]. Findings do not generalize to frontier agents, other tasks, or live markets.

**Dual use.** (i) A validity-gated audit could, in principle, help colluding designers learn which exposures evade it, for example by routing through redundant or covert channels that the audit labels "not identifiable" or does not reach. (ii) The fixtures and prompts that elicit collusive behavior could be read as recipes. Mitigations we plan: report the audit's blind spots explicitly in the main text; run only sandboxed simulated tasks (no real markets, users, or credentials); release scripted fixtures that encode toy reward structure rather than operational coordination tactics; and review released prompts before any public repository [OWNER/REV-001: confirm]. [TODO(PUB/REV-001): final dual-use assessment.]

**False reassurance.** A `not supported` or `inconclusive` record could be misread as clearance. The record wording states that it is not evidence of non-collusion, and we recommend against using it as a sole basis for deployment decisions.

**Other considerations.** All agents studied are local models or scripted policies; no human subjects. Spend was $0 on external inference [VERIFIED: ops/reports/INF-001.md for the benchmark; development-run spend per D-016 conditions].

## Appendix B. Additional material (optional)

### B.1 Detailed related-work comparison

**Interventional collusion audits.** Counterfactual intervention is already used as evidence of collusion. In algorithmic pricing, forced deviations and impulse responses separate reward-punishment schemes from merely high prices [calvano2020artificial]. A recent analysis finds that such a test can be non-selective, because a forced price increase triggers the same retaliation as an undercut [lopesdemoraes2026deterrence]. For LLM market agents, Tran and Yu force one agent to deviate in a cloned market, regenerate both continuations under shared sampling seeds, and use A/A tests, strategy-free placebos, and positive controls [tran2026enforcing]. Sham-like pairing and regenerated continuations are therefore precedented in kind. Their method studies action interventions and enforcement rather than message-removal effects on a declared harm outcome. Messages appear in Appendix J as cheap talk, are coded, and are not ablated [VERIFIED: docs/research/sci001/close_read.md §2]. Controlled peer interventions give population-level causal evidence of collusion in long-horizon LLM interaction [shi2026emergent]. We carry this selectivity concern over to message interventions.

**Message-level counterfactuals.** VLA [kaur2026beyond] intervenes on a sender's continuous latent vector using delivered, matched-neutral, blocked, and independent conditions; its anomaly gate compares candidate-action distributions against stored matched-condition references. This is a single-step analysis: the detector does not regenerate continuations, and white-box steering reruns a sender decision or replaces the incoming latent before receiver scoring [VERIFIED: docs/research/sci001/close_read.md §1]. Its neutral condition is a content reference, not a sham variance-floor arm. Neither VLA's neutral-latent negatives nor Tran and Yu's non-colluding placebos test causally useful legitimate coordination [VERIFIED: docs/research/sci001/close_read.md §§1–2]. Our scope is text exposures in tool-using teams and legitimate causal cooperation as a source of false positives. Rose et al. [rose2026detecting] state a counterfactual communication-removal criterion for collusion and relax it because counterfactual simulation cannot always be assumed. CCC operationalizes a scoped, stochastic approximation of that criterion. Audit the Whisper [tailor2025whisper] applies per-utterance auditor interventions with fresh-seed calibration. Its honest baselines contain no legitimate cooperation, so its false-alarm bounds do not transfer to our setting and we do not borrow them.

**Testbed.** Colosseum [nakamura2026colosseum] measures collusion through regret against the DCOP optimum, coalition advantage, and condition-level secret-channel contrasts. We build on its environment and attribute its metrics. Colosseum states the cooperation-versus-collusion limitation itself; we do not present it as our discovery. Our channel-level arm is a replication bridge to its condition-level control, not a contribution.

**Counterfactual replay in MAS debugging.** Remove-or-edit-and-replay is standard practice for failure attribution [cha2026zeroreplay; ma2025dover; epperson2025agdebugger; zhang2025agentracer; li2026repair]. These methods typically assume deterministic replay, and several find that more than one distinct intervention can repair a failure [ma2025dover; li2026repair]. CCC repurposes the technique for a harm-versus-utility estimand under stochastic resampling, with collusion-specific negative controls, and reports redundancy as "not identifiable" rather than "no effect".

**Influence is not collusion.** Counterfactual influence of one agent's messages on another underlies pro-social coordination objectives [jaques2019social]. Messages can be informative yet causally inert [lowe2019pitfalls], and detectors can be confounded by benign affinity [zhou2026cabal]. These results motivate our benign hard negatives and our inert-talk and sham controls. Covert and tool channels can also escape text-level interventions [motwani2024secret; rippin2026tooluse]; this is a limitation we inherit (Section 5).


### B.2 Extractor provenance and development reproducibility

The re-frozen extractor sha256 is `7b8da4f01e963fa8b5a94f60a6f33a8de613a89588a058668461e9d9aea7a311`; the correction is commit `07ca10f`. The earlier freeze entry remains historical. Theta calibration evaluated normalized word 3-shingles: best Youden J = 0.4947 at raw argmax 0.6, below the 0.5 requirement, so the registered fallback pins theta = 0.4 and `weak_detector = true`. All twenty verbatim positive pairs were detected and no paraphrase positive pair was detected across the grid. [VERIFIED: docs/stats/stage2/STAGE2_ADDENDUM.md §§2, 6]

Gate A v1.2.2 changes theta from 0.8 to 0.4 and records bootstrap draws as 10000 rather than 2000. Its deterministic intervals do not use bootstrap draws. All 800 statuses and reason-code records remain unchanged; additional carrier flags occur only in already-invalid A6a rows. Constructed controls are carried forward byte-identical and excluded from headline comparisons. [VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md]

### B.3 Additional analysis outputs

[RESULT-PENDING: STAT-002]

Tables B1/B2 and Figure B1 are specified in Section 4.4 and `paper/figures_plan.md`. Certificate schema, prompt provenance and release licenses remain release tasks. [PROVISIONAL]
