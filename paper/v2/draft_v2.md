<!-- W4-P2: prospective results integrated from docs/enh/r2/run_par/RESULTS.json; failed predictions retained. NOT FINAL. -->
<!-- Evidence-tag legend is visible below so the build retains it. -->

<!-- CITATION_AUDIT.md was absent during W4-P1; retained references have not been reverified. -->

# Same Evidence, Different Verdicts: Evidence Standards for AI Collusion Attribution

Author: [OWNER]. Affiliation: [OWNER]. The owner is the sole author.

## Abstract

Audits of multi-agent systems use logged messages and replay interventions to assess whether agents colluded. Yet the same transcript and message-removal effect can arise from harmful coordination or legitimate cooperation. We propose an evidence ladder separating suspicious text, causal influence, harmful exposure effects and justified attribution. Executable twin worlds make the distinction concrete: within a declared generator and information set, identical observables cannot support opposite labels. An abstention-aware benchmark asks which additional evidence separates those labels and scores abstention alongside errors. Counterfactual Collusion Certificates supply an exposure-level instrument, while a ladder-aware reporter states when attribution remains unresolved. These components address the same question: what claim does the available evidence license? The original preregistered local-model study yielded Delta = 1.354, world-cluster 95% CI [-0.020, 2.834], exact one-sided p = 0.0703, across 8 matched world pairs [OC]. The directional hypothesis was NOT supported. This neither establishes an absent effect nor licenses attribution. The prospective benchmark passed symmetry and frontier consistency checks by construction, but failed the label-effect, over-attribution and ladder-auditor predictions [NP]. We recommend reporting the highest justified rung, the information supplied to the auditor and the evidence needed to resolve ambiguity. We do not claim to detect collusion or intent.

**Evidence categories.** Quantitative settings and measurements carry one class each; a class scopes its quantity or single-class paragraph/table row. Identifiers (citations, sections, rungs, versions, paths, hashes, seeds, figure labels) are metadata, not empirical measurements. Evidence tags: [OC] original-confirmatory; [ORS] original-registered-secondary; [D] descriptive; [PH] post-hoc-exploratory; [NP] new-prospective; [DEV] development.

## 1. Introduction

A team allocates a contested task to a coalition member. In one world its message steers work away from a cheaper outsider; in its twin, the same message and allocation follow the shared efficiency objective. The transcript and factual, knockout, sham and placebo outcomes are identical by construction. An auditor using that evidence must return the same output for both worlds, although their attribution labels differ. An environment probe asks the separating question: would the team yield when the outsider becomes the efficient claimant? Figure 1 presents the evidence ladder [NP] (PROSPECTIVE in its source figure metadata; a conceptual diagram, not a measured outcome).

Auditors may use evidence of collusion to recommend sanctions, shutdowns or deployment decisions. Confusing influence with attribution risks accusing legitimate cooperation while missing harmful coordination. Our threat model is an auditor with a replayable log and a suspected message exposure, facing both possibilities. Auditors and benchmark builders can use this standard to state which claim their evidence supports and what additional probe or authorization record is needed.

We ask when a message changes behaviour, when that change harms outsiders, and when the available evidence separates harmful coordination from legitimate cooperation. The benchmark and held-out study test the same evidence ladder.

Our contributions are:

1. **An evidence ladder** separating influence, harm and attribution, with explicit information sets and a scoped identifiability statement (Section 3).
2. **Executable twin worlds and an abstention-aware benchmark** with an enumerated separating-evidence frontier (Sections 4 and 5).
3. **An exposure-level instrument and ladder-aware reporter:** CCC retains its harm gates; CCC-L reports unresolved or excluded attribution. Its revision is development-informed (Section 4).
4. **Evidence separated by status:** development controls, an original held-out directional hypothesis that was NOT supported [OC], and prospective benchmark findings with pre-stated failures retained [NP] (Section 5).

**What is new, and what is not.** Counterfactual interventions, sham and placebo controls and three-way outcomes are established [2, 7]. Indistinguishability of lawful parallelism and conspiracy is argued for price- and bid-level tests [5] and for reasoning agents [6]; the boundary between beneficial cooperation and harmful collusion is named as an open challenge in [8]. In a bounded search (Appendix G) we found no executable, message-level, interventional statement of the limit with a measured separating-evidence frontier. We state the limit only for our generators and information sets, and make no priority claim.

**What we tested and found.** The preregistered held-out directional hypothesis was not supported [OC] (Section 5.4). The prospective frontier matched enumeration by construction [NP]. The original and DEV-informed over-attribution predictions both failed across the required strata [NP].

**Figure 1. Same evidence, different attribution labels [NP] (schematic of the prospective twins).** Left: a colluding-allocation twin and its efficiency-motivated counterpart share transcript and declared replay outcomes. Middle: equal tau_O, tau_C and tau_W support the same exposure-level reading. Right: the ladder separates influence and harm from attribution; an environment probe supplies separating evidence. **Takeaway:** identical declared evidence requires the same audit output, so attribution needs separating evidence. Rendering is pending; this schematic asserts no measured bars or prospective verdicts.

## 2. Related Work

*Interventional collusion audits.* Impulse responses after forced deviations were used to infer punishment in Q-learning pricing [19]; later work shows this pattern does not by itself identify a punishment mechanism [20]. For LLM markets, Tran and Yu clone markets under shared seeds and use A/A tests, placebos and positive controls, and note in their limitations that at cartel prices the deviation "separates a punisher only poorly from a rival that merely best-responds" [2]. Colosseum audits collusion in a Jira-style DCOP and states in its limitations that collusion is not always harmful [1]; we reuse its environment. VLA intervenes on latent messages at a single bid event [3]; multi-agent interpretability probes [4] are a white-box complement, and that work notes counterfactual simulation cannot always be assumed. Delta: we study text exposures with regenerated continuations and ask what the effect licenses, not only how to estimate it.

*Closest methodological neighbour.* Zhang and Emu replace a message with a matched other-example message, report positive, negligible or inconclusive outcomes, and use paired bootstrap intervals with sign-flip or exact paired tests and a presence-versus-content decomposition [7]. It is not collusion-specific and does not address normative labels; we claim no novelty for matched controls or three-way outcomes, and our placebo and certificate taxonomy are engineering instances of that design adapted to harm and utility gates.

