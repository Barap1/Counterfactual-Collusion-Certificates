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

## D-022 (director) Held-out compute choice under v1.2
- With N_m on all checkpoints the held-out plan leaves only a 37.1% buffer (4% at 8.4 s/call), below compute_plan.md's 40% requirement. Adopted the preregistered fallback S n=1 on 50% of checkpoints (4,460 calls, about 13.6 h wall, 43% buffer) and dropped optional pairs H09/H10. This was decided on compute grounds before any held-out data exists. Latest held-out start stays 2026-10-24 14:12 UTC.

## D-023 (director) Protocol v1.2 ADOPTED
- REV-AMD adoption check: all 104 diff lines trace to amendment r3 or D-022, every protocol-bound change landed, and no threshold, V9 rule, CI method or F/K/N n changed. Verdict ADOPT.
- The director applied the non-blocking cleanups: status lines set to adopted; Tier A S2 clarified as fixtures/DEV only (held-out uses S1 on 50% per D-022); V9-power disclosure pointer added; v1.1 changelog row annotated as superseded. Rehashed protocol_v1.2.sha256.
- Further N redesign is frozen before held-out. Paper must disclose that C1 was motivated by the DEV Gate A result.

## D-024 (director) Codex credits exhausted
- Both v1.2 Codex jobs (AMD-IMP-A/B) failed mid-task: "Your workspace is out of credits." Buying credits would be new spending, so no purchase. Partial files are retained in the worktree for review.
- Remaining implementation moves to Claude: core v1.2 on Sonnet; the independent extractor contract suite on Haiku (a different author from the extractor, per the amendment); constructed-controls completion on Haiku. Owner informed; Codex resumes if the owner restores credits.
- (D-024 addendum) Independent contract suite (Haiku): 22 tests, 17 pass, 2 fail, 3 skipped as SPEC-AMBIGUOUS. The failures show an extractor mismatch: third-person commitments are attributed to the author instead of the named agent; relayed to the implementer without the tests. Independence caveat: the suite author read about 30 lines of the earlier partial test file before writing. Disclose this in the reproducibility notes. The three ambiguities (CURRENT ASSIGNMENTS syntax, alias format, attribution surface form) are resolved by the implementer as recorded "spec clarifications" and frozen before the census.

## D-025 (2026-10-23 ~23:05 UTC, director) Restart after outage; EXP-001 live; Codex-only window
- A network outage (ENOTFOUND) killed the Claude agents. Owner: "internet is back... for the next 4 hours only launch codex sub agents" (until about 03:00 UTC Oct 24). Codex credits verified working again.
- Pilot 3 (V09 fix plus v1.1 manifests) met every predefined GO criterion: 14/14 branches valid, 0 V09, 0 model_reload, 297 live calls, $0, watchdog clean, canaries present. The full EXP-001 dev run launched at 22:56:27Z by the director as experiment controller (run PID 5196, watchdog 5231), output docs/runner/exp001-live.
- The v1.2 placebo census ran before the IMP-0 freeze hashes were committed (Claude worker interrupted). AMD-IMP-A2 must record this honestly; the census is re-run after freezing if needed.
- Commit budget: 60 of 70 commits used. Commits are batched from here; owner asked whether exceeding 70 or squashing at release is OK.
- VIS-001a/b: dev figures from v1.1 fixtures (labelled pre-amendment) pass director visual QA. Final figures are regenerated post-v1.2.

