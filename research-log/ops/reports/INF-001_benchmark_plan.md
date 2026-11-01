# INF-001 bounded backend benchmark plan (proposal from BOOT-001; nothing run yet)

Owner: the inference controller, the sole process allowed to make model calls. Gate: GATE-A passed. Policy: `ops/resource_policy.local.json`.

1. **Local first (Ollama 0.32.5, already installed).** Start one server bound to 127.0.0.1:11434 with a placeholder key. Candidates already on disk: `gemma4:latest` (5.49 GB) and `gemma4:26b` (17.99 GB, under the 30 GB memory policy). Confirm the license and tool-schema support with `ollama show`, and record the blob digests from `ops/environment.local.json`. Tests: 20 tool round trips (single and sequential calls, JSON-argument validity, tool-result follow-up), a realistic Colosseum prompt length (pilot `agent_prompts.json` ~115 KB per run), then one short JiraTicket scenario. Record malformed/empty rate, p50/p95 latency, memory pressure, and context truncation. New spend: $0.
2. **OpenRouter (limited external check).** Model `cohere/north-mini-code:free` only. Re-check catalog pricing = 0 immediately before use. Allow 1 in flight and at most 10 requests total, and log every call in `ops/budget_ledger.jsonl`. Halt on any positive `usage.cost`. The key has a $0.01 credit limit and free tier, and the daily quota is unverified (docs say 50/day).
3. **Modal: blocked** until the owner confirms the $0 net-spend limit and credit balance. If it is unblocked later: a short-lived function with pinned weights, a hard timeout, an authenticated endpoint, teardown verification, and a ledger reservation before launch.

Output: the module 09 comparison table in `ops/reports/INF-001.md`.
