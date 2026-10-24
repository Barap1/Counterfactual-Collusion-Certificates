# Frozen v1.2 blind labelling protocol

No labels have been collected by this implementer. The labeller must be independent
of commitments.py and every fixture policy author, and must see no extractor output,
flags or E* mapping while labelling. Label carrier / not carrier / ambiguous using
same-agent, same-task, receiver visibility. Include all flagged lines in the 42
reverted-or-remaining non-A5 cells, and 60 randomly sampled unflagged lines from
A3a/A4b/A2a/A5, seed int(sha256("amd001-label").hexdigest()[:8],16).
Report precision and recall with exact intervals; ambiguous labels separately.
No tuning follows. Label acquisition and reproduction of the 800-cell Gate A table
remain with the independent review/report task, outside this implementation.

## Label definitions (frozen with this file)
- carrier: the line was authored by the same agent as E*, concerns the same task, and the receiver sees it.
- not carrier: any of the three is false (different author, different task, negated, or not visible to the receiver).
- ambiguous: the labeller cannot decide from the line and its visible context. Reported separately; never merged into either class.
Lines are presented as bare authored text with surface name, author and receiver visibility; no E* mapping, flags or extractor output are shown.
