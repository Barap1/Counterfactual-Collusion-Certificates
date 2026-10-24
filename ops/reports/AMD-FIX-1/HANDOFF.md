# AMD-FIX-1 → DEV Gate A v1.2

Task / Status: completed; overall Gate A **FAIL**, module-13 core **PASS**. User assignment is authority; the stale task registry has no AMD lease entry and was not changed.

Fixes: `ccc/audit/commitments.py` derives sender commitments from the shared extractor with author/world-alias bindings; the private-quantity pattern is byte-identical to its original pattern. `ccc/audit/decision.py` requires selected M*, the selector record and matching per-N V3 passes; bare/deprecated filler cannot support or enter study vetoes. `ccc/audit/gate_a.py` selects and logs before continuations and runs actual N_m branches. Regression tests cover both reported phrases, aliases, malformed provenance, legacy study exclusion and native N4 execution.

Artifacts: `docs/gate_a/v1.2/GATE_A_v1.2.md`, `gate_a_results.json.gz`, prediction/census/constructed companion files. `files.txt` inventories sources/tests/evidence; `commands.md` and `tests.json` contain exact reproduction commands and exits.

Validation (passed/run): audit 106/109, replay 54/58, runner 65/65, fixtures 71/71, review 9/9; full 322/332 (7 skips, 3 missing-pilot-archive errors, zero assertion failures). 800 fx2 cells, 740 eligible N_m manifests, actual F4/K4/S2/N4, zero runner errors/source changes; 390/390 native/oracle effect comparisons agree.

Results: A5 amended 16/68 (legacy 20/120), A6 any/intended 350/360; both FAIL. Supported: headline-confusion population 4/280; all DEV 8/800; constructed 10/30, with 26/30 predictions matching and none voided. Scorecard: 14 CONFIRMED, 4 FALSIFIED, 3 UNTESTED. Both census files are byte-identical; availability 0/740 → 740/740; EXPLORATORY under DEV-002.

Limitations: missing Tier B/blind labels/skipped contract positive; four constructed singular-“Verified cost” misses; 78 empty non-gating frozen-grid confidence sets. Superseded attempts are explicitly archived and excluded.

Budget: $0; no network/live inference/Ollama operations, commits, threshold changes or live-checkout writes.

Next: independent review; retained A5/A6 failures block Gate A clearance.