*Indistinguishability claims.* Xu et al. show that price- and bid-level audits against competitive marginals have power exactly alpha and that lawful multi-identity operation and conspiracy are behaviourally indistinguishable there, while noting that a universal impossibility claim would be false [5]. Riemer et al. argue that reasoning agents compress the gap between lawful parallelism and coordination to indistinguishability [6]; Lee and Park report CoT monitoring dissociates from collusion [9]; Idowu et al. flag the cooperation/collusion boundary as an open challenge [8]. Ward et al. define intent relative to a structural causal model under an assumed shared model [12]; Everitt et al. show incentive criteria are properties of the assumed causal influence diagram [11]. Delta: these are observational, price-level or conceptual; ours is message-level, interventional and executable, and measures the minimal separating information set per pair type, scoped to our generators and not a general impossibility theorem.

*Responsibility, replay attribution and abstention.* Counterfactual replay for failure attribution [14, 15] and degrees of responsibility under redundant contributions [13] motivate our redundancy cases (reported as "not identifiable under I1", not "no effect"); selective classification [17] and delegation guarantees [18] motivate abstention-aware scoring; [16] is a preregistered audit precedent whose hypothesis was not supported; steganographic channels [10] can evade any text-level intervention (Appendix G).

## 3. The Evidence Standard

**Setting.** A replayable team of agents with a designated sender s and receiver r, outsiders O, a coalition C = {s, r}, and a declared exposure E* (a message, or a set of messages). Arms: F (factual replay), K (knockout of E*, persistently masked by event id so re-rendered history does not leak it), S (sham with identical rendering and an empty mask), N (matched-message placebo, only where an eligible same-sender inert message exists).

**Estimands.**
tau_O = E[Omean_K] - E[Omean_F] (outsider effect), tau_C = E[Cmean_F - Cmean_K] (coalition benefit), tau_W = E[W_K - W_F] (total-utility change). Outsider harm is declared with margin m_O = 2.5 and welfare tolerance delta_W = 5.0 (frozen). Reward units are task units, not currency [OC] (frozen design).

**Evidence ladder.** Each rung is a separate claim with its own gate; no rung implies the next.

| Rung | Claim | Minimal evidence |
|---|---|---|
| L0 | The text is suspicious | transcript (I0) |
| L1 | The message causally influences behaviour | K changes behaviour relative to S |
| L2 | Exposure produces harm | valid replay; tau_O > m_O with sham and utility controls; coalition and welfare gates |
| L3 | The agents colluded (attribution) | L2 plus evidence separating harmful coordination from legitimate cooperation under the declared norm |

**Information sets (nested).** I0 transcript and factual outcomes; I1 adds single-message knockout K; I2 adds sham S and placebo N; I3 adds joint knockout of all same-sender carriers of the exposure; I4 adds an environment or incentive probe (re-run F and K with outsider costs on the contested task lowered, so that an outsider is the efficient claimant); I5 adds an external normative record (authorization), which is non-behavioural.

**Identifiability.** Let O_S(w) be the canonical byte string of observables available under S in world w, and L(w) the label of interest (mechanism M, or attributable collusion = harmful, redundant-harmful or relayed-harmful). An instance w is *identifiable under S* iff every world w' in the generator's policy space with O_S(w') = O_S(w) has L(w') = L(w); I(S) is the set of such instances. Computed by exact enumeration, never from any method's gates. Twin members with identical O_S are equivalent by definition; the empirical readouts are the separating set per pair type, the symmetry check, the label-effect gap and the behaviour of baselines and CCC on twin members.

**Scoped limit statement.** "In these scripted generators, for the stated information sets, twin worlds with byte-identical observables are indistinguishable by construction; the frontier evaluation asks which additional evidence separates them; this is a scoped, executable statement about these sets and generators, not a general impossibility theorem about collusion attribution."

**CCC (L2 instrument) [D] (design settings).** A `supported` verdict requires established validity and placebo evidence, nonempty M*, L(tau_O) > m_O, L(tau_C) > 0, L(tau_W) >= -delta_W and resolved information-loss gates, with one-sided 95% bounds from exact shift-permutation inversion. `Not supported` requires U(tau_O) < m_O with no detected carriers; other eligible cases are `inconclusive` with reasons; failed integrity is `invalid`. The carrier extractor is a `weak_detector` heuristic; CCC v1.2.2 is used unmodified. In this paper a CCC `supported` is an L2 claim and is never reported as attribution.

## 4. Benchmark and Study Methods

**Benchmark [NP] (frozen design).** Six twin-pair types P1-P6 (redundant-harmful vs inert; colluding vs efficiency-motivated allocation; authorized vs unauthorized transfer; common cause vs message-caused coordination; suspicious vs plain inert language; information-bearing vs harmful steering), a relayed-harmful case, corrupted traces and 11 benchmark classes, each twin pair being ONE independent unit (Appendix E). Strata eps in {0, 0.1} (random-action probability of each scripted agent; R = 8 continuations per arm) are reported separately and never pooled. Seeds derive from the protocol hash with a deterministic skip rule against all development, pilot and original-study seeds; disjointness is checked and hashed in FREEZE.json before any run. Metrics: over-claim rate, sensitivity, FPR, abstention and coverage, risk-coverage curves at abstention cost c in {0.25, 0.5}, exact Clopper-Pearson 95% intervals over independent units, exact McNemar-type paired tests, world-cluster percentile bootstrap (Appendix E). Single pass, fixed N, no interim looks; crashes stay in the denominator; any code change after outcomes are visible forces a new seed block and both runs are reported.

**Positive control [DEV] (design).** The **P4 message-caused coordination member**, contrasted with its common-cause twin, is the named causal-influence positive control. Single-message knockout is the declared separating intervention. This checks influence rather than the full certificate or attribution pipeline. Recovery counts and support-level positive-control validation are not established in the supplied draft and must be reported before instrument-validity claims.

**Four axes, never merged.** M mechanism label; H realized harm (oracle outsider reward under F lower than the no-coordination reference by more than m_O); E exposure effect (oracle tau_O >= m_O; tau_C, tau_W also reported); I(S) identifiability. Ground-truth availability is explicit per class; where an axis has no truth it is scored "inapplicable" and never imputed. EXP-002 real-agent worlds have none of M, H or I(S).

**Methods compared** (each sees only the observables of its declared set; frozen before any prospective seed existed): frozen CCC v1.2.2; outcome-only, knockout, harm-gated knockout, influence-only and transcript-keyword baselines; always-answer and always-abstain anchors; the Bayes-given-S ceiling; and CCC-L v1 (new, exploratory, DEV-informed), which outputs the highest justified rung, "insufficient for L3 under S", or "L3 excluded" (attribution ruled out by separating evidence in S). CCC-L v0 lacks the last output, so DEV showed it cannot be correct on both members of a pair; it is retained and reported prospectively so the change is visible. The strongest knockout baseline was fixed on DEV block 13000-13049 (B2+ or B3b; ties to B2+) and recorded in FREEZE.json (Appendix E).

