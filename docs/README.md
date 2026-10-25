# Research and evidence guide

Start with the [project overview](../README.md), [verified results](RESULTS.md), [reproduction guide](REPRODUCING.md) and [limitations](LIMITATIONS.md). The latest manuscript source is indexed in [paper/README.md](../paper/README.md).

## Canonical scientific records

| Record | Purpose |
| --- | --- |
| [`enh/r2/run_par/RESULTS.json`](enh/r2/run_par/RESULTS.json) | Completed prospective benchmark aggregate report |
| [`enh/r2/RESULTS_BY_STRATUM.md`](enh/r2/RESULTS_BY_STRATUM.md) | Deterministic and noisy strata; original failures |
| [`enh/r2/PROTOCOL.md`](enh/r2/PROTOCOL.md) · [`enh/r2/FREEZE.json`](enh/r2/FREEZE.json) | Frozen benchmark design and hashes |
| [`enh/r2/PLATFORM_DIVERGENCE.md`](enh/r2/PLATFORM_DIVERGENCE.md) | Cross-platform discrepancy and post-hoc restriction |
| [`analysis/exp002_heldout_v3/`](analysis/exp002_heldout_v3/) | Corrected real-agent analysis |
| [`stats/`](stats/) | Real-agent preregistration, freeze and deviations |
| [`runner/archives/`](runner/archives/) | Archived real-agent experiment inputs and hash files |
| [`enh/fix/`](enh/fix/) | Certificate mapping correction and review |
| [`../demo/data/TRACE.md`](../demo/data/TRACE.md) | Explorer data lineage |
| [`assets/README.md`](assets/README.md) | Editable explanatory figures and sources |

## Supporting history

Research paths stay stable so archived hashes, generators and citations remain valid. Earlier `analysis/exp002_heldout*` versions, development fixtures in `gate_a/` and `enh/bench/`, the interrupted serial `enh/r2/run/`, and stopped `enh/exp003/` are supporting provenance. They are not competing final results. Completed prospective execution is `enh/r2/run_par/`.

`eng/`, `inf/`, `review/`, `research/`, `spec/` and `../ops/` retain design, engineering, audit and coordination records. They include superseded plans and historical task status. Current release instructions are this guide and [REPRODUCING.md](REPRODUCING.md), not old agent restart prompts. `../viewer/` is a legacy viewer builder; the maintained reader entry is `../demo/explorer/index.html`.

The [repository cleanup inventory](../ops/reports/repo_final/INVENTORY.md) records retained, archived and removed presentation material. Frozen outputs and negative findings remain in place.

## Provenance and acknowledgments

Colosseum/Terrarium, upstream checkpoint machinery and the prompted seed-1 pilot were inherited development infrastructure. CCC's protocol, replay layer, controls, runner, baselines, analysis, EXP-002 and prospective benchmark were developed during October 23–25, 2026. “Original study” means earlier than the later benchmark, not before the sprint. The pilot is development-only.

Author: Aarav Patel, Georgia Institute of Technology. The research used substantial Claude/Codex assistance; this does not imply independent human verification. Prior work is credited in the [verified bibliography](../paper/v2/references_v2.bib) and [citation audit](../paper/v2/CITATION_AUDIT.md). PlaneFuse influenced visual presentation only and supplied no scientific content. New README diagrams are original editable SVGs.

Original CCC work is MIT licensed. [NOTICE](../NOTICE.md) and the [license inventory](release/LICENSES.md) retain distinct third-party terms and unresolved upstream rights. See [current release boundaries](LIMITATIONS.md#release-status).
