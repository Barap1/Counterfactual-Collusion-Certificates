# Disclosed label correction (D-034 / REV-001 F-1)

The original docs/analysis/exp002_heldout and all collection artifacts were preserved.
No estimator, numeric value, threshold, statistical test, seed, ordering, or data selection changed.
Delta_total and S1–S3 are confirmatory when the preregistered floors pass in holdout, with tier A-confirmatory.
Delta_total is supported only when bootstrap L > 0 AND exact one-sided sign-flip p <= 0.05; otherwise not supported.
The held-out result is not supported. Delta_conditional remains descriptive; Tier-B case certificates remain exploratory.
General table labels now describe this distinction without attributing study exploratory status to DEV-001.
The existing claim candidate's identifier, text, scope and tier, and aggregate limitation wording reflect the corrected labels/decision.

Every original output file was compared below. Every numeric field is byte-identical in its serialized representation
(JSON numeric tokens compared as literal strings; CSV numeric cells compared verbatim, including nested cells).
No original output file was omitted. Detailed old/new field values: output_diff.json.
The sole non-label/decision differences are the mandatory aggregate.json code_hashes for study.py and pipeline.py.
These truthfully identify the edited source; therefore the literal request that *only* label/decision fields differ
cannot hold for source provenance hashes. No hashes were falsified or copied from the old analysis.

## Per-file comparison
- `aggregate.json`: 0, label, pipeline.py, study.py.
- `attempts.csv`: label.
- `attempts.json`: label.
- `checkpoint_certificates.csv`: label.
- `checkpoint_certificates.json`: label.
- `claims_candidates.jsonl`: claim_id, scope, text, tier.
- `continuations.csv`: label.
- `continuations.json`: label.
- `cost_throughput.csv`: label.
- `cost_throughput.json`: label.
- `coverage.csv`: label.
- `coverage.json`: label.
- `effects_study.csv`: confirmatory, decision, inference_tier, label, tier.
- `effects_study.json`: confirmatory, decision, inference_tier, label, tier.
- `events_accounting.csv`: label.
- `events_accounting.json`: label.
- `figure_data/fig_delta_by_world.csv`: label.
- `figure_data/fig_delta_by_world.json`: label.
- `figure_data/fig_missingness.csv`: label.
- `figure_data/fig_missingness.json`: label.
- `figure_data/fig_sham_noise.csv`: label.
- `figure_data/fig_sham_noise.json`: label.
- `figure_data/fig_status_stack.csv`: label.
- `figure_data/fig_status_stack.json`: label.
- `figure_data/fig_tau_vector.csv`: label.
- `figure_data/fig_tau_vector.json`: label.
- `missingness.csv`: label.
- `missingness.json`: label.
- `scheduled_statuses.csv`: label.
- `scheduled_statuses.json`: label.
- `sensitivity.csv`: label.
- `sensitivity.json`: label.
- `status_crosscheck.csv`: byte-identical.
- `status_crosscheck.json`: byte-identical.
- `validation_report.json`: label.
- `validity_checks.csv`: label.
- `validity_checks.json`: label.
- `world_effects.csv`: label.
- `world_effects.json`: label.

## Commands and validation
- `starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.analysis run --input docs/runner/exp002-live --watchdog-dir docs/runner/exp002-live.watchdog --out docs/analysis/exp002_heldout_v2` (exit 0).
- `PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest discover -s tests/analysis -t .`
- Comparison: `starter/collusion_hackathon/colosseum/.venv/bin/python docs/analysis/exp002_heldout_v2/verify_correction.py` (all assertions passed).
- Initial unguarded unittest discovery exposed an obsolete exploratory-label assertion and the suite's required network-guard expectation; the label assertion was corrected and the suite rerun with its offline guard.
Guarded suite result: 57 tests run, OK (1 guard-required skip of the real manifest contract test).
No live/model calls or commits. Owner remains sole author.
