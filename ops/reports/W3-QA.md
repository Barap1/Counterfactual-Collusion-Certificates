## Task
W3-QA: apply all nine QA_EXPLORER findings within the explorer.

## Status
Complete; static verification only.

- P1-1 fixed: UI-derived L0/L1 wording, accessible label, L1 scope, and tour corrected.
- P1-2 fixed: both exoneration overclaims replaced with assumption-qualified upper-bound language.
- P1-3 fixed: shrinkable twin cards, wrapping transcripts, focusable overflow tables, visible scroll hint.
- P2-1 fixed: twin title accommodates differing verdicts.
- P2-2 fixed: scripted-label/non-detection note beside verdicts.
- P2-3 fixed: bundled sensitivity category note corrected; other bundled bytes unchanged.
- P2-4 fixed: uncertainty copy uses bound span.
- P2-5 fixed: light exposure-tag background darkened to #7a5600.
- P2-6 fixed: source-clipped transcript snippets disclosed.

## Artifacts
- demo/explorer/app.js
- demo/explorer/style.css
- demo/explorer/data/index.js
- demo/explorer/qa_W3_static.txt
- docs/enh/qa/QA_EXPLORER_FIXES.md
- ops/reports/W3-QA.md

## Validation
Commands run: `node --check demo/explorer/app.js`; `node --check demo/explorer/data/index.js`; inline `python -` source assertions, removed-copy searches, and bundled-study JSON parsing. All final checks pass. Initial static assertion caught one remaining “Interval width” phrase; corrected and checks rerun successfully. Read/search commands: `cat`, `sed`, `rg`, `head`, inline `python -` metadata inspection. No removed DOM elements or dependent references were introduced.

## Limitations
No browser rendering, keyboard interaction, screen-reader check, build, or experiment execution. Registry inspected: W3-QA absent; no active conflicting explorer lease listed. Direct user assignment supplied scope. Numbers and evidence labels preserved.

## Budget
$0 new spend; Codex worker. No model/API experiment calls, network, git, or Modal.

## Next
Integration owner may perform rendered mobile/accessibility review and integrate the fixes.
