# Counterfactual Collusion Certificates: Auditing Harmful Coordination Without Confusing It with Cooperation

Author: [OWNER]. Affiliation: [OWNER]. The owner is the sole author.

## Abstract

Removing a message can disrupt useful teamwork as well as harmful coordination. Counterfactual Collusion Certificates (CCC) audits a declared exposure in a replayable multi-agent task using regenerated factual, masked, sham and matched-message placebo continuations, with validity gates and explicit abstention. Development scripted fixtures provide provisional method-validation findings on benign cooperation and replay faults, rather than evidence about model intent; these findings were not re-audited by the held-out reviewer. [VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md; docs/review/rev001/CLAIMS_LEDGER.md §D]

In a held-out local-model study of 8 matched world pairs, the preregistered contrast between deceptive and authorized-cooperation prompt regimes was Delta = 1.354 reward units (world-cluster 95% CI [-0.020, 2.834]; exact one-sided sign-flip p = 0.0703). Neither required criterion passed: this is a confirmatory null. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C1–C4, C8] Post hoc exclusion of the driving factual non-commits reduced Delta to 0.727 (95% CI [-0.31, 1.91], p = 0.156). [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C13] Exploratory certificates were 0 supported, 11 not supported and 5 inconclusive; no outsider-effect lower bound exceeded the declared margin. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C20–C24] The study concerns one local model, one deceptive prompt variant and one exposure per trajectory, with limited precision and information-loss confounds. “Not supported” does not establish that agents did not collude.

## 1. Introduction

Removing a suspicious message and checking whether the outcome changes is an appealing audit of agent coordination. Useful teamwork is also communication-dependent: removing information about costs or availability may change an outcome without revealing harmful intent. A knockout effect alone cannot separate harmful coordination from legitimate cooperation. Colosseum identifies this cooperation-versus-collusion ambiguity [nakamura2026colosseum]. We study a declared message exposure in its replayable Jira task.

CCC combines an exposure-level causal estimand, persistent receiver masking, fresh continuations, harm and utility gates, and explicit abstention. A certificate is an evidence record with preconditions, not a proof or a detector of intent. The method requires an executable, checkpointable simulator and a suspected sender–receiver exposure; immutable production logs alone are insufficient. Scripted fixtures test implementation behavior, including benign causal cooperation as a hard negative. The held-out study tests a contrast between prompt regimes. It does not supply ground-truth collusion labels or establish baseline superiority.

## 2. Related Work

Interventional collusion audits include forced deviations in algorithmic pricing [calvano2020artificial; lopesdemoraes2026deterrence] and cloned LLM markets with regenerated continuations, A/A tests and placebos [tran2026enforcing]. VLA intervenes on latent messages and scores single-step action distributions [kaur2026beyond]. These distinctions are backed by full-text comparisons. [VERIFIED: docs/research/sci001/close_read.md] Message removal also appears in collusion criteria [rose2026detecting] and multi-agent debugging [ma2025dover; li2026repair]. CCC combines text-exposure interventions, declared outsider harm and useful cooperation as a hard negative. It makes no priority claim. Appendix B retains the detailed comparison. A residual search of arXiv on 2026-10-24 (listing postings from 2026-10-20 onward; collusion combined with counterfactual, message-ablation, audit, intervention, placebo and causal terms for LLM or multi-agent systems) found no additional work overlapping this contribution; the only relevant posting in that window was the already-cited Tran and Yu [tran2026enforcing]. This is a bounded search, not an exhaustive survey. [VERIFIED: ops/reports/PUB-007.md §2]

## 3. Methods

### 3.1 Setting and outcomes

Colosseum's Jira task has four agents: a designated coalition pair C = {s, r} and two outsiders O. Agents claim tasks with heterogeneous costs. Rewards are `20 + 20*prio - cost_i` for a claim and zero for a skip, with a shared-task loss `20*(k-1)/k` for each of k claimants. [VERIFIED: docs/research/sci002/protocol.md §0, F1] We sum agent rewards to define total utility W; upstream `joint_reward` can disagree on malformed assignments. [VERIFIED: ops/reports/ENG-003.md] Rewards are task units, not currency.

