# BOOT-001: Environment and delegation bootstrap report

Task: BOOT-001 · Status: READY_FOR_REVIEW · Date: 2026-10-23 (UTC ~16:03–16:30)
Inputs: docs/spec modules 00, 02, 03, 08, 09, 14, plus the module 13 dependency table only.
Lock: `ops/locks/BOOT-001.lock`

## Verdict

| Field | Value | Evidence / reason |
|---|---|---|
| offline_ready | **true** | Starter preflight exit 0 under a network-denied `sandbox-exec` (`ops/reports/preflight_offline.log`). CCC offline tests 4/4 OK, also network-denied (`ops/reports/offline_tests.log`) |
| free_api_ready | **conditional** | OpenRouter `/key`: free tier, usage 0, key limit $0.01. `cohere/north-mini-code:free` is listed at $0 prompt/completion with tools. Daily quota unverified. Live use only via INF-001 |
| local_inference_ready | **false (pending INF-001)** | Ollama 0.32.5 installed, server not running. gemma4:latest (5.49 GB) and gemma4:26b (17.99 GB) are on disk. Tool loop untested |
| modal_ready | **false (blocked on owner)** | Profile/workspace `barap1`. This month: $0.00 metered, $0.00 billed. Only app is the stopped `getting-started`. The CLI does not expose the credit balance or the net-spend limit |
| drive_sync_ready | **unverified** | The Google Drive MCP tools are listed in the session but were not exercised. Module 12 is outside BOOT inputs, so this is deferred to PUB-001 |
| nested_claude_ready | **true (depth 3 verified)** | Director → BOOT-001 → NEST-A → NEST-B. See `ops/reports/delegation_check/` |
| codex_bridge_ready | **true; nested_codex_supported: true** | The companion `task` route wrote a nonce file. A native Codex subagent `/root/hash_check` returned the correct sha256 |

## A. Workspace and pilot

- Root `/Users/aarav/Documents/Projects/ApartSprint`, branch `main` tracking `origin/main`. Remote `Barap1/Counterfactual-Collusion-Certificates`, PRIVATE (gh account Barap1, ADMIN). Git author `Aarav Patel <aarav.patel.1@icloud.com>` was left unchanged.
- `project_start_commit = 097619b24a748b543d332eb010f25d9081f5bb72`. The only tracked file at start was `README.md`. Git history contains no key-like strings (`git log --all -p | grep -c` returned 0).
- Starter is at `d585a7b3be50366cc2bdf5789bf8add5890b2abd`, the same as the reviewed upstream, with 0 tracked modifications. Local additions are ignored only: venvs, outputs, logs, compute.env.
- Pilot: 27 files across two batches, hashed in `ops/pilot_manifest.sha256` (sha256 of the manifest is `2b99fa29…013310`).
  - Archived read-only (`chmod a-w`) at `results/baselines/colosseum_positive_control_seed1/` (complete run) and `…_interrupted/` (20261023-111229, `status: running`, 0 completed runs).
  - The archive is hash-identical to the source. No prior copy existed.
- All 16 module 02 values re-read from the files match.
  - Corrections are in `ops/reports/pilot_metric_audit.md`: coverage = 3/min(4,8), and normalized_score is an artefact of optimal_cost=0.
  - The batch config requested `Qwen/Qwen2.5-7B-Instruct`, but the run recorded `cohere/north-mini-code:free`.
- The research report is present at `docs/research/CCC_Updated_Deep_Research_Report.md`. It was not read.
- `.gitignore` now additionally covers `*.local.json`, `results/baselines/`, `results/raw/`, model weights, `.venv/`, `__pycache__/`, and `.DS_Store`. Verified with `git check-ignore`.

## B. Inventory (versions)

- Tools: Python 3.14.7 (miniforge and both starter venvs) · uv 0.12.13 · git 2.55.0 · gh 2.100.0 · node 24.18.0 · Claude Code 2.1.309 · codex-cli 0.163.0 · codex plugin 1.0.6 · modal 1.6.2 · Docker 29.7.2 (daemon up, 0 running containers) · Ollama 0.32.5.
- Machine: Apple M5 Pro, 48 GiB, macOS 27.0. 555 Gi of 926 Gi disk free. 65% memory free at the time of the check.
- Colosseum venv: terrarium-agents 0.1.1, openai SDK 2.21.0, five environments (Hospital, JiraTicket, MeetingScheduling, PersonalAssistant, SmartGrid). Nothing was installed, upgraded, or downgraded.

## C. Credentials and routing (names and presence only)

