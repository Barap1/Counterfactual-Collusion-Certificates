# CCC STATUS — handoff (2026-10-24 15:00 UTC)

**Deadline:** 2026-10-26 11:59 UTC (Apart AI Collusion Sprint; Sunday 23:59 AoE).
**Gates:** A PASSED (D-028) · B MET (D-032) · C PASSED with narrowing (D-035) · D technical checks done; owner decisions pending.
**Science is complete and FROZEN.** Do not rerun experiments or change analysis numbers.

## Verified result
Held-out EXP-002 (protocol v1.2, local gemma4:26b, 8 matched world pairs): Delta = 1.354, 95% CI [-0.020, 2.834], one-sided p = 0.0703, so the preregistered decision is **not supported** (confirmatory null). Holm S1–S3 not significant. Certificates 0/11/5. Integrity 143/143, 0 failed or invalid, $0. Claims: ops/CLAIMS.md (final section) and docs/review/rev001/CLAIMS_LEDGER.md.

## Running
Nothing. No agents, no Codex jobs, no experiments, Ollama stopped.

## Git
main at b89093e; **1 unpushed commit** (D-036 record) plus this handoff commit. origin = github.com/Barap1/Counterfactual-Collusion-Certificates, **currently PUBLIC** (unexpected; it was private on Oct 23). Local backups: backup/pre-squash, backup/pre-squash-2. Worktree ../ApartSprint-wt-v12 (branch v1.2-impl) is fully merged and can be removed with owner OK.

## Owner blockers
1. Repo visibility (recommend `gh repo edit Barap1/Counterfactual-Collusion-Certificates --visibility private --accept-visibility-change-consequences` — owner approval required). Private Google Doc IDs appear in 5 files and in history; scrub before any deliberate public release.
2. Paper [OWNER] placeholders: author/affiliation; LLM-usage wording + human-verification sentence; dual-use review (Appendix A); public-release line.
3. Google Doc working-copy sync (writes never authorized yet).
4. Push of the remaining local commits.
5. Final submission (the owner submits).