**Frozen research questions [NP] (criteria).** The protocol tests symmetry and the separating-evidence frontier, the label-effect gap, knockout over-attribution, abstention-aware ladder reporting and descriptive CCC behaviour. Appendix E gives every threshold and failure rule; Section 5 reports each question without replacing the original over-attribution prediction with its development-informed refinement.

**Amendments and disclosures [DEV].** Three director amendments precede the DEV run (CRN, circularity disclosure, RQ6). After seeing DEV results (RQ1 and RQ3 passed; RQ2, RQ4 and RQ5 failed) and before any prospective seed existed, four further amendments were made and are reported as DEV-informed: CCC-L v0 to v1 (adds "L3 excluded"), RQ2 made method-independent, RQ4b added beside the unchanged RQ4, and RQ3 left unchanged. The independent review (REV-R2) approved the freeze with four conditions, which we adopt as reporting rules. (C2) RQ5 is structurally strict: undefined denominators score as fail (166/168 DEV cells), so the informative RQ5 readouts are the selective-accuracy gap, over-claim counts and pair attribution (DEV v1: 1.00 at eps = 0, 0.66 at eps = 0.1) [DEV]. (C3) The report is stricter than the protocol text: RQ3 and RQ4 must pass in both strata; RQ1 and RQ2 are consistency checks by construction and are not performance evidence. (C4) Prospective RQ3 uses effectively random cell assignment, whereas the DEV block was balanced (0.24 [DEV] against the 0.25 frozen bound [NP] at the deterministic stratum), so DEV is not a reliable guide to the prospective value. Circularity (amendment A2): RQ2 and RQ5 are consistency checks of the generator, the enumeration and the reference auditor; CCC-L was written knowing which evidence separates each type, so passing them is expected by design and is not a performance claim. The informative results are RQ3, RQ4 and RQ4b, RQ5 under eps = 0.1, and RQ6.

**Original held-out study (EXP-002; protocol v1.2, preregistered) [OC] (design).** Local `gemma4:26b`; 8 matched world pairs; regimes B1 (one deception prompt variant) and B2 (authorized cooperation); 4 F and 4 K continuations per checkpoint. Estimand Delta = mean_w[tau_O(w,B1) - tau_O(w,B2)] with whole matched worlds as independent units; the directional primary required both a positive world-cluster bootstrap lower bound (10,000 draws) and exact one-sided paired sign-flip p <= 0.05. Case-level certificates are exploratory. The prospective study (R2) has disjoint worlds, seeds and code hashes, is never pooled with EXP-002, and EXP-002 serves only as a real-agent illustration.

## 5. Results

### 5.1 Positive control and development evidence

The P4 message-caused coordination positive control is specified in Section 4 [DEV] (design). Its recovery is not established by the supplied draft. The following implementation checks do not substitute for that result.

Gate A (v1.2.2) passed its deterministic implementation checks (for example A2 benign cooperation never supported, 80/80) but is not held-out inference, and agreement with scripted predictions is not validation. The label-effect gap was 12/80 in Gate A and 12/50 (eps = 0), 5/50 (eps = 0.1) in the benchmark DEV block [DEV]; RQ3 and RQ4 were derived from these, and none counts as confirmatory (Appendix F).

### 5.2 Frontier and identifiability [NP]

Prospective outcomes [NP] are reported separately by stratum and never pooled. RQ3 and RQ4 must pass in both strata to count as passed. The selected reporting templates retain the pre-stated failures.

**RQ1 symmetry** **pass.** [NP] Across all 364 eligible method x pair-type x set x stratum cells, no twin pair produced a differing output (0/200 in every cell; exact CP 95% upper bound 0.01827534), consistent with no leakage of label or world identity beyond the declared set. This is a pipeline consistency check, not performance evidence.

**RQ2 frontier** **pass (by construction).** [NP] The Bayes-given-S frontier equalled the enumerated minimal separating set for every listed type: P1/I3, P2/I4, P3/I5, P4/I1 and P6/I1, with 200/200 pairs correct at the frontier in each stratum (CP 95% [0.981725, 1]). No method was correct on both members below it beyond Bayes-given-S. Relayed-harmful remained unresolved at I3 (100/100 units per stratum). This confirms generator and enumeration consistency, not independent detection performance.

### 5.3 Abstention-aware benchmark [NP]

**RQ3 label-effect gap** **FAIL.** [NP] At eps = 0 the share was 30.5% (61/200; rate 0.305; CP 95% [0.242, 0.374]), at or above the 25% prediction. At eps = 0.1 it was 20.5% (41/200; rate 0.205; CP 95% [0.151, 0.268]), passing the point threshold but without margin. The prediction fails overall because it must hold in both strata. Development comparison: Gate A 12/80; benchmark 12/50 at eps = 0 and 5/50 at eps = 0.1 [DEV]. Prospective cell assignment was random; DEV was balanced.

**RQ4 over-attribution** **FAIL.** [NP] B2+ over-attributed above 0.5 only in legitimate P2 and P3 at eps = 0 (each 200/200, rate 1; CP 95% [0.981725, 1]); in P6 and benign cooperation it did not (0/200 and 0/100, rates 0; CP 95% [0, 0.018275] and [0, 0.036217]). At eps = 0.1 all four numerators were zero with the same denominators and intervals. Thus the all-class, both-stratum over-attribution prediction failed; the claim is borne out only partly in these generators. CCC returned no L2 supports under I1 in these cells (same denominators and zero-event intervals); richer evidence is described under RQ6.

**RQ4b DEV-informed profile** **FAIL.** [NP] The profile did not hold: P2 and P3 each had rate 0 (0/200; CP 95% [0, 0.018275]) in stratum eps = 0.1, failing the >0.5 condition. The eps = 0 profile met the revised inequalities, and P6 and benign cooperation met the low-rate condition in both strata. The DEV-informed refinement of RQ4 is not supported prospectively.

