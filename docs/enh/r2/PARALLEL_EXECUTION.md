# Frozen R2 execution on Modal CPU

W1-MODAL adds `scripts/bench_modal_run.py`, reusing the crashed worker's
`scripts/bench_parallel_run.py` per-seed orchestration without editing frozen
benchmark sources. This is an execution-only deviation: no scientific logic,
threshold, seed, denominator, method failure handling, or outcome selection changes.

The driver creates a Modal App lazily and maps seed tasks on CPU containers
(default maximum 3). Each input validates FREEZE, protocol, seed exclusions and
code hashes before and after execution. Driver hashes, Python major/minor and
NumPy version must agree. Python patch version and zlib version are recorded in
receipts. The original cross-platform identity gate failed; the replacement
acceptance rule and the limits of the subsequent checks are reconciled below.
The image requests the launching interpreter's Python major/minor and exact
NumPy version. Actual image availability and SDK execution remain ORCH checks.

An explicit file allowlist mounts frozen Python/JSON sources, the two execution
drivers, FREEZE/protocol/seeds, enumeration references, and historical seed-census
sources. It excludes credentials and run outputs. Every input uses a private
scratch cache: the frozen cache uses non-atomic writes. No shared Volume or
external inference is used. Population and the unchanged aggregation/report tail
execute locally after all mapped seed outputs have been restored in frozen
schedule/epsilon order.

Enumeration tasks finish before method tasks are submitted. The 40-seed gate
has its own enumeration barrier; the full run enumerates all remaining seeds
before submitting remaining method tasks. Valid gate outputs are reused.

Resume is automatic for the same output manifest and execution identities.
SHA-256 receipts validate both epsilon unit files, partitions and metadata;
corruption refuses resume. Unreceipted identical partial files can be completed;
differing files are never overwritten. Dispatch attempts are logged before
submission, limited to three per phase/seed; Modal automatic retries are off.
ORCH may resume only infrastructure failures with identical inputs, never
because of an unfavourable scientific outcome. Unstarted inputs in an aborted
map can conservatively consume an attempt. Frozen method failures remain rows.

`--gate 40` compares opaque bytes for 80 unit and 80 partition files against the
first 40 frozen schedule-order seeds in read-only `docs/enh/r2/run/`. The serial
unit inventory was 297 at implementation time; only files belonging to those
40 seeds form this gate. Missing references or differing bytes fail. The driver
writes `run_par/GATE.json`, prints `GATE PASS` or `GATE FAIL`, and exits nonzero
on failure. A full run requires a current PASS receipt and rechecks its bytes.
That is the original driver contract, not the final run status: the original
cross-platform gate failed and D-046 authorized the narrower replacement below.
The initial implementation worker did not execute a cloud gate.

From the repository root, ORCH commands (requires installed/authenticated Modal
SDK and approved cloud budget; do not use the offline guard for cloud commands):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m scripts.bench_modal_run --gate 40 --containers 3
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m scripts.bench_modal_run --containers 3
```

Repeat the applicable command for an infrastructure-only resume. Keep the local
process alive until its map returns; outputs and checkpoints are written locally.
After full completion the driver generated the frozen report in `docs/enh/r2/run_par/`.
For an offline report check, first copy the run to a new scratch directory and use
`python -m ccc.bench report --run <scratch-copy>`; never target the preserved original.

Offline plan (no Modal import, world generation or output directory creation):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m scripts.bench_modal_run --dry-run --gate 40
```

DEV validation uses seeds 13000 and 13001 only, the real frozen serial runner,
and the exact mapped callable locally. It compares all report-consumed artifacts
byte-for-byte, including the final report, and checks checksum-based resume,
corruption refusal, gate failure, runtime identity refusal and frozen-tail AST
agreement. No prospective world was executed by this worker.

Validation result: **5 passed in 72.90 seconds**, using this exact command:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD:/opt/homebrew/Caskroom/miniforge/base/lib/python3.14/site-packages" starter/collusion_hackathon/colosseum/.venv/bin/python -m pytest tests/test_bench_modal.py -q
```

The venv lacks pytest, so the existing system pytest package was exposed through
PYTHONPATH. Initial invocations with the venv alone (missing pytest) and system
Python alone (missing NumPy/native adapters) failed; no installation was done.

After tightening infrastructure-error gate reporting, the focused checks were
rerun: **4 passed, 1 deselected in 15.22 seconds**. Exact command:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD:/opt/homebrew/Caskroom/miniforge/base/lib/python3.14/site-packages" starter/collusion_hackathon/colosseum/.venv/bin/python -m pytest tests/test_bench_modal.py -q -k 'not dev_serial'
```

## Reconciled execution provenance (D-046; final audit)

This replaces the contradictory earlier narrative, not the historical receipts.
D-046 changed the **execution acceptance rule** after the original cross-platform
identity requirement failed. It did not amend the frozen study protocol, scientific
sources, seeds or thresholds. The protocol and all 34 frozen source hashes still
match. The unchanged scientific code does not establish cross-platform equivalence.