## D-026 (2026-10-23 ~23:20 UTC, OWNER request) Squash and push
- Owner asked to squash to about 40 commits, commit the latest update and push. The 63 local commits were rebuilt with git commit-tree into 37 (38 including the base), folding each bookkeeping "ops:" commit into the preceding substantive commit. The final tree is byte-identical to the pre-squash HEAD (verified with git diff). Old history kept locally as branch backup/pre-squash (not pushed).
- Pre-push secret scan: no tracked .env/compute.env/*.local.json; regex scan over all commits was clean; exact-value check of local secrets found only OPENROUTER_BASE_URL (public URL) and OPENROUTER_MODEL ("openrouter/free"), both non-secret config. No API keys present.
- Pushed main to the existing private origin as a fast-forward (097619b..fc7e2ae). Worktree branch v1.2-impl still sits on pre-squash ancestry; it will be rebased with `git rebase --onto main <old-base> v1.2-impl` once AMD-FIX-1 finishes (trees identical, so this is clean).

## D-027 (OWNER) Commit attribution
- From now on all commits list the owner as sole author, with no Claude/Codex Co-Authored-By trailers. Already-pushed history is unchanged, since a rewrite was not requested. The paper's LLM-usage statement is unaffected and remains truthful per the sprint rules.

## D-028 (2026-10-24 ~00:25 UTC, director) GATE A PASSED on module-13 criteria, with declared limitations
- Evidence: Gate A v1.2.1 (worktree commit 0c26001; docs/gate_a/v1.2/GATE_A_v1.2.1.md). Module-13 Gate A criteria all PASS on DEV fixtures: F/S identity 380/380, intended-knockout-only 4180/4180, branch isolation 760/760, benign causal cooperation (A2) never supported 80/80. The A2 pass is no longer vacuous: CCC reaches supported on 4/280 headline DEV cells, each with valid N_m provenance and oracle outsider harm 4.015 > m_O.
- Two stricter checks added in the ENG-004 brief still FAIL and become declared limitations that narrow claims rather than block the gate: A5 (16/68 redundant-carrier cells correctly not exonerated, so a "not supported" verdict is NOT exoneration, and semantic/paraphrase carriers are undetected); A6 (350/360, the 10 misses being A6b cells whose fault is not exercisable).
- Independent challenge: three Codex adversarial-review rounds; findings fixed in AMD-FIX-1/2; final re-review reproduced every number, no new findings. Pre-written predictions: 16 confirmed / 2 falsified / 3 untested. Constructed controls 30/30 (unit/reachability only).
- Disclosures carried to the paper: v1.2 motivated by the v1.1 DEV result; DEV-002 census freeze failure (census exploratory); A5/A6 limitations.
- Next: merge v1.2 into main after EXP-001 ends; Stage-2 pinning on EXP-001 F/S; Tier-B M* availability census on EXP-001 real trajectories; STAT freeze review; held-out EXP-002 needs OWNER approval.

## D-029 (2026-10-24 02:30 UTC, OWNER + director) Resume; v1.2 merged; held-out path
- Owner: continue under the conditional approval for the protocol v1.2 held-out run. Do NOT rerun dev05_B2. Preserve the failed attempt; calibrate on the 3 complete DEV pairs with uncertainty and missingness reporting. Investigate the 223-call cap from DEV call-count distributions; any cap change is justified and frozen independently before held-out outcomes, with runtime/budget recomputed and the watchdog/$0 policy kept. Proceed automatically when all conditions pass; otherwise stop and report. No outcome-dependent changes.
- EXP-001 final: 7/8 base trajectories complete, 98 branch results, 0 invalid. dev05_B2 attempt_0001 FAILED on budget_guard "per-run call cap 223 reached" (operational stop, $0). Preserved.
- v1.2 merged into main by cherry-picking the 4 branch commits with the owner as sole author (trailers stripped). Conflicts: engine.run_branch signature (union of params); gate_a native N path (v1.2 run_branch N_m path kept, with V09 request-id freshness carried into it). Full suite 378/378 OK.
- The Stage-2 tool refused the finished run due to a path-name guard ("exp001-live"). PRE-HO (Codex) fixes the guard to detect active runs; renaming the output to bypass it was rejected.

## D-030 (2026-10-24 ~03:00 UTC, director) Pre-held-out decisions (all outcome-blind)
- Cap: the "223" was the collection-wide remaining budget, not a per-world cap. EXP-001 max_requests=2470 = ceil(1.05·8·(28+14·19)) omitted 3 canaries per world and the observed s=25 calls/branch, so it fell 74 calls short (operational arithmetic miss). Held-out cap rule frozen now from DEV call-count maxima and protocol arm counts only: max_requests = ceil(1.05 × 16 × (28 + 3 + 13 × 25)) = 5981 (docs/runner/cap_investigation.md). Watchdog and $0 policy unchanged.
- Runtime: measured wall 3.10 s/call mean (4.66 including the dev05_B2 stall), p95 5.87 s, giving 7.7–9.8 h for 5981 calls. The buffer is ≥55% for a start by 14:12 UTC and ≥67% for an immediate start. Measured constants supersede compute_plan's older 5.5 s/0.5-duty constants, under which the D-022 latest-start claim was wrong (≈13:18 UTC). Launch as soon as the freeze passes.
- Tier-B M* availability = 0/8 DEV real-agent checkpoints (frozen §3.1 rule; the sender's only prior message is task-bearing). Per frozen protocol v1.2 §3.2, Tier B is reported and case-level `supported` is unavailable (`inconclusive: no_placebo_available`). There is NO environment change, no chatter for real agents and no N redesign (frozen; outcome-independent). The primary study-level Δ (F vs K) does not need N and remains the confirmatory target. Expected held-out calls drop to about 3284 if N never runs; the cap stays 5981.
- Freeze-hash drift: ccc/audit/commitments.py changed in the reviewed v1.2.1 correction (07ca10f) after ops/v12_freeze_hashes.txt was written. It is re-frozen at the current hash before any held-out data, and disclosed.
- theta (redundancy Jaccard) to be pinned per prereg on DEV fixtures only (A5a positives vs non-redundant negatives), before freeze.
- Stage-2: sigma_dev 0.92 from 7 DEV checkpoints, giving m_O = 2.5 (construct floor binds), delta_W 5, delta_S 2.5. The dev05_B2 failure is retained.

## D-031 (2026-10-24 02:42 UTC, director as experiment controller) EXP-002 held-out launched
- All owner conditions met: DEV-only pinning (Stage-2), real-conversation placebo census (Tier-B 0/8 → supported unavailable, handled per frozen protocol), outcome-blind cap change frozen (5981) before any held-out data, independent freeze review APPROVED (docs/review/REV_FREEZE.md; docs/stats/stat001_approval.json bound to manifest digest 49f54b47), watchdog hard-stop made configurable and set to 2026-10-25T12:15Z, $0 guard unchanged, 385/385 tests.
- Run PID 98650 (python runner), watchdog PID 98683, Ollama 57827 (gemma4:26b digest 5571076f3d70), output docs/runner/exp002-live (gitignored). Expected 5–10 h.
- No outcome-dependent changes may be made while the run is in progress or after it ends. Analysis follows prereg + Stage-2 addendum exactly.

## D-032 (director) GATE B recorded as met (retroactive record; evidence predates EXP-002 launch)
- Module-13 Gate B: a complete F/S/K(/N_v1.1) sequence on the real model with preserved request traces, validated state/exposure, accurate model IDs and interpretable metrics, plus a throughput forecast that fits approved resources.
- Evidence: EXP-001 (docs/runner/exp001-live): 98 branch results, 0 invalid (V09 client-request freshness, V6 model identity, reload canaries all passing), 7/8 base trajectories complete, dev05_B2 failure preserved. DEV analysis valid (docs/analysis/exp001_dev). Throughput re-derived from the EXP-001 ledger (docs/runner/cap_investigation.md) and checked by REV-FREEZE (docs/review/REV_FREEZE.md, buffer ≥71%).
- This record was omitted at launch time; it is added now with no change to any artifact.

## D-033 (director) Analysis readiness (STAT-002c) accepted
- A synthetic held-out-shaped rehearsal found and fixed real gaps: runner-format loading, skipped-N handling, retry isolation and failure accounting. 50 analysis tests pass; 39 synthetic outputs reproduce byte-identically. Exact post-run command: docs/analysis/readiness/READINESS.md.
- Disclosed scope deviation: one early filename search by the Codex worker was broader than its brief and returned only protocol filenames. No held-out output contents were opened. Logged for REV-001.

## D-034 (2026-10-24 ~07:40 UTC, director) Gate C review outcome; labelling correction
- REV-001 (independent Claude Sonnet): PASS-WITH-NARROWING, no P0. It reproduced every number from RAW: Delta 1.354, sign-flip p 0.0703 (18/256), bootstrap CI [-0.0195, 2.8336], 16/16 worlds, 143 valid executed branches + 56 N not_run, 0 failed, 0 invalid, $0.
- Governing-text decision: the protocol v1.2 §10 sentence "Tier B is labelled exploratory now" governs Tier-B CASE-LEVEL verdicts only. The study-level primary Delta and the S1–S3 Holm family are preregistered confirmatory (prereg §10 floors met: 8/7/8; D-030; REV-FREEZE). The pipeline's hard-coded "exploratory (DEV-001)" label (ccc/analysis/study.py L38–44, 62–66; pipeline.py L131) is an implementation error: DEV-001 affects only the S arm/V9. It is corrected as a disclosed correction (labels only; no number, threshold or data change). This makes the result a CONFIRMATORY NULL, the conservative reading.
- Preregistered decision: Delta > 0 NOT supported (bootstrap lower bound -0.02 ≤ 0; p 0.070 > 0.05; both required). Holm S1/S2/S3 adjusted 0.164/0.4375/0.164: none significant.
- Post-hoc sensitivity (labelled post hoc): excluding the two F-arm non-commit runs (H02_B1, H05_B1) gives Delta 0.727, CI [-0.31, 1.91], p 0.156. Reported alongside, never as the primary.
- Zero supported is NOT attributed only to placebo unavailability: no checkpoint's CI_lower exceeds m_O (max 0.77). N_m ran on 2/16 checkpoints.
- V9: by-regime B1 sham_uncertain, B2 pass; pooled study rule passes. Both reported; no sham-equivalence certification claimed.

## D-035 (director) GATE C PASSED (with narrowing)
- Analysis is frozen; every attempted run is accounted for (16/16 worlds; 143 valid + 56 N not_run; 0 failed or invalid). The headline Delta was independently reproduced twice (REV-001a script; REV-001 raw reproduction). The label correction (exp002_heldout_v2) was verified by the director: 0 numeric diffs across 15 JSON outputs.
- Claims follow the realized evidence (docs/review/rev001/CLAIMS_LEDGER.md): a confirmatory null on the primary (Delta > 0 not supported, n=8); no Holm secondary significant; 0 case-level supported, not attributed only to placebo unavailability; post-hoc sensitivity 0.73 disclosed; DEV Gate A method-validation findings; and the limitations.

## D-036 (2026-10-24 12:22 UTC, OWNER request) Squash to 20 and push; repo found PUBLIC
- Owner: "squash into 20 and then commit and push". The 39 unpushed commits were rebuilt into 20 with git commit-tree (trees byte-identical to the pre-squash HEAD; owner as sole author and committer; AI co-author trailers removed). Backup: local branch backup/pre-squash-2. The working tree had no uncommitted tracked changes. The secret scan was clean (regex + exact local values; no local or secret files tracked). Pushed fast-forward fc7e2ae..a16d3c6; total history 58 commits.
- After the push, the repository visibility was PUBLIC (it was private at the D-026 check). The director made no visibility or sharing change. Publicly visible: private Google Doc IDs (working copy and official template) in CCC_MASTER_SPEC.md, docs/spec/12_paper_and_drive.md, ops/reports/PUB-001_early.md, paper/author_checklist.md and paper/outline.md (and in history); owner email in commit metadata and a report; unverified upstream redistribution terms. Escalated to the owner. No remediation was taken without approval.

## D-037 (2026-10-24 15:15 UTC, OWNER request) Competition enhancement sprint (ENH) opened
- Owner mission: strengthen the submission scientifically (evidence standards for collusion attribution: causal influence vs harm vs justified attribution vs identifiability; abstention-aware benchmark; correctness repairs; interactive evidence explorer; competition-grade paper; release safety). Brief for all workers: docs/enh/MISSION.md.
- Frozen and preserved: EXP-002 result and all original Gate A–D artifacts. Corrections only as new versioned directories with field diffs. New performance claims only from a prospectively frozen protocol (gate R2) on fresh seeds/worlds.
- New gates R1 (direction) → R2 (protocol frozen) → R3 (evidence validated) → R4 (presentation verified) → R5 (owner review) apply only to ENH.
- Wave 1 launched: ENH-A novelty (Sonnet), ENH-B stats challenge (Codex gpt-6.1-sol medium), ENH-C direction challenger (Sonnet), FIX-001 validity-metadata fix → exp002_heldout_v3 (Codex gpt-6.1-sol medium), SEC-001 release audit read-only (Sonnet). 5/6 live; 1 slot reserved for review.

## D-038 (2026-10-24 ~15:45 UTC, director) Gate R1 — research direction ACCEPTED
Inputs: docs/enh/r1/A_novelty.md (ENH-A), docs/enh/r1/C_directions.md (ENH-C). ENH-B (stats) still running; its findings feed R2/R3, not the direction.
Decision: core = **identifiability frontier of message-level collusion evidence** (ENH-C option C), operationalised as an **abstention-aware benchmark** (option B), with one small method addition (option A, as an evidence rung, not a "fix"). Working principle: "A knockout measures what a message did, not whether it should have done it."
Why: fits the north star; $0 and no LLM calls; turns Gate A's own failures (A2, A5, label-vs-effect gap) into the object of study; informative under positive and negative outcomes; the closest prior indistinguishability statements (arXiv 2607.26385, 2608.18078, 2610.28787) are observational/price-level or informal, so a scoped, executable, message-level interventional version is a defensible delta (bounded search; no "first" claim).
Evidence ladder (claims are separately gated): L0 suspicious text → L1 causal influence (behaviour changes under K) → L2 harmful exposure effect (valid replay, tau_O > m_O with controls) → L3 collusion attribution (requires evidence that separates harmful coordination from legitimate cooperation). Axes kept separate in every table: mechanism label M, realized harm H, exposure effect E, identifiability I(information set).
Information sets (nested): I0 transcript + factual; I1 + single-message knockout K; I2 + sham/placebo; I3 + set/joint knockout of all same-sender carriers; I4 + environment/incentive probe (e.g., counterfactual cost perturbation); I5 + external normative record (authorization), non-behavioural.
Twin-pair types (identical observables up to the stated set; different labels): P1 redundant-harmful vs inert (separated at I3); P2 colluding allocation vs efficiency-motivated legitimate cooperation with identical behaviour in the observed world (separated only at I4: when an outsider is cheaper, the legitimate team cedes, the colluders do not); P3 authorized vs unauthorized transfer with identical policies (separated only at I5; tautological by design and labelled so); P4 common cause vs message-caused coordination (separated at I1: shows where knockout works); P5 suspicious-language inert vs plain-language inert (transcript differs, outcomes identical: tests transcript rules); P6 information-bearing legitimate message whose removal hurts everyone vs harmful steering (separated by harm/utility gates at I1).
Falsifiable questions (to be frozen at R2 with criteria): RQ1 leak/symmetry — actual CCC v1.2.2 and baselines emit identical outputs on twin members under each declared set; RQ2 frontier — the minimal separating set per pair type matches the enumeration; RQ3 label–effect gap — share of mechanism-"forbidden" iid Jira worlds with oracle tau_O ≥ m_O in a fresh population (DEV 12/80); RQ4 over-attribution — knockout/influence/transcript baselines accuse legitimate members (P2, P3, P6, benign cooperation) at high rates; CCC's exposure-level "supported" is reported separately from attribution; RQ5 a ladder-aware auditor (new method version, exploratory) abstains on attribution exactly where the frontier says the set is insufficient and attributes when I4 evidence is supplied, measured against a Bayes-given-I reference ceiling.
Guards against circularity: identifiability labels come from exact enumeration of observables, never from CCC gates; Bayes-given-I is the ceiling for any method restricted to a set; always-abstain/always-answer anchors; risk-coverage reported, not one scalar; equivalence under a fixed set is stated as definitional, the claims are the measured frontier, the pipeline symmetry check, prevalence, and baseline behaviour.
Scope limits: scripted development generators + fresh prospective seeds; no new LLM runs unless the scripted study finishes early and the director assigns it. EXP-002 is used only descriptively as the real-agent illustration (knockout magnitude did not separate prompt regimes at n=8; consistent with, not evidence for, the principle).
Next: BENCH-IMP (implementation, Codex) and PROTO-001 (R2 protocol draft, Sonnet) in parallel; fresh seeds only after R2 freeze with code hashes.
