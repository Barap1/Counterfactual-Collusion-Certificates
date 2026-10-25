# Frozen R2 execution on Modal CPU

W1-MODAL adds `scripts/bench_modal_run.py`, reusing the crashed worker's
`scripts/bench_parallel_run.py` per-seed orchestration without editing frozen
benchmark sources. This is an execution-only deviation: no scientific logic,
threshold, seed, denominator, method failure handling, or outcome selection changes.

The driver creates a Modal App lazily and maps seed tasks on CPU containers
(default maximum 3). Each input validates FREEZE, protocol, seed exclusions and
code hashes before and after execution. Driver hashes, Python major/minor and
NumPy version must agree. Python patch version and zlib version are recorded in
receipts; cross-platform compression equivalence is established by the gate.
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
No cloud gate was executed by this worker; PASS has not been established.

From the repository root, ORCH commands (requires installed/authenticated Modal
SDK and approved cloud budget; do not use the offline guard for cloud commands):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m scripts.bench_modal_run --gate 40 --containers 3
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m scripts.bench_modal_run --containers 3
```

Repeat the applicable command for an infrastructure-only resume. Keep the local
process alive until its map returns; outputs and checkpoints are written locally.
After full completion the frozen report is generated in `docs/enh/r2/run_par/`;
it can also be regenerated with `python -m ccc.bench report --run docs/enh/r2/run_par`.

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
