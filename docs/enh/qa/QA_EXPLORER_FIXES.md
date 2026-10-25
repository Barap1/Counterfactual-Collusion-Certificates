# Explorer QA fixes — W3-QA

- P1-1 fixed: L0/L1 use “highest reached (UI-derived, not a certificate rung)” in visible and accessible descriptions. Only supported certificates use “highest supported.” L1 explains one-sided, case-conditional bounds, n_independent = 1, and the distinction between influence and harm. Tour copy agrees.
- P1-2 fixed: both “ruled out” statements now qualify the upper bound by its interval assumption and explicitly avoid a test or exoneration claim.
- P1-3 fixed: twin cards can shrink within grid tracks; transcript text wraps; overflow tables are keyboard-focusable regions. A visible continuations scroll hint identifies the Action column.
- P2-1 fixed: the twin page asks when evidence separates verdicts, covering both identical and differing views.
- P2-2 fixed: a note beside the verdicts identifies private labels and attribution verdicts as scripted benchmark labels, not a detection.
- P2-3 fixed: the bundled study category note identifies the registered sensitivity as original-registered-secondary and its p-value as post hoc. All other bundled bytes are unchanged.
- P2-4 fixed: uncertainty descriptions use “bound span,” including the introductory explanation and computed spans.
- P2-5 fixed: exposure tags use white on #7a5600 in light mode; the existing dark-mode palette is preserved.
- P2-6 fixed: twin transcripts explain that snippets may end mid-sentence because they are clipped in source.

Static validation: both edited JavaScript files pass `node --check`; source assertions and bundled-study JSON parsing pass. Evidence: `demo/explorer/qa_W3_static.txt`. No browser or build was run. Numbers, evidence labels, source transcripts, and experiment results were preserved.
