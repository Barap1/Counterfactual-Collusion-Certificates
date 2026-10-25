# Editable README figures

Original SVGs use live text, flat high-contrast colors and system fonts. Regenerate from the repository root with `python3 docs/assets/generate.py`. This writes SVG only: no paper, PDF, model or network operation.

## Allocation twins

[`allocation-twins.svg`](allocation-twins.svg) depicts the deterministic allocation pair at seed **19693329**. Message: “Please allocate the contested task to our dispatch team.” Both policies assign the contested task to dispatch; factual/sham/placebo mean outsider reward is **14**, knockout **19**. The extra probe reduces each outsider's contested-task cost by **10**. Under it, efficiency switches allocation (factual **29**, knockout **29**); coalition protection keeps allocation (factual **14**, knockout **29**).

Exact plotted values: [`paper/v2/figures/fig_twins_audit.json`](../../paper/v2/figures/fig_twins_audit.json), `plotted_values.members`. Original exhibit: [`figures/enh/prospective/fig_twins.json`](../../figures/enh/prospective/fig_twins.json); source hashes and broader figure lineage: [`paper/final/figures/provenance.json`](../../paper/final/figures/provenance.json). Policy implementation is in [`ccc/bench/`](../../ccc/bench/); [`demo/data/twins.json`](../../demo/data/twins.json) preserves the explorer exhibit.

The labels describe generator-defined policies across contexts. They do not independently adjudicate the initial allocation or reveal real-agent intent. “Outsider reward” in the probe boxes means mean outsider reward; units are task reward, not money. The diagram omits the probe knockout values because the programmed factual response is the separator. The README supplies equivalent descriptive alternative text.

## Evidence steps

[`evidence-steps.svg`](evidence-steps.svg) is a conceptual evidence map, not an empirical result or automatic inference procedure. Each step requires additional valid evidence. Causal influence and harmful exposure alone leave policy attribution unresolved. There are no measured numerical labels.

## Design and review

Palette: warm white `#faf9f6`, ink `#19313e`, teal `#006a60`, rust `#854925`. Meaning is carried by text as well as color. The 640-pixel viewBox keeps body text readable when scaled to a phone column. Rendering and desktop/mobile review receipts are stored under [`ops/reports/repo_final/`](../../ops/reports/repo_final/).