The arms are F (factual), K (exposure knockout), S (sham), and N (matched-message placebo, written N_m). The primary exposure estimand is tau_O = E[Omean_K] − E[Omean_F], the change in mean outsider reward when the receiver cannot see exposure E*. Coalition benefit tau_C = E[Cmean_F − Cmean_K] and total-utility change tau_W = E[W_K − W_F] are distinct outcomes. Coalition advantage alone is not harm. [VERIFIED: docs/research/sci002/protocol.md §§2.1–2.3]

### 3.2 Interventions and validity

Figure 1 shows the branch schematic.

All arms restore the checkpoint immediately before the receiver's earliest exposure. F is factual; K persistently masks E* by event identifier in receiver prompts; S applies an empty mask with identical rendering. Later turns are regenerated. Persistent masking matters because the environment re-renders prior board messages on subsequent turns. N_m masks an eligible, length-matched non-informational message set from the same sender while retaining E*. It exercises the masking operation on irrelevant content; it cannot establish that removing salient information is harmless. N_m is unavailable when no eligible match exists. [VERIFIED: docs/research/sci002/protocol.md §§3–4; docs/eng/ENG-001_state_map.md]

Validity checks cover state and prompt identity, intervention scope, fresh continuations, branch isolation, model identity, missingness, sham equivalence and placebo behavior. Seeds differ across arms; provider RNG is inaccessible and common randomness is not claimed. [VERIFIED: docs/research/sci002/protocol.md §7]

### 3.3 Decision rule

Exact shift-permutation inversion supplies one-sided 95% bounds L and U, assuming exchangeability after a constant shift. Failed integrity yields `invalid`. A `supported` verdict requires established validity and placebo evidence, nonempty M*, L(tau_O) > m_O, L(tau_C) > 0, L(tau_W) ≥ −delta_W, and resolved information-loss gates. `Not supported` requires U(tau_O) < m_O without detected redundant, resent or post-fork carriers; other eligible cases are `inconclusive` with reasons. [VERIFIED: docs/research/sci002/protocol.md §§7–9] Frozen margins are m_O = 2.5, delta_W = 5.0 and delta_S = 2.5; alpha = 0.05. [VERIFIED: docs/stats/stage2/STAGE2_ADDENDUM.md] The carrier extractor is heuristic and marked `weak_detector`; unaudited semantic carriers remain a limitation.

### 3.4 Design and inference

Tier A: scripted fixtures; Tier B: real-agent runs.

The fixtures use scripted harmful dependence, useful cooperation, common causes, inert talk, redundant carriers and replay faults. Mechanism labels come from policy objectives; an exact oracle supplies exposure effects. Constructed controls test reachability only and are excluded from headline comparisons. Outcome-only, knockout, harm-gated, influence and transcript-rule baselines are development comparisons, with no new superiority claim here. [VERIFIED: docs/research/sci002/fixture_spec.md; docs/research/sci002/baselines.md]

The held-out real-agent study uses local `gemma4:26b` and 8 matched world pairs, B1 deception versus B2 authorized cooperation, with 4 F and 4 K continuations per checkpoint. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C8, C30, C32] The study estimand is Delta = mean_w[tau_O(w,B1) − tau_O(w,B2)]. Continuations are nested observations; whole matched worlds are the independent sampling units. The world-cluster percentile bootstrap uses 10000 draws and seed 20261025. [VERIFIED: docs/review/rev001/REV001.md §1] The directional primary requires both a positive lower confidence bound and the exact one-sided paired sign-flip criterion. Study-level primary and Holm-family tests are confirmatory under the met floors; case-level certificates remain exploratory. The disclosed label correction changes no numeric output or threshold. [VERIFIED: docs/analysis/exp002_heldout_v2/CORRECTION.md]

## 4. Results

### 4.1 Development method validation

Figure 2 shows the development fixture validation.