- `.env` (mode 0600) holds `OPENROUTER_API_KEY` (sk-or- format), `OPENROUTER_BASE_URL` (openrouter.ai/api/v1), and `OPENROUTER_MODEL=openrouter/free`.
- `starter/compute.env` holds `NEBIUS_API_KEY` (empty) and `OPENROUTER_API_KEY` (the same key, compared by hash). **Its mode was 0644; it is now 0600.**
- Session process env exports the `OPENROUTER_*` names and an **empty `NEBIUS_API_KEY`**. `LLM_MODEL`, `LLM_BASE_URL`, and `LLM_API_KEY` are unset. No stale override exists now.
- Effective starter routing from `llm_config`: endpoint_kind=openrouter, base_url=https://openrouter.ai/api/v1, using the compute.env file.
- Risks (all recorded in DECISIONS):
  1. `llm_config._load()` never overrides an existing env var, so the exported empty NEBIUS_API_KEY would mask a Nebius key later added to compute.env.
  2. `OPENROUTER_MODEL=openrouter/free` violates the pin-a-model rule. The starter does not read it.
  3. Experiments must run with a controlled subprocess env (INF-001).
- No `.env.example` was created because `compute.env.example` already exists upstream.

## D. Delegation

- **Claude nesting** works with real artifacts at depth 3. The installed binary contains `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` and `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`. I created the project `.claude/settings.json` with values 3 and 6 (no prior file existed; nothing was overwritten). **It takes effect only in a new Claude Code session.**
- **Codex bridge.**
  - The plugin `codex@openai-codex` 1.0.6 is installed at local scope for `/Users/aarav` and is not enabled for this project. The `codex:codex-rescue` agent type is therefore absent in this session.
  - Working invocation (verified, exit 0, 23.8 s):
    `node ~/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/codex-companion.mjs task [--write] [--effort low|medium|high] [--model <slug>] "<prompt>"`
    Other subcommands: `status`, `result`, `cancel [job-id]`, `review`, `adversarial-review`, `setup --json`.
  - `setup --json` reports ready: ChatGPT login (subscription, not an API key) and verified auth. **The logged-in ChatGPT account email does not match the owner's Claude/git emails. The owner should confirm it is their approved plan.**
  - Model slugs come from `~/.codex/models_cache.json`. Listed: gpt-6.1-sol (config default), gpt-6-astra, gpt-6-sol, gpt-6-luna, gpt-5.6-sol, gpt-5.6-terra, gpt-5.6-luna. Hidden: gpt-reserve, codex-auto-review. The plugin's `spark → gpt-5.3-codex-spark` alias is **not** in this account's catalog.
  - Codex `multi_agent` feature: stable and enabled. Native subagent verified.
  - Codex threads and subagents are invisible to the Claude concurrency env cap, so the director must count them in `ops/tasks.json`.
- Not tested: cancellation of either runtime, and the effective Codex model of the test run (not echoed by the companion).
- Live children of BOOT-001: both completed and collected. None remain.

## E. Spending barrier

- `ops/resource_policy.local.json` is gitignored. It sets $0 cap, allows only cohere/north-mini-code:free, bans `openrouter/free`, allows 1 in flight, halts on any positive cost, keeps Modal BLOCKED, binds local inference to 127.0.0.1, and never sends the OpenRouter key to a local endpoint.
- Ledger: `ops/budget_ledger.jsonl`, 5 entries, all $0 out-of-pocket. No inference was run against any experimental backend. Development usage came from subscriptions: 1 Codex thread and 2 Claude haiku subagents.

## F. Offline package and tests

- Package: `ccc/__init__.py`, `ccc/paths.py`, `ccc/adapters/colosseum.py`. Import-only; no client construction.
- Tests: `tests/test_offline_adapter.py`, 4 tests. They cover environment import with a socket-connect guard, archive vs. manifest hashes, the metric recompute, and model provenance.
- Command (repo root):
  `sandbox-exec -p '(version 1)(allow default)(deny network-outbound (remote ip))' starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest discover -s tests -t . -v`
  Exit 0, 4 tests OK. A control test confirms `urlopen` is blocked under that profile.
- Not done (outside BOOT inputs): `submission/paper_outline.md` and the author checklist need module 12 and template checks. Handed to PUB-001 or the director.

## G. Owner actions (blocking only the named backend)

1. Modal dashboard: set the workspace **net spend limit to $0** and report the remaining promotional credit and its expiry.
2. Confirm that the ChatGPT account logged into Codex is the approved subscription for this project.
3. Optional: remove `OPENROUTER_MODEL=openrouter/free` and the empty `NEBIUS_API_KEY` export from whatever launches the session. Optional: enable the codex plugin for this project via `/plugin`.
4. Restart Claude Code in the project so `.claude/settings.json` (depth 3 / concurrency 6) applies.
