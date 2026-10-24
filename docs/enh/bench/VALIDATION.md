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