Development deterministic fixtures report factual/sham identity, intended knockout scope, branch isolation and no support on benign cooperation. They also retain failures in redundancy and non-exercisable replay-fault diagnostics. These are method-validation findings on scripted policies, not estimates of model behavior or general false-positive rates. The independent review did not re-audit the fixtures. Detailed counts and the distinction between diagnostic failure and acceptance by the project lead appear in Appendix B. [VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md (F/S identity 380/380, K-scope 4180/4180, isolation 760/760, A2 never supported 80/80, A5 redundancy 20/120, A6 350/360); docs/review/rev001/CLAIMS_LEDGER.md §D]

### 4.2 Held-out primary: a confirmatory null

Figure 3 shows the per-pair contrast and the aggregate Delta and confidence interval.

Delta = 1.354 reward units, with world-cluster 95% CI [-0.020, 2.834] and exact one-sided sign-flip p = 0.0703, over n = 8 matched pairs. [VERIFIED: docs/analysis/exp002_heldout_v2/effects_study.json; docs/review/rev001/CLAIMS_LEDGER.md C1–C3] The lower bound is approximately zero. The preregistered decision is **not supported**: both L > 0 and p ≤ 0.05 were required, and neither holds. Floors were met: 8 attempted pairs, 7 nonzero paired effects and 8 eligible complete pairs. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C4, C8] This is a failed confirmatory directional test, not evidence that the effect is absent.

Delta compares prompt regimes, not realized collusion. B1 used one deceptive prompt variant; the study has one local model and one audited exposure per trajectory. Sender identity and exposure timing matched across regimes in every pair, but message text and prompts differed and suffix length was not checked. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C37, §E; docs/review/rev001/REV001.md §6]

### 4.3 Secondary tests and exploratory certificates

Figure 4 shows the case-level certificate intervals against m_O.

| Confirmatory family | Estimate | Holm-adjusted p | Interpretation |
|---|---:|---:|---|
| S1: B1 mean tau_O > 0 | 0.970 | 0.164 | Not significant |
| S2: B2 mean tau_O ≠ 0 | -0.384 | 0.4375 | Not significant; feasibility limitation |
| S3: B1−B2 mean tau_C ≠ 0 | -1.820 | 0.164 | Not significant |

No secondary is significant after Holm adjustment. S2 has only 5 nonzero values against its floor of 6; it cannot establish that authorized cooperation causes no harm. [VERIFIED: docs/review/rev001/REV001.md §3; docs/analysis/exp002_heldout_v2/effects_study.json] [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C11–C12]

Exploratory case-level outcomes are 0 supported, 11 not supported and 5 inconclusive across 16 checkpoints; B1 contributes 0/4/4 and B2 0/7/1 respectively. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C20] Every inconclusive record carries `imprecise`; 4 carry `pattern_ambiguous` (H02_B1, H07_B1, H07_B2, H08_B1), 1 carries `pattern_mutual_disruption`, all 5 `validity_unestablished`, and 3 `no_placebo_available`. The validity reason is a loader artifact, and the placebo reason is over-assigned to cases that were not would-be positives; neither should be read as a raw replay failure. [VERIFIED: docs/analysis/exp002_heldout_v2/checkpoint_certificates.json (recounted 2026-10-24); docs/review/rev001/REV001.md F-5, F-10]

Zero support is not attributable only to unavailable placebos: the maximum outsider-effect lower bound is 0.77, below m_O = 2.5. N_m ran on 2/16 checkpoints, H05_B1 and H08_B1. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C21, C23] The certificates do not themselves assert established validity; raw integrity evidence is reported separately below.

### 4.4 Validity, accounting and sensitivity

All 16 trajectory attempts completed. Of 199 planned branch records, 143 executed and were valid (F64, K64, S7, N8); 56 N records were `not_run: no_placebo_available`. There were 0 failed, invalid or retried branches. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C30] V3, V6, V05b, V08, V09 and V-echo checks passed on 143/143 executed branches; this tally is not a claim that every aggregate validity gate was established. F and K missingness was 0/32 per arm per regime. Model identity had one digest and one load session, with no reloads. The run used 3516 local calls at $0 inference and new out-of-pocket cost. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C31–C34] [VERIFIED: README.md §Reproduce without inference]

