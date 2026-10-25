# Results and claim boundaries

This page maps the public summary to preserved records. The two studies are separate. No experimental output was changed for the repository overhaul.

## Constructed benchmark

Canonical aggregate report: [`enh/r2/run_par/RESULTS.json`](enh/r2/run_par/RESULTS.json). Read the [per-stratum summary](enh/r2/RESULTS_BY_STRATUM.md) alongside the [platform-divergence disclosure](enh/r2/PLATFORM_DIVERGENCE.md).

| README claim | Frozen source field |
| --- | --- |
| Allocation and transfer twins share early observations | `tables.T3.by_set` and retained frontiers; `tables.T2` checks method symmetry conditional on byte-identical views |
| Legitimate allocation accusations: 200/200 | `tables.T5`, epsilon `0`, pair type `P2` |
| Authorized transfer accusations: 200/200 | `tables.T5`, epsilon `0`, pair type `P3` |
| Useful-information accusations: 0/200 | `tables.T5`, epsilon `0`, pair type `P6` |
| Benign-cooperation accusations: 0/100 | `tables.T5`, epsilon `0`, benign-cooperation row |
| Full utility: revised rule 2/84; previous rule 5/84 | `tables.T8` (v1), `tables.T8_v0` (v0), epsilon `0`; 73 undefined accuracy gaps in each version |
| Two consistency checks pass; four prospective predictions fail | Aggregate verdicts RQ1/RQ2 PASS by construction; RQ3/RQ4/RQ4b/RQ5 FAIL; RQ6 descriptive |

The 84 settings cross benchmark classes and evidence access. They are not independent agent samples or an accuracy denominator. The selected allocation cost probe and transfer authorization separator succeed by design; that does not establish recovery of arbitrary hidden policies. Normative labels are generator-defined, not independently adjudicated real-agent intent.

The refined RQ4b passes in the deterministic stratum but fails the original aggregate criterion. All established benchmark findings are restricted to epsilon = 0, a post-hoc decision made after outcomes were visible. Epsilon = 0.1 has substantive cross-platform decision disagreements with unresolved cause. The original aggregate failures and noisy outputs remain available.

## Real-agent study

Canonical corrected analysis: [`analysis/exp002_heldout_v3/`](analysis/exp002_heldout_v3/). Raw input archive: [`runner/archives/exp002-live.tar.gz`](runner/archives/exp002-live.tar.gz), with its [SHA-256](runner/archives/exp002-live.tar.gz.sha256). The [preregistration](stats/prereg.md), [freeze](stats/FREEZE.md) and [deviations](stats/deviation_log.md) are preserved.

In `effects_study.json`, row `Delta_total`:

| Quantity | Value |
| --- | ---: |
| Independent matched-world pairs | 8 |
| Primary contrast | 1.354325711018898 reward units |
| World-cluster 95% bootstrap interval | [−0.01954964911635066, 2.8336288730243204] |
| Exact one-sided sign-flip p | 0.0703125 (18/256) |
| Preregistered directional decision | Not supported |

Sixteen worlds produced 143 valid executed continuations and 56 scheduled but unexecuted placebo continuations; no executed continuation was invalid. `checkpoint_certificates.json` records 0 supported, 11 not supported and 5 inconclusive exploratory case-level certificates. Prompt regimes are not verified ground truth for realized collusion. A nonsignificant result does not establish a null effect.

The independent standard-library reduction prints `1.354325711018899`; its difference from the frozen NumPy estimate is about 10⁻¹⁵ from arithmetic order. The [independent bootstrap receipt](../ops/reports/final_audit/tests/independent_bootstrap.json) verifies the frozen interval. The primary quickstart does not recompute it.

## Corrections and current terminology

The [analysis correction](enh/fix/) repairs certificate-validity mapping and leads to v3. Earlier analysis versions remain provenance, not alternative headline results. The [platform audit](enh/r2/PLATFORM_DIVERGENCE.md) narrows benchmark claims without deleting the noisy condition. The [latest claim ledger](../paper/final/CLAIMS_LEDGER.md) provides finer source mappings.

Some historical files, including the hash-bound [prospective protocol](enh/r2/PROTOCOL.md), use the phrase “confirmatory null” or retain a draft header. They are preserved verbatim to protect the freeze. Current interpretation is **the preregistered directional hypothesis was not supported**, not proof of a null effect. EXP-003 was stopped without completion and supplies no result.
