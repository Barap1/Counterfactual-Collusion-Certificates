# CCC STATUS (director)

**Phase:** v1.2 implementation + dev pilot. Deadline 2026-10-26 11:59 UTC. EXP-001 hard stop 2026-10-24 09:00 UTC; held-out latest start 2026-10-24 14:12 UTC; freeze 2026-10-25 22:00 UTC.
**GATE-A: FAIL (v1.1).** Integrity checks demonstrated (9/9 independent fault injections). v1.1's N-placebo makes "supported" unreachable. Amendment v1.2 adopted by REV-AMD (r3), now being implemented in worktree `../ApartSprint-wt-v12` (branch v1.2-impl). Gate A is re-run on v1.2.

| Task | State | Owner |
|---|---|---|
| EXP-001 | pilot 2 (1 checkpoint, watchdog) running; full run awaits report to owner | Claude Haiku operator |
| AMD-001 | finalizing protocol.md v1.2 | Claude Sonnet |
| AMD-IMP-A | core v1.2 impl in worktree | Codex gpt-6.1-sol/medium |
| AMD-IMP-B | constructed controls derivation (no runs) | Codex gpt-6.1-sol/low |
| Next | merge v1.2 → Gate A v1.2 → REV check → EXP-001b (N_m dev) → STAT freeze → held-out | - |

**Budget:** $0 out-of-pocket. **Tests:** 263 OK on main (ENG-005).
**Held-out:** compute fallback D-022 (S n=1 on 50%, 43% buffer). Not yet approved by owner.