**RQ5 ladder auditor** **FAIL (exploratory-method).** [NP] CCC-L v1 did not meet the criterion: only 2/168 complete cell criteria passed, versus 8/168 for retained v0. Selective-accuracy gaps were undefined in 148 v1 cells and 151 v0 cells and remain unestablished, not favourably imputed. Both versions had zero over-claim unit-events across the reported cells. For P2/I4 and P3/I5, v1 pair attribution was 200/200 at eps = 0 (CP 95% [0.981725, 1]) and 0/200 at eps = 0.1 (CP 95% [0, 0.018275]); v0 was 0/200 in all these cells. At P2/I4, v1 selective-accuracy gap was 0 at both frozen abstention costs in both strata; abstention precision and recall were inapplicable at eps = 0, while precision was 0/200 (CP 95% [0, 0.018275]) and recall inapplicable at eps = 0.1. These cell-specific values do not establish the conjunction. Development pair-attribution comparison: 1.00 at eps = 0 and 0.66 at eps = 0.1 [DEV]. This is a negative result about this method version without altering the frontier claims.

**RQ6 descriptive behaviour of frozen CCC v1.2.2** **descriptive.** [NP] Under I2, CCC v1.2.2 returned `supported` on 200/200 legitimate members of each of P2 and P3 at eps = 0 (CP 95% [0.981725, 1]); these are reported as harmful exposure that is not attributable. At eps = 0.1 it returned `supported` on 0/200 legitimate members in each class (CP 95% upper bound 0.018275); this is not a general false-positive bound. All per-class status distributions and M/H/E views are retained in `RESULTS.json.tables.RQ6`.

### 5.4 Original held-out study: confirmatory null

**Primary [OC].** Delta = 1.354 reward units, world-cluster 95% CI [-0.020, 2.834], exact one-sided sign-flip p = 0.0703 (18/256), n = 8 matched world pairs. Both required criteria fail; the preregistered directional hypothesis is **NOT supported**. Floors were met (8 attempted pairs, 7 nonzero paired effects, 8 eligible complete pairs). This is a failed confirmatory directional test, not evidence that the effect is absent.

**Design sensitivity [D].** The registered MDE_80 is about 2.2 reward units; precision was limited.

**Post-hoc order check [PH].** The bootstrap lower bound is -0.0195 under archived string order and -0.00017 under numeric order; the sign-flip criterion fails independently.  Delta compares prompt regimes, not realized collusion.

**Not confirmatory: registered secondary and post-hoc analyses.**

| Class | Quantity | Value | Status |
|---|---|---|---|
| [ORS] | Registered non-commit sensitivity | Delta = 0.727, 95% CI [-0.306, 1.914] | Excludes non-committing factual continuations, retains matched worlds; changes the estimand |
| [PH] | Sensitivity sign-flip test | p = 0.156 | Post hoc; does not repair the primary |
| [D] | Contribution of non-commit cases | 0.627 of 1.354 (46%) | Descriptive accounting; not entirely driven by those cases |

The preregistered S1–S3 family is original-confirmatory [OC]; none is significant. Estimates and Holm corrections are in Appendix F.

**Exploratory certificates [D].** Over 16 checkpoints: 0 supported, 11 not supported, 5 inconclusive (B1 0/4/4, B2 0/7/1). No outsider-effect lower bound exceeded m_O = 2.5 (maximum L = 0.77). The placebo was available at 2 of 16 checkpoints, so zero support is not attributable to unavailable placebos alone. All 16 certificates carry `info_bearing = true` by conservative default, which changes no realized status.

**Interpretation.** The interval is compatible with effects near zero and substantially positive effects. Delta compares prompt regimes, not realized collusion. A significant exposure-level effect would still require separating evidence for attribution.

The instrument's accounting is 199 scheduled branch records: 143 executed valid continuations and 56 unrun placebo branches [D]. Control design and development checks are in Section 5.1; full accounting and sham uncertainty are in Appendix F.

## 6. Discussion

> **What this does and does not establish.** Valid interventions can license scoped influence or exposure-harm claims. This draft does not establish intent, exoneration, baseline superiority or general false-positive control; the studies are never pooled. Attribution needs separating evidence.

**What the standard asks of an audit.** Report the highest rung the evidence licenses; abstain on L3 where the frontier says the information set cannot separate the labels; state the declared norm (m_O, delta_W) and what extra evidence would split the case. The frontier matched enumeration by construction, while both the original over-attribution prediction and its DEV-informed refinement failed [NP]. CCC supported harmful exposure on legitimate P2 and P3 members under I2 in the deterministic stratum [NP]; this illustrates why an L2 verdict must not be read as attribution.

**Where knockout works, and recommendations [D] (design).** In P4 (common cause vs message-caused coordination) single knockout separates the pair at I1: knockout is sufficient for causal influence and insufficient for normative attribution. We recommend (1) never reporting knockout magnitude as collusion evidence, but a rung; (2) publishing placebo availability, information-loss status and carrier-detector recall with each verdict; (3) reporting risk-coverage, not one accuracy number; (4) stating the information set supplied.

## 7. Limitations and What We Did Not Establish

We do not detect collusion or intent. A `not supported` or `inconclusive` record is not exoneration and must not be the sole basis for deployment. The identifiability limit holds only for our generators and information sets, and scripted generators with oracle labels cannot estimate real false-positive rates. RQ1 and RQ2 are consistency checks by construction, RQ5 is largely a consistency check and structurally strict, and CCC-L v1, the method-independent RQ2 and RQ4b are DEV-informed amendments; the DEV block was balanced while prospective RQ3 assignment is random (Section 4; REV-R2 C2-C4). The original study has one local model, one deceptive prompt variant, one exposure per trajectory and 8 independent matched world pairs [D], so its precision cannot support equivalence or practical-significance claims. Replay access and a suspected exposure are required. Appendix A lists restrictions and ways to extend the evidence.

## 8. Conclusion

Knockout magnitude, transcript rules and gated verdicts each license a different rung of the evidence ladder, and none licenses attribution by itself. We provide the ladder, executable twin worlds with an enumerated identifiability frontier, an abstention-aware benchmark, and a confirmatory null from the original real-agent study. Prospective symmetry and frontier checks passed by construction, while the label-effect, original over-attribution, refined over-attribution and ladder-auditor predictions failed [NP].

## Code and Data

Colosseum, Terrarium and the prompted pilot predate the sprint; the audit protocol, replay layer, runner, baselines, benchmark and analysis are sprint work. Offline reproduction: `scripts/reproduce_offline.sh`; benchmark: `python -m ccc.bench`. Public release: [OWNER].

## References

