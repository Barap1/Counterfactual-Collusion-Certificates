# BENCH-ALIGN2 handoff

**Task / Status:** Complete A4–A6. CCC-L v1 adds observable `L3 excluded`;
v0 remains unchanged and runs beside primary v1. RQ2 uses Bayes-given-S;
original RQ4 is unchanged and DEV-informed RQ4b is separate.

**Artifacts:** `ccc/bench/{methods,report,__main__}.py`;
`tests/test_bench_alignment.py`; `docs/enh/bench/{README,ALIGNMENT,VALIDATION}.md`;
`dev_run/RESULTS{,_dev}.json` (both explicitly development), including
figure-compatible P2/eps=0/seed-13000 `twin_exhibit`;
`hash_manifest.json`; regenerated demo JSON/JS; `figure_compat/`.

**Every DEV numeric change:** Exact before/after values for all **57,457**
changed/added/removed numeric fields are listed in
`docs/enh/bench/align2_numeric_delta.json`, with artifacts and semantic paths.
Pre-change artifacts: `docs/enh/bench/bench_align_snapshot/`.
Methods **12→13**; v1 adds **600** negative outputs (50 per
P1/I3–I5, P2/I4–I5, P3/I5 cell, each stratum).
P2/I4 and P3/I5 pair correctness: v0 **0/50** to v1 **50/50** at eps=0,
**33/50** at eps=.1; CP95 **[0,.0711217]→[.9288783,1] / [.5123475,.7879453]**.
RQ2 fail→pass; new RQ4b passes. RQ4/RQ5 still fail. All observations and
12 original methods are identical; population and CCC support numbers unchanged.

**Validation / Commands:** Final DEV command/log and every exact command are
in `docs/enh/bench/VALIDATION.md` and `align2_validate.sh`: DEV run, enumerate,
report, hashes, exclusion/replay/delta audits, all three prescribed demo scripts,
targeted tests, full guarded suite, figure-consumer check and lineage checks.
**30/30 bench tests; 453 guarded tests: 449 passed, 4 skipped, zero failures.**
Zero stale demo sources; 24 frozen files unchanged; zero symmetry violations/crashes.

**Limitations:** Development only; noisy v1 pair correctness remains .66;
RQ5 failures/undefined denominators retained. No prospective seeds or FREEZE.json.

**Budget:** $0; Codex/GPT-6 session; no experimental model/API calls,
network, subagents or git mutations.

**Next:** Director review of code, numeric ledger and prospective freeze.
