# BENCH-IMP validation and exact commands

All benchmark evidence is **development**. No prospective world was generated.
New benchmark draws and new tests use only seeds 13000–13049. The separately
requested existing offline suite retains its frozen fixture seed contracts.
No frozen production file was edited. All experiment computation is local Python;
new spend $0, model/API inference calls 0, network access 0, git mutations 0.

## Commands

Run from the repository root, with the existing interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest tests.test_bench_core > docs/enh/bench/targeted_tests.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -u docs/enh/bench/prewarm.py > docs/enh/bench/prewarm.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -u docs/enh/bench/prewarm.py > docs/enh/bench/prewarm_corrected.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -u -m ccc.bench run --block dev --out docs/enh/bench/dev_run > docs/enh/bench/dev_run/run.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.bench enumerate --out docs/enh/bench/enumeration > docs/enh/bench/enumeration.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.bench hashes > docs/enh/bench/hash_manifest.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python docs/enh/bench/verify_run.py > docs/enh/bench/dev_run/verification.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python docs/enh/bench/run_tests.py > docs/enh/bench/offline_suite.log 2>&1
```

`run_tests.py` invokes `python -m tests.replay.offline_runner -s tests -t .`,
redirecting only the existing suite's persistent coverage_simulation.json write
to the owned docs/enh/bench directory. It does not patch production modules.
The release guard forbids network, credentials and real held-out runner access.
Its pre-existing real-manifest test skip remains in force.

The actual missing-freeze CLI refusal (exit 2, before output creation) is saved
in `prospective_refusal.log`. Freeze unit tests additionally cover exact hash
mismatch, prior-seed reuse, schedule counts, and missing freeze.

## Corrections made during benchmark development

- Added explicit task tokens to duplicate/paraphrase carriers so the frozen
  N selector excludes them and selects the actual same-sender inert filler.
  No selector or baseline threshold was changed.
- Converted class-count boolean keys to explicit strings for finite JSON when
  bool and `n/a` labels coexist. First CLI attempts generated the DEV census but
  failed during serialization, before audited study records were written; a
  regression now serializes the entire exact partition.
- Required persistent cost-probe harm as well as denied authorization for the
  transfer-record CCC-L branch: an unauthorized efficiency policy otherwise
  remained an off-pair legitimate counterexample. This enforces the specified
  separation requirement, before the completed DEV study; no threshold tuning.
- Replaced a proposed fixed alternating A1a/A1b population schedule with an
  independent fair named RNG so the pooled prevalence sample is an iid mixture.
- Separated pairwise discrimination from global identifiability and added
  explicit observed-versus-enumerated joins.
- Corrected P6's initially unmatched factual payoffs: the productive variant now
  shares the transfer ledger under F for every random action; useful-information
  removal reduces each actor's productivity by 2*d under K/J/REF, never N. Thus
  twin F traces match under both epsilon strata, K hurts all actors in the useful
  member, and the pair separates at I1 as specified. This new information-gated
  payoff is a benchmark-generator correction, not a frozen method change or
  replay artefact; all P6/productive policy recipes have the useful-information
  mechanism. Cached calls for the old variant are harmless unused pure results.

Two initial sequential DEV invocations were interrupted during exact numerical
interval work, then replaced by a bounded two-thread pure-call prewarm followed
by the complete CLI. Cached results remain keyed by the entire argument payload,
Python/NumPy version and frozen decision/placebo hashes. No resampling or sample
compression is used. Diagnostics `call_plan.json`/`call_costs.json` count calls,
not experimental units or model/API calls. Failed read-only process-list probes
(`pgrep`, `ps`) returned sandbox errors; no process metadata was obtained.

## Results

The initial full release discovery ran 441 tests: 436 passed, one failed, four
skipped. The failure was `tests.test_demo_data.DemoDataTests.test_manifest_complete_hashes_and_size`:
`demo/data/MANIFEST.json` expects the source hash of `docs/enh/MISSION.md` to be
`063c88f0fd8cdfad0fcbd4451a7c7109b76a42d645af3343c36503d7382456a5`, while the
read-only file hashes to
`73a274d60afaa2eec0a892d99156396eb5e23ebaff053f12c0147daeb6b14a37`.
Both are outside this task's write scope and remain unchanged by BENCH-IMP.
A final suite run and complete DEV artifact verification are recorded below.

## Final results (2026-10-24)

- Targeted benchmark suite: **19 tests passed**, `targeted_tests.log`.
- Complete guarded offline discovery: **442 tests; 437 passed, one failed,
  four skipped**, 121.718 seconds, `offline_suite.log`. The sole failure is the
  same unrelated demo/MISSION source-hash mismatch described above. Neither
  file was changed. A clean repository-wide suite therefore remains unavailable
  within this task's write scope; the failure was not suppressed or rebaselined.
- DEV CLI exit 0, exact enumeration exit 0, hashes exit 0, artifact verifier
  exit 0. `dev_run/COMPLETE.json` exists and its code hashes match the current
  source and run manifest.
- **12,600** instance/set records, **12** methods, **50** independent seed blocks.
  Each epsilon stratum is analyzed separately. Eight continuations remain nested
  within each noisy arm; no replicate or twin is counted as a new unit.
- **Zero** identical-view twin symmetry violation events; no method separates
  twins before the enumerated observable separator. All realized CCC-L L3 claims
  are in pure positive attribution classes, including the stochastic stratum.
- Complete seed 13000 replay, both epsilon strata: **252** records with identical
  canonical bytes. The **24** frozen source/data files match the initial recorded
  hashes (`frozen_sources_before.json`).
- Pairwise separators across all 100 seed/epsilon combinations per type:
  P1 I3, P2 I4, P3 I5, P4 I1, P5 I0 (same-label control), P6 I1.
- RQ3: **12/50 = .24**, CP95 **[.1306099162, .3816907481]**. This is development
  evidence only. Every population seed is in the authorized DEV block.
- Frozen CCC exposure support on legitimate P2/P3: **664 member/set records**,
  retained and flagged in the DEV report. This is an L2 exposure verdict, not
  collusion attribution, and 664 is not an independent sample size.

`prewarm.log` records the initial 960-call prototype cache; after the documented
P6 correction, `prewarm_corrected.log` records all **927** unique calls for the
final design (1179.3 seconds, including cache hits). Unused prototype entries do
not enter study outcomes. Both passes call the frozen decision function with
exact inputs; all retained numeric results are reproduced by the final CLI.

Inspect `dev_run/verification.json`, `scores.json`, `population.json`,
`symmetry.json`, `separators.json`, `frontiers.json`, `records.json.gz`, and
`partitions/`. `hash_manifest.json` is the final source manifest for director
review and later freeze. The hand-written short DEV report summarizes these
verified numeric artifacts; it is not itself an input to any method or score.

No prospective block, network access, external inference, git mutation, or
out-of-scope source edit was performed. An independent scientific review and
director-owned R2 freeze remain next steps, not completed validation claims.

## BENCH-ALIGN — R2 alignment (2026-10-24, development only)

Implementation details, the exact seed encoding and historical census procedure
are in ALIGNMENT.md. No prospective seed list or world was materialised. The only
seed lists generated by tests use dummy protocol text/hash and temporary roots.
No protocol, frozen method, historical result or out-of-scope source was edited.

Exact final commands (from the repository root):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest tests.test_bench_core.FreezeTests tests.test_bench_alignment.AlignmentTests.test_collision_with_previously_used_label_is_salted tests.test_bench_alignment.AlignmentTests.test_prospective_schedule_is_only_frozen_file_values > docs/enh/bench/align_freeze_tests.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -u -m ccc.bench run --block dev --out docs/enh/bench/dev_run > docs/enh/bench/align_dev_run_strata.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.bench enumerate --out docs/enh/bench/enumeration > docs/enh/bench/align_enumeration.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.bench hashes > docs/enh/bench/hash_manifest.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.bench run --block prospective --out docs/enh/bench/should-not-exist > docs/enh/bench/align_prospective_refusal.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.bench report --run docs/enh/bench/dev_run > docs/enh/bench/align_report.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python docs/enh/bench/audit_seed_exclusions.py > docs/enh/bench/align_seed_audit.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python docs/enh/bench/verify_run.py > docs/enh/bench/dev_run/verification.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python docs/enh/bench/compare_alignment.py > docs/enh/bench/align_delta.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest tests.test_bench_core tests.test_bench_alignment > docs/enh/bench/align_targeted_tests_final.log 2>&1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python docs/enh/bench/run_tests.py > docs/enh/bench/align_offline_suite_final.log 2>&1
```