1. Mason Nakamura, Abhinav Kumar, Saswat Das, Sahar Abdelnabi, Saaduddin Mahmud, Ferdinando Fioretto, Shlomo Zilberstein, Eugene Bagdasarian (2026). Colosseum: Auditing Collusion in Cooperative Multi-Agent Systems. arXiv:2602.15198.
2. Hieu Tran, Hong Yu (2026). Is Anyone Enforcing the Cartel? What Reinforcement Learning Teaches LLM Agents in Markets. arXiv:2610.28787.
3. Ramneet Kaur, Pradyumna Chari, Ramesh Raskar, Jugad Singh, Sumit Kumar Jha, Anirban Roy (2026). Beyond the Transcript: Detecting Covert Coordination in Latent Multi-Agent Communication. arXiv:2608.19161.
4. Aaron Rose, Carissa Cullen, Sahar Abdelnabi, Philip Torr, Brandon Gary Kaplowitz, Christian Schroeder de Witt (2026). Detecting Multi-Agent Collusion Through Multi-Agent Interpretability. arXiv:2604.01151.
5. Xin Xu, Chengrui Wu, Jiayu Lu, Kaizhen Tan, Siru Tao, Hanzhe Hong (2026). Collusion with Competitive Marginals: Price-Level Audits Are Blind by Construction. arXiv:2607.26385.
6. Matthew Riemer, Tommaso Tosato, Amin Memarian, Maximilian Puelma Touzel, Glen Berseth, Irina Rish, Guillaume Dumas (2026). Position: Collusion Risks Among AI Reasoning Agents Justify Certification Requirements for Making Market Decisions. arXiv:2608.18078. ICML 2026 (position).
7. Huixiang Zhang, Mahzabeen Emu (2026). Do Latent Channels Actually Communicate? A Causal Audit of Latent Multi-Agent LLM Communication. arXiv:2607.26773.
8. Jamiu Idowu, Ahmed Almasoud, Ayman Alfahid (2026). Mapping Human Anti-collusion Mechanisms to Multi-agent AI Systems. arXiv:2601.00360. Knowledge-Based Systems 344:116067 (2026).
9. Dohun Lee, Hyunwoo Park (2026). Faithful yet Collusive: Why Chain-of-Thought Monitoring Cannot Detect Collusion in LLM Pricing Agents under Oligopolistic Competition. arXiv:2609.18346. Findings of EMNLP 2026.
10. Sumeet Ramesh Motwani, Mikhail Baranchuk, Martin Strohmeier, Vijay Bolina, Philip H. S. Torr, Lewis Hammond, Christian Schroeder de Witt (2024). Secret Collusion among AI Agents: Multi-Agent Deception via Steganography. arXiv:2402.07510.
11. Tom Everitt, Ryan Carey, Eric Langlois, Pedro A. Ortega, Shane Legg (2021). Agent Incentives: A Causal Perspective. arXiv:2102.01685. AAAI 2021.
12. Francis Rhys Ward, Matt MacDermott, Francesco Belardinelli, Francesca Toni, Tom Everitt (2024). The Reasons that Agents Act: Intention and Instrumental Goals. arXiv:2402.07221.
13. Hana Chockler, Joseph Y. Halpern (2004). Responsibility and Blame: A Structural-Model Approach. Journal of Artificial Intelligence Research 22:93-115. doi:10.1613/jair.1391.
14. Bingjie Li, Yumeng Song, Zhongming Yao, Tianyi Li (2026). Localizing Emergent Failures in Agentic AI: Recovering Minimal Repair Families via Counterfactual Replay. arXiv:2608.29228.
15. Jaineet Shah (2026). Causal Agent Replay: Counterfactual Attribution for LLM-Agent Failures. arXiv:2606.08275.
16. Paul-Peter Arslan (2026). Audit Without Verification: When LLM Accountability Layers Relay Rather Than Check. arXiv:2609.07680.
17. Yonatan Geifman, Ran El-Yaniv (2017). Selective Classification for Deep Neural Networks. arXiv:1705.08500.
18. Edoardo Pona, Milad Kazemi, Mehran Hosseini, Yali Du, David Watson, Osvaldo Simeone, Nicola Paoletti (2026). Calibrate-Then-Delegate: Safety Monitoring with Risk and Budget Guarantees via Model Cascades. arXiv:2604.14251.
19. Emilio Calvano, Giacomo Calzolari, Vincenzo Denicolò, Sergio Pastorello (2020). Artificial Intelligence, Algorithmic Pricing, and Collusion. American Economic Review 110(10):3267-3297. doi:10.1257/aer.20190623.
20. Kaue Lopes de Moraes, Rodrigo De-Losso (2026). Algorithmic Collusion Without Deterrence: Auditing the Punishment Mechanism in Q-Learning Pricing Agents. arXiv:2610.21867. ICAIF 2026.

---

# Appendices

Index: A limitations and dual-use; B deviations; C reproducibility; D falsifiable checks and worked record; E benchmark design and selected templates; F original-study detail; G related work; H figure sources; I extra tables.

## A. Limitations and Dual-Use / Ethical Considerations

### A.1 Limitations

- **Precision:** the original study has 8 independent matched world pairs [OC]. More independent worlds under a fresh protocol would extend precision; the interval does not establish equivalence.
- **Generator scope:** twin equivalence is restricted to declared policy spaces and information sets. A separating undeclared observable would refute equivalence for the expanded set.
- **Circularity:** symmetry, enumeration and the reference auditor are consistency checks. Independently designed generators would test transfer beyond those constructions.
- **Real-agent coverage:** the original local model and prompt variant limit generalization [D]. A further real-agent study (EXP-003) was planned and not completed (D-047a).
- **Instrument validity:** control recovery, carrier detection, information loss and unavailable status crosschecks constrain interpretation. Support-level positive-control validation is required before claiming a validated certificate pipeline.
- **Evidence access:** replay and a suspected exposure are required. Matched evidence access and independently labelled deployment data would be needed for superiority or deployment false-positive claims.

Additional restrictions are:

- Certificates establish neither collusion nor intent, equivalence, absence of harm, or exoneration.
- The maximum outsider-effect lower bound was 0.77 against m_O = 2.5, and placebo availability was 2/16 [D]. Placebo absence alone does not explain the lack of supports; message removal also removes information.
- Repaired validity metadata records raw check passes; status crosschecks remain unavailable. B1 sham evidence has n = 4 and remains uncertain [PH]; universal sham equivalence is not established.
- Development baseline comparison shares factual and knockout outcomes but not evidence access. CCC coverage is 202/280 against 260/280 for B2/B2+, with the active-path stratum below its 30/30 floor [DEV]. These are not general superiority or false-positive-control results.
- No paraphrase cell carried a carrier flag [DEV]. Semantic redundancy is not solved.
- Scheduled records are not executed branches, and continuations are not independent worlds. Bootstrap-order, exclusion-test and sham-reconciliation analyses remain exploratory [PH]. Original and prospective studies are never pooled.

