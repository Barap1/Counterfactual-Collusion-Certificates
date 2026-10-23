# RESUME packet (read in one pass)

- Repo `/Users/aarav/Documents/Projects/ApartSprint`, branch main, start commit 097619b. No push has happened (owner approval required).
- Control files: `ops/STATUS.md`, `ops/tasks.json` (registry + gates + policy), `ops/DECISIONS.md`, `ops/CLAIMS.md`, `ops/budget_ledger.jsonl`. Local only: `ops/environment.local.json` and `ops/resource_policy.local.json`.
- Pilot: archived read-only at `results/baselines/`. Hashes are in `ops/pilot_manifest.sha256`. Metric audit: `ops/reports/pilot_metric_audit.md`. Development data only.
- Offline test: `sandbox-exec -p '(version 1)(allow default)(deny network-outbound (remote ip))' starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest discover -s tests -t . -v` (expected 4 OK).
- Codex delegation: `node ~/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/codex-companion.mjs task --write --effort <lvl> [--model gpt-6.1-sol|gpt-6-luna|gpt-6-astra|...] "<prompt>"`. It counts toward the 6-agent cap.
- In flight: SCI-001 (read-only, director-owned). BOOT-001 has no live children.
- Next executable action: launch ENG-001 with modules 07 and 15 plus `ccc/adapters/colosseum.py`. Acceptance: exact hooks and inaccessible state documented.
- Open owner items: Modal $0 net-spend limit and credits; Codex account confirmation; session restart for settings.