[PROVISIONAL: V9 interpretation] By-regime V9 is B1 `sham_uncertain` (n = 4, 90% CI [-3.82, 0.54]) and B2 `pass` (n = 3). The reviewer's pooled study-level calculation passes (n = 7, 90% CI [-0.20, 2.10] within ±2.5); neither route is `invalid_batch`. Individual S−F gaps are +3.77 at H02_B1 and +2.62 at H05_B1. We report both aggregation rules and do not claim sham-equivalence certification. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C35; docs/review/rev001/REV001.md §5]

**Post hoc sensitivity:** excluding the F-arm non-committing continuations at H02_B1 and H05_B1, rather than dropping their matched worlds, gives Delta = 0.727, 95% CI [-0.31, 1.91], p = 0.156. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C13; docs/analysis/exp002_heldout_v2/sensitivity.json] These outcomes remain data in the primary analysis. The associated sham gaps make a content-specific explanation inseparable from factual-arm sampling noise. This diagnostic does not replace the confirmatory result.

## 5. Discussion and Limitations

The study establishes that the preregistered directional contrast did not pass under the realized design. It does not establish equivalence, absence of harmful coordination, spontaneous collusion, or the causal role of collusive content. “Not supported” concerns the declared exposure effect and margin; it does not mean “no collusion.” Fixture findings concern controlled implementation behavior and remain provisional under the review scope.

Precision is limited: MDE_80 ≈ 2.2 reward units exceeds the observed 1.35, with only 8 matched worlds. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md §E; docs/review/rev001/REV001.md §6] The borderline bootstrap lower bound depends on ordering and Monte Carlo variation; the exact sign-flip criterion fails regardless. Masking removes useful information with the message. The runner did not emit `info_bearing`; analysis conservatively defaults it to true, affecting no realized status but leaving the information-loss confound unresolved. [VERIFIED: docs/review/rev001/REV001.md §6, F-6]

The method requires replay access and a suspected exposure. Provider RNG, semantic redundancy, covert/tool channels and the heuristic carrier matcher limit identification. A legitimate transfer with the same harm/utility pattern can be outcome-equivalent under the declared norm. One model, one deceptive prompt variant and a Jira world generator cannot establish generalization to other models, tasks or markets. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md §E]

Development informed the placebo redesign. Deviation 1 reduced sham replication on held-out; Deviation 2 (placebo-availability census run before its inputs were hash-committed) marks the development census exploratory because prior hash commitment was not established. The later label correction separates confirmatory study tests from exploratory certificates without changing numbers or thresholds. Appendix B records these deviations and the remaining certificate limitations. [VERIFIED: docs/stats/deviation_log.md; docs/analysis/exp002_heldout_v2/CORRECTION.md]

## 6. Conclusion

CCC makes exposure-level harm claims conditional on replay validity, utility patterns and control availability. Development fixtures offer provisional method-validation evidence; the held-out primary is a confirmatory null, secondary tests provide no confirmed effects, and case certificates provide no supported exposure. The resulting evidence supports a scoped audit with explicit uncertainty, not a finding about agent intent or a clearance of the team. A `not supported` result concerns the declared exposure effect and margin; it does not mean that the agents did not collude.

## Code and Data

Colosseum and Terrarium, starter checkpoint machinery and the prompted pilot predate the sprint. The audit protocol, replay layer, fixtures, runner, baselines and analysis are sprint work; the pilot is development data only. [VERIFIED: docs/eng/ENG-001_state_map.md; ops/pilot_manifest.sha256] Corrected held-out outputs and the independent review accompany the reproducibility materials. [VERIFIED: docs/analysis/exp002_heldout_v2/; docs/review/rev001/] A one-command offline reproduction script (scripts/reproduce_offline.sh) regenerates the development checks, Gate A evidence and analyses from committed artifacts and verifies their hashes; raw development and held-out traces are archived with SHA-256 checksums. Third-party components and licenses are inventoried in the release license inventory; redistribution terms for Colosseum, poseidon-compute and CoLLAB are unverified, and the starter code is not redistributed. [VERIFIED: docs/release/LICENSES.md] Public release: [OWNER].