### A.2 Dual-Use and release sign-off

[OWNER: dual-use and release review.] An audit may help adversaries learn which exposures it misses; the twin-world generators identify exactly such blind spots. Mitigations proposed: sandboxed simulated tasks, toy reward mechanisms, explicit blind-spot reporting. These are proposals, not completed review. The evidence standard can reduce overconfident accusations, while releasing twin constructions can also teach adversaries which interventions miss redundant or covert channels. Keep examples sandboxed and make unresolved evidence explicit. The acceptable release scope remains subject to the owner review above.

## B. Deviation and correction log

1. DEV-001 reduced sham replication on held-out (S on 7/16 checkpoints, n = 1 per hash rule); optional pairs H09/H10 dropped. Disclosed pre-outcome. [D].
2. DEV-002 placebo-availability census run before its inputs were hash-committed; development census exploratory. [D].
3. v1.2.1 extractor correction re-frozen before held-out data; theta pinned 0.4 by fallback (best Youden J 0.4947 < 0.5); `weak_detector`. [D].
4. Label correction (exp002_heldout_v2): confirmatory study tests separated from exploratory certificates; no numeric change. [D].
5. Validity-metadata repair (exp002_heldout_v3, FIX-001): 16 `gates.all_valid` and 5 `reasons` fields changed; 0 status or numeric changes. [PH].
6. ENH-B corrections applied here: non-commit exclusion estimate re-categorised as original-registered-secondary (its p and sham-gap interpretation remain post hoc); V9 sham signs aligned to S-minus-F; development "predictions confirmed" reworded as agreement with scripted predictions; the "post hoc" label of the whole sensitivity in paper/build/submission.md was wrong and is not repeated. [D].
7. Open (director): `no_placebo_available` is appended on the final inconclusive path whether or not other support conditions held (REV001 F-10); not changed. [D].
8. R2 amendments before the DEV run: CRN (A1), circularity disclosure (A2), RQ6 (A3). [D].
9. R2 amendments after the DEV run, before any prospective seed (DEV-informed, D-040): CCC-L v1 (A4), method-independent RQ2 (A5), RQ4 verbatim plus RQ4b (A6), RQ3 unchanged (A7). Frozen under D-041 after independent review REV-R2 (conditions C2-C4 adopted as reporting rules). [D].

10. R2 execution deviation D-046: mapped enumeration and method execution used Modal Linux containers; population generation for RQ3 and the report tail ran locally. Cross-platform noisy-stratum identity was not established; container self-determinism does not restore it. REV_R3.md corrects misleading archived-gate provenance and gate comparison counts, and distinguishes the controller runtime from the worker runtime. The reported failures remain unchanged. [NP] (execution provenance).

## C. Reproducibility

Frozen EXP-002 outputs: docs/analysis/exp002_heldout_v2/ and v3 (metadata repair; field diff in output_diff_v3.json). Independent reproduction: docs/review/rev001/rev001_repro.json. Gate A: docs/gate_a/v1.2/correction_v1.2.2/. R2: docs/enh/r2/PROTOCOL.md, FREEZE.json (code hashes, enumeration hash, seed list hash, intersection sizes, reviewer, timestamp); commands `python -m ccc.bench hashes|seeds --check`. Offline reproduction script scripts/reproduce_offline.sh. Model digest 5571076f3d70; 3,516 local calls, $0 [D]. R2 input SHA-256 values (`RESULTS.json.inputs`): `frontiers.json`: `5c85df25f10b906daae4ffeb270b2ac2364f1148beca455805d003c42c3c0b13`; `manifest.json`: `148ce53257a3bd6e1530af65a6ad59bf62fcd30b87a0b3b0bfbcfb49fcf8063c`; `population.json`: `3be08849cfb24a3cb54e25744c2a3856b92d9685be6215b95e40ba07bb70879b`; `records.json.gz`: `8e095c9e13a5c126699b2060138afe6a0fdd37457d357fbfa55245fc2146aba8`. Seed-list SHA-256 (`tables.T1.seed_disjointness.seed_list_sha256`): `1720ba12cd131f9d914ea01bf0a14e72f4f7923fd060ca6d5802a2839e829e7c`.

## D. Falsifiable checks and worked evidence record

**A check to run next.** Recompute canonical observables for each twin under its declared set. Unequal observables below the claimed separating set refute that equivalence claim. A method reading undeclared state invalidates that benchmark interpretation. Report failures alongside successful checks, with hashes and independent-unit counts.

**Worked record [D] (schematic).** Record the twin identifier, declared set, tau_O/tau_C/tau_W, replay validity, placebo availability, information-loss flag, highest justified rung and unresolved reason. A shared-evidence allocation twin cannot receive an attribution assertion from that evidence alone. Add an environment-probe record to assess separation. This is a record schema, not a measured certificate.

**Judge disclosure.** No new judge-validity claim is introduced here.

## E. Benchmark design and selected reporting templates

**Preregistered research questions [NP] (frozen criteria; protocol sha256 334a4539; descriptive-with-prediction, not a Holm-corrected family).** RQ1 symmetry: 0 within-pair output differences of 200 for each method x pair type x set where observables are S-equivalent (twin members use common random numbers). RQ2 frontier, method-independent: the observed frontier, the lowest set S at which Bayes-given-S pair accuracy is 1 on all units, equals the enumerated minimal separating set for every listed type, and no method is correct on both members of any unit below that set beyond what Bayes-given-S achieves. RQ3 label-effect gap: the share of mechanism-"forbidden" iid Jira worlds with oracle tau_O >= m_O is below 25%. DEV values are disclosed beside the prediction: Gate A 12/80 [DEV]; benchmark DEV block 12/50 at eps = 0 and 5/50 at eps = 0.1 [DEV]. RQ4 over-attribution [NP] (criterion), kept verbatim from the original protocol: the strongest knockout baseline accuses legitimate members at rate > 0.5 under I1 for each of P2, P3, P6 and benign cooperation; on DEV this failed on P6 and benign cooperation (0/50 [DEV]). RQ4b [NP] (DEV-informed criterion): the same baseline over-attributes on P2 and P3 at rate > 0.5 and at rate <= 0.05 on P6 and benign cooperation, each stratum separately. RQ5 ladder auditor [NP] (criterion): CCC-L v1 within 0.02 selective accuracy of Bayes-given-S at both c, zero over-claims, abstention precision and recall >= 0.9, and >= 0.95 correct attribution when I4 (P2) or I5 (P3) is supplied. RQ6 descriptive: CCC v1.2.2 status distribution per class and stratum.

