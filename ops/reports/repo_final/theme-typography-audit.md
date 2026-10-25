# GitHub-native figure typography and theme audit

## Change

Owner requested smaller figures whose ordinary words visually match normal GitHub README text and work in light and dark mode. The prior 24-unit labels rendered larger than repository prose; opaque panels also made the figures look like separate posters.

The new allocation comparison uses the same system-font stack as GitHub at **16px throughout**, no poster heading, transparent backgrounds, thin borders and restrained accents. Desktop is 640×292; the stacked narrow layout is 294×382. Natural image dimensions prevent accidental mobile upscaling. Below a 1100px viewport, `picture` selects the narrow layout instead of shrinking desktop type. Separate light/dark anchors use GitHub's active-theme image markers, so selection is not tied only to the operating system's preference.

The old evidence-map image is replaced with a native Markdown table. Its type, wrapping, borders and colors inherit GitHub's active theme automatically. All four allocation SVGs are generated from one editable source and the same scientific values. The explicit `.light.svg` filename also avoids reusing the old poster's cached image URL.

## Manuscript and scientific check

Read the owner-supplied native Google Doc using the Google Drive connector, read-only. No paper export, PDF, document edit or sharing change was performed. The private document URL/content was not copied into the repository. Its Figure 1 and methods confirm the existing frozen exhibit: same message/allocation, mean outsider reward14→19 after removal, each outsider cost reduced by10, probe factual rewards29 for efficiency and14 for coalition protection. Policy labels are programmed and the separating claim is pair-specific. Source paths remain in `docs/assets/README.md`.

Independent science review: `theme-science-review.md`. Independent source/engineering review: `theme-technical-review.md`. All 16,992 protected scientific records remain byte-identical to `final_audit/frozen_before.json`. Negative findings, real-agent uncertainty and post-hoc narrowing are unchanged.

## Rendering checks

Actual GitHub preview branch, in the existing automatic/dark appearance:

- Desktop1280px: README text16px; exactly one visible diagram; native640px image gives effective16px figure type. Inactive light anchor has `display:none`.
- Phone390px and intermediate800/1000px: the mobile source is selected at its natural width and effective type remains16px. The earlier324px narrow variant was checked live; the final294px refinement is also checked after publication.
- Desktop layout fits at1101px. A source switch briefly leaves an unloaded candidate; measurements were repeated after image load rather than reporting that transient state as a pass.
- The evidence table is native GitHub text, not an image. No duplicate theme image occupies layout space.

Non-mutating local previews: inspected both light and dark palettes on desktop and phone. Final294px mobile source fits a360px viewport at16px with no page overflow. Direct browser SVG measurements found no text bounds outside the desktop640px or mobile294px viewBox. All visible SVG text computed to16px.

Automatic approval review rejected changing the saved GitHub appearance setting for a live opposite-theme test. No alternate setting control or bypass was used. The original `Sync with system` preference remained `auto`, with the original light/dark defaults. Thus the audit distinguishes live GitHub dark-mode selection from non-mutating light-palette preview checks; it does not claim the saved account theme was switched.

Text contrast against GitHub white and `#0d1117` backgrounds is at least6.11:1 across all four text roles, exceeding4.5:1. Exact ratios: `theme-contrast.json`. Meaning is always in text as well as color.

## Engineering checks

Executed:

```sh
python3 docs/assets/generate.py
python3 scripts/check_artifact.py
python3 scripts/reproduce_headline.py
python3 -m unittest discover -s review/reproduce_headline/tests -v
python3 -m unittest tests.test_demo_data -v
python3 scripts/secret_scan.py --changed-only
```

The four SVGs regenerate byte-for-byte. Navigation checker now validates `source/srcset` candidates as well as image src/alt and Markdown links:15 reading-path pages,114 local links/anchors and four SVG variants pass. The primary estimate and exact test still reproduce;11 independent arithmetic tests and eight explorer provenance tests pass. This presentation-only refinement does not require rerunning the complete experimental or implementation suite. No inference/experiment was launched.

The ordinary missing-file check continues to reject nonexistent paper links while permitting the owner's later real PDF. There is no active README paper-PDF link and no paper PDF/DOCX in the public tree. Separate `paper/graphics_redesign/`, its reports and shared registry updates belong to another session and were not staged or altered for this redesign.

Final source is verified on GitHub before fast-forwarding `main`; final publication and CI receipts are checked before handoff. The temporary preview branch is removed after its commits are reachable from `main`. No force push or public history rewrite is used.
