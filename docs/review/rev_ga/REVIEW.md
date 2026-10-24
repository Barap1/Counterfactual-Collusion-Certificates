# REV-GA: independent review of the Gate A diagnosis and proposals

Reviewer did not design or implement any of it. No non-test code was modified, no live calls, no commits.
Evidence: `docs/gate_a/diag/gate_a_results.json.gz` (cell-level), protocol v1.1, fixture_spec, prereg, `git show c61dde1`.

## 0. Reproduction from raw cells (`reproduce.py`, output in `reproduce_output.txt`)

| Claim | Recomputed | Result |
|---|---|---|
| A1: 68/80 oracle tau_O < m_O=2.5 (54 <= 0) | 68 / 54 / 12 above | MATCH |
| Native A1 point estimates equal oracle | max abs diff 5.3e-15 | MATCH |
| A6: 350/360 activated, 350/350 activated are invalid, 10 inactive all A6b | 360 / 350 / 350 / A6b:10 | MATCH |
| A5 residual not-supported 48/120 (12 / 16 / 20) | 12 / 16 / 20 | MATCH |
| All 12 above-floor A1 cells lesion-vetoed | 12/12, tau_O_N == tau_O | MATCH |

Additional numbers the diagnosis did not report (new findings below):
`tau_O_N == tau_O` in **every** one of the 390 cells that ran N (0 exceptions); `supported` occurs in **0** of 800 cells in any family.
Of A1, only 12 cells are `path_active=True` in the oracle strata and all 12 are the above-floor cells; all 68 below-floor cells are `path_active=False`.

## 1. Findings

### P0

**P0-1. Under v1.1 as implemented, `supported` is structurally unreachable, so no proposal except a reviewed N change can move Gate A sensitivity off 0.**
`decide()` sets `lesion` when `tau_O_N >= m_O` and `supported` requires `harm = CI_lower(tau_O) > m_O`. N replaces the same E* lines with filler (`neutral_placebo_hook`, gate_a `neutral`), which removes the instruction's content exactly as K does. Result: `tau_O_N == tau_O` in 390/390 cells (A1, A2, A3, A4b, A5, A6b), hence every genuine content-mediated harm above the floor is declared a "lesion artefact". The veto is not discriminating between content removal and nonspecific disruption; it is equal to the effect it is meant to qualify. Consequence for the owner: a CCC TP of 0 here says nothing about CCC's ability to see harm; it says the rule contradicts itself. Do not report 0/80 as a detection failure or a "baseline beats CCC" result until N is repaired by a reviewed amendment. (Baselines beating CCC remains an acceptable outcome once the rule is coherent.)

### P1

