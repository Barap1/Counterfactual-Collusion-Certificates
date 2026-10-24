# RESUME packet (2026-10-24 00:25 UTC)

Read CCC_START_HERE.md, ops/STATUS.md, this file, and the last ~6 entries of ops/DECISIONS.md (D-023..D-028). Do not reload the master spec.

Rules in force: $0 out-of-pocket; owner is SOLE commit author, with no Co-Authored-By trailers (D-027); conservative models (Codex gpt-6.1-sol medium / gpt-6-luna; Claude Sonnet/Haiku); push only on explicit owner request; no held-out run without owner approval.

Next steps, in order (as of 02:45Z: steps 1-5 DONE; EXP-002 running, see STATUS):
1. Confirm EXP-001 finished: `kill -0 5196`; docs/runner/exp001-live/WATCHDOG_EXIT.json (or WATCHDOG_STOP.json and its reason); `python -m ccc.runner status --output docs/runner/exp001-live`. Commit a summary only (raw dirs are gitignored).
2. Rebase the worktree branch onto squashed main: `git -C ../ApartSprint-wt-v12 rebase --onto main 666d41a v1.2-impl` (666d41a = the pre-squash commit the branch forked from; trees identical; branch backup/pre-squash keeps the old history). Then merge v1.2-impl into main and resolve the V09 client-request-id fix (main) against worktree validators.py changes. Run the full suite.
3. Stage-2 pinning: `python -m ccc.analysis pin --input docs/runner/exp001-live --out docs/stats/stage2/exp001` (F/S only). Write the Stage-2 addendum (STAT B3).
4. Tier-B M* availability census on EXP-001 real trajectories (counts only). If < 30%, supported is unavailable on real agents; narrow the claims.
5. Independent freeze review (prereg + v1.2 + Stage 2), then the held-out EXP-002 manifest (v1.2: N_m on all checkpoints, S1 on hashed 50%, 8 world-pairs, fx2 not applicable to real runs) and owner approval, then launch under the watchdog.
6. In parallel: STAT-002 analysis on EXP-001 (DEV, not evidence), figures regenerated post-v1.2, paper results slots, REL checklist (module 17).

Ollama server PID 57827 (local only, keep_alive -1) is still running. Stop with `kill 57827` if pausing for a long time.