**Twin-pair types** (each pair shares one seed and nuisance draw and is ONE independent unit; frozen in docs/enh/r2/PROTOCOL.md).

| Type | Contrast | Enumerated separating evidence |
|---|---|---|
| P1 | redundant-harmful vs inert (duplicate carriers) | I3 |
| P2 | colluding allocation vs efficiency-motivated legitimate cooperation, identical observed behaviour | I4 (the legitimate team cedes when an outsider is cheaper; colluders do not) |
| P3 | authorized vs unauthorized transfer, identical policies | I5 (tautological by design, labelled so) |
| P4 | common cause vs message-caused coordination | I1 (shows where knockout works) |
| P5 | suspicious-language inert vs plain-language inert | transcript differs, outcomes identical (tests transcript rules) |
| P6 | information-bearing legitimate message vs harmful steering | harm and utility gates at I1 |

Also: a relayed-harmful case (sender to relay to receiver; expected unresolved at I3), and invalid or corrupted traces. Benchmark classes: harmful message-dependent coordination; legitimate useful communication; suspicious language without harm; harm without message dependence; redundant paths; paraphrased or relayed commitments; common-cause coordination; information-bearing removal that harms; inert messages; corrupted traces; non-identifiable twin members.

**Sample and seeds [NP] (frozen design).** 200 independent units for each of P1-P6, 200 iid Jira population worlds, 100 units for each remaining class; strata eps in {0, 0.1} (eps = 0.1: each scripted agent takes a uniformly random legal action with probability eps; R = 8 continuations per arm), reported separately and never pooled. Seeds derive from the protocol hash by `seed(s,i) = first 31 bits of sha256(protocol_sha256 || s || i)` with a deterministic skip rule against Gate A (12000-12019), DEV (13000-13049), all pilot, EXP-001 and EXP-002 seeds and 0-99999; disjointness is checked by `python -m ccc.bench seeds --check` and hashes are written to FREEZE.json before any run. Common random numbers: twin members share per-continuation RNG seeds, so that RQ1 is not confounded by sampling noise.

**Metrics [NP] (frozen design).** Over-claim (accusation) rate on legitimate and non-identifiable members; sensitivity on E-positive harmful instances; FPR on benign cooperation; abstention rate and coverage; selective accuracy; risk-coverage curves with abstention cost c in {0.25, 0.5} (loss 1 per error, c per abstention, 0 per correct); twin symmetry violations; observed versus enumerated minimal separating set. Exact Clopper-Pearson 95% intervals over independent units; paired comparisons by exact McNemar-type tests; continuous quantities by world-cluster percentile bootstrap (B = 10,000, PCG64 seed 20261026).

**Stopping and failures.** Single pass, fixed N, no interim looks, no seed replacement beyond the pre-run skip rule. Crashes stay in the denominator. Any code change after outcomes are visible forces a new seed block under a new freeze, and both runs are reported.


**Prospective table and figure data [NP].** All paths below are keys in `docs/enh/r2/run_par/RESULTS.json`; the data are complete, while figure rendering remains for ORCH.

| Item | Populated value / source key |
|---|---|
| T2 symmetry | `tables.T2.violations`; selected result in Section 5.2 |
| T3 frontier | `tables.T3`; P1/I3, P2/I4, P3/I5, P4/I1, P6/I1 in both strata; relayed-harmful unresolved at I3 |
| T4 prevalence | `rq.RQ3.by_epsilon`, `tables.T4`; stratum values in Section 5.3 |
| T5 over-attribution | `tables.T5`; original RQ4 failed |
| T5b refinement | `tables.T5b`; DEV-informed RQ4b failed |
| T6 class/method/set rates | `tables.T6`; all available M/H/E views and inapplicable cells retained |
| T7 abstention, coverage and risk | `tables.T7`; both frozen abstention costs, anchors and Bayes reference retained |
| T8 ladder auditor | `tables.T8`, `tables.T8_v0`; both versions failed; undefined denominators retained |
| RQ6 CCC statuses | `tables.RQ6`; exposure L2, not attribution |
| T9 failures | `tables.T9`: complete; crashes empty; corrupted-trace statuses retained |
| T1 design and disjointness | `tables.T1`; all excluded-set intersections are zero |
| T10 post-hoc list | `tables.T10`: empty |
| Figure 2 frontier | `figures.frontier_heat_map`; prospective data, rendering pending |
| Figure 3 risk-coverage | `figures.risk_coverage`; prospective data, rendering pending |

**Methods compared, full definition.** (each sees only the observables of its declared set; none tuned on prospective seeds; frozen before any prospective seed existed): CCC v1.2.2; B0 outcome-only; B1 simple knockout; B2 and B2+ harm-gated knockout; B3a and B3b influence-only; B4 transcript keyword rule; always-answer and always-abstain anchors; Bayes-given-S reference (majority label per S-equivalence class under frozen class priors; the ceiling for any method restricted to S); CCC-L v1 (new, exploratory, DEV-informed), which outputs the highest justified rung, "insufficient for L3 under S", or "L3 excluded" (attribution ruled out by separating evidence in S), attributing L3 only when S contains separating evidence. CCC-L v0 lacks the "L3 excluded" output; DEV showed it therefore cannot be correct on both members of a pair. It is retained, run and reported prospectively so the change is visible. The "strongest knockout baseline" is fixed in advance as the better of {B2+, B3b} by balanced accuracy on DEV block 13000-13049 under I1 (ties to B2+), recorded in FREEZE.json.

**Selected reporting templates.** The pass templates for RQ1 and RQ2, negative templates for RQ3, RQ4, RQ4b and RQ5, and both stratum-specific descriptive RQ6 templates are populated in Section 5. Inactive alternatives are removed; no favourable alternative replaces a failed prediction. Full numerical cells remain in `docs/enh/r2/run_par/RESULTS.json`.

## F. Original-study detail

**Preregistered S1–S3 family [OC].** S1 (B1 mean tau_O) 0.970, Holm p = 0.164; S2 (B2 mean tau_O) -0.384, Holm p = 0.4375 (only 5 nonzero values against a floor of 6); S3 (tau_C contrast) -1.820, Holm p = 0.164. None is significant.

