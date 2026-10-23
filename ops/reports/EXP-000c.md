# EXP-000c handoff

Task / Status: Implemented real-shaped Ollama load-session detection; offline tests pass.
Registry checked: ops/tasks.json contains EXP-000b ACTIVE but no EXP-000c entry;
explicit director assignment supplies ownership. Registry and other workers' paths untouched.

Design: keep_alive=-1 on all generation requests. Fingerprint digest, size_vram,
context_length, expires_at, /api/version and local listener PIDs; retain optional
loaded_at/load_session_id. Mandatory loopback listener validation remains. Fixed canary
prompt, seed 731921, T=0.7, max_tokens=16 before/after each eligible checkpoint branch
set; compare UTF-8 output bytes across the session. GuardedChatClient admission, mirrored
ledgers, request-cap counting and canary request/response artifacts include both probes.
Canary mismatch/failure or changed fingerprint invalidates all checkpoint branches with
model_reload, null outcomes and retained raw traces. Before-boundary failures use the
same invalidation path. Ordinary calls retain before/after fingerprint checks.

Artifacts / Files touched:
- ccc/runner/live.py
- ccc/runner/collector.py
- tests/runner/test_live.py
- docs/runner/README.md
- ops/reports/EXP-000c.md

Validation command (repository root; offline audit guards active):
```sh
starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests/runner -t .
```
Real captured output (fixture counts are synthetic calls, not real inference):
```text
......................................
----------------------------------------------------------------------
Ran 38 tests in 20.396s

OK
fixture counts: 182 guarded calls; 2 canaries; 8 branches; complete
fixture counts: 50 guarded calls; 1 canaries; 8 branches; invalid
fixture counts: 182 guarded calls; 2 canaries; 8 branches; invalid
fixture counts: 182 guarded calls; 2 canaries; 8 branches; complete
```
Counts in test order: legacy no-reload; legacy load-ID change mid-branches;
real-shaped ps with final-canary change only; real-shaped ps no-reload.
`git diff --check -- ccc/runner tests/runner docs/runner/README.md` exited 0, no output.
Tests use the real stdlib HTTP handler/parser over in-memory streams; no bind/connect.

Operator commands (documented, NOT executed):
```sh
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NO_CLOUD=1 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1 OLLAMA_CONTEXT_LENGTH=32768 OLLAMA_KEEP_ALIVE=-1 ollama serve
curl --fail --silent --show-error http://127.0.0.1:11434/api/generate -H 'Content-Type: application/json' -d '{"model":"gemma4:26b","keep_alive":-1,"options":{"num_ctx":32768},"stream":false}'
```
Limitations: no live compatibility assertion. Canary detection follows supplied INF-001
observations, not a guarantee every reload changes output. Infinite keep-alive is an
operator requirement; changing expiry fails closed. Two canaries consume the existing
frozen request cap per eligible checkpoint; the cap was not raised. Listener inspection
still fails closed if unavailable, to preserve the local-only bind requirement.
Budget: $0; zero live model calls; Ollama not started; no secrets read; no commits.
Next: director review/integration; INF-001 operator may validate against authorized server.
