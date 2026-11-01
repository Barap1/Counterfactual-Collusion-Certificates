# EXP-000b handoff

Task: runner follow-up for Gate-B. Status: implemented and offline-verified; live backend
compatibility remains unverified. Direct user ownership authorized the scoped paths;
`ops/tasks.json` had no EXP-000b entry/lease. No registry or other workers' paths edited.
Budget: $0; no live model calls, Ollama startup, secrets access, commits, or remote network.

Changes: per-arm counts; default held-out F4/K4/S2/N4, N on exactly half the frozen
checkpoint slots; dev F4/S4/K4/N2 on all slots. Deterministic arm/replicate/turn/call seeds
from master seed, with derivation in README; T=0.7. Guarded live local transport checks
listener bindings, exact digest, resident context and session identity/expiry before/after
calls and checkpoints. Reload invalidates every scheduled branch, retains traces, halts,
and permits only one explicit whole-world retry. Shared and attempt budget ledgers are
mirrored. Held-out execution requires frozen STAT-001 manifest-bound approval/hash.
EXP-001 manifest: four dev pairs, seeds 2–5, B1 deception/B2 legitimate, fixed order;
09:00Z Oct 24 hard stop checked before worlds and after source/before branches.

Limitation: `/api/ps` must expose trustworthy `loaded_at` or `load_session_id`. A server
exposing only renewable `expires_at` is refused; expiry cannot prove absence of reload.
INF-001 must provide session telemetry before that server can collect. No compatibility
or scientific result is claimed. The sandbox denied localhost bind, so the fake HTTP
server runs stdlib HTTP parsing/handling over in-memory streams under the unchanged
socket/DNS audit guard.

Validation (repo root):

```sh
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner.offline unittest discover -s tests/runner -t .
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner.offline ccc.runner plan docs/runner/exp001_manifest.json
git diff --check -- ccc/runner tests/runner docs/runner
```

Actual: **35 tests, 15.298s, OK** (`docs/runner/exp000b-tests.txt`); diff check clean;
`docs/runner/exp001-plan.json` records 8 base trajectories/112 planned continuations.

Operator command, after residency prerequisites in README:

```sh
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner run docs/runner/exp001_manifest.json --output docs/runner/exp001-live --live
```

Files: `ccc/runner/{__main__,collector,manifest,live}.py`,
`tests/runner/{test_runner,test_live}.py`,
`docs/runner/{README.md,dev_manifest.json,exp001_manifest.json,exp001-plan.json,exp000b-tests.txt}`,
`ops/reports/EXP-000b.md`.