All Python module invocations used the existing interpreter and release guard. The wrapper still
redirects only coverage_simulation.json into owned space.

The first alignment DEV run completed. A subsequent development rerun was
rejected at finalisation because source checks were tightened while it was in
progress (`align_dev_run_final.log`); it was not accepted as completed evidence.
The final complete rerun is `align_dev_run_strata.log`, with hashes verified
by verify_run.py. An earlier full-suite attempt overlapped that development
rerun and encountered the deliberately absent COMPLETE.json; the final full
suite was rerun after completion. These intermediate logs are retained.

### Changes and numeric effects relative to BENCH-IMP

Every change is listed in align_delta.json and ALIGNMENT.md; the original
records/summary files are preserved in bench_imp_snapshot/. No payoff, noise,
continuation RNG, census recipe, method or threshold changed.

- CRN was already implemented. New direct tests cover identical policies,
  every arm/probe/stratum and eps=.1 full-output RQ1 symmetry. Zero violations
  remain zero. RQ1 now keeps pair types and cells with no eligible equivalent
  twins: 864 cells, 336 eligible, each eligible cell has 50 DEV units and CP95
  upper bound .0711217 for zero events; the others are explicitly inapplicable.
- The standalone roster now implements the protocol's nine classes. Removed
  harmful/paraphrased standalone copies (1,200 records); added explicit common
  cause, redundant, suspicious-no-harm and info-bearing copies (2,400 records).
  Relay/useful names were aligned and the three invalid variants grouped under
  one invalid class per seed. Total records: **12,600 → 13,800**. All **11,400**
  matched records are byte-identical after metadata normalization. Enumeration
  partitions/frontiers and all population exposure values are unchanged.
