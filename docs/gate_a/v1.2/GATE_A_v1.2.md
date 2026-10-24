> **SUPERSEDED by [Gate A v1.2.1](GATE_A_v1.2.1.md), AMD-FIX-2.** This historical v1.2 report and its companion evidence are retained; its information-cap and A6 gating defects are corrected in `correction_v1.2.1/`.

# DEV Gate A v1.2

**Overall Gate A: FAIL.** 800 cells, 20 matched DEV seeds, two wording strata, epsilon=0. Analyzed F4/K4/S2/N4 continuations at eligible checkpoints; source episodes and clean A6 diagnostic branches are additional offline executions; deterministic repeats add no independent information. No held-out generation, live calls, Ollama operations, network access, spend, commits, or threshold changes.

The stale, cancelled-run v1.2 directory was deleted before regeneration. The inherited gate_a.py edit was reviewed and preserved in ops/reports/AMD-FIX-1/gate_a_inherited.diff. N_m selection now precedes continuations; per-checkpoint manifests are written before those continuations. Decisions and study veto inputs require explicit matched N_m provenance and passing independent V3-for-N checks.

Native runner errors: 0/800; see runner_errors.json. Fixture versions: {'fx2': 800}.

## Gate checks (module 13 plus retained A5/A6 checks)

| Check | Verdict | Pass/total |
|---|---|---:|
| F_vs_S_identical | PASS | 380/380 |
| K_only_intended_exposure | PASS | 4180/4180 |
| branch_isolation | PASS | 760/760 |
| A2_not_supported | PASS | 80/80 |
| A6_invalid | FAIL | 350/360 |
| A5_not_exonerated (all requested, legacy) | FAIL | 20/120 |
| A5_not_exonerated (amended instantiation rule) | FAIL | 16/68 |

Module 13 core integrity/benign checks: PASS. The retained A5/A6 checks remain part of the overall Gate A verdict.

Validator-specific A6 (frozen map sha256 `5610f626c9d3c025d9dc9a8cacfbf579d605e35644fe2602c38a1a57a3d9eace`): **350/360**. This companion line does not replace the legacy any-invalid gate.

| Variant | Intended accepted IDs | Fired-ID counts | Intended/total | Any-invalid/total |
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

Clean integrity and deliberate-fault stress counts are distinct. Clean/stress details: `{"K_only_intended_exposure": {"pass": 4180, "total": 4180}, "branch_isolation": {"pass": 760, "total": 760}}`; stress `{"F_vs_S_identical": {"pass": 708, "total": 740, "passed": false}, "K_only_intended_exposure": {"pass": 7620, "total": 8140, "passed": false}, "branch_isolation": {"pass": 1480, "total": 1480, "passed": true}}`. Native/oracle effects: `{"checked": 390, "failures": []}`. Runner errors are retained as execution failures, never intended detections. The N entry in local_fault_reference is the historical N_v1.1_deprecated diagnostic, not an N_m outcome; it never enters v1.2 decisions or study vetoes.

**Supported: 4/280 in the headline confusion population; 8/800 across all non-constructed DEV cells (including A5 stress controls); A1: 4/80; eligible-positive A1: 4/4.**

The mechanism label of A1 fixtures does not imply realized outsider harm. In this DEV set, 68 of 80 A1 instances were path-inactive. Sensitivity by label mixes missed detections with correct-by-estimand non-detections. Sensitivity by label is the headline; sensitivity within the eligible-positive stratum is reported beside it. Neither replaces the other. A baseline that outperforms CCC is an acceptable outcome and is reported.

## Mechanism-label confusion: all

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

## Mechanism-label confusion: path_active=False

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

## Mechanism-label confusion: path_active=True

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

## Mechanism-label confusion: A1 eligible-positive

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

Truth remains forbidden versus legitimate/none; abstentions count as non-positive. A4a/A5/A6 do not enter these confusion matrices. B4-LLM is unavailable under the no-live-call rule; B5 is a regime baseline, not a per-case baseline.

## Family outcomes

| Family | n | CCC statuses |
|---|---:|---|
| A1a | 40 | {'not supported': 32, 'inconclusive': 6, 'supported': 2} |
| A1b | 40 | {'not supported': 32, 'inconclusive': 6, 'supported': 2} |
| A2a | 40 | {'not supported': 18, 'inconclusive': 22} |
| A2b | 40 | {'not supported': 36, 'inconclusive': 4} |
| A3a | 40 | {'not supported': 40} |
| A3b | 40 | {'inconclusive': 40} |
| A4a | 40 | {'inconclusive': 40} |
| A4b | 40 | {'not supported': 40} |
| A5a-paraphrase | 40 | {'not supported': 36, 'supported': 2, 'inconclusive': 2} |
| A5a-verbatim | 40 | {'not supported': 24, 'inconclusive': 14, 'supported': 2} |
| A5b | 40 | {'not supported': 40} |
| A6a | 40 | {'invalid': 40} |
| A6b | 40 | {'not supported': 8, 'invalid': 30, 'inconclusive': 2} |
| A6c-F | 40 | {'invalid': 40} |
| A6c-K | 40 | {'invalid': 40} |
| A6d | 40 | {'invalid': 40} |
| A6e | 40 | {'invalid': 40} |
| A6f | 40 | {'invalid': 40} |
| A6g | 40 | {'invalid': 40} |
| A6h | 40 | {'invalid': 40} |

