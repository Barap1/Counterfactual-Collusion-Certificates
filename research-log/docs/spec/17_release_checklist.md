# 17 - Definition of done and final owner handoff

## Scientific completion

- [ ] The primary question and operational harm definition are explicit.
- [ ] The novelty paragraph names close prior work and avoids unsupported first/proof claims.
- [ ] The archived pilot is separated from holdout evidence.
- [ ] Exact replay validity is tested, or the paper is explicitly narrowed to a different intervention design.
- [ ] A legitimate causal-cooperation hard negative is present.
- [ ] Common-cause, inert-talk, and invalid-replay controls are included or limitations state exactly what is absent.
- [ ] Real-agent labels are not equated with prompted intent without justification.
- [ ] Independent worlds, branch repeats, failures, ineligible cases, and abstentions are counted separately.
- [ ] Main effects have the appropriate uncertainty and units.
- [ ] No model/backend switching, seed hunting, cached duplicate sampling, or hidden post-selection contaminates the reported comparison.
- [ ] Every headline sentence has a verified evidence chain.

## Engineering completion

- [ ] A documented clean setup reproduces the analysis without spending money.
- [ ] Actual upstream commit, patches, dependency versions, model IDs/digests, and prompts are recorded.
- [ ] Core invariants, corruption tests, and budget barriers pass.
- [ ] Raw traces and immutable manifests are preserved.
- [ ] Figures, viewer, certificates, and paper agree on the same frozen analysis version.
- [ ] Public artifacts are sanitized; secrets and private working-document IDs are not accidentally published.
- [ ] No unrelated owner changes were overwritten.
- [ ] Commits are coherent and within the owner's cap.

## Presentation completion

- [ ] The report fits the official template and current event rules.
- [ ] Abstract, figures, methods, results, limitations, references, ethics appendix, and LLM disclosure are complete.
- [ ] Every final PDF page has been inspected or an explicit visual-review gate remains for the owner.
- [ ] Template guidance and placeholder authors/results are removed before finalization.
- [ ] The demo is offline-safe and distinguishes constructed fixtures, real observations, and recorded replay.
- [ ] A cold reader can explain the principal finding and its limits.
- [ ] Google Doc synchronization is either verified with revision information or honestly marked pending.

## Operational completion

- [ ] Actual resource usage is reconciled separately from environment task cost.
- [ ] New spending remains within the owner's authorization; unknown amounts are not labeled zero.
- [ ] All project cloud jobs/endpoints and unnecessary local inference servers are stopped or explicitly handed off.
- [ ] No publication/sharing/submission action occurred without authorization.
- [ ] The owner has the exact final artifact paths, repo state, prepared Doc link, and deadline.

## Final director message format

Keep the owner handoff short but concrete:

```text
Completed: what genuinely exists
Main finding: one evidence-backed sentence, including scope
Evidence: independent sample count, effect/interval or honest null
Artifacts: final PDF, working Doc, code, reproduction bundle, demo
Verification: tests/reviewer reports and any unresolved limits
Resources: free API usage, local backend, Modal gross/credit/net status
Owner decisions: author details/review/publication/submission approvals still needed
```

Never end with "everything passed" if a mandatory step was skipped. A polished limitation statement is better than a false completion claim.

## What makes this project worth presenting

The intended contribution is not that agents can coordinate, that messages can affect behavior, or that a dashboard can display two timelines. It is a disciplined answer to a harder question: **what evidence is sufficient to call a communication-dependent outcome harmful coordination, and when should an auditor refuse to make that claim?**

Deliver the strongest answer supported by the actual work. The judges, not the spec, determine the award.