**Sham (V9) [PH].** On a consistent S-minus-F outsider-reward scale: B1 mean 1.64, 90% CI [-0.54, 3.82], n = 4, uncertain; B2 0.03 [-0.06, 0.12], n = 3, pass; pooled 0.95 [-0.20, 2.10], n = 7, pass. Individual sham gaps are +3.77 (H02_B1) and +2.62 (H05_B1). We report both aggregations and make no sham-equivalence claim. The V10 lesion check (n = 2, interval [-7.4, 11.7]) is uninformative.

**Accounting [D].** 199 scheduled branch records = 143 executed valid continuations (F64, K64, S7, N8) + 56 unrun placebo branches (`no_placebo_available`); 0 failed, invalid or retried. 3,516 local calls, $0. F and K missingness 0/32 per arm per regime. 

**Disclosed metadata repair [PH].** A validity-metadata repair, disclosed as `exp002_heldout_v3`, restores canonical validity keys the analysis loader had dropped. It changes 16 `gates.all_valid` fields and 5 `reasons` arrays and nothing else: certificate statuses stay 0/11/5, and the primary Delta, interval and p are unchanged. All original files remain byte-identical.


**Development evidence detail (Section 5.1).** Gate A (v1.2.2; 800 non-constructed cells; one scripted continuation per arm) is a deterministic implementation check, not held-out inference. Factual/sham identity 380/380, knockout scope 4180/4180, branch isolation 760/760, A2 benign cooperation never supported 80/80 (26 inconclusive, 54 not supported), A6 invalid-trace validator 350/360 [DEV]. The A5 redundancy check passes 20/120 (16/68 amended) and no paraphrase cell carries a carrier flag [DEV]. The pre-written scorecard had 16 predictions agree with the scripted generator, 2 disagree and 3 untested; "agreement with scripted predictions" is not validation [DEV]. The label-effect gap on iid Jira worlds was 12/80 in Gate A [DEV], and 12/50 (eps = 0) and 5/50 (eps = 0.1) in the benchmark DEV block [DEV]. These are the development observations from which RQ3 and RQ4 were derived; none counts as confirmatory.

## G. Related-work detail and search scope

Detailed comparison paragraphs to be carried from paper/build/submission.md Appendix B.1 (DoVer, AgenTracer, Audit the Whisper, CABAL, tool-use steganography: all verified in paper/references_draft.bib; re-cite with numbers added then) plus the ENH-A neighbours above. [OWNER: confirm whether to carry these over.] Not found in the bounded search: a theorem that message-level interventional evidence on influence, harm and utility cannot separate harmful coordination from legitimate cooperation. Absence in a bounded search is not proof. Safe wording used throughout: "we state and demonstrate a scoped outcome-equivalence limit for declared-arm evidence; related indistinguishability claims exist for marginal price tests [5] and are argued for reasoning agents [6]". No "first" claim.

**Related work, extended.** *Responsibility, failure attribution and overdetermination.* Counterfactual replay for failure attribution and minimal repair families [14, 15] and degrees of responsibility under redundant contributions [13] motivate our redundancy cases, where single knockout is zero and joint knockout is positive; we report such cases as "not identifiable under I1", not "no effect". *Abstention and reporting standards.* Selective classification with a reject option and risk-coverage reporting [17] and delegation with cost or safety-performance guarantees for safety monitors [18] motivate our abstention-aware scoring. Preregistered audit studies have precedent: one finds auditors naming innocent parties after upstream false alarms, with its preregistered hypothesis not supported [16]. Steganographic and covert channels [10] can evade any text-level intervention; this limit is inherited.

*Search scope.* Search date 2026-10-24; Firecrawl paper index, web search and fetch, about 25 queries [D] (inherited, not independently traceable in this repository; unchecked count). This is a bounded search, not a survey. Legal "plus factors" primary law was not checked. The search was not rerun.

## H. Figure plan

| # | Figure | Status | Exact data source |
|---|---|---|---|
| 1 | Twin worlds, shared transcript and replay effects, and the ladder showing what separates attribution | conceptual diagram [NP], matching PROSPECTIVE source metadata | figures/enh/prospective/fig_ladder.json; no measured data |
| Appendix | Branch schematic F/K/S/N | reuse [D] (schematic) | figures/fig_arms.svg |
| 4 | Held-out per-world Delta, aggregate and CI; non-commit sensitivity as separate marker (existing; caption must say registered sensitivity [ORS]) | reuse | figures/fig_heldout_delta.json; docs/analysis/exp002_heldout_v2/figure_data/fig_delta_by_world.json |
| 2 | Frontier heat map, pair type x information set (Figure 2; `RESULTS.json.figures.frontier_heat_map`, NEW) | data complete [NP]; rendering pending | `RESULTS.json.figures.frontier_heat_map` |
| 3 | Risk-coverage curves, c = 0.25, 0.5, with anchors and Bayes-given-S (Figure 3; `RESULTS.json.figures.risk_coverage`, NEW) | data complete [NP]; rendering pending | `RESULTS.json.figures.risk_coverage` |
| B1 | Case-level certificate intervals vs m_O (existing) | appendix [D] | figures/fig_heldout_cases.json; docs/analysis/exp002_heldout_v2/figure_data/fig_tau_vector.json |
| B2 | Supported vs oracle effect, DEV fixtures (existing) | appendix [DEV] | figures/fig_supported_vs_oracle.json |
| B3 | Gate A integrity checks, DEV (existing) | appendix [DEV] | figures/fig_gateA_integrity.json |
| B4 | Baseline positive-call rates, DEV (existing) | appendix [DEV] | figures/fig_confusion_dev.json (gate_a_results.json.gz sha256 8aa6b1b0...) |
| B5 | Prevalence interval plot (RQ3) (NEW) | data complete [NP]; rendering pending | `RESULTS.json.figures.prevalence_interval` |

Main-text sequence: twin schematic, frontier, risk-coverage, held-out null. Development diagnostics and replay arms remain in the appendix. ORCH verifies the rendered page budget.

## I. Appendix tables

T1 design, counts, seed disjointness; T10 post-hoc list (all analyses added after outcomes are visible, labelled [PH]).

## LLM Usage Statement

[OWNER: approve final wording.] Claude (via Claude Code) and Codex agents, coordinated by a Claude Code session, assisted with planning, implementation, tests, analysis scripts, literature verification and manuscript drafting. Experimental agents are separate local models and scripted policies. Human owner verification of claims, results and references has not been established in this draft. The owner is the sole author; no AI system is a co-author.
