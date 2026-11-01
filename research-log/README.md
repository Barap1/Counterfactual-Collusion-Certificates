# Research log

This directory preserves the process records of the October 23 to 25, 2026 research sprint: the decision log, the claims register, freeze and hash records, task reports, independent reviews, and the agent coordination files that organised the work. It is kept for provenance and auditability. Nothing here is needed to read the results or run the reproduction; start with the [project README](../README.md) for that.

## Where things moved

These items were moved here unchanged from the repository root and from `docs/`. **To resolve an old path, prefix it with `research-log/`.** For example, `ops/DECISIONS.md` is now `research-log/ops/DECISIONS.md`, and `docs/review/rev001/` is now `research-log/docs/review/rev001/`. Paths quoted inside the records themselves, and in the final paper, refer to the original locations.

| Path | Contents |
| --- | --- |
| [`ops/DECISIONS.md`](ops/DECISIONS.md) | Dated decision log, D-001 to D-049, including corrections and post-hoc decisions |
| [`ops/CLAIMS.md`](ops/CLAIMS.md) | Claims register: each claim, its status (verified, rejected, corrected) and evidence |
| [`ops/reports/`](ops/reports/) | Task reports (engineering, statistics, review, publication), and the final audit with the independent bootstrap verifier |
| [`ops/pilot_manifest.sha256`](ops/pilot_manifest.sha256) | SHA-256 hashes of the 27 seed-1 pilot files (development data, kept local) |
| [`ops/v12_freeze_hashes.txt`](ops/v12_freeze_hashes.txt) | Extractor and placebo-rule freeze hashes for protocol v1.2 |
| [`ops/budget_ledger.jsonl`](ops/budget_ledger.jsonl) | Append-only ledger of every resource request made through the inference controller |
| `ops/STATUS.md`, `ops/RESUME.md`, `ops/tasks.json`, `ops/briefs/`, `ops/locks/` | Coordination state: status page, restart packet, task registry, worker briefs, locks |
| [`review/reproduce_headline/`](review/reproduce_headline/) | Independent standard-library reconstruction of the primary estimate, used by [`scripts/reproduce_headline.py`](../scripts/reproduce_headline.py) and tested in CI |
| [`docs/review/`](docs/review/) | Independent reviews: the held-out result review (REV-001), the freeze review, and the Gate A review |
| [`docs/spec/`](docs/spec/) | The original specification modules that governed the sprint |
| [`docs/eng/`](docs/eng/) | Engineering evidence for the replay layer |
| [`docs/release/`](docs/release/) | Third-party license inventory, recorded environment, release checklist and development inputs |
| [`docs/archive/`](docs/archive/) | Superseded planning material |
| [`patches/`](patches/) | Two patches applied to the upstream starter during development |
| [`viewer/`](viewer/) | Legacy evidence viewer builder, superseded by [`demo/explorer/`](../demo/explorer/) |
| `AGENTS.md`, `CLAUDE.md`, `CCC_START_HERE.md`, `.claude/` | Agent coordination instructions and settings used during the sprint |

## What stayed in `docs/`

The scientific records stayed in place: `docs/enh/`, `docs/runner/`, `docs/analysis/`, `docs/stats/`, `docs/gate_a/`, `docs/research/`, `docs/inf/` and `docs/fix/`. Frozen manifests, seed-exclusion hashes and hash-pinned source files reference these exact paths. For example, the benchmark freeze ([`docs/enh/r2/FREEZE.json`](../docs/enh/r2/FREEZE.json)) records the path of the protocol it binds, the seed check hashes the paths of the archives it scans, and the analysis code reads `docs/research/sci002/protocol.md` at run time. Moving them would invalidate those checks.

## Notes on use

* Some hash-pinned source files keep default paths under `ops/` (for example the inference controller's default ledger path, `ops/budget_ledger.jsonl`). Those files are unchanged so their recorded hashes stay valid. The sprint's ledger is archived here; any future live run would pass a ledger path explicitly.
* Restart prompts, task leases and status pages describe the sprint as it ran. They are historical, not current instructions.
* Records here were written during the work and are not edited after the fact. Corrections appear as later decisions and reports, not as rewrites.
