## Task
W2-FIX2: address REV_PROTO2 findings 1–3 within assigned paths. Registry checked: RA-LEAD owns EXP-003; no W2-FIX2 lease. Direct assignment supplies scope; registry untouched.

## Status
Finding 2 CLOSED at code/test level: hash-bound measured-cost parameters determine full-block projection; actual configuration/lifetime, startup/shutdown, committed spend and both $45/$51 caps gate reservation and collector attachment. Placeholder measured values refuse before spawning.
Finding 3 candidate-inventory portion CLOSED: seven stale hashes refreshed; freeze/slots/feasibility/refresh modules and controls tests included. Final release approval/artifacts remain ORCH-owned.
Finding 1 template requirement CLOSED; actual measured feasibility remains OPEN. Targets, hypotheses, thresholds and seeds unchanged; no outcome-dependent edits.

## Artifacts
- `ccc/exp003/{feasibility,refresh_candidate,freeze,budget,modal_ctl,collector}.py`
- `tests/test_exp003_controls.py`
- `docs/enh/exp003/{PROTOCOL.md,FEASIBILITY_TEMPLATE.md,FREEZE_candidate.json,WIRING.md}`
- `ccc/exp003/offline_evidence/W2_FIX2_validation.txt`

## Validation
38 light EXP-003 tests passed in 28.16s. Exact guarded command: WIRING.md, “W2-FIX2 final light-test command”; pytest arguments: `-q tests/test_exp003_controls.py tests/test_exp003_probe.py tests/test_exp003_wiring.py --basetemp /tmp/W2-FIX2-release -p no:cacheprovider`.
Ran `PYTHONDONTWRITEBYTECODE=1 python -B -m ccc.exp003.refresh_candidate`: verified 218 code/6 evidence hashes and protocol. Initial fixture-resolver failures corrected; subsequent suite passed. Read-only cat/rg/sed inspections; no Git.

## Limitations
No measured-cost evidence invented. No FREEZE.json created/edited. No cloud teardown/billing certification, network, Modal commands, model/API calls or secret reads. Final approved freeze, manifest/plan and audited seed artifacts cannot be regenerated without ORCH inputs.

## Budget
$0 experimental spend. Codex GPT-6; exact serving identifier unavailable.

## Next
ORCH records valid spike measurements/reconciliation, resolves affordable planning scope prospectively, regenerates final release artifacts after integration, commits final freeze, and obtains release re-review.
