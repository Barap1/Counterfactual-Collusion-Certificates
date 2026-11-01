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

## Final source review after responsive fixes — 2026-10-25

This section supersedes the pending source/layout dimensions above. Reviewed working branch `codex/readme-native-type`; revised294px sources were not yet pushed at review time. No unrelated graphics-session files or task registry were modified by this reviewer.

**Source and navigation PASS.** The README now uses `(max-width: 1100px)` for both mobile sources and omits forced img width, allowing each selected source to keep its natural pixel dimensions. Desktop SVGs remain640×292; narrow variants are now294×382. Every SVG retains16px system-font styling. The asset guide lists the four correct paths and dimensions and explains the native Markdown evidence table. The figure map now describes responsive/theme allocation SVGs plus that native table. The obsolete conceptual SVG link is gone.

Executed `python3 scripts/check_artifact.py`: **PASS —15 pages,114 local links/anchors,4 editable SVG variants, no README PDF link**. Source `srcset` candidates, normal HTML src/href, Markdown targets, fragments and nonempty img alternative text are covered. `git diff --check` passed. All four final assets again regenerated byte-identically from a copied generator executed in a temporary directory, leaving repository sources untouched:

| Final SVG | SHA-256 |
| --- | --- |
| allocation-twins.svg | fd501e0d4798aa914ac828965e796e7d1ca7748c69a67794fc5a3f604992d1af |
| allocation-twins.dark.svg | 98c910236fbcf23c4a80332262f5c5af0decd07f3a5ad3e67bb4cbbccca66767 |
| allocation-twins.mobile.svg | 431531e5c230bd1d4451fdd4f337b25c75ff4cc861ec454a598b5ec8f39d8d1e |
| allocation-twins.mobile-dark.svg | 0fdf94cc76caf3450c9047a071677806796493fa6c16f2852904297e005aa86d |

### Browser-evidence boundary

The root integrator reports **actual GitHub preview** measurements: one theme anchor hidden and one visible;16px effective image text at1280 desktop and390/800/1000 viewports, with desktop fitting at1101. Root reports **local preview** checks for the final294px variant at360px, no overflow and all SVG text bounds within their viewBoxes. Both palettes were inspected using non-mutating local previews.

This child independently verified the final source, dimensions, regeneration and checker results; it did **not** independently repeat those browser measurements. Actual GitHub appearance-setting mutation was blocked by automatic approval review. The original sync-system preference remained unchanged, so the root did not claim a live preference-switched opposite-theme audit. The local palette checks and live GitHub theme-marker/source behavior are distinct evidence.

No remaining actionable source/checker finding in the reviewed working-tree revision. Final push, CI and live delivery confirmation remain root integration work. No inference, experiment, paper generation or secret-file read was needed.

Final naming note: the default desktop light asset was renamed to `allocation-twins.light.svg` to avoid reusing the old poster URL. Its SVG bytes/hash and scientific content are unchanged. The final source paths are checked by the maintained checker.
