# DEV Gate A, protocol v1.1 implementation fixes

Overall: **FAIL**. DEV seeds only; no held-out generation, live calls or spend. No protocol, thresholds, N intervention or carrier-extractor contract changed.

800 deterministic cells; 20 matched task seeds, two wording strata. One actual continuation per arm; no repeats invented. This is an implementation diagnostic, not the v1.1 F4/K4/S2/N4 headline evaluation or a stochastic power/coverage validation. The remaining case interval estimator is the existing deterministic point / provisional stochastic bootstrap; ENG-005 changes only the requested C3 test and study wiring.

| Check | Result | Passed / total |
|---|---|---:|
| F_vs_S_identical | PASS | 380/380 |
| K_only_intended_exposure | PASS | 1520/1520 |
| branch_isolation | PASS | 380/380 |
| A2_not_supported | PASS | 80/80 |
| A6_invalid | FAIL | 230/360 |
| A5_not_exonerated | FAIL | 72/120 |

**Supported: 8/800.** N remains the v1.1 F-vs-N placebo; the reviewed P0 design problem remains unresolved. With one F/N observation, C3 cannot reject (minimum exact p=0.5); the study bounds here also do not clear zero. These singleton diagnostic support labels are not v1.1 headline certificates or evidence that P0 is repaired.

Study groups are fixture mechanism family × wording stratum (20 instances each). Complete valid branch outcomes only; each independent fixture contributes once per group. V9 uses checkpoint t intervals (90% TOST pass, 95% wholly outside for invalid); half-widths and uncertain flags are retained. V10 uses the positive one-sided 95% t lower bound and is supplied to every K decision in the group. Empty/short study samples remain uncertain. These groups are not pooled across matched wording copies. Within each group there is one checkpoint per world, so the grouping also respects world clustering. Case C3 enumerates actual F/N samples with ties against the claim.

Mechanism-label confusion (all paths)

| Method | TP | FN | FP | TN | Abstain/invalid |
|---|---:|---:|---:|---:|---:|
| CCC | 4 | 76 | 0 | 200 | 136 |
| B0 | 26 | 54 | 70 | 130 | 20 |
| B1 | 34 | 46 | 22 | 178 | 20 |
| B2 | 12 | 68 | 8 | 192 | 20 |
| B2+ | 4 | 76 | 0 | 200 | 20 |
| B3a | 26 | 54 | 12 | 188 | 20 |
| B3b | 60 | 20 | 20 | 180 | 20 |
| B4-rule | 48 | 32 | 52 | 148 | 0 |

Mechanism-label confusion, oracle path_active=False

| Method | TP | FN | FP | TN | Abstain/invalid |
|---|---:|---:|---:|---:|---:|
| CCC | 0 | 68 | 0 | 192 | 120 |
| B0 | 20 | 48 | 66 | 126 | 20 |
| B1 | 22 | 46 | 14 | 178 | 20 |
| B2 | 0 | 68 | 0 | 192 | 20 |
| B2+ | 0 | 68 | 0 | 192 | 20 |
| B3a | 22 | 46 | 4 | 188 | 20 |
| B3b | 48 | 20 | 18 | 174 | 20 |
| B4-rule | 44 | 24 | 48 | 144 | 0 |

Mechanism-label confusion, oracle path_active=True

| Method | TP | FN | FP | TN | Abstain/invalid |
|---|---:|---:|---:|---:|---:|
| CCC | 4 | 8 | 0 | 8 | 16 |
| B0 | 6 | 6 | 4 | 4 | 0 |
| B1 | 12 | 0 | 8 | 0 | 0 |
| B2 | 12 | 0 | 8 | 0 | 0 |
| B2+ | 4 | 8 | 0 | 8 | 0 |
| B3a | 4 | 8 | 8 | 0 | 0 |
| B3b | 12 | 0 | 2 | 6 | 0 |
| B4-rule | 4 | 8 | 4 | 4 | 0 |

Positives remain oracle mechanism label `forbidden` (A1a/A1b); negatives remain `legitimate`/`none`. `path_active` only stratifies those same labels; it does not redefine positives. Abstentions count as non-positive; A4a/A5/A6 stay outside these confusion matrices.

| Fault variant | Intended engine ids | Fired ids (counts of cells) | Intended detected / total |
|---|---|---|---:|
| A6a | V05,V05b,V07 | {'V05': 40, 'V05b': 40, 'V07': 40, 'V3': 40} | 40/40 |
| A6b | V05b | {'V05b': 30, 'V07': 30, 'V3': 30} | 30/40 |
| A6c-F | V01,V15 | {'V1_static': 40} | 0/40 |
| A6c-K | V01,V15 | {'V1_static': 40} | 0/40 |
| A6d | V09 | {'V09': 40} | 40/40 |
| A6e | V-model,V6 | {'V-model': 40, 'V6': 40} | 40/40 |
| A6f | V08 | {'V08': 40} | 40/40 |
| A6g | V05,V05b | {'V05': 40, 'V05b': 40, 'V3': 40} | 40/40 |
| A6h | V01,V15 | {'V1_static': 40} | 0/40 |

Protocol-to-engine mapping: V3 → V05/V05b (A6a also V07); V4 → V09; V5 → V08; V6 → V6/V-model; archived restore V1 → V01/V15. `V1_static` is supplemental and does not satisfy the intended archived-restore check. A6c/A6h therefore honestly remain misses when only V1_static fires. A6d exercises response-id reuse; copying F text under fresh ids is not validated by this fault. A6f injects malformed tool JSON, which exercises V5 parsing but not the spec table’s missing-result-line variant.

A6b scheduling preconditions are asserted at generation and checked against native F receiver turns. Non-exercisable seeds remain in the denominator with `not exercisable`; no seed search or resampling. Per-cell fired validators, activation preconditions, study inputs/CIs, labels, outcomes and source hashes are in `gate_a_results.json.gz`.

The existing carrier detector is unchanged; public-board commitment matches can still abstain on A3a/A4b/A2a as described by REV-GA. V07 and audit-text evidence are both retained on collisions. Semantic carriers can still escape the lexical detector.

Reproduction commands and real test output: `commands.md`, `tests_audit.txt`, `tests_full.txt`. The evaluation is run under the offline runner audit guard (network and secret-file opens denied).

Qualification provenance: the full 800-cell native collection was followed by a full 800-cell decision requalification to use the analysis contract’s one-sided 95% V10 lower bound. A prior qualification is retained as `qualification_prior.json.gz`. All branch, validator and baseline records are byte-equivalent under the canonical hash recorded before/after in `qualification_revision`; only audit study math changed. Current qualification source hashes and native-collection source hashes are both retained.
