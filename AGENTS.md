# CCC agent rules (Codex and other agents; keep consistent with CLAUDE.md)

Read `CLAUDE.md` in this directory - the same rules apply to you. Key points:
- Work only on the task ID and owned paths you were given; check `ops/tasks.json` leases.
- Load only the `docs/spec/` modules named in your brief; never the master spec.
- No model/API calls for experiments, no secrets read or printed (`.env`, `compute.env`, `*.local.json`), no network unless your brief allows it.
- No git push/force/reset/clean. Write evidence to disk; return a short handoff with exact paths and commands run.