## References

Citation keys refer to the accompanying bibliography. All 18 keys cited in the text were checked on 2026-10-24: each is present in the bib file and marked V-meta or V-text in the source ledger or its addendum. Title, authors, year and arXiv identifier were re-checked against the arXiv API for all 17 arXiv entries and against Crossref for Calvano et al. (DOI 10.1257/aer.20190623); no mismatch was found. V-meta entries are cited only for abstract-level claims. Owner verification of the references has not been established. [VERIFIED: ops/reports/PUB-007.md §1]

---

## Appendix A. Limitations and Dual-Use / Ethical Considerations

The held-out primary did not pass its preregistered decision. The study cannot establish that agents did not collude, identify intent, or bound false positives beyond the tested fixtures. Development fixture diagnostics retain redundancy and replay-fault limitations; acceptance by the project lead applies to the narrower preregistered Gate A criteria. [VERIFIED: docs/review/rev001/REV001.md; docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md]

An audit may help adversaries find exposures or channels it misses. Fixtures and prompts could also inform evasion. Proposed mitigations are sandboxed simulated tasks, explicit blind-spot reporting, toy reward mechanisms and owner review of released prompts. These are proposed release measures, not claims that public-release review has occurred. [OWNER: final dual-use and release review.]

A `not supported` or `inconclusive` record must not be treated as clearance or the sole basis for deployment. The scope is local models and scripted policies in a simulator, without human subjects. Held-out inference cost and new out-of-pocket spend were $0. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C31]

## Appendix B. Additional material

### B.1 Detailed related-work comparison


**Interventional collusion audits.** Counterfactual intervention is already used as evidence of collusion. In algorithmic pricing, forced deviations and impulse responses separate reward-punishment schemes from merely high prices [calvano2020artificial]. A recent analysis finds that such a test can be non-selective, because a forced price increase triggers the same retaliation as an undercut [lopesdemoraes2026deterrence]. For LLM market agents, Tran and Yu force one agent to deviate in a cloned market, regenerate both continuations under shared sampling seeds, and use A/A tests, strategy-free placebos, and positive controls [tran2026enforcing]. Sham-like pairing and regenerated continuations are therefore precedented in kind. Their method studies action interventions and enforcement rather than message-removal effects on a declared harm outcome. Messages appear in Appendix J as cheap talk, are coded, and are not ablated [VERIFIED: docs/research/sci001/close_read.md §2]. Controlled peer interventions give population-level causal evidence of collusion in long-horizon LLM interaction [shi2026emergent]. We carry this selectivity concern over to message interventions.

**Message-level counterfactuals.** VLA [kaur2026beyond] intervenes on a sender's continuous latent vector using delivered, matched-neutral, blocked, and independent conditions; its anomaly gate compares candidate-action distributions against stored matched-condition references. This is a single-step analysis: the detector does not regenerate continuations, and white-box steering reruns a sender decision or replaces the incoming latent before receiver scoring [VERIFIED: docs/research/sci001/close_read.md §1]. Its neutral condition is a content reference, not a sham variance-floor arm. Neither VLA's neutral-latent negatives nor Tran and Yu's non-colluding placebos test causally useful legitimate coordination [VERIFIED: docs/research/sci001/close_read.md §§1–2]. Our scope is text exposures in tool-using teams and legitimate causal cooperation as a source of false positives. Rose et al. [rose2026detecting] state a counterfactual communication-removal criterion for collusion and relax it because counterfactual simulation cannot always be assumed. CCC operationalizes a scoped, stochastic approximation of that criterion. Audit the Whisper [tailor2025whisper] applies per-utterance auditor interventions with fresh-seed calibration. Its honest baselines contain no legitimate cooperation, so its false-alarm bounds do not transfer to our setting and we do not borrow them.

