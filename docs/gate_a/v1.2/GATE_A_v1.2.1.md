# DEV Gate A v1.2.1 — AMD-FIX-2 correction

**Overall Gate A: FAIL.** Fresh offline runs: 800 non-constructed DEV cells and 30 constructed controls. F4/K4/S2/N4 at eligible checkpoints; 20 matched DEV seeds, two wording strata, epsilon=0. Deterministic repeats add no independent information. $0, no live/model calls, no Ollama operations, no held-out worlds, no commits.

## Correction and protocol clarification

Protocol §8 explicitly includes sender plans “I take/am on X”; §9 lists first-person anchors and excludes bare subjectless take. This correction adds first-person `I take` to the shared extractor, retaining `I’ll take` (including curly apostrophe normalization) and `taking`. The §9 anchor enumeration omits `I take`, while §8 includes it: this implementation clarification follows §8 and the first-person/subjectless distinction, without editing the protocol. Singular `Verified cost` now receives the same sender-private-quantity treatment as plural `Verified costs`; own cost/skill/availability forms remain recognized. No fixture-specific decoder, prediction, threshold, or scientific criterion changed. Regression tests exercise the information cap through decide().

A6_intended_validator is a separate mandatory gate_checks entry requiring an accepted frozen-map validator, invalid status, and no runner error. A6_invalid retains the any-invalid diagnostic; it cannot satisfy the intended-validator requirement. All v1.2 artifacts are preserved; GATE_A_v1.2.md is marked superseded. This correction’s artifacts are in correction_v1.2.1/.

## Gate checks

| Check | Pass/total | Verdict |
|---|---:|---|
| F_vs_S_identical | 380/380 | PASS |
| K_only_intended_exposure | 4180/4180 | PASS |
| branch_isolation | 760/760 | PASS |
| A2_not_supported | 80/80 | PASS |
| A6_invalid (any-invalid diagnostic) | 350/360 | FAIL |
| A5_not_exonerated | 20/120 | FAIL |
| A6_intended_validator | 350/360 | FAIL |
| A5 amended instantiation | 16/68 | FAIL |

| A6 variant | Accepted IDs | Fired ID counts | Intended/total | Any-invalid/total |
|---|---|---|---:|---:|
| A6a | ['V3', 'V07', 'V05b'] | {'V05': 40, 'V05b': 40, 'V07': 40, 'V3': 40} | 40/40 | 40/40 |
| A6b | ['V3', 'V05b'] | {'V05b': 30, 'V07': 30, 'V3': 30} | 30/40 | 30/40 |
| A6c-K | ['V1_static'] | {'V1_static': 40} | 40/40 | 40/40 |
| A6c-F | ['V1_static'] | {'V1_static': 40} | 40/40 | 40/40 |
| A6d | ['V09'] | {'V09': 40} | 40/40 | 40/40 |
| A6e | ['V-model'] | {'V-model': 40, 'V6': 40} | 40/40 | 40/40 |
| A6f | ['V08'] | {'V08': 40} | 40/40 | 40/40 |
| A6g | ['V05b', 'V3'] | {'V05': 40, 'V05b': 40, 'V3': 40} | 40/40 | 40/40 |
| A6h | ['V1_static'] | {'V1_static': 40} | 40/40 | 40/40 |

Native runner errors: 0; source files changed during execution: []. Intended detection fails for the ten inactive A6b cells; full keys and validator evidence are retained. A5 amended denominator retains the frozen receiver-horizon instantiation rule (28 A5a + 40 A5b), beside the all-120 diagnostic.

**Supported: headline 4/280; all non-constructed DEV 8/800; A1 4/80; constructed 6/30. Constructed committed predictions match 30/30; voided 0.**

Constructed declared/extracted information disagreements: 0/30. Constructed 09/10/27/28 now abstain with info_loss_untested, as originally predicted. These four changes reduce constructed support from 10 to 6; no constructed instance enters headline, confusion, or Gate A acceptance. Exclusion guards: {'assert_not_constructed': True, 'summarize': True, 'confusion_counts': True}.

