# 00 - Coordinator contract and execution map

**Project:** Counterfactual Collusion Certificates (CCC)  
**Specification:** 1.0, prepared October 23, 2026  
**Working root:** `~/Documents/Projects/ApartSprint`  
**Primary outcome:** a rigorous, reproducible research submission, not a large agent framework.  
**Operating principle:** observation raises suspicion; a valid intervention can strengthen a *scoped* causal claim. An invalid intervention must not produce a certificate.

## Read this first; do not ingest the whole specification

The main Claude Code session is the **research director and dispatcher**. It does not implement application code, read entire traces, run exploratory sweeps, or draft the whole paper. Its job is to assign bounded tasks, inspect compact evidence-backed handoffs, resolve dependencies, and enforce gates. Heavy work belongs in fresh worker contexts. This specification is intentionally extensive; loading it into every agent would defeat its purpose.

Use `CCC_START_HERE.md` as the initial entry point. The modular files under `docs/spec/` and the complete `CCC_MASTER_SPEC.md` contain the same requirements. The master is a human/reference edition, not an automatically injected system prompt. If only the master is present, the first bootstrap worker extracts its numbered sections into the module paths listed below without changing their contents. Do not make the parent read the entire master just to split it.

### Hard rules inherited by every delegated task

1. **No fabricated results, references, tool executions, delegated agents, reviews, or uploads.** A task is complete only with inspectable artifacts and passing acceptance checks.
2. **No additional out-of-pocket spending.** Existing subscription allowances, verified free inference, local compute, and eligible Modal credits are the only approved resources. No silent paid fallback.
3. **Preserve the owner's working project and secrets.** Inspect before changing. No destructive resets, credential disclosure, unrelated Drive edits, or automatic publication.
4. **Treat the successful seed-1 run as pilot data.** Do not use it as a held-out validation example or proof of causal collusion.
5. **Use bounded recursive delegation.** Default maximum three worker layers below the director; six live delegated agents across Claude and Codex combined; one experiment/inference controller. A parent waiting for children still consumes a slot.
6. **Independent scientific and software review is mandatory.** Independence means a separate task/context that examines evidence, not a claim that model agreement constitutes proof.
7. **End with a submission-ready paper and reproducibility package.** The demonstration supports the evidence; it never substitutes for it. Human approval remains required for final submission and publication.

## First action

Launch **BOOT-001, Environment and delegation bootstrap**, with modules 00, 02, 03, 08, 09, and 14 as scoped inputs. It must inspect and configure the existing environment, protect the pilot, verify real nested delegation and the Codex bridge, establish cost controls, and return an environment manifest. It must not start a large experiment. The director may concurrently assign a read-only source/novelty review after BOOT-001 has acquired its ownership lock; no competing setup writers.

## Routing map

| Module | Read by | Purpose |
|---|---|---|
| `00_control_plane.md` | Director; all leads | Nonnegotiables, initial routing |
| `01_research_strategy.md` | Science and publication leads | Contribution, scope, novelty, competition fit |
| `02_known_state.md` | Bootstrap; evidence auditor | Actual setup, pilot, corrections |
| `03_agent_orchestration.md` | Director; all leads | Recursive delegation, context, ownership |
| `04_causal_contract.md` | Science, replay, statistics workers | Estimands, interventions, interpretation |
| `05_experiment_design.md` | Science and experiment leads | Controls, sampling, ground truth |
| `06_analysis_plan.md` | Statistician; independent reviewer | Preregistration, uncertainty, claims |
| `07_engineering_architecture.md` | Engineering workers | Replay, adapters, storage, CLI |
| `08_bootstrap_runbook.md` | BOOT-001 | First delegated setup task |
| `09_inference_and_budget.md` | Inference controller; bootstrap | Backend choice, limits, zero-spend policy |
| `10_verification.md` | Test and red-team reviewers | Unit, integration, causal, release gates |
| `11_visual_experience.md` | Visualization and demo workers | Evidence-first, polished presentation |
| `12_paper_and_drive.md` | Publication lead | Official-template paper and Drive target |
| `13_workplan.md` | Director; all leads | Dependency graph, milestones, fallbacks |
| `14_git_and_security.md` | Integrator; all workers | Safe worktrees, commits, credentials |
| `15_artifact_contracts.md` | Engineers; reviewers | Data, certificate, handoff schemas |
| `16_agent_briefs.md` | Director; named role | Copyable task prompts |
| `17_release_checklist.md` | Director; release reviewer | Definition of done, owner handoff |
| `18_sources.md` | Research and writing workers | Stable references and verification status |

## Persistent control files

The bootstrap worker creates these only if absent, or reconciles existing equivalents:

- `ops/STATUS.md`: one screen of phase, active tasks, blockers, budgets, next gate.
- `ops/tasks.json`: task IDs, owners, dependencies, leases, review state, artifact paths.
- `ops/DECISIONS.md`: dated decisions with reasons and superseded alternatives.
- `ops/CLAIMS.md`: claim-to-evidence index, including explicitly rejected claims.
- `ops/RESUME.md`: compact restart packet; no hidden dependence on chat history.
- `ops/budget_ledger.jsonl`: actual resource accounting; sensitive account details stay local.
- `ops/environment.local.json`: local paths, runtime versions, plugin capabilities; gitignored.
- `ops/reports/`: detailed worker reports; the director reads only their short summaries unless escalation requires more.

The director normally reads only `CCC_START_HERE.md`, this module, `ops/STATUS.md`, and the current gate's short report. Modules 13 and 17 are targeted references. Never put this entire specification or raw experiment transcripts into `CLAUDE.md` or `AGENTS.md`.

## Decision rights

The director may prioritize, delegate, accept verified work, and reduce scope. Science changes require a recorded decision and reviewer sign-off. After the holdout is frozen, changes create a new exploratory analysis version; they do not rewrite the preregistration. The integration worker is the sole merger/pusher. The inference controller is the sole owner of billable or quota-consuming experiment processes. The publication worker is the sole writer to the designated Google Doc.

When blocked, stop only the affected task. Continue other safe work. Ask the owner only for genuinely unavailable authorization, credentials, authorship information, or an irreversible decision. Do not repeatedly ask about hardware, budget, directory, or integrations already established here.

**Victory is an aspiration, not an acceptance test.** Acceptance is a defensible contribution, valid evidence, polished communication, and a complete artifact delivered before the deadline. No instruction authorizes altering results to fit the intended story.
