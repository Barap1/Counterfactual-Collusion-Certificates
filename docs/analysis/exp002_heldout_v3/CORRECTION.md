# Disclosed validity metadata correction — FIX-001 / REV001 F-5

Evidence category: **original-confirmatory** for the unchanged registered study result;
**post-hoc-exploratory** for this disclosed metadata repair and Tier-B certificate review.
All original v1/v2 analysis and collection artifacts remain untouched. No estimate,
interval algorithm, sample, seed, order, threshold, primary statistic, or status rule changed.
Only ccc/analysis/loaders.py changed in production. pipeline.py, status.py,
study.py, and ccc/audit/decision.py were not edited by FIX-001.

## Root cause confirmed

REV001's failure-only loop is in the legacy DEV adapter: it discarded pass records.
The actual held-out path calls runner_input.adapt, which already collects pass records
but retains engine IDs. For example, raw checkpoint restore_validation has V01/V02/V06/V6;
branch results have V3/V08/V09/V07/V05b/V-model. The pipeline asks for V1–V7, leaving
V1, V2, V4, V5, and V7 unestablished despite successful recorded checks. Its all_valid
condition therefore failed on every certificate.

The loader now keeps positive evidence in legacy inputs and adds canonical protocol
keys to runner-adapted metadata. The mapping follows the existing engine/check names
and protocol-to-engine mapping in ccc/audit/gate_a.py: V01→V1, V02→V2,
V05/V05b→V3, V09→V4 (fresh continuation), V08→V5 (tool syntax),
V06/V-model→V6, V07→V7. Engine V08/V09 are not the statistical batch V8/V9 gates.
Raw keys are retained; not_applicable is normalized to na. Failures dominate passes;
unknown or absent evidence cannot establish a canonical pass. No unrecorded success
is inferred. This does not reconstruct missing info_bearing evidence, which remains
conservatively true.

Raw archive verification streamed tar members in memory, without extraction. The
existing docs/runner/exp002-live tree plus sidecars matches all **15,728 regular files**
from the archive; **16,471 AppleDouble metadata members** were excluded. Raw branch
records are **143 valid executed / 56 not_run**, with no failed executed check.
See docs/enh/fix/raw_verification.json and check_archive.py. The requested external
extraction path was outside sandbox writable roots; no extraction was needed or done.

## Certificate and numeric consequences

**No certificate STATUS changed.** Counts remain **0 supported / 11 not_supported /
5 inconclusive**. All 16 certificates change gates.all_valid from false to true.
The five inconclusive certificates lose only validity_unestablished; other reasons
are unchanged. None becomes not_supported or supported.

The original-confirmatory primary remains Delta=1.354325711018898,
95% world-cluster interval [-0.01954964911635066, 2.8336288730243204],
one-sided exact sign-flip p=0.0703125, n=8 matched world pairs, decision **not supported**.
These are preserved original values, not new evidence. All estimates, p-values,
intervals, L/U bounds, thresholds, counts in existing records, and sensitivity
outputs retain their literal numeric serialization.

The verifier checks every field of every generated JSON/JSONL and every CSV cell
across all 39 outputs. It matches added validity rows by checkpoint/regime/check,
reports every addition and changed field, checks literal numeric tokens rather than
floating-point equality, and stops on any numeric or unexpected scientific change.
Scalar CSV numeric cells remain byte-identical; nested JSON cells also receive
literal numeric-token comparisons. It reports 33,292 unchanged numeric tokens and
222 changed fields/records across the JSON and CSV versions. Detailed old/new values
and baseline output hashes are in output_diff_v3.json. The other 34 output files are
byte-identical.

Two provenance hash fields also differ: loaders.py reflects this repair; study.py
already differs from v2's recorded hash and matches the current unchanged HEAD source.
FIX-001 did not edit study.py. This pre-existing provenance difference is disclosed
rather than replacing the rerun's truthful source hash. See docs/enh/fix/provenance.json.
All effects_study outputs are byte-identical despite that provenance difference.

## REV001 F-10 assessment — unchanged

status.py appends no_placebo_available whenever execution reaches its final
inconclusive reason-building path and placebo_available is false. It does not first
require the other support conditions to hold. The earlier invalid, ineligible,
insufficient-continuations, supported, and not_supported returns bypass this append;
therefore “unconditional” means unconditional within that final inconclusive path.
In v3 the reason appears on H02_B1, H07_B1, and H07_B2, each also imprecise and
pattern_ambiguous. It truthfully reports missing placebo but can overstate its role
as the reason support was withheld. Restricting the causal reason label or separating
availability metadata is left to the director. No F-10 code or reason was changed.

## Validation and reproduction

Independent regression tests were written before production changes. The initial
six tests failed on the original loader (seven assertion failures across subtests).
Final regression coverage additionally checks unknown evidence and not_applicable.
All **8 regression tests pass**. Full offline suite: **415 tests in 116.383s, OK
(skipped=4)**. Final test results are recorded in docs/enh/fix/regression_after.log and tests.log.
The full offline discovery uses the existing release network/secret guards, with
only the persistent test coverage artifact redirected into owned evidence space.
See docs/enh/fix/COMMANDS.md for exact commands, the earlier guard refusal, wrapper
purpose, and evidence paths. No network or experiment/model calls; $0 new spend.

## Every output file

- `aggregate.json`: 2 changed fields/records.
- `attempts.csv`: byte-identical.
- `attempts.json`: byte-identical.
- `checkpoint_certificates.csv`: 21 changed fields/records.
- `checkpoint_certificates.json`: 21 changed fields/records.
- `claims_candidates.jsonl`: byte-identical.
- `continuations.csv`: byte-identical.
- `continuations.json`: byte-identical.
- `cost_throughput.csv`: byte-identical.
- `cost_throughput.json`: byte-identical.
- `coverage.csv`: byte-identical.
- `coverage.json`: byte-identical.
- `effects_study.csv`: byte-identical.
- `effects_study.json`: byte-identical.
- `events_accounting.csv`: byte-identical.
- `events_accounting.json`: byte-identical.
- `figure_data/fig_delta_by_world.csv`: byte-identical.
- `figure_data/fig_delta_by_world.json`: byte-identical.
- `figure_data/fig_missingness.csv`: byte-identical.
- `figure_data/fig_missingness.json`: byte-identical.
- `figure_data/fig_sham_noise.csv`: byte-identical.
- `figure_data/fig_sham_noise.json`: byte-identical.
- `figure_data/fig_status_stack.csv`: byte-identical.
- `figure_data/fig_status_stack.json`: byte-identical.
- `figure_data/fig_tau_vector.csv`: byte-identical.
- `figure_data/fig_tau_vector.json`: byte-identical.
- `missingness.csv`: byte-identical.
- `missingness.json`: byte-identical.
- `scheduled_statuses.csv`: byte-identical.
- `scheduled_statuses.json`: byte-identical.
- `sensitivity.csv`: byte-identical.
- `sensitivity.json`: byte-identical.
- `status_crosscheck.csv`: byte-identical.
- `status_crosscheck.json`: byte-identical.
- `validation_report.json`: byte-identical.
- `validity_checks.csv`: 89 changed fields/records.
- `validity_checks.json`: 89 changed fields/records.
- `world_effects.csv`: byte-identical.
- `world_effects.json`: byte-identical.
