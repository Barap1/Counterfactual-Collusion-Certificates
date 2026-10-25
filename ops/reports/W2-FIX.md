## Task
W2-FIX: resolve REV_PROTO findings within assigned EXP-003 code/protocol paths. Direct user assignment; RA-LEAD registry checked, no W2-FIX lease; registry untouched.

## Status
Closed at code/protocol level: findings **2, 3, 4, 5, 6**, and finding **1**'s request-budget, units, projection and admission requirements. Finding **1 measurement remains OPEN** for ORCH's valid GPU spike, reconciled usage and demonstrated block feasibility. Release remains blocked pending ORCH freeze and independent re-review.

## Artifacts
Implementation: ccc/exp003/budget.py, ccc/exp003/modal_ctl.py, ccc/exp003/modal_server.py, ccc/exp003/modal_runner.py, ccc/exp003/manifest.py, ccc/exp003/collector.py, ccc/exp003/analysis.py, ccc/exp003/freeze.py, ccc/exp003/slots.py.
Tests: tests/test_exp003_controls.py.
Documentation: docs/enh/exp003/PROTOCOL.md, docs/enh/exp003/WIRING.md.
Evidence: ccc/exp003/offline_evidence/W2_FIX_validation.txt, ccc/exp003/offline_evidence/W2_FIX_hashes.json.

## Validation
33 light EXP-003 tests passed. Exact guarded Python/pytest command is in WIRING.md; stdout saved above. Placeholder-admission dry-run refuses unverified hash/commit without creating FREEZE.json. AST syntax and byte-identical EXP-002 quotation checks passed. Inspection used cat/rg/sed; Python performed edits/checks. No Git, Modal commands, network, prohibited secret reads or experimental model calls.

## Limitations
Cloud stop/teardown and provider billing behavior were not exercised. Rates are conservative estimates. Commit authenticity/runtime identity require ORCH attestation. Candidate hashes are stale after these changes; refreshed changed-file hashes are evidence, not freeze approval.

## Budget
$0 experimental spend. Codex worker; exact runtime model identifier unavailable. Live budget ledger untouched; runtime events use ccc.budget_ledger.v1.

## Next
ORCH measures valid GPU feasibility, refreshes full dependency hashes, supplies audited artifacts/final FREEZE.json, verifies live shutdown, and obtains independent re-review before held-out launch.