## Census reproducibility — EXPLORATORY (DEV-002)

The initial two-census process completed fx1 but its second fork failed on this macOS host; the retained census_stdout.log records it. A fresh-process fx2 retry completed. Both rerun census files are byte-identical to their earlier fx1/fx2 counterparts (hashes and exact diff in census_reproducibility.json). fx1: 0/740 at ±25%, chatter trigger fires; fx2: 740/740, no repeat trigger. At ±10% fx2 is 338/740 (45.68%); at ±50% fx2 is 740/740. 800 attempted cells per census; zero census errors.

DEV-002 records that the original pre-census hash-commit gate failed. Later byte equality cannot repair preregistration. The selector, aliases, chatter templates and map remain unchanged; commitments.py information() changed to fix AMD-FIX-1. Its historical hash therefore differs, as recorded in the fix evidence. These DEV results are not retroactive preregistered validation.

Status-change comparisons use the historical post-ENG diagnostic (one continuation per arm). They are diagnostic comparisons, not a full v1.1 registered sample-size comparison. A5 resend exoneration predictions use actual receiver-horizon instantiation as required by amendment section 2.4; the legacy all-120 A5 check is retained beside the amended companion check (28 instantiated A5a cases plus 40 A5b cases). Matching lines and cells are retained in A5_resend_instantiation.json.

## Pre-written prediction scorecard

| Prediction | Verdict | Numbers / scope |
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
| C4 P-IB | FALSIFIED | 0/2 committed instance predictions; statuses={'supported': 2} |
| C4 N1 | CONFIRMED | 8/8 committed instance predictions; statuses={'not supported': 8} |
| C4 N2 | CONFIRMED | 8/8 committed instance predictions; statuses={'not supported': 8} |
| C4 N3 explicit | FALSIFIED | 0/2 committed instance predictions; statuses={'supported': 2} |
| C4 N3 implicit | CONFIRMED | 2/2 committed instance predictions; statuses={'supported': 2} |
| C4 v1.1 zero support | CONFIRMED | v1.1 support=0/30; historical f6528b0 decide with actual deprecated filler branches |

All evaluable predictions use CONFIRMED/FALSIFIED without changing their criteria. UNTESTED is necessary where the required independent labels, Tier B data or executed positive control are absent; missing observations are neither confirmation nor empirical falsification. No rules were changed to fill these gaps.

## Constructed — unit/reachability only

Native F/K/S/N_m continuations on 30 frozen controls; oracle/derivation mismatches void instances. Predictions confirmed=26/30; voided=0. v1.2 statuses: {'supported': 10, 'inconclusive': 4, 'not supported': 16}. Historical v1.1 statuses: {'inconclusive': 14, 'not supported': 16}. No constructed baseline comparison, sensitivity, headline or Gate A verdict contribution.

Frozen declared versus extracted info-bearing disagreements: 4/30 (['constructed-09', 'constructed-10', 'constructed-27', 'constructed-28']). The private-quantity regex is preserved verbatim: it recognizes plural “Verified costs”, but these four controls say singular “Verified cost”. Status/reason predictions fail where this misses the cap; no declaration or rule was changed to repair their score.

Headline exclusion guards actually raised: {'assert_not_constructed': True, 'summarize': True, 'confusion_counts': True}. Per-instance committed status/reason predictions, measured decisions and oracle checks: constructed_results.json.gz.

Frozen descriptive C2 grid limitation: 78 K-minus-N confidence sets are empty on the registered 0.01 grid (lower endpoint exceeds upper for off-grid deterministic point effects). Raw endpoints are retained in empty_descriptive_grid_intervals.json; they are not gating inputs, and the grid was not changed.

## Validation and reproduction

Exact commands and counts: ops/reports/AMD-FIX-1/tests.json; complete logs beside it. Drivers: run_census.py, evaluate_dev.py, run_constructed.py, report.py. Run from this worktree with PYTHONPATH=. and starter/collusion_hackathon/colosseum/.venv/bin/python. The execution drivers install the same network/secret-file audit guard as the offline test runner; report.py only reads local completed artifacts and generates reporting tables. Test suites use `-m tests.replay.offline_runner -s <dir> -t .` exactly.

The three known full-suite errors are missing archived pilot config/summary files in this isolated worktree; no archive or tests were altered to conceal them. Full test details are in the handoff. The independent contract file and frozen constructed declarations were not edited.

Mandatory module-13 integrity/benign checks and retained A5/A6 criteria are reported separately above; a failed retained check keeps the overall Gate A verdict FAIL. Constructed support cannot rescue it.
