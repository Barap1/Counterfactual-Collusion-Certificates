# R4 consistency fixes — W5-FIXR4

Each failing row in `R4_CONSISTENCY.md` maps to:

- S1–S3: Appendix F and Section 5.4 now say original-confirmatory [OC], preserving estimates, Holm p-values and failed significance findings.
- Duplicate metadata-repair counts: deviation log now uses [PH], matching Appendix F and the explicit post-hoc-exploratory category in `docs/analysis/exp002_heldout_v3/CORRECTION.md`.
- Explorer source hashes: regenerated index summary reports 422 from `demo/data/MANIFEST.json`; generator continues computing the length rather than hardcoding it. Manifest HEAD metadata also refreshes from that source.
- Explorer sensitivity note: estimate/interval are original-registered-secondary; separately reported p-value remains post-hoc-exploratory.
- Explorer competing descriptive label: generator removes the legacy result label from the presentation copy, retaining the canonical category and every numerical/source field. Source JSON stays unchanged.
- Explorer manifest counts: generator and index assign descriptive to the summary counts.
- README category scope: quick-check values explicitly original-confirmatory; accounting descriptive; MDE descriptive and observed effect original-confirmatory.
- Paper legend/Figure 1: legend moved outside an HTML comment so build stripping retains it. Figure 1 prose and figure plan use [NP], following `figures/enh/prospective/fig_ladder.json` and its PROSPECTIVE caption; explicitly identified as a conceptual diagram, without measured outcomes. Figure source/build files unchanged.
- Appendix G: about 25 queries remains [D], explicitly “inherited, not independently traceable in this repository” and unchecked.

Validation: local Python syntax, numerical-preservation, generator/index equality, source-hash and category assertions passed. No EXP-002 numerical changes. Full explorer/paper builds remain ORCH-owned; no git, network, Modal or experiment/model calls. Registry inspected: no W5-FIXR4 lease; direct brief supplies scoped authorization.