| Phase/check | Platform/runtime and evidence | Independent seeds | Files/records and result |
|---|---|---:|---|
| Preserved partial serial method run | Local macOS; CPython 3.14.7/Clang, NumPy 2.2.6 reported in W1-DIAG | 149 with eps=0, 148 with eps=0.1; paired overlap, not 297 independent seeds | 297 unit files retained in `run/`; these method outputs were not imported into final `run_par` results |
| Original 40-seed gate receipt | `run_par/GATE.json` and `ops/reports/codex_runs/gate1_failed/run_par_prev/GATE.json` | 40 | Historical **FAIL**, infrastructure error: 160 missing-file comparisons (80 unit + 80 partition files). This receipt demonstrates no successful content comparison |
| Post-run comparison on those same 40 seeds | Read-only comparison of current preserved `run/` and `run_par/`; durable final-audit script/output linked below | 40, each in both strata | eps=0: 40/40 unit and 40/40 partition files identical, compressed and decompressed. eps=0.1: 2/40 unit files identical, 38 differ even after decompression; 40/40 partition files identical |
| Replacement container self-check | `run_par/gate_v2/A` versus `B`; `GATE_v2.json`; worker CPython 3.14.2/GCC 12.2.0, NumPy 2.2.6 | 5, each in both strata, executed in two separate container runs | 10 unit + 10 partition files identical (20 file comparisons). All 20 A files also match final run files |
| Replacement eps=0 cross-platform check | Gate A versus preserved serial | Same 5 | 5 unit + 5 partition files identical. `GATE_v2.cross_platform_eps0.compared=20` retains the driver's all-epsilon count; the actual eps=0 subset has 10 files, not 20 independent units |
| Mapped enumeration and methods | Modal Linux containers; CPython **3.14.2**/GCC 12.2.0, NumPy 2.2.6, zlib 1.2.13. All 2,100 method receipts agree on runtime and gate identity | 2,100 mapped seed units; two epsilon strata are nested | 4,200 unit + 4,200 partition files, 42,000 method records. All 8,400 method-receipt artifact SHA-256 checks pass; no failed method receipt |
| RQ3 population generation | Local `finalize()` calls `population()` in `scripts/bench_modal_run.py`; not a Modal-mapped phase. Local controller CPython 3.14.7/NumPy 2.2.6 is reported by the historical execution record; no separate per-population runtime receipt establishes its patch version | 200 population seeds reused across two strata | `run_par/population.json`; 200 rows per stratum. Local RQ3 population computation is part of the final results, distinct from importing serial method units |
| Aggregation and report tail | Local controller, after container artifacts are restored; frozen `report.py` | No new independent units | `records.json.gz`, `RESULTS.json`, `RESULTS.md`. Report reproduction checks arithmetic, not platform invariance |
| All available cross-platform unit overlap (D-048) | Preserved local versus Modal unit files | 149 deterministic; 148 noisy, overlapping seed sets | eps=0: 149/149 byte-identical; 0/1458 records differ. eps=0.1: 142/148 unit files differ; 1160/1452 records contain method-output differences, including decisions |

`GATE_v2.json.platform` says "modal linux, CPython 3.14.7" because the driver
formatted that field from the **local launching interpreter**. The worker runtime
is 3.14.2 in all 2,100 method receipts; controller and worker versions must not
be conflated. The original `compared` and `platform` fields are preserved as
historical evidence, not silently repaired.

The D-046 replacement checks demonstrate five-seed container self-determinism
and deterministic-stratum identity on the stated overlap. They do **not** satisfy
the original noisy-stratum cross-platform identity requirement. The technical
cause of the noisy difference remains unresolved: floating-point/RNG behaviour is
a hypothesis, not an established diagnosis. The final benchmark was not entirely
computed on Modal because population generation and reporting ran locally.

D-048 was decided **post hoc, after outcomes were visible**. Established
prospective claims are restricted to eps=0 within this benchmark and available
overlap; eps=0.1 is fully retained as **platform-dependent, not established**.
Substantive method decisions differ, so the issue is not merely compressed bytes
or harmless rounding. The restriction is not a prospective validation success.

The original aggregate criteria remain **RQ1 PASS and RQ2 PASS by construction;
RQ3 FAIL; RQ4 FAIL; RQ4b FAIL; RQ5 FAIL; RQ6 descriptive**. RQ4b's eps=0 pass
does not repair its aggregate failure. RQ3's eps=0 interval includes 0.25, so the
failed `<0.25` prediction does not establish that the population rate exceeds
0.25. End-to-end support-level positive-control recovery and useful real-agent
detection sensitivity remain unestablished.

Durable final-audit verification (stdlib-only; no benchmark execution):
- `ops/reports/final_audit/science/verify_receipts.py`
- `ops/reports/final_audit/science/receipt_verification.json`
- `ops/reports/final_audit/science/stratum_reproduction.json`

Run `python3 ops/reports/final_audit/science/verify_receipts.py` from the checkout.
The all-overlap audit and stratum re-tabulation were independently executed with
`python3 scripts/eps_platform_check.py --out ops/reports/final_audit/science`;
the three resulting files were byte-identical to their existing counterparts.
These are offline checks of preserved evidence; no new world or inference was run.