**Testbed.** Colosseum [nakamura2026colosseum] measures collusion through regret against the DCOP optimum, coalition advantage, and condition-level secret-channel contrasts. We build on its environment and attribute its metrics. Colosseum states the cooperation-versus-collusion limitation itself; we do not present it as our discovery. Our channel-level arm is a replication bridge to its condition-level control, not a contribution.

**Counterfactual replay in MAS debugging.** Remove-or-edit-and-replay is standard practice for failure attribution [cha2026zeroreplay; ma2025dover; epperson2025agdebugger; zhang2025agentracer; li2026repair]. These methods typically assume deterministic replay, and several find that more than one distinct intervention can repair a failure [ma2025dover; li2026repair]. CCC repurposes the technique for a harm-versus-utility estimand under stochastic resampling, with collusion-specific negative controls, and reports redundancy as "not identifiable" rather than "no effect".

**Influence is not collusion.** Counterfactual influence of one agent's messages on another underlies pro-social coordination objectives [jaques2019social]. Messages can be informative yet causally inert [lowe2019pitfalls], and detectors can be confounded by benign affinity [zhou2026cabal]. These results motivate our benign hard negatives and our inert-talk and sham controls. Covert and tool channels can also escape text-level interventions [motwani2024secret; rippin2026tooluse]; this is a limitation we inherit (Section 5).


### B.2 Extractor provenance and development reproducibility

The re-frozen extractor sha256 is `7b8da4f01e963fa8b5a94f60a6f33a8de613a89588a058668461e9d9aea7a311`; the correction is commit `07ca10f`. The earlier freeze entry remains historical. Theta calibration evaluated normalized word 3-shingles: best Youden J = 0.4947 at raw argmax 0.6, below the 0.5 requirement, so the registered fallback pins theta = 0.4 and `weak_detector = true`. All twenty verbatim positive pairs were detected and no paraphrase positive pair was detected across the grid. [VERIFIED: docs/stats/stage2/STAGE2_ADDENDUM.md §§2, 6]

Gate A v1.2.2 changes theta from 0.8 to 0.4 and records bootstrap draws as 10000 rather than 2000. Its deterministic intervals do not use bootstrap draws. All 800 statuses and reason-code records remain unchanged; additional carrier flags occur only in already-invalid A6a rows. Constructed controls are carried forward byte-identical and excluded from headline comparisons. [VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md]

### B.3 Development checks

Figures B1 and B2 show the development fixture integrity checks and baseline confusion comparisons.

Development findings below were not re-audited by the independent review; provenance tags identify archived evidence, not a new verification.


Gate A v1.2.2 covers 800 non-constructed development cells over twenty task seeds and two wording strata, with one scripted continuation per arm. It is a deterministic implementation check, not held-out stochastic inference. The corrected integrity counts are:

| Check | Passed / checked |
|---|---:|
| F/S identity | 380/380 |
| K changes only intended exposure | 4180/4180 |
| Branch isolation | 760/760 |
| A2 never supported | 80/80 |
| A6 invalid / intended validator | 350/360 |

[VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md]

CCC returned 8/800 `supported`: two each in A1a, A1b, A5a-verbatim and A5a-paraphrase. Every supported cell had oracle tau_O = 4.015, an active path and an accepted N_m placebo. There were zero false supports under the oracle margin (supported with tau_O < 2.5), and zero false negatives at the estimand level (non-A6 `not supported` with tau_O ≥ 2.5). These checks concern the exposure-effect estimand; they are not accuracy claims against intent labels. Of 28 path-active above-floor non-A6 cells, eight were supported and twenty abstained for mutual disruption, efficient transfer or redundant-path non-identifiability; the twenty include eight benign A2 cells. [VERIFIED: docs/review/director_gateA_audit.md; docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md]