- Because the roster changes the member mixture, 396 aggregate method/axis/set/
  stratum score cells change; every old/new cell is stored in align_delta.json.
  No individual matched output changed. DEV I1 balanced accuracy, averaged over
  the two equal-size strata: B2+ **.5997596 → .6074554**, B3b **.5432692 → .5357143**.
  B2+ wins both before and after. strongest_baseline.json freezes the aligned
  DEV choice and retains stratum-specific values; no prospective selection.
- Added literal RQ1–RQ6 criteria, T1–T10, figure data, per-class M/H/E scores,
  paired discordant-unit CP intervals and continuous oracle-effect cluster
  intervals (10,000 PCG64 bootstrap draws, seed 20261026). This adds analysis
  outputs without changing observations. RQ1 and RQ3 pass DEV-sized checks;
  RQ2/RQ4/RQ5 fail and RQ6 is descriptive. RQ2/RQ5 disclose A2 circularity.
  CCC-L abstains on negative members, so literal two-member correctness is not
  established; zero-denominator criteria remain visible, never imputed.
- RQ4 B2+ over-attribution: P2/P3 **50/50** at eps=0 and **33/50** at eps=.1;
  P6/benign cooperation **0/50** in both strata. Hence the whole RQ fails.
  RQ3 at eps=0 remains **12/50=.24**, CP95 **[.1306099,.3816907]**. Frozen CCC supports
  on legitimate members remain **664** member/set records, now explicitly
  tabulated with independent-unit CP intervals under RQ6 as “harmful exposure,
  not attributable”. This is not a count of independent observations.
- Seed/freeze changes affect only future prospective execution: exact §4
  hash/salt rule, global uniqueness, full historical seed exclusions, R2 schema,
  protocol/code/enumeration/prior hashes, parameters, past timestamp, independent
  review, frozen baseline and seed-file checks. Missing freeze refusal exits 2
  before creating output. Every prospective partition is hashed before methods;
  prospective output cannot overwrite an existing run. None was run here.
