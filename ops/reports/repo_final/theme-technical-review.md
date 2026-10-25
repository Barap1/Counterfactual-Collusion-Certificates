# README native typography and themes — technical review

2026-10-25. Task scope: read-only review of README picture/source markup, four original allocation SVGs, generator, public navigation and the maintained checker. Owned output: this report only. Separate `paper/graphics_redesign/` and `ops/reports/graphics_redesign/` work was not opened or modified. No secrets, models, experiments or external research used.

## Source checks executed

All four SVGs parse successfully, retain editable text, accessible title/description and viewBox, and contain no script or foreignObject. Text uses exactly `font-size:16px` and the native stack `-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif`, matching the relevant system-font portion of GitHub's body stack. Color is explicit; backgrounds are transparent so the surrounding GitHub theme supplies the canvas.

The desktop light/dark variants are 640×292; mobile light/dark variants are 324×442. All contain 14 text elements. A copy of `docs/assets/generate.py` executed in a temporary directory produced byte-identical output for every SVG, without overwriting repository assets:

| SVG | SHA-256 at source inspection |
| --- | --- |
| allocation-twins.svg | fd501e0d4798aa914ac828965e796e7d1ca7748c69a67794fc5a3f604992d1af |
| allocation-twins.dark.svg | 98c910236fbcf23c4a80332262f5c5af0decd07f3a5ad3e67bb4cbbccca66767 |
| allocation-twins.mobile.svg | 6e561d2063785206d590c46f08558523a9e766e40bf18892dc3c4fcb570716af |
| allocation-twins.mobile-dark.svg | 4881687de29cf5bfa065eb85c1abc689aca1c1afd2482f612ed8e76d2a886ac2 |

Numeric content remains source-backed: same factual14/knockout19 and probe factual29 for efficiency,14 for coalition protection; each outsider cost reduction10. SVG descriptions and README alternative text preserve the constructed-policy boundary. The former evidence-map image is replaced with a native Markdown table, allowing body-font inheritance, wrapping and native theme colors.

## Conditional image markup

The README uses separate light and dark anchor/picture blocks. Each anchor and fallback image has the corresponding `#gh-light-mode-only` or `#gh-dark-mode-only` fragment. Mobile sources select the paired mobile SVG at `(max-width: 600px)`. Fallback img width640 matches the desktop viewBox. Both fallback images carry equivalent substantive alternative text.

This is structurally consistent, but two conditions require actual GitHub inspection rather than a source-only pass:

1. GitHub must hide the complete inactive anchor/picture block for the fragment marker, including when the browser selects a source URL without that fragment. If it only hides a fallback image based on its selected URL, mobile could display a wrong-theme or duplicate diagram. Root was asked to verify both selected `currentSrc` and visible image count in each theme.
2. Source media queries use **viewport width**, while actual GitHub article width depends on layout and padding. Effective glyph size is `16 × displayed SVG width / viewBox width`. It is exactly16px when desktop image width640 or mobile image width324. At intermediate viewport widths above600, GitHub may narrow the article while the desktop source remains selected, reducing glyph size. Root was asked to measure displayed width/currentSrc at desktop,390px mobile and an intermediate width (roughly601–800px), and adjust the breakpoint/layout if necessary.

Transparent backgrounds do not dynamically recolor the SVG. The explicit theme alternatives therefore need the correct GitHub visibility behavior. Standalone or non-GitHub Markdown renderers may show both branches because the fragment visibility convention is GitHub-specific; the target reading surface is GitHub.

## Navigation findings sent during implementation

At initial inspection, `docs/assets/README.md` still described the previous600px display cap,640×536/640×246 assets/palette and linked the now-deleted `evidence-steps.svg`. The checker still expected that deleted asset and did not yet inspect source `srcset`; root had already assigned those updates to itself. These are pending implementation consistency checks, not a request to retain the obsolete image.

Final review should confirm all four source paths are validated by `scripts/check_artifact.py`, ordinary HTML href/src paths and alt checks remain intact, the asset guide gives current dimensions/themes, and the paper figure map does not retain an active link to the deleted conceptual SVG. Frozen paper graphics and research records need no changes for this README revision.

## Review status

No scientific-data or SVG-source-generation defect found. Final source-path/checker pass and actual GitHub desktop/mobile/light/dark rendering remain root-owned verification at this review stage. This report does not claim browser execution or exact rendered16px typography from source inspection alone.