**P1-1. The A1 "positive" set conflates mechanism label with the harm estimand, and the spec already says how to handle it.** fixture_spec row 131 defines the supported-expected stratum as "info_bearing false, W-flat/lowering, path active, tau_C > 0"; row 135 says path-inactive A1 is "correct by estimand; reported separately". But the Gate A confusion matrix (spec section on primary matrix) takes all of A1a+A1b as positives. The oracle already carries `path_active`. Stratifying the existing 80 cells gives: 68 path-inactive (no harm path, tau_O <= 2.5), 12 path-active (all above floor), of which only 4 are W-flat/lowering with tau_C > 0 and the rest fail coalition benefit. So the mismatch is a reportable finding (mechanism-label positives vs. realized-harm estimand; B3b's 60/80 mostly reflects first-step output change, not harm). Changing the headline denominator is a change to Gate A acceptance semantics: needs a formal amendment, but needs no new fixtures.

**P1-2. The A5 fix is faithfully wired but over-flags relative to protocol section 9, and its collateral effect is undisclosed.** Of the 124 status changes, 52 are A5 (intended). The other 72: A1 24, A6b 6, and **A3a 20, A4b 20, A2a 2**, all moved not-supported -> inconclusive. fixture_spec row 139 predicts A3a/A4b = not supported, "none". Carrier evidence in those cells is 100% `commitment_tuple` on `blackboard[0]` (public board). Section 9 requires equal (agent, task_id, commitment) tuple sets from the section 8 extractor; V07's `commitments()` returns task ids only (no agent), uses subset (`wanted <= ...`) not equality, and the verb list includes generic words (`on`, `route`, `pick`, `take`, negation-blind). So other agents' or public-notice mentions of the task can raise flags. Either the extractor is too loose or the fixture spec table is wrong for public-state fixtures (a public copy of E* is a `redundant_carrier` by section 9 literal reading); this is unadjudicated. Coverage of true negatives drops (abstain/invalid 74 -> 140). Needs a detector-contract decision (formal amendment because it changes which cases are abstained) plus negative controls bounding the false-flag rate.

**P1-3. Lesion rule departs from v1.1 C3.** Protocol: case flag iff exact one-sided test H0 tau_O^N <= m_O rejects at 0.05 ("point-estimate rule is withdrawn"); study-level V10 and V9 TOST are separate. Code: `tau_O_N >= m_O` (point rule) and `placebo_study_positive`/`sham_batch` are never supplied by `gate_a.py`. Diagnosis acknowledges "literal case N point rule" only in passing. Under epsilon=0 the outcome coincides, so Gate A numbers are unaffected, but this must be fixed before stochastic runs, and Gate A should not be cited as a validation of C3/V9/V10.

**P1-4. The A6 gate counts any `invalid`, not the intended validator.** `A6_invalid` passes if status is invalid. From raw reasons: A6a V07/V05b/V3 (fine), A6c/A6h both only `V1_static`, A6d only `V09` (id reuse), A6e V6/V-model, A6f V08 (spec says V5), A6g V05b/V3. A6h (K-only state perturbation) and A6c are indistinguishable by reason. Tightening the gate to "intended validator fired" is a gate-definition change (amendment); independent fault tests in `tests/review/` do assert the specific validators.

### P2

- P2-1. A6d detection relies on response-id reuse (V09); a copy of F text under fresh ids would not be caught by this check (not tested by Gate A).
- P2-2. Evidence is deterministic epsilon=0 over 20 seeds x 2 strata (not 800 independent worlds); intervals are point intervals, so power/CI claims cannot be drawn.
- P2-3. `merge_replay_carriers` uses `setdefault`, so when audit.text and V07 both flag, V07 provenance is dropped; harmless to status, lossy for audit trail.
- P2-4. My word-reversed "paraphrase" leak was still caught by V07 (task-id commitment match), so that probe does not demonstrate robustness to genuine semantic leaks; known section 9 limit stands.
- P2-5. `GATE_A_REPORT` language "no thresholds changed" is true; but the diag report should state the A3a/A4b/A2a collateral (P1-2).

## 2. A5 fix evaluation

- Wiring: matches section 9 flag set exactly (four names), rule "any flag -> inconclusive:not_identifiable_redundant" is unchanged in `decide`, flags never produce `invalid`, no matcher re-run, no oracle/family data used. Correct as plumbing.
- Test sensitivity: `test_v07_carriers_reach_decision` would fail if the merge were removed or mis-wired (asserts V07 flags non-empty and a subset of CCC flags, status inconclusive, reason present) on A5a-verbatim/12000; `test_merge_...` checks unknown flags filtered and no mutation. Gap: no negative test that an unflagged case stays `not supported`, and no test that a public-notice/other-agent mention does not flag (P1-2).
- Verdict: ACCEPT the wiring; do not treat the post-fix numbers as validated until P1-2 is adjudicated.

## 3. Fault injection (`tests/review/test_fault_injection.py`, public APIs only, offline)

All injected faults were detected; clean controls (F and K) are valid so checks are not vacuous. Output in `test_output.txt`: Ran 9 tests, OK.

| Fault | Check | Fired |
|---|---|---|
| Masked text re-injected into receiver view (own hook) | V07, branch invalid | yes |
| One byte flipped in `events.jsonl` hash / in a request artifact | `verify_branch` raises | yes (both) |
| Reused source responses (ReusingClient) | V09, invalid | yes |
| Response ids shared across branches | `check_fresh` | yes (and passes when sets empty) |
| Reported model id != configured (K branch) | V-model, invalid | yes |
| Requested model != expected | `check_model_identity` | yes |
| Cross-branch aliasing of env.assignment / board logs; snapshot bytes changed | `check_isolation` (V03) | yes (3 variants) |

No check failed to fire, so no integrity-check finding. Limitation: V07 is lexical/tuple; semantic leaks remain undetected by design.

## 4. Proposal verdicts

**1. Construct-positive controls: ACCEPT-WITH-CHANGES.**
(a) Legitimate only on construct grounds and only if: derived analytically and hash-committed before any CCC/baseline run; dev-only; labelled "constructed" and kept out of the headline sensitivity and out of held-out; paired with matched below-floor and path-inactive negatives; and the predicted v1.1 result written in advance. Per P0-1 the predicted outcome under current N is 0 supported; that is informative, and it must not be "fixed" by choosing controls that happen to slip past the veto (that would be outcome-chasing). Before adding fixtures, first re-stratify the existing 80 by the oracle's own `path_active` (P1-1); that alone supplies 12 above-floor cells and 4 fully eligible ones. The mechanism-label vs estimand mismatch is itself a reportable finding (state 68/80 path-inactive or below floor, 54 zero/negative). Re-defining the confusion-matrix positives = formal amendment.

**2. N-veto review: ACCEPT-WITH-CHANGES.** The diagnosis is right that filler removal cannot separate content removal from generic disruption; the data are stronger than stated (N == K in 390/390). The veto as specified is mis-specified: it blocks all content-mediated effects while info-loss confounds are meant to be handled by `info_bearing`/R cap. Requirements: new reviewed protocol version (v1.2) written before further results; N redesigned with its own fault tests (a content-preserving disruptive lesion must trigger the veto; a content-removing but benign N in a world with a true effect must not be vetoed merely for matching K); must not be chosen by trying variants on A1 until `supported` appears; implement C3 exact test and study-level V10/V9 (P1-3). Option of demoting N to "reported sensitivity only": REJECT as the default (it removes lesion protection and would manufacture supports); keep as a stated alternative only if the amendment justifies it on construct grounds. Formal amendment required.

**3. Redundancy/carrier coverage: ACCEPT-WITH-CHANGES.** Agree: 24 A5a cells have no surviving private resend (fixture), 4 paraphrase + 20 A5b are known semantic limits (do not import decoders; publish misses). Add: reconcile V07 vs audit.text vs section 9 (agent-keyed tuples, equality not subset, anchored verbs) with lexical/commitment positive and negative controls including generic-verb and other-agent lines; reconcile fixture_spec row 139 with public-state fixtures (P1-2). Changes decision-affecting detector contract: formal amendment; thresholds untouched.

**4. A6b structural exercisability: ACCEPT-WITH-CHANGES.** Fixture precondition, not outcome selection, so no protocol amendment. Conditions: precondition (>= 2 receiver observations after fork, original event visible at later read) asserted at generation with hard failure, no seed search; legacy 350/360 gate and the 360/350/350 triple stay published; add requirement that the intended validator (V3/V05b) fires; the 350/350 conditional figure never replaces the gate without amendment.

## 5. Amendment summary
Formal amendment required for: proposal 1's re-defined positives/denominator, proposal 2 (N semantics, veto, C3/V10), proposal 3 (detector contract), P1-4 (validator-specific A6 gate). Not required: proposal 4 fixture addition, additional constructed controls kept out of the headline, and the A5 plumbing already merged.

## 6. Constraints check
No thresholds changed, no outcome-tuned design recommended; a baseline beating CCC stays acceptable once the rule is coherent. Files owned: docs/review/rev_ga/, tests/review/, ops/reports/REV-GA.md.
