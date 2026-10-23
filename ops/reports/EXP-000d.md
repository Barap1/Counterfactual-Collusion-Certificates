# EXP-000d — reload detector correction

Status: implemented; offline validation passed. Task supplied directly by owner; registry inspected (EXP-000d not yet listed; no conflicting runner lease). No registry edits, commits, live calls, server inspection/actions, secrets, or remote network. $0 new spend. Other workers' changes left untouched.

## Changes

- Fingerprint excludes expires_at and optional load timestamps; retains digest, size_vram, context_length and listener PID checks. Version change remains a fail-closed condition.
- Local process inspection selects one model-serving descendant of the listener using `ps -axo pid=,ppid=,command=`. The existing dedicated single-model server requirement binds this runner to the requested resident model. Ambiguous/unavailable PID falls back to fingerprint plus canary, recorded in attestation and each session check. A later discoverable PID becomes the baseline; a changed known PID halts.
- Canary sent immediately after successful source completion, before eligible checkpoint branches, and after branches. Tests assert exact HTTP call positions 28, 29, and final call for the fixture. All probes still use the guard and frozen request cap.
- Status handles raw WATCHDOG_EXIT/STOP sidecars without treating them as hash envelopes; collector artifacts still require valid envelopes/seals. Failed/invalid/interrupted attempts report halted.
- Confirmed advisory lock release on halt by reacquisition tests. Lock file deliberately remains to preserve inode exclusion; README explains this and unchanged-code whole-world retry versus fresh directory after code changes. Historical pilot lock/output left untouched.

## Commands and evidence

Commands run: `cat` for CLAUDE.md, AGENTS.md, CCC_START_HERE.md, docs/spec/00_control_plane.md, ops/tasks.json, ops/reports/EXP-001_pilot.md and owned source/docs; `rg`, `find`, `sed`, `tail`, scoped Python read/edit scripts; `git status --short`, `git diff --stat`, `git diff --numstat -- ccc/runner tests/runner docs/runner/README.md`, `git diff --check`, scoped `git diff`. No master spec or secrets read.

Final test command:
`starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner.offline unittest discover -s tests/runner -t .`

Final captured output (synthetic fixture calls only):

```
..............................................................
----------------------------------------------------------------------
Ran 62 tests in 27.052s

OK
fixture counts: 183 guarded calls; 3 canaries; 8 branches; complete
fixture counts: 50 guarded calls; 2 canaries; 8 branches; invalid
fixture counts: 30 guarded calls; 2 canaries; 8 branches; invalid
fixture counts: 183 guarded calls; 3 canaries; 8 branches; complete
```

The prior intermediate run also passed 61 tests; final run adds subprocess selection coverage.
Four integration scenarios total 446 fake guarded HTTP calls and 10 canaries; 16 completed branch records plus 16 invalid scheduled branch records. Real calls made by this task: 0. These counts are fixture evidence, not experimental outcomes.

Read-only historical pilot check:
`starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.runner.offline ccc.runner status --output docs/runner/exp001-pilot`
returned exit 0, status halted, live_calls 1 (historical), verified_artifacts 15, dev02_B1 attempt_0001 failed, seven slots without attempts.

## Owned files changed

ccc/runner/live.py; ccc/runner/collector.py; ccc/runner/storage.py;
tests/runner/test_live.py; docs/runner/README.md; ops/reports/EXP-000d.md.

Limitations: no real Ollama compatibility run was authorized or performed. Canary is a secondary heuristic, not proof of absence of every reload. Process matching relies on the dedicated single-model listener and an unambiguous runner command. Next: integration review, then owner-controlled fresh-output pilot if authorized.
