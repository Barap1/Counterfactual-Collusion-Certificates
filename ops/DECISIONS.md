# Decisions (dated; newest last)

**2026-10-23 D-001 (BOOT-001) - Starter checkout stays gitignored.** `starter/collusion_hackathon/` is a separate upstream git checkout (SHA d585a7b, clean tracked tree), ignored by the project `.gitignore`. Kept as-is to avoid a nested repo in history; its absolute paths live in `ops/environment.local.json`. Alternative (submodule/vendoring) deferred to REL-001.

**2026-10-23 D-002 - Pilot archived locally, hashes tracked.** Both pilot batches copied read-only to `results/baselines/colosseum_positive_control_seed1/` (complete, 20261023-111625) and `..._interrupted/` (20261023-111229, status "running", 0 completed). Raw traces gitignored until a sanitized release; `ops/pilot_manifest.sha256` (27 files) is tracked. Source left untouched.

**2026-10-23 D-003 - Pilot model provenance kept unedited.** Batch `config.json` requested `Qwen/Qwen2.5-7B-Instruct` (label `openai_gpt4o_mini`); `run_config.json` recorded `cohere/north-mini-code:free`. Mechanism most likely an `LLM_MODEL` override at run time (unset now) - unverified. Archived labels are not rewritten.

**2026-10-23 D-004 - Use the existing Colosseum venv read-only for CCC dev.** Python 3.14.7, Terrarium 0.1.1 pass the offline preflight; no reinstall/downgrade. CCC tests are stdlib-only and run with that interpreter via `-m unittest`; a separate env is created only on a demonstrated incompatibility.

**2026-10-23 D-005 - Codex bridge = direct companion script.** The `codex@openai-codex` plugin (1.0.6) is installed for `/Users/aarav` scope and not enabled here, so the `codex:codex-rescue` agent type is absent. The verified route is `node ~/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/codex-companion.mjs task ...` via Bash. Enabling the plugin for this project is an owner choice (adds hooks).

**2026-10-23 D-006 - Modal blocked until account-side $0 net-spend limit is verified.** CLI shows $0 metered/billed this month but not credits or limits.

**2026-10-23 D-007 - OpenRouter: pin `cohere/north-mini-code:free`; forbid `openrouter/free`.** `.env` and the session env export `OPENROUTER_MODEL=openrouter/free`; the starter does not read it, but CCC code must never use it.

**2026-10-23 D-008 - Hardened `starter/collusion_hackathon/compute.env` to mode 0600** (was 0644). Contents untouched.

## D-009 (2026-10-23, director) Accept BOOT-001 and SCI-001
- BOOT-001 accepted. `.claude/settings.json` (depth 3 / concurrency 6) was created by the bootstrap worker; flagged to owner for review, not relied on. Codex usage pending owner confirmation of the logged-in ChatGPT account; Claude workers used meanwhile.
- SCI-001 accepted. Contribution narrowed per `docs/research/sci001/claim_review.md`: no "first causal audit" or "novel knockout" claims; core claim = validity-gated protocol + benign-cooperation hard-negative evaluation. Fallback ladder in claim_review §3 adopted.
- INF-001 benchmark (local Ollama + free OpenRouter, no experiments) started in parallel with Gate A work to de-risk throughput; it is a backend benchmark, not experimental collection.

## D-010 (2026-10-23, owner via director) Codex, Modal, commits
- Owner confirmed the Codex ChatGPT account is correct and asked to prefer Codex workers over Claude workers. New implementation tasks route to Codex via `codex-companion.mjs task --write --background`; Claude agents kept for review/coordination.
- Owner approved Modal use up to the existing ~$51 credit. Director policy: hard stop at $45 cumulative Modal spend (margin below credit), billing checked before/after each job, no always-on deployments. Out-of-pocket remains $0.
- Owner approved committing any files (spec pack included). Push/publish/submission still require explicit approval.

## D-011 (2026-10-23 21:15 UTC, director) Wave 2 routing and SCI-002 choices
- SCI-002 v1 accepted as freeze-candidate (docs/research/sci002/). STAT-001 must re-review before freeze.
- B1 prompt variant: `deception` for the primary Tier-B stratum. Reason: the frozen estimand is outsider harm (tau_O); the deception variant instantiates an explicit outsider-harming objective, so mechanism-level positives can exist. `simple` may run only as a labelled exploratory stratum if compute remains. `colluder_selection: random`.
- ENG agent (Claude) stopped on a usage limit after committing ENG-001/002 (46/46 replay tests). Remaining ENG work reassigned to Codex (ENG-003). Owner asked to prefer Codex.
- INF-001 accepted: primary backend local Ollama gemma4:26b no-think; all arms of one checkpoint in one model-load session; OpenRouter free only as a small corroborating stratum (50 req/day). Modal not used: the `modal billing` check was denied by the permission system; director will not route around it. Local throughput (~1,200 continuations by Oct 25 12:00) suffices.
- Codex sandbox cannot write .git; Codex workers leave changes in the working tree and the director/integrator commits.
- Model selection: gpt-6-astra/high for science-critical code (ENG-004 audit), gpt-6.1-sol/high for replay hardening (ENG-003), gpt-6.1-sol/medium for runner plumbing (EXP-000), Claude Opus for STAT-001 judgment (cross-family independence from Codex implementers).

## D-012 (2026-10-23 21:30 UTC, owner via director) Conservative model policy
- Owner: "be conservative with sub agent choices; don't launch super expensive Claude and Codex". Cancelled ENG-004 on gpt-6-astra/high and STAT-001 on Claude Opus within ~2 min of launch (no partial outputs kept).
- Relaunched ENG-004 on gpt-6.1-sol/medium; STAT-001 on Claude Sonnet, no child. ENG-003 (gpt-6.1-sol/high) and EXP-000 (gpt-6.1-sol/medium) left running.
- Default policy from now: Codex gpt-6.1-sol medium (high only when justified), gpt-6-luna for easy tasks; Claude Sonnet/Haiku. No gpt-6-astra or Opus without recording a reason.
- (owner follow-up) Be stingy with model/reasoning choices; use Claude Haiku for simple builds, edits and checks. Escalate tier only for science-critical judgment, with the reason logged.

## D-013 (2026-10-23 21:50 UTC, director) STAT-001 draft accepted; freeze path
- STAT-001 prereg accepted as draft, NOT frozen. Freeze blockers: B1 protocol v1.1 (C1–C8; Haiku SCI-002b, then spot-check), B2 runner manifest per-arm map {F4,K4,S2,N4} + per-arm/rep/call seeds (follow-up to EXP-000), B3 Stage-2 dev-pinned addendum after EXP-001.
- Schedule adopted: EXP-001 Gate-B dev pilot (4 dev world-pairs) must finish by 2026-10-24 09:00 UTC hard stop; held-out EXP-002 latest start 2026-10-24 14:12 UTC; collection ends 2026-10-25 12:00 UTC.
- STAT-001 test-vector reference script copied from /tmp into docs/stats/ref_enumeration.py for reproducibility.
