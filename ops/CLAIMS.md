# Claim-to-evidence index

| ID | Claim | Status | Evidence |
|---|---|---|---|
| C-P01 | Seed-1 positive-control pilot completed with the 16 values in module 02 | machine-verified (values match) | `results/baselines/colosseum_positive_control_seed1/.../summary.json`, `final_summary.json`; `ops/pilot_manifest.sha256` |
| C-P02 | Pilot `coverage` = tasks_done / min(n_agents, n_tasks) = 3/4 (not 3 of 8 tasks) | machine-verified | `ops/reports/pilot_metric_audit.md`; `tests/test_offline_adapter.py::test_pilot_metrics_recompute` |
| C-P03 | Pilot `total_cost` (22.27) is task-cost units, not API dollars | verified in code | installed `envs/dcops/jira_ticket/jira_ticket_env.py` |
| C-P04 | Pilot shows causal collusion | **REJECTED** (pilot is prompted positive control, development data only) | module 02 |
| C-P05 | Pilot model was GPT-4o-mini | **REJECTED** (stale label; recorded model cohere/north-mini-code:free) | `run_config.json` |