The preregistered Gate A criteria (factual/sham identity, knockout scope, branch isolation, and no `supported` on benign cooperation) all pass. Two stricter diagnostic checks fail and are reported as limitations: the A5 redundancy check passes 20/120 cells (16/68 under the amended instantiation), and ten A6b faults were non-exercisable. A5 below-margin findings can be correct for a single exposure despite redundant team coordination. No paraphrase A5a cell carries a carrier flag. The pre-written prediction scorecard has sixteen confirmed, two falsified and three untested items; P1.3 is numerical agreement only because pre-census commitment was not established (Deviation 2; placebo-availability census run before its inputs were hash-committed). Constructed controls are excluded from the headline denominator. [VERIFIED: docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md; docs/review/director_gateA_audit.md]

The real-agent development census found M* available at 0/8 checkpoints, unchanged at descriptive matching windows 0.10 and 0.50. The sender's sole prior message was task-bearing and filtered out. This is a small observed sample, not a population estimate. In that development sample, case-level real-agent `supported` was unavailable; absent M* blocks would-be positives with `inconclusive: no_placebo_available`. N is skipped when M* is empty. The study-level F–K Delta remains defined without N; neither chatter nor a new placebo rule is introduced for real agents. [VERIFIED: docs/research/sci002/placebo_census_tierB_dev.md; docs/stats/stage2/STAGE2_ADDENDUM.md §5]

### B.4 Deviations and development provenance

Protocol v1.2 was motivated by the v1.1 development result: the old N filler removed audited content like K, preventing support. The redesign is development-informed. Deviation 1 (reduced sham replication on held-out) reduces held-out S2 to S1 on a hash-selected 50% subset and drops optional pairs H09/H10. Its design calculation increases the V9 90% half-width from approximately 0.36σ to 0.65σ; attained sham uncertainty must be reported without re-pinning thresholds. Deviation 2 (placebo-availability census run before its inputs were hash-committed) records that the development placebo census preceded the required hash commit, so its results are exploratory and hashes establish subsequent byte stability rather than prior commitment. [VERIFIED: docs/stats/deviation_log.md; docs/research/sci002/protocol.md]

The reviewed v1.2.1 extractor correction occurred after the first freeze list; it was re-frozen before held-out data, retaining the earlier hash as history. The development pilot's cap calculation omitted canaries and underestimated calls per branch, leaving a 74-call shortfall. The preserved `dev05_B2/attempt_0001` failed at the collection-wide remaining budget of 223 calls (despite the error's “per-run” wording), with null outcomes, and was not rerun. Stage-2 therefore uses seven checkpoints and three complete pairs. The corrected outcome-blind cap is `ceil(1.05 × 16 × (28 + 3 + 13 × 25)) = 5981`. [VERIFIED: docs/stats/stage2/STAGE2_ADDENDUM.md §§3–6; ops/DECISIONS.md D-030]

### B.5 Held-out accounting and certificate details

| Regime | Supported | Not supported | Inconclusive | Determinate coverage |
|---|---:|---:|---:|---:|
| B1 | 0 | 4 | 4 | 0.50 |
| B2 | 0 | 7 | 1 | 0.875 |

Coverage is determinate verdicts divided by attempted checkpoints, not accuracy against collusion truth. No empirical held-out false-positive risk can be inferred without truth labels. [VERIFIED: docs/analysis/exp002_heldout_v2/coverage.json; docs/review/rev001/CLAIMS_LEDGER.md C20]

| Inconclusive checkpoint | Recorded reasons |
|---|---|
| H02_B1 | `imprecise`, `pattern_ambiguous`, `validity_unestablished`, `no_placebo_available` |
| H05_B1 | `imprecise`, `pattern_mutual_disruption`, `validity_unestablished` |
| H07_B1 | `imprecise`, `pattern_ambiguous`, `validity_unestablished`, `no_placebo_available` |
| H07_B2 | `imprecise`, `pattern_ambiguous`, `validity_unestablished`, `no_placebo_available` |
| H08_B1 | `imprecise`, `pattern_ambiguous`, `validity_unestablished` |

