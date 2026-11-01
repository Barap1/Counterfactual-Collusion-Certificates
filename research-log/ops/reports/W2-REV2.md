## Task
W2-REV2: independent skeptical re-review of EXP-003 fixes, protocol and candidate hashes. Direct assignment; task registry checked, no W2-REV2 lease recorded.

## Status
ISSUES. Findings 4–6 closed; finding 3's admission implementation is substantially closed, with stale candidate inventory/final release artifacts pending. Finding 2 adds concrete controls but fails to bind session duration/configuration to projected block feasibility. Finding 1 needs valid GPU measurements, reconciliation and a frozen projection; release is not waiting only on the spike.

## Artifacts
- `docs/enh/exp003/REV_PROTO2.md`
- `ops/reports/W2-REV2.md`

## Validation
Read-only `cat`, `rg`, `sed`, `nl`; guarded `CCC_STARTER_ROOT="$PWD/starter/collusion_hackathon" PYTHONDONTWRITEBYTECODE=1 python -B - <<'PY'` inline probes. Details and reproducible hash command are in the review. Seven of 213 code hashes and the protocol hash are stale; all three evidence hashes match. New freeze/slots modules lack candidate entries. Confirmatory refusals, exploratory labels, exact sign-flip arithmetic, terminal slots and both monetary watchdog callbacks checked. Mocked launch reached a 60-second reservation for a 4,000-second projection. AST parsing passed. Initial tempfile discovery was denied before any write; corrected read-only probes passed.

## Limitations
No pytest rerun, real final-freeze admission, historical archive rehash, live teardown or billing verification. No Git, network, Modal, model/API calls or prohibited secret reads. Only the two assigned Markdown files written; science pins unchanged.

## Budget
$0 experimental spend; Codex reviewer. Exact serving model identifier unavailable.

## Next
ORCH binds actual session configuration/lifetime to feasibility, completes valid measured feasibility/reconciliation, refreshes inventory and final freeze artifacts, verifies shutdown, and obtains release re-review.
