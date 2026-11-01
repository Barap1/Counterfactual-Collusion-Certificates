# CCC project rules (pointer file - do not paste the spec here)

- Entry: `CCC_START_HERE.md`, then `docs/spec/00_control_plane.md`. Load other `docs/spec/NN_*.md` modules only when your task names them. Never load `CCC_MASTER_SPEC.md` or `docs/research/*` whole.
- State: `ops/STATUS.md` (one screen), `ops/tasks.json` (registry/leases), `ops/RESUME.md` (restart packet), `ops/DECISIONS.md`, `ops/CLAIMS.md`. Detailed reports go in `ops/reports/`.
- $0 new spend. Only the INF-001 inference controller may make model calls; follow `ops/resource_policy.local.json` and log in `ops/budget_ledger.jsonl`. No paid fallbacks, no `openrouter/free` alias.
- Never print or commit `.env`, `compute.env`, `ops/*.local.json`, tokens or auth headers.
- Pilot (seed 1) is development data only; archived read-only under `results/baselines/` with hashes in `ops/pilot_manifest.sha256`. Never overwrite it.
- Delegation: max 3 worker layers, 6 live delegated agents total (Claude + Codex), check `ops/tasks.json` before spawning. Codex bridge: see `ops/reports/BOOT-001.md` §Delegation.
- Git: no push, force, reset --hard, or broad clean without owner approval; integration custodian is the sole merger. End commits with the repo's attribution line.
- Handoffs: ≤300 words (leaf) / ≤500 (lead), with Task / Status / Artifacts / Validation / Limitations / Budget / Next.