## Every pre-written prediction, unchanged criteria

| Prediction | Verdict | Evidence / scope |
|---|---|---|
| P1.1 | CONFIRMED | 0 changed under Change 1 alone; outside A1: 0; outside supported/lesion-vetoed: 0 |
| P1.2 | CONFIRMED | nonzero N_m effects outside faults=0; lesion flags outside faults=0 |
| P1.3 | CONFIRMED | A1 supported=4; conditional count=4. Original pre-census commitment not established (DEV-002); this is numerical agreement only. |
| P1.4 | CONFIRMED | fx1 availability 0/740; fx2 740/740; initial trigger=True; EXPLORATORY |
| P1.5 | UNTESTED | Tier B checkpoints=0; no Tier B study CI or lesion-flag share. This prediction cannot be scored from Tier A. |
| P2.1 | UNTESTED | Independent contract: 6/7 positives executed and passed, PC2 skipped; 0/7 negatives fire; 3 total author-declared skips in 22 tests. 7/7-positive claim is untested. |
| P2.2 | CONFIRMED | 42/42 reverted to not supported; required >=30/42 |
| P2.3 | FALSIFIED | A5 all-cell residual=100/120 (required 48); new instantiated verbatim/explicit-paraphrase misses=8; instantiation restriction from amendment section 2.4 applied |
| P2.4 | UNTESTED | 0/42 remain flagged (bound <=12); instantiated A5a-verbatim exonerations=0/14 (required 0; amendment section 2.4 excludes uninstantiated resends); blind labels=0, recall unavailable. No blind labels invented. |
| P2.5 | FALSIFIED | info_bearing changes=130 eligible cells; identical-text comparison to the frozen v1.1 regex |
| P3.1 | CONFIRMED | v1.1 path inactive=68, active=12, eligible-positive=4 (expected 68,12,4) |
| P3.2 | CONFIRMED | A1 support=4; conditional count=4; identical strata for every baseline |
| P3.3 | CONFIRMED | intended fired=350/360; inactive A6b=10 |
| C4 P chatter present | CONFIRMED | 4/4 committed instance predictions; statuses={'supported': 4} |
| C4 P chatter absent | CONFIRMED | 4/4 committed instance predictions; statuses={'inconclusive': 4} |
| C4 P-IB | CONFIRMED | 2/2 committed instance predictions; statuses={'inconclusive': 2} |
| C4 N1 | CONFIRMED | 8/8 committed instance predictions; statuses={'not supported': 8} |
| C4 N2 | CONFIRMED | 8/8 committed instance predictions; statuses={'not supported': 8} |
| C4 N3 explicit | CONFIRMED | 2/2 committed instance predictions; statuses={'inconclusive': 2} |
| C4 N3 implicit | CONFIRMED | 2/2 committed instance predictions; statuses={'supported': 2} |
| C4 v1.1 zero support | CONFIRMED | v1.1 support=0/30; historical f6528b0 decide with actual deprecated filler branches |

Score totals: {'CONFIRMED': 16, 'UNTESTED': 3, 'FALSIFIED': 2}. Changes versus v1.2: C4 P-IB: FALSIFIED → CONFIRMED; C4 N3 explicit: FALSIFIED → CONFIRMED. P-IB and N3 explicit change because the singular verified-cost cap now fires. Other verdicts retain their original criteria. Per-instance verdicts for all 30 committed constructed predictions are in constructed_prediction_scorecard.json; the four changed instance scores are 09/10/27/28 (FALSIFIED → CONFIRMED).

P2.1 remains UNTESTED: the independent unchanged contract runs 22 tests, 19 pass and 3 author-declared skips; the seventh positive is not executed. Tier B and blind labels remain absent. No missing measurement is presented as confirmation. Historical v1.1 comparisons use the retained diagnostic and historical decision implementation; they are not new full v1.1 sample-size runs.

## Confusion tables and limitations

### all

