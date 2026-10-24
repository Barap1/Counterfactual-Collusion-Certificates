Task: FIX-001 — disclosed validity metadata repair (REV001 F-5).

Status: Complete. Held-out adapter retained passes but used engine IDs; legacy loader also discarded passes. loaders.py now adds protocol mappings, normalizes NA, and retains failures. No pipeline/statistic/threshold/status-rule edits. All 16 certificates now have all_valid=true; five spurious validity_unestablished reasons disappear. No STATUS changes: 0 supported / 11 not_supported / 5 inconclusive. Original-confirmatory primary and all numeric serialization unchanged.

Artifacts: ccc/analysis/loaders.py; tests/test_fix001_validity_mapping.py; docs/analysis/exp002_heldout_v3/{CORRECTION.md,verify_correction_v3.py,output_diff_v3.json} plus 39 rerun outputs; docs/enh/fix/{COMMANDS.md,raw_verification.json,provenance.json,regression_before.log,regression_after.log,tests.log,verification.log,analysis.log} and reproducible wrappers.

Validation: Tests written first; six initial tests produced seven assertion failures. Final eight regression tests pass. Full guarded offline discovery: 415 tests, 116.383s, OK (4 skips). Verifier: 39 files, 222 changed fields/records, 33,292 identical numeric tokens; every CSV cell compared. Archive: all 15,728 regular files match existing input; 143 valid / 56 unrun branches. Exact commands: docs/enh/fix/COMMANDS.md. Main commands: python docs/enh/fix/run_tests.py; python docs/enh/fix/run_analysis.py; python docs/analysis/exp002_heldout_v3/verify_correction_v3.py (existing venv and documented guards).

Limitations: No extraction; requested external destination is outside writable roots. F-10 assessed only, unchanged. study.py's pre-existing v2/current hash discrepancy is disclosed; current source matches HEAD and scientific outputs match v2. Four standard guard/optional-test skips remain. No original analyses overwritten.

Budget: $0 new spend; Codex (GPT-6-based agent); no experiment/model/API/network calls or git mutations.

Next: Director reviews correction/provenance and decides F-10 reason-label policy.
