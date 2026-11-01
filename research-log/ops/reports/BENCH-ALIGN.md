# BENCH-ALIGN handoff

**Task:** Align ccc/bench with R2 §4–§10 before director freeze.

**Status:** Implemented; complete DEV rerun and report. No prospective seed
list/world generated. Existing CRN verified and tested; frozen methods unchanged.

**Artifacts:** `ccc/bench/{seeds,report}.py` and aligned CLI/roster/scoring;
`tests/test_bench_{core,alignment}.py`; `docs/enh/bench/ALIGNMENT.md`,
`VALIDATION.md` (exact guarded commands), `seed_exclusions.json`,
`align_delta.json`, `hash_manifest.json`, `enumeration/`,
`dev_run/RESULTS_dev.{json,md}`, `dev_run/strongest_baseline.json`.
Original BENCH-IMP evidence preserved in `bench_imp_snapshot/`.

**Validation:** 27 bench tests pass. Final guarded suite: 450 tests,
445 passed, one failed, four skipped. Sole failure: demo manifest pins old DEV
source hashes; exact mismatches in `align_integration_mismatches.json`.
DEV/replay/enumeration/report/hash/exclusion audits pass: 13,800 records,
50 DEV seeds, zero symmetry violations, 24 frozen files unchanged.
All 11,400 matched original records are byte-identical after class metadata
normalization. RQ3: eps=0 unchanged at 12/50; eps=.1 now 5/50; legitimate-member CCC supports unchanged:
664. RQ1/RQ3 pass DEV criteria; RQ2/RQ4/RQ5 fail; RQ6 descriptive.
B2+ wins DEV balanced accuracy (.6074554 vs B3b .5357143).
Historical-only census: 27,209 sources, 6,247 distinct seeds.

**Limitations:** Full suite remains red until the demo owner refreshes its
manifest/data. CCC-L abstains on negative members, failing literal pairwise
correctness criteria; failures remain visible. Population H now uses the frozen no-coordination J oracle; RQ3 exposure
values are unchanged. No prospective
validation or independent freeze approval claimed.

**Budget:** Codex session; $0 new spend, zero experimental model/API calls,
network access, sub-agents or git mutations.

**Next:** Director review of negative DEV results and freeze metadata; demo
owner integration refresh; independent review before committing FREEZE.json.