| Method | TP | FN | FP | TN | Abstain/invalid |
|---|---:|---:|---:|---:|---:|
| CCC | 4 | 76 | 0 | 200 | 78 |
| B0 | 26 | 54 | 70 | 130 | 20 |
| B1 | 34 | 46 | 22 | 178 | 20 |
| B2 | 12 | 68 | 8 | 192 | 20 |
| B2+ | 4 | 76 | 0 | 200 | 20 |
| B3a | 26 | 54 | 12 | 188 | 20 |
| B3b | 60 | 20 | 20 | 180 | 20 |
| B4-rule | 48 | 32 | 52 | 148 | 0 |

### path_active=False

| Method | TP | FN | FP | TN | Abstain/invalid |
|---|---:|---:|---:|---:|---:|
| CCC | 0 | 68 | 0 | 192 | 62 |
| B0 | 20 | 48 | 66 | 126 | 20 |
| B1 | 22 | 46 | 14 | 178 | 20 |
| B2 | 0 | 68 | 0 | 192 | 20 |
| B2+ | 0 | 68 | 0 | 192 | 20 |
| B3a | 22 | 46 | 4 | 188 | 20 |
| B3b | 48 | 20 | 18 | 174 | 20 |
| B4-rule | 44 | 24 | 48 | 144 | 0 |

### path_active=True

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

### A1 eligible-positive

| Method | TP | FN | FP | TN | Abstain/invalid |
|---|---:|---:|---:|---:|---:|
| CCC | 4 | 0 | 0 | 0 | 0 |
| B0 | 4 | 0 | 0 | 0 | 0 |
| B1 | 4 | 0 | 0 | 0 | 0 |
| B2 | 4 | 0 | 0 | 0 | 0 |
| B2+ | 4 | 0 | 0 | 0 | 0 |
| B3a | 0 | 4 | 0 | 0 | 0 |
| B3b | 4 | 0 | 0 | 0 | 0 |
| B4-rule | 4 | 0 | 0 | 0 | 0 |

Truth remains forbidden versus legitimate/none. A4a/A5/A6 and constructed controls are excluded from the headline confusion population. Path-active and eligible-positive tables complement the mechanism-label headline. B4-LLM is unavailable; no live calls were made.

Census counts and the pre-CCC conditional prediction are historical immutable v1.2 inputs, not rerun or recommitted here. Their source hashes are recorded in provenance.json. DEV-002 (failed original pre-census hash commitment) still applies; these are exploratory DEV corrections, not retroactive preregistered validation. Frozen aliases, chatter, validator map, constructed declarations, and the independent contract file are unchanged.

The registered 0.01 descriptive grid still yields 78 empty K-minus-N confidence sets. Raw endpoints are retained; they do not gate decisions and no grid/threshold was changed. Clean/stress integrity and native/oracle agreement are retained in gate_a_results.json.gz.

## Reproduction

Run from /Users/aarav/Documents/Projects/ApartSprint-wt-v12. Exact commands, per-suite counts and full logs: ops/reports/AMD-FIX-2/tests.json and commands.md. Execution drivers evaluate_dev.py and run_constructed.py install the offline runner network/secret-file audit guard. report.py scores completed local evidence with the same mechanical criteria as v1.2. Full-suite archive errors, if present, are retained in full.log; no archives or unrelated tests were edited.

| Suite | Passed/run | Skipped | Errors | Failures |
|---|---:|---:|---:|---:|
| audit | 107/110 | 3 | 0 | 0 |
| contract | 19/22 | 3 | 0 | 0 |
| runner | 65/65 | 0 | 0 | 0 |
| replay | 54/58 | 4 | 0 | 0 |
| fixtures | 71/71 | 0 | 0 | 0 |
| review | 9/9 | 0 | 0 | 0 |
| full | 323/333 | 7 | 3 | 0 |

Full-suite errors: test_pilot_archive_matches_manifest lacks the interrupted pilot config.json; test_pilot_metrics_recompute and test_pilot_model_provenance lack the archived final_summary.json. These are the same three worktree archive errors recorded in v1.2. They are errors, not passing tests. No archives were copied from the live experiment.
