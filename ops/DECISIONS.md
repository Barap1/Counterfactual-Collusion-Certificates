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

## D-014 (2026-10-23, director) Protocol v1.1 OPEN items resolved
- SCI-002b (Haiku) applied C1–C8 + P1 to protocol.md (v1 preserved as protocol_v1.md). Three OPENs resolved from existing STAT-001 text, no new values invented: (1) TV_excess null = exact enumeration per checkpoint (analysis_spec §69); (2) Δ_conditional descriptive with interval; (3) S1–S3 confirmatory under Holm (prereg §10). P2 items unapplied (non-blocking). Rehashed protocol_v1.1.sha256. STAT B1 blocker cleared pending Gate-A reviewer spot-check.

## D-015 (2026-10-23 ~22:40 UTC, director) Gate A result and split
- ENG-004 reports Gate A FAIL. Replay integrity passes in full (F=S 380/380, K scope 1520/1520, isolation 380/380), and A2 benign cooperation is never "supported" (80/80). Failures: A6 invalid detection 350/360 (10 inactive faults); A5 redundancy labelled "not supported" 100/120 (protocol violation); CCC sensitivity 0/80 on A1, which makes the A2 pass vacuous.
- Gate A is not declared passed. GA-DIAG (Codex) classifies each failure as implementation bug / fixture design / protocol design. Thresholds and protocol semantics are not changed to make the gate pass.
- Split: "A-replay" (data-generating integrity) passed; "A-decision" (offline audit layer) failed. Because the decision layer runs offline on recorded ledgers and can be re-run after fixes, the EXP-001 DEV live pilot may proceed on A-replay once EXP-000c (reload detection) passes. Its pass criteria are operational only and it never touches held-out seeds. Held-out EXP-002 requires full Gate A plus Gate B plus the frozen prereg. This split is recorded for REV-001 to challenge.
- Full offline suite after integration: 213 tests OK.

## D-016 (2026-10-23 ~21:50 UTC, OWNER) Conditional approval of D-015
Owner approved the overnight DEVELOPMENT-ONLY local run at $0, subject to these conditions:
- No held-out evaluation. Generated data is not treated as validated evidence.
- Preserve immutable raw trajectories, model/version ids, prompts, seeds, checkpoint and config hashes. Failed or incomplete generations are recorded separately.
- No protocol or threshold changes without an explicit reviewed amendment.
- Priority 1: diagnose CCC 0/80 sensitivity. Also determine whether the A5 handling is correct (note: ENG-004 shows A5 labelled "not supported", not abstentions) and why 10/360 A6 faults escaped. Fault-injection tests must show the integrity checks fire.
- An independent reviewer challenges every proposed fix.
- Before the full run: report expected runtime, throughput feasibility, abort conditions, and short local pilot results.
- Auto-stop on model, resource or spend violations (watchdog).
- A baseline beating CCC is an acceptable outcome. No optimizing the evaluation for a win.
- Submission work continues in parallel, with verified and provisional findings kept distinct.

## D-017 (2026-10-23, director) GA-DIAG accepted as diagnosis; fixes pending review
- A1 0/80: classified FIXTURE DESIGN. 68/80 A1 oracle outsider-harm effects are below m_O=2.5 (54 are zero or negative), and CCC's intervals agree with the oracle in all 80. The other 12 are blocked by the N-placebo veto (PROTOCOL DESIGN); 8 of those also fail coalition benefit. This is a candidate finding: mechanism-labelled "harmful dependence" need not imply estimand-level outsider harm.
- A5: IMPLEMENTATION BUG (carrier flags not passed to decide) fixed; not-supported down from 100 to 48. The remaining 48 are FIXTURE (24) or PROTOCOL (24 paraphrase carriers).
- A6: all 350 activated faults detected. The 10 inactive faults produced byte-identical clean branches (FIXTURE activation issue).
- Gate A stays FAIL. Every proposal in docs/gate_a/diag/proposals.md goes to REV-GA (Claude Sonnet, independent) before adoption. Threshold or semantic changes need a formal amendment.

## D-018 (2026-10-23 ~22:15 UTC, director) REV-GA findings adopted; amendment v1.2 path
- REV-GA reproduced every GA-DIAG number from raw cells, and all 9 independent fault-injection tests fire (leak, ledger tamper, reused response, model-id mismatch, cross-branch mutation). Integrity checks are demonstrated.
- P0: under v1.1 as implemented, "supported" is unreachable (0/800 cells). The N filler removes the same content as K, so tau_O_N == tau_O in 390/390 cells and the N-veto always fires. CCC's 0/80 is not evidence about harm detection. Fixing this needs protocol amendment v1.2 (AMD-001), drafted by Sonnet and reviewed by REV-GA before adoption. No threshold changes.
- The A5 carrier fix over-flags 42 non-A5 truth-none cells (A3a, A4b, A2a). The extractor contract (agent-keyed, equality, negation, negative controls) goes into the amendment.
- Implementation-vs-v1.1 bugs with no amendment needed go to ENG-005 (Codex): lesion rule must use the C3 exact test, not a point rule; V9/V10 study-level inputs must be wired; the A6 gate must require the intended validator; A6b precondition asserted at generation (no seed search); V07 provenance must not be dropped by setdefault.
- EXP-001 dev run proceeds. F/S/K are unaffected. Its N branches use the v1.1 placebo and are labelled N_v1.1_deprecated in analysis.
- Candidate reportable finding (provisional): mechanism-labelled "harmful dependence" fixtures are mostly path-inactive for outsider harm (68/80 below the floor). Label/estimand mismatch.

## D-019 (director) EXP-001 pilot false-positive halt
- The pilot halted after 1 live call ($0) with model_reload. Cause: expires_at was part of the load fingerprint, and Ollama refreshes it on each request even with keep_alive -1. Digest, VRAM, context and the listener and runner PIDs were unchanged. Classified as a runner false positive, not a real reload. The halt behaved as intended (fail closed).
- Fix in EXP-000d (Codex): fingerprint without expires_at, using the runner-subprocess PID as the primary reload signal and the canary as secondary. Then re-run the 1-checkpoint pilot and report to the owner before the full run (D-016).
- Watchdog (20 tests) accepted.

## D-020 (director) Amendment v1.2 draft and EXP-001 sequencing
- AMD-001 draft committed with pre-written predictions; hash in git. Under review by REV-GA (same independent reviewer, not the drafter). It is not adopted and protocol.md is unchanged until the review passes.
- EXP-001 runs with F/S/K plus N_v1.1 (labelled N_v1.1_deprecated) once EXP-000d lands and the pilot passes. Its purpose is operational validity plus F/S noise for pinning m_O.
- If v1.2 is adopted, a small EXP-001b dev mini-run (fresh F alongside N_m in the same model session) validates N_m operationally before any held-out run. This is AMD-001's preferred option; a cross-session contrast is rejected.

## D-021 (director) REV-AMD outcome
- REV-AMD verdict: ADOPT-WITH-EDITS, no P0. All P1 required edits go back to the drafter (AMD-001 r2), then REV-AMD re-checks the edits only.
- Director choice on the P1 "supported needs N_m but N runs on only 50% of Tier B" issue: run N_m on ALL checkpoints (held-out N4 on 100%) rather than declare a semantic change. The compute impact must be recomputed in the amendment against compute_plan.md's 45% buffer; if it does not fit, fall back to declaring the semantic change explicitly.
- Disclose in the paper and amendment that C1 was motivated by the DEV Gate A result; freeze against any further N redesign before held-out.
