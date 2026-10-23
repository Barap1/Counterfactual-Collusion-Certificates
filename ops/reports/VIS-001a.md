# VIS-001a — publication figure pipeline

## Status

Complete. Static, offline figure pipeline built from committed Gate A DEV evidence. No live experiment files were read or changed; no network, model/API calls, package installs, or commits were used.

## Artifacts

- `figures/fig_arms.svg` and `.pdf`: F/S/K/Nₘ branch schematic; Nₘ is the v1.2 placebo mask. Caption sidecar: `figures/fig_arms.json`.
- `figures/fig_gateA_integrity.svg` and `.pdf`: integrity-check table labeled “DEV fixtures, protocol v1.1”; reports A6 invalid detection 230/360 and the stated Gate A FAIL. Sidecar: `figures/fig_gateA_integrity.json`.
- `figures/fig_confusion_dev.svg` and `.pdf`: positive-call-rate heatmaps with `k/n` counts across fixture families and methods, stratified by mechanism label and oracle `path_active`; labeled “DEV fixtures · protocol v1.1 · pre-amendment”. Sidecar: `figures/fig_confusion_dev.json`.
- `figures/scripts/build_publication.py`: deterministic offline source-to-figure build.
- `figures/make_results.py`: future `ccc.analysis` figure template. It expects `results/analysis/<phase>/aggregate.json` and documented `figure_data/fig_delta_by_world.csv`; it was not run on result data and emitted no results figure.

## Provenance

Every figure sidecar names its source files and SHA-256. DEV outcome and family counts come from `docs/gate_a/eng005/gate_a_results.json.gz` (SHA-256 `e1925956c3c836d3b8b65eac17768103508b26fee5b2718fb79ee59d4d9570dc`). Integrity table values come from its `gate_checks`; the overall FAIL label and explanatory note are cross-checked against `docs/gate_a/GATE_A_REPORT.md` (SHA-256 `e2b0805b7f938522d6b3b1e0f4c33a0f46a3127720ea0749c9e59937978cf2f9`). Arm schematic is conceptual and has no plotted empirical values. The future-template schema follows `docs/stats/analysis_spec.md` §8.

## Validation

Command run: `MPLCONFIGDIR=/tmp/mpl-cache starter/collusion_hackathon/colosseum/.venv/bin/python figures/scripts/build_publication.py` (exit 0). Matplotlib 3.10.8 was available in the starter venv. Generated SVG/PDF and sidecar JSON files are present. No tests were run.

## VIS-001b visual corrections

- `fig_arms` now describes Nₘ per protocol v1.2 §3.1: mask preregistered matched non-audited M* from the same sender while E* remains visible; the schematic states this checks whether masking irrelevant content itself is harmless. S and K descriptions use the reviewed receiver-view wording, and t* is separated from the shared-prefix title. Its sidecar hashes `docs/research/sci002/protocol.md` (SHA-256 `8f7dcd896c524aa0a056bf11490641c8cc116a2b099de0b903285109f0a92549`).
- `fig_confusion_dev` is now three stacked heatmaps (mechanism label; oracle `path_active=false`; oracle `path_active=true`), with fixture families by rows, CCC/B0/B1/B2/B2+/B3a/B3b/B4-rule by columns, cividis sequential scale, colorbar, `k/n` positive-call rates, and a divider after CCC. The title and exact pre-amendment subtitle are distinct. The 7.15-inch-wide PDF uses 7 pt or larger text for a two-column paper.
- Rebuilt offline, then rendered both PDFs using `sips -s format png <pdf> --out /tmp/ccc_figqa/<name>.png`. Inspected `/tmp/ccc_figqa/fig_arms.png` and `/tmp/ccc_figqa/fig_confusion_dev.png`; no title/subtitle collisions, cell-label overlap, or clipping observed. Confusion data remain from the committed Gate A DEV source (SHA-256 `e1925956c3c836d3b8b65eac17768103508b26fee5b2718fb79ee59d4d9570dc`).

## Limits

These are synthetic development fixtures from protocol v1.1, pre-amendment, with one deterministic continuation per arm and 20 independent world groups as documented by the source. They are not held-out or real model observations and do not support population performance claims. The future analysis template is intentionally unexecuted until documented analysis outputs exist.
