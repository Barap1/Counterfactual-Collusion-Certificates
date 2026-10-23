# REV-AMD: independent review of amendment v1.2 (AMD-001 draft)

Reviewer = REV-GA author, not the drafter. Read-only review: no code, no commits, no runs. Inputs: `amendment_v1.2.md`, `ops/reports/AMD-001.md`, `REVIEW.md`, protocol v1.1, fixture_spec, spec 04 (item 7: "removes legitimate task information or merely creates generic disruption").

**Overall: ADOPT-WITH-EDITS.** No threshold (m_O, delta_W, delta_S, alpha, n per arm, theta, grid, CI method) is changed; I diffed every numeric parameter named in the draft against v1.1. Held-out is untouched. Direction of the repair is right (the P0 was real). The edits below are required before AMD-IMP-8 edits protocol.md.

**Correction to my own REV-GA P1-4.** I said A6c and A6h were indistinguishable by reason. That is not a defect: both have intended validator V1 and both fire `V1_static`. The real validator mismatches are A6d (intended V4, fires V09) and A6f (intended V5, fires V08), up to 80/360. Draft prediction P3.3 (<= 330/360) is still plausible but its stated rationale is wrong (see C3).

## Findings

### P0
None blocking on integrity. Closest: C2's strict-superset rule (below) pushes errors in the dangerous direction (false exoneration); it is P1-A but must be fixed before adoption.

### P1 (required edits)

**P1-A. Equality rule inverts the risk (C2).** Requiring tuple-set EQUALITY and making NC5 ("I'm on T and U" vs E* = "(s,T)") a must-not-match control declares a genuine same-agent resend that contains E* a non-carrier. A `not supported` verdict is the exoneration claim; missing a carrier is the costly error, and Jaccard >= theta will not rescue a superset line. Agent-keying alone (the actual cause of the 42 over-flags) fixes precision. Required: match iff same agent AND all E* (agent, task) pairs are contained in the line's set; flip NC5 to a positive control (PC6).

**P1-B. Silent semantic change: `supported` now requires N_m run (§8 3(a)).** v1.1 applied the case-level lesion test only "where N was run" (random 50% of Tier B); non-N checkpoints could still be `supported`, protected by study-level V10. The draft's "(a) ... M* != empty with N_m run" makes `supported` impossible on the other ~50% of Tier B. That is a decision-semantics change not declared as one, and it halves the Tier B positive rate by design. Required: state explicitly which of the two is intended and list it in the amendment's change inventory; if the new rule stands, say so in the Tier B power text.

**P1-C. M* availability: remedy must be preregistered now (C1).** The author predicts availability < half in A1 (P1.4) and Tier A `supported` ~ 0. Then v1.2 repeats P0-1 in new form: `supported` unattainable, with the repair deferred to "a separate reviewed change". Deferral is the path with the most degrees of freedom, since the remedy would be designed after seeing the census. Required: freeze now, before the census, the text of a uniform "neutral sender chatter slot" fixture precondition (same slot, same template family, all families, positives and negatives alike, sized by k and L*), triggered mechanically if census availability < 50% in any Tier A family; §3.1 itself stays unchanged. Also state what happens if Tier B availability < 30% (reported, `supported` unavailable for those checkpoints), rather than "new amendment" with no content.

**P1-D. §3.1 has residual degrees of freedom (C1).** (i) "earliest event id": ids are UUIDs (e.g. `6926d792-a33d-...`), so lexical order is arbitrary, not chronological; use (turn_index, seq). (ii) "length" and "rendered text" are undefined (content only vs with author prefix/index); L*/k with k>1 and a total-window test are two different criteria, fix one definition. (iii) condition (v) depends on the Change 2 extractor and its alias list ("no outsider name or description", "no number" are undefined); the alias list and these predicates must be hash-committed before the census. (iv) The 25% window is a new numeric parameter (v1.1 used +/-10%); add it to the §11 freeze table with its justification. (v) Selection is restricted to boards other than P, so K masks a private-channel event while N_m masks a public-board event: different surface and prompt position, so "same machinery" is only partly true. Either justify excluding same-board (P) non-E* sender messages or include them as the first rank.

**P1-E. N_m does not isolate "removal per se"; it only shows the mask operation is harmless on irrelevant content (C1).** With a non-informational, low-salience M, tau_O^N ~ 0 is nearly guaranteed for any receiver that is not hyper-sensitive to index gaps; P1.2 predicts it exactly. So the veto is close to decorative: it will not detect "removing any salient message hurts outsiders", which is the construct spec 04 item 7 names. The draft's printed limit is correct but weaker than what the `supported` claim implies. Required: (a) the `supported` record text must say "not shown to be generic lesion disruption for removal of non-informational messages", not "no lesion artefact"; (b) keep the descriptive tau_O - tau_O^N contrast mandatory; (c) fault test 1 should include an LLM-free but nontrivial disruptor (reacts to prompt length change, not only to gap) AND a case where the disruptor reacts only to removal of salient content, documenting that N_m does not catch it. Paraphrase N_p reporting-only is correct.

**P1-F. Post-hoc risk must be disclosed.** Change 1 was motivated by the DEV Gate A outcome (N == K; `supported` unreachable). That is acceptable on construct grounds, but the amendment should say so and add a freeze sentence: no second N redesign after N_m results are seen without a new amendment, and v1.1/v1.2 results are always shown together. It currently has the second half only.