[VERIFIED: docs/analysis/exp002_heldout_v2/checkpoint_certificates.json, recounted from the `reasons` field of the 5 inconclusive records: `imprecise` 5, `validity_unestablished` 5, `pattern_ambiguous` 4, `no_placebo_available` 3, `pattern_mutual_disruption` 1.] The table shows the frozen per-case reasons from that file. `Imprecise` means the outsider-effect interval crosses the margin. The loader records failures without establishing all required pass keys, leaving `all_valid=false` on every certificate; the validity reason above is therefore an analysis artifact. The raw checks establish the separate integrity tallies in the main text. The unavailable-placebo reason was applied even where the positive-effect gate failed. These artifacts are disclosed, not silently repaired here. [VERIFIED: docs/review/rev001/REV001.md F-5, F-10]

Every `not supported` checkpoint has U(tau_O) ≤ 1.81 < m_O = 2.5. Four (H04_B2, H05_B2, H06_B1, H06_B2) have L = U = 0 because all 8 outsider outcomes are identical. These are protocol-compliant zero-variance results, not evidence about unaudited carriers. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C21]

Raw V05 checks pass 64/64, V04 cross-checks 7/7 and applicable V07 checks 64/64. Model digest is `5571076f3d70`; session evidence records 7080 probes and 48 canaries without reload or session break. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C32–C33] The raw accounting separates 16 trajectory attempts, 143 executed continuations and 56 unavailable N records; planned records must not be described as executed branches. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C30]

Observed F/K missingness is zero; its exact upper bound is 0.109, so meeting the 0.10 limit refers to observed shares, not an established population bound. B1 F includes 2/32 behavioral non-commits, versus 0/32 K; these are recorded outcomes, not missingness, and the rate difference was not tested. [VERIFIED: docs/analysis/exp002_heldout_v2/missingness.json; docs/review/rev001/REV001.md §5, F-2]

The V10 lesion check is not established by these data; we do not use its pipeline status as evidence. TV_excess is also provisional because no frozen interval algorithm was specified; no communication-dependence finding is asserted. [VERIFIED: docs/analysis/exp002_heldout_v2/checkpoint_certificates.json (`TV_interval` is null with reason "no frozen interval algorithm specified" on all 16); docs/review/rev001/CLAIMS_LEDGER.md C26, C36; docs/review/rev001/REV001.md F-8]

### B.6 Sensitivity and power details

Leave-one-world-out Delta estimates range from 0.796 to 1.703. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C16; docs/analysis/exp002_heldout_v2/sensitivity.json] Missingness and ineligibility alternatives coincide because no such cases occurred; agreement is vacuous, not a robustness finding. [VERIFIED: docs/analysis/exp002_heldout_v2/sensitivity.json (`ineligible_zero` and `drop_ineligible` both give 1.354, L = -0.0195); docs/review/rev001/CLAIMS_LEDGER.md C15] The non-commit exclusion is a post hoc diagnostic, retains the matched worlds and does not alter the registered primary.

For the primary bootstrap, the archived string-sorted world order yields a lower bound of -0.0195; numeric ordering yields -0.00017. Both are approximately zero and neither passes the positive-lower-bound criterion; the exact paired test fails independently. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md C3] The review's approximate power calculation uses paired-effect SD = 2.23 and MDE_80 ≈ 0.99 × SD ≈ 2.2, above observed Delta ≈ 1.35. This is a precision diagnostic, not another confirmatory test. [VERIFIED: docs/review/rev001/CLAIMS_LEDGER.md §E]

## LLM Usage Statement

[OWNER: approve final wording.] Claude (via Claude Code) and Codex agents, coordinated by a Claude Code session acting as project coordinator, assisted with planning, implementation, tests, analysis scripts, literature verification and manuscript drafting, including this revision. Experimental agents are separate local models and scripted policies. Human owner verification of claims, results and references has not been established in this draft. [OWNER: update after review.] The owner is the sole author; no AI system is a co-author.
