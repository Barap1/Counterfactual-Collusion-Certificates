# Editable README comparison

The allocation comparison uses GitHub's system-font stack at **16px**, matching normal README text at its native display size. It has no poster title, opaque background or filled panels. Thin rules and text labels carry the structure; color is supplementary.

Regenerate with `python3 docs/assets/generate.py`. It writes SVG only and performs no network, inference or paper generation.

## Responsive theme variants

These are four renderings of one scientific comparison, generated from the same values:

| Layout | Light | Dark | Native size |
| --- | --- | --- | --- |
| Desktop | [SVG](allocation-twins.svg) | [SVG](allocation-twins.dark.svg) | 640×292 |
| Narrow screen | [SVG](allocation-twins.mobile.svg) | [SVG](allocation-twins.mobile-dark.svg) | 324×382 |

The README uses GitHub's active-theme image markers and a `picture` source for narrow viewports. Images keep their natural width so selecting the mobile source does not enlarge its typography. Mobile uses a stacked comparison, rather than shrinking the desktop text. Both themes use transparent backgrounds, readable foreground colors and identical geometry.

The former evidence-map SVG is now a native Markdown table in the README. Its font, wrapping, borders and colors inherit GitHub's active theme automatically.

## Scientific source

Deterministic allocation pair, seed **19693329**. Message: “Please allocate the contested task to our dispatch team.” Both policies assign the contested task to dispatch. Mean outsider reward is **14** factually and **19** after message removal; sham and placebo are **14**. The cost probe lowers each outsider's contested-task cost by **10**. Efficiency switches allocation (factual **29**, knockout **29**); coalition protection keeps allocation (factual **14**, knockout **29**).

Exact values: [`paper/v2/figures/fig_twins_audit.json`](../../paper/v2/figures/fig_twins_audit.json), `plotted_values.members`. Original exhibit: [`figures/enh/prospective/fig_twins.json`](../../figures/enh/prospective/fig_twins.json). Broader lineage: [`paper/final/figures/provenance.json`](../../paper/final/figures/provenance.json). Implementation: [`ccc/bench/`](../../ccc/bench/). Explorer exhibit: [`demo/data/twins.json`](../../demo/data/twins.json).

Labels describe generator-defined policies across contexts, not independently adjudicated initial actions or real-agent intent. All displayed rewards are mean outsider task reward. The diagrams show factual probe responses; probe-knockout values remain in the source. The example separates these specified policies, not arbitrary legitimate alternatives.