- Method exceptions are retained as failed outputs for every method and counted
  in the crash table. Final DEV has zero method crashes. The invalid class keeps
  all three corruptions, with H/E unavailable rather than zero-imputed.

### Final evidence

- Bench regression suite: **27 tests passed**, 53.200 seconds;
  align_targeted_tests_final.log. Five focused freeze/skip/schedule tests also pass.
- Historical exclusion replay: **27,209 sources, 6,247 historical seeds**;
  source ledger and all four exclusion hashes reproduce exactly. No prospective
  list was drawn; tests exercise zero intersections using dummy hashes only.
- Complete final DEV: **13,800 records, 50 seed blocks, 12 methods**, eps=0/.1,
  all seeds 13000–13049. Verifier passes; all 24 frozen files remain unchanged,
  and all 276 records of the complete seed-13000 replay are byte-identical.
- Enumeration, hashes, automatic report, explicit report CLI, historical seed
  audit and artifact comparison exit 0. Missing-freeze prospective refusal exits 2.
- Final complete guarded offline suite (after DEV completion): **450 tests,
  445 passed, one failed, four skipped**, 169.530 seconds;
  align_offline_suite_final.log. The sole failure is
  `tests.test_demo_data.DemoDataTests.test_manifest_complete_hashes_and_size`.
  Its demo manifest still pins pre-alignment hashes for bench DEV COMPLETE.json,
  DEV_REPORT.md, manifest.json and records.json.gz. All four expected/actual
  hashes are in align_integration_mismatches.json. The first failing comparison
  is COMPLETE.json, expected
  `65b222516a0dfcaf7c132e9531daa50958c6c09839dd50b3c37d370f66d9b205`, actual
  `23c50a204a700381d4075c4c32e7388a060e78847841f486d3e1ca53e070ad62`.
  This is an integration consequence of the requested DEV refresh, rather than
  the older MISSION mismatch. demo/data/ is outside BENCH-ALIGN ownership; no
  test was suppressed and no demo manifest was rebaselined. Its owner must
  rebuild/revalidate the explorer data against the aligned DEV artifacts.
- Scoped `git diff --check` exits 0. Read-only inspection used cat, sed, rg,
  filesystem listing, git diff/status and JSON/tarfile readers. No git mutation,
  network request, secret read, experimental inference or new spend occurred.

All reported outcomes are **development**. A passing DEV-sized criterion is not
a prospective pass. RQ2/RQ4/RQ5 failures are retained in both report formats.
Population H is now defined using the frozen J no-coordination reference for
A1a/A1b; its strict >2.5 threshold is distinct from exposure >=2.5. The frozen
agent code has no independent public sender carrier in these two mechanisms:
removing all sender directives also removes the receiver's induced claim/block
relay. Both F/J expected outsider rewards are retained per world. This supplies
the §5 truth previously missing in BENCH-IMP; all existing eps=0 RQ3 exposure values are unchanged. The population now also
receives the required eps=.1 stratum, evaluated by exact expectation over the
frozen iid error law; its estimate/interval are separate, never pooled. R=8
continues to apply to observed structural auditor arms. Iid oracle continuation
replication would add no independent data.
No new method version, frozen artifact or real-agent conclusion is asserted.

Final population-stratum completion: eps=0 **12/50=.24**, CP95
[.1306099,.3816907]; eps=.1 **5/50=.10**, CP95 [.0332751,.2181354].
Both pass the point-estimate criterion; only eps=.1 is supported with margin.
H is defined and retained in both strata (12/50 and 5/50, respectively).
The two estimates share seeds and are never pooled. The latest final source
run is align_dev_run_strata.log; earlier complete development logs remain
available but are not the final source manifest.

Additional final lineage/sample/integration check:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python docs/enh/bench/final_checks.py > docs/enh/bench/align_final_checks.log 2>&1
git diff --check -- ccc/bench tests/test_bench_core.py tests/test_bench_alignment.py docs/enh/bench ops/reports/BENCH-ALIGN.md
```
