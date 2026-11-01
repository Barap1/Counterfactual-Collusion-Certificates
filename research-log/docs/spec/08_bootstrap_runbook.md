# 08 - BOOT-001: first delegated environment task

**Owner:** Environment/Bootstrap Lead.  
**Goal:** turn the already working setup into a safe, reproducible research workspace without breaking it.  
**Non-goal:** install all starter projects, upgrade everything, run the whole experiment matrix, or build the final UI.

## A. Establish and preserve the workspace

Resolve the existing directory `~/Documents/Projects/ApartSprint`. Confirm the Git root, current branch, remote, user identity, tracked files, and dirty state. Record the initial project commit as `project_start_commit`. Inspect but do not reset or stash owner changes without permission.

Locate the upstream checkout, research report, completed pilot, and any previous copy of the pilot. Record the upstream SHA and a safe diff summary. Protect the raw baseline with hashes and an immutable archive location. An absent report is a nonblocking documentation issue if the current spec is present; an absent full pilot must be reported rather than reconstructed from the summary row.

Check `.gitignore` against `.env`, `compute.env`, local runtime manifests, model weights, raw private traces, and the nested starter checkout. Also check whether sensitive files are already tracked. Ignoring a previously committed secret does not remove it from history; report and rotate an exposed credential through the owner rather than claiming the issue is solved.

## B. Inventory, do not reinstall blindly

Record versions and paths for Python, uv, Git, GitHub CLI, Claude Code, Codex, the bridge/plugin, Modal, Docker, and Ollama if present. Inspect available disk, memory pressure, and active model/GPU jobs. Do not require Ollama merely because it is allowed. Do not stop unrelated Docker containers or alter system-wide Python.

Confirm the installed Colosseum dependencies in their existing virtual environment. Run the offline preflight only; the already observed free tool call does not need to be repeated reflexively. Lock or record the dependency environment used for the pilot. New CCC package dependencies should be minimal and compatible with the working adapter.

Do not downgrade Python 3.14.7 to a README example version without a demonstrated incompatibility. If a dependency demands another version, create a separate environment and document the migration. Never silently invalidate the archived baseline environment.

## C. Credential and routing audit

Verify that the starter can read its root `compute.env`. Check variable names and whether nonempty values exist, not their values in logs. Existing process environment variables can override file-loaded settings; inspect the effective endpoint/model routing safely. [S11](https://github.com/poseidon-research/collusion_hackathon/blob/d585a7b3be50366cc2bdf5789bf8add5890b2abd/util/poseidon_compute/llm_config.py)

Identify stale `LLM_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY`, or `NEBIUS_API_KEY` overrides. Do not delete owner credentials. Use a controlled subprocess environment for experiment invocations so an old export cannot silently reroute a batch.

Create a credential-free `.env.example` only if needed. Do not duplicate real keys across many worktrees. The inference controller receives necessary credentials by approved environment inheritance or secret store; research, visualization, and writing workers do not need them.

Confirm subscriptions are used for development-agent authentication. Detect a configured separately billed API mode and mark it unapproved until the owner authorizes spending. Never print auth configuration or tokens to demonstrate success.

## D. Verify delegation and configure lean operation

Inspect the installed Claude/Codex integration and official/local instructions. Test one real child and a nested verifier on a harmless artifact. Record task IDs, effective models where exposed, depth support, cancellation behavior, and result collection. Do not fabricate a successful nesting check because a model wrote "done."

Establish the module routing, concise project rules, task registry, file ownership, and global six-agent policy. Apply supported project-local settings by merging, not replacing. Prepare a read-only reviewer role and an integration role. Do not give every worker shell, network, Git push, and Drive write permissions by default.

If a setting requires restarting the main session, persist a small restart packet and give the owner one exact instruction. Do not make an undocumented self-relaunch loop. If nesting is unavailable, use scoped sibling delegation and continue.

## E. Establish the spending barrier before live work

Write `ops/resource_policy.local.json` with the owner's zero-new-spend rule. Verify the current OpenRouter quota/model catalog and Modal credit applicability. Where a dashboard action cannot be performed through the installed authenticated tools, ask the owner for that one necessary action while continuing offline work.

Require a Modal **net spend limit of $0** or an equivalent verified account-side guard before cloud execution. An internal $40 allowance alone is not a billing guarantee. Record an upper bound for any proposed job including warm-up, CPU, memory, storage, and cleanup. Do not launch a job until the remaining verified credits cover its conservative reservation.

Do not purchase OpenRouter credits. Do not activate an automatic fallback that could select a paid model. Do not assume an existing subscription pays for experimental API calls.

## F. Make the scientific and publication paths runnable

Create the smallest CCC package skeleton and an offline test that can import the adapter without making a network request. Inspect the exact reward and `total_cost` semantics; issue `ops/reports/pilot_metric_audit.md` correcting the earlier interpretation.

Verify that the designated Google Doc can be read using tools available **inside the local Claude workflow**. ChatGPT's connected Drive access is not automatically transferred to Claude Code. Record either a working local connector or `DOC_SYNC_PENDING` plus the safe fallback route. Do not block replay work on a missing document connector.

Check the official deadline and template requirements, and create `submission/paper_outline.md` with empty result placeholders. Do not fill the result section with expected outcomes. Create an author-information checklist without inventing the owner's legal name, affiliation, or coauthors.

## G. Return the bootstrap verdict

Required artifacts:

- `ops/environment.local.json`, with versions, paths, effective routing, and missing capabilities.
- `ops/STATUS.md`, `ops/tasks.json`, `ops/RESUME.md`, and a concise decision log.
- Pilot archive/hash manifest and metric audit.
- Actual delegation verification record.
- Credential-safe resource policy and cost-control status.
- A bounded backend benchmark plan; no large batch yet.
- A small offline test suite with exact command and exit result.

Verdict fields: `offline_ready`, `free_api_ready`, `local_inference_ready`, `modal_ready`, `drive_sync_ready`, `nested_claude_ready`, and `codex_bridge_ready`, each with evidence or a reason. False does not mean the whole project must stop: offline fixtures can begin while one optional backend is unavailable.

BOOT-001 passes when the workspace is protected, offline development works, the delegation path is real, and no live inference can bypass the resource policy. It is not necessary to configure every optional resource before starting science and replay development.
