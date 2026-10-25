## Task
W2-PROTO: finish EXP-003 PF/PK collector wiring and draft freeze candidate.

## Status
Implemented and offline validated; candidate awaits independent review and ORCH freeze. No commits.

## Artifacts
- `ccc/exp003/collector.py`, `manifest.py`, `storage.py`, `mock.py`; updated `modal_runner.py`, `analysis.py`.
- `tests/test_exp003_wiring.py`.
- `docs/enh/exp003/PROTOCOL.md`, `FREEZE_candidate.json`, `WIRING.md`.
- Development mock evidence: `ccc/exp003/offline_evidence/{rows.json,analysis.json,validation.txt}`; 44 scheduled rows, shared B1/B2 pair ID.
- Full final mock traces: `/tmp/W2-PROTO-release/test_mock_full_pipeline0/`.

## Validation
80 combined EXP-003/replay tests passed; Modal manifest entrypoint test passed; final wiring suite 9/9 passed. Exact guarded Python/pytest commands and prior failed iterations are recorded in `docs/enh/exp003/WIRING.md`. Tests cover full fake-model collection and analysis CLI, PF/PK, probe ineligibility, cross-check/canary failures, request caps, missingness and backend validation. Candidate hashes verified against disk.

## Limitations
No live/model/network/Modal calls. Initial inherited replay provenance attempted read-only Git inspection; final tests blocked all subprocesses. No Git mutation or direct Git command. Cloud cost admission, in-flight cancellation and container teardown remain inference-controller responsibilities. Approval/hash fields do not independently authenticate approval. W2 has direct user assignment but no registry lease; ORCH owns registry updates.

## Budget ($0 + model used)
$0 experimental spend. Codex (GPT-6 family; exact runtime model ID unavailable).

## Next
Owner/director decisions: independent protocol review; accept directional hypotheses and first-k-complete semantics; audit/hash seed exclusions; choose Plan M or L; establish feasible capped budgets. Hard stop is 2026-10-25 09:00 UTC. ORCH refreshes hashes after edits, commits freeze and confirms before held-out runs. Never pool EXP-002.
