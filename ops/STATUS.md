# CCC STATUS (updated 2026-10-23 ~17:00 UTC by director)

**Phase:** 1 → Gate A work. Deadline 2026-10-26 11:59 UTC. Internal freeze target 2026-10-25 22:00 UTC; owner-review package 2026-10-26 01:00 UTC.
**Next gate:** GATE-A (deterministic F=S identity, knockout-only-changes-exposure, isolation, benign-cooperation fixture not mislabeled).

| Task | State | Owner |
|---|---|---|
| BOOT-001 | ACCEPTED | bootstrap agent (done) |
| SCI-001 | ACCEPTED (`docs/research/sci001/`) | source agent (done) |
| SCI-002 | active | causal-design agent (+≤1 reviewer child) |
| ENG-001/002 | active (offline only) | replay engineer (+≤1 child) |
| INF-001 | active (benchmark only; Modal blocked) | inference controller |
| PUB-001 (early) | active (outline, read-only Drive check) | publication agent |
| FIX-001 | queued: after SCI-002 fixture_spec | - |
| rest | queued (see `ops/tasks.json`) | - |

**Live agents:** 4 (+ up to 2 children) of 6.
**Budget:** new out-of-pocket $0.00.
**Owner items:** Modal $0 net-spend limit + credit; confirm Codex ChatGPT account (Codex unused until then); review subagent-created `.claude/settings.json`.
