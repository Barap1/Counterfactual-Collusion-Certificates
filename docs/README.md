# Documentation

Start with the [project README](../README.md). The documents below are written for readers; the scientific records they cite are listed after them.

## Reader documents

| Document | What it covers |
| --- | --- |
| [MATH.md](MATH.md) | Formal setting, estimands, both propositions with proofs, the exact sign-flip test, the bootstrap, and the utility criterion, each tied to code and a test |
| [ENGINEERING.md](ENGINEERING.md) | Architecture, data flow, design decisions and the correctness strategy |
| [RESULTS.md](RESULTS.md) | Every reported number mapped to its frozen source field |
| [LIMITATIONS.md](LIMITATIONS.md) | Scientific scope, reproduction limits and release status |
| [REPRODUCING.md](REPRODUCING.md) | Commands for the dependency-free check, the explorer and the full suite |
| [STUDIO_RESEARCH_PLAN.md](STUDIO_RESEARCH_PLAN.md) | A proposed continuation study (a proposal, not a conducted study) |
| [assets/README.md](assets/README.md) | Sources and values for the README figures |
| [../ccc/README.md](../ccc/README.md) | Package layout and what each module computes |

## Canonical scientific records

These paths are fixed: frozen manifests, seed checks and hash-pinned code refer to them.

| Record | Purpose |
| --- | --- |
| [`enh/r2/run_par/RESULTS.json`](enh/r2/run_par/RESULTS.json) | Completed prospective benchmark aggregate report |
| [`enh/r2/RESULTS_BY_STRATUM.md`](enh/r2/RESULTS_BY_STRATUM.md) | Deterministic and noisy strata; original failures |
| [`enh/r2/PROTOCOL.md`](enh/r2/PROTOCOL.md) · [`enh/r2/FREEZE.json`](enh/r2/FREEZE.json) | Frozen benchmark design and hashes |
| [`enh/r2/PLATFORM_DIVERGENCE.md`](enh/r2/PLATFORM_DIVERGENCE.md) | Cross-platform discrepancy and post-hoc restriction |
| [`analysis/exp002_heldout_v3/`](analysis/exp002_heldout_v3/) | Corrected real-agent analysis |
| [`stats/`](stats/) | Real-agent preregistration, freeze and deviations |
| [`runner/archives/`](runner/archives/) | Archived real-agent experiment inputs and hash files |
| [`research/sci002/`](research/sci002/) | Audit protocol (v1, v1.1, v1.2) and amendment |
| [`enh/fix/`](enh/fix/) | Certificate mapping correction and review |
| [`gate_a/`](gate_a/) | Development fixture validation (Gate A) |
| [`../demo/data/TRACE.md`](../demo/data/TRACE.md) | Explorer data lineage |

Earlier `analysis/exp002_heldout*` versions, development fixtures in `gate_a/` and `enh/bench/`, the interrupted serial `enh/r2/run/` and the stopped `enh/exp003/` are supporting provenance, not competing results. The completed prospective execution is `enh/r2/run_par/`. `inf/` holds the inference backend benchmark and `fix/` the fixture evidence.

## Process records

The decision log, claims register, task reports, independent reviews, specification modules and agent coordination files are in [`../research-log/`](../research-log/README.md). To resolve an old path such as `ops/DECISIONS.md`, prefix it with `research-log/`.

## Provenance and acknowledgments

Colosseum/Terrarium, the upstream checkpoint machinery and the prompted seed-1 pilot were inherited development infrastructure. CCC's protocol, replay layer, controls, runner, baselines, analysis, the real-agent study (EXP-002) and the prospective benchmark were developed during October 23 to 25, 2026. "Original study" means earlier than the later benchmark, not before the sprint. The pilot is development data only.

Author: Aarav Patel, Georgia Institute of Technology. Prior work is credited in the [verified bibliography](../paper/v2/references_v2.bib) and [citation audit](../paper/v2/CITATION_AUDIT.md). PlaneFuse influenced visual presentation only and supplied no scientific content. The README diagrams are original editable SVGs.

Original CCC work is MIT licensed. [NOTICE](../NOTICE.md) and the [license inventory](../research-log/docs/release/LICENSES.md) retain distinct third-party terms and unresolved upstream rights. See [release status](LIMITATIONS.md#release-status).