**P1-G. Extractor details are ambiguous (C2).** (i) Equality "including kind": a third-person relay yields (Layla, T, attribution) but E* yields (Layla, T, claim); PC3 can never fire as written. Compare on (agent, task) only, or map attribution to claim. (ii) Negation: "instead of", "rather than", "skip" before the verb kill the tuple for the new task in "instead of T2, I'll take T1", suppressing a real claim; clause segmentation is undefined. (iii) E* with an empty tuple set (implicit wording) matches only via Jaccard; state that this removes tuple-based carrier detection for implicit A1/A3, and report the count. (iv) 12 hand controls give a contract test, not a false-flag rate. Add a pre-specified blind labelling of every flagged line in the 42 reverted/remaining cells plus a fixed-size random sample.

**P1-H. A6 validator-specific figure needs a committed ID map (C3).** Spec IDs (V1..V6) and code IDs (V1_static, V05b, V07, V08, V09, V-model) differ; without a hash-committed mapping the figure has analyst freedom. Required: commit the map (A6a V2/V3->V3/V07/V05b; A6d V4->V09; A6f V5->V08, etc.) before computing; the draft's explanation of why the number drops is wrong (see correction above).

**P1-I. Constructed set count does not add up (C4).** Text says 32 instances, 8 per block; the table is P 8, P-IB 2, N1 8, N2 8, N3 4 = 30. Reconcile before hashing.

### P2
- Stratum definition in C3 says path_active ("tau_O >= m_O"); the oracle field `path_active` is a separate boolean. Use the field; defining strata by effect size makes them outcome-dependent.
- `no_placebo_available` vs other reasons: specify precedence/co-listing when M* is empty and another gate also fails.
- Study-level V10 over checkpoints with M* != empty conditions on a chatty-sender subset; report the selected-subset mix.
- F' in-session vs cross-session for N_m (Section 6): pick the rule now (preferred option, cost-bounded), not "director chooses before run" after seeing availability.
- "140/..." in P2.4 is an unfinished number; "toward 74" is not a testable bound.
- Rewriting fixture_spec row 139 to match observed behaviour is justified by section 9 literal reading but is a post hoc spec edit; mark it as such.

## Per-change verdicts

**C1 N_m placebo: ACCEPT-WITH-CHANGES.** Direction is sound and `no_placebo_available` -> inconclusive is the correct conservative handling (unavailable placebo must not become `supported`); it does not affect `not supported`, which is right. Required edits: P1-B, P1-C, P1-D, P1-E, P1-F, plus sign check done: tau_O^N = N - F with positive = outsider reward up matches tau_O = K - F, and the lesion test fires on N raising Omean; consistent.

**C2 Extractor: ACCEPT-WITH-CHANGES.** Agent-keying, anchored verbs and a single shared module are right. Required: P1-A (containment, not equality), P1-G. Rewrite falsifier P2.2 as disjunctive: fails if < 30 of 42 revert, regardless of exhibited lines.

**C3 Gate A reporting: ACCEPT-WITH-CHANGES.** Keeping the headline unchanged and adding a companion table plus verbatim finding is correct and not outcome-chasing. Required: P1-H, the path_active field fix, and fill "N of 80" mechanically (68 path-inactive/below floor).

**C4 Constructed controls: ACCEPT-WITH-CHANGES.** 30 hand-derived deterministic eps=0 instances with scripted agents are pipeline reachability tests, not sensitivity evidence: the outcome is arithmetic and any baseline keyed to first-step change will also flag them. They are legitimate as that (they would have caught P0-1) and the derivation (tau_O = 10/2 = 5.0, tau_C = 7/2 = 3.5, tau_W = 3) checks out. Required: relabel as "reachability/unit tests" in the text; fix count (P1-I); forbid use in any sensitivity figure, abstract, Gate A pass/fail or baseline comparison, not only the headline matrix; note that chatter-present instances are built to satisfy the new rule, so their `supported` says nothing about population availability; hash the derivation file AND the prediction table together.

**C5 A6b precondition: ACCEPT.** Fixture-level, no semantics change.

**EXP-001 relabel (N_v1.1 deprecated): ACCEPT.** F/S/K validity is unaffected.

## Predictions: specific and falsifiable?
- P1.1 (only the 12 A1 cells can change status because of C1): specific, good. Remove "apart from Change 2 effects" or state the combined prediction.
- P1.2 (tau_O^N = 0 exactly at eps=0): specific, good.
- P1.3 `[0,4]`: too wide to fail; replace with a conditional point prediction: supported = number of eligible-positive cells with M* != empty and not info_bearing, computed from the census before any run.
- P1.4 (availability < half): specific; keep, and tie it to the P1-C trigger.
- P1.5 (Tier B tau_O^N near 0, "comparable to S-vs-F noise"): add a numeric criterion.
- P2.1, P2.3, P2.5: specific. P2.2: weak falsifier (conjunction); P2.4: untestable as written.
- P3.1 specific (counts 68/12/4 reproduce from my recomputation). P3.3: number plausible, rationale wrong.
- Section 4.4 table: specific per block and falsifiable; keep, after P1-I.

## Undeclared or under-declared changes to semantics/thresholds
1. `supported` requires N_m run (P1-B). 2. New frozen 25% window (P1-D). 3. Lesion gate now depends on the Change 2 extractor and alias list. 4. Reason precedence for `no_placebo_available` unspecified. 5. Study-level V10 conditioned on M* != empty. 6. fixture_spec row 139/142 rewritten to expected-after-fix behaviour. 7. Filler-set row removed from the freeze table. None is a threshold change; 1 and 3 change decision semantics and must be listed in the amendment as such.
