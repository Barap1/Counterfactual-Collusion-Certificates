# 10 - Verification gates and adversarial review

## Tests are part of the research result

An attractive interface on top of an invalid replay is worse than a modest but correct study. Build tests alongside the replay code. Default tests must run offline and must not consume API quota. Mark live tests explicitly and require the resource-policy gate.

## Required test matrix

| ID | Test | Acceptance evidence |
|---|---|---|
| V01 | Snapshot/restore round trip | Canonical state equality and identical next deterministic observation |
| V02 | Prefix reconstruction | Every replayed request/tool event matches its recorded hash and order |
| V03 | Branch isolation | Mutating one branch cannot change another branch or the source archive |
| V04 | Sham identity | Factual and sham delivered input payloads are identical before fresh sampling |
| V05 | Targeted exposure | Only the declared receiver/surface changes at the intervention boundary |
| V06 | Prior exposure detection | Already-seen message/history leak is flagged, not certified |
| V07 | Repeated rendering | Persistent mask remains effective for the declared horizon |
| V08 | Tool protocol validity | Function IDs, arguments, result pairing, and message order remain valid |
| V09 | Fresh continuation | Diverged branches do not reuse original downstream responses |
| V10 | Cache independence | Repeated fresh replicates cannot collapse to a single cached sample unnoticed |
| V11 | Known harmful mechanism | Scripted signal-dependent harmful fixture produces the designed contrast |
| V12 | Benign causal cooperation | A large useful message effect is not sufficient for a harmful certificate |
| V13 | Common cause / inert talk | Suspicion without the relevant causal path is not treated as established causation |
| V14 | Redundant signals | Null single-event intervention is not represented as exoneration |
| V15 | Invalid restore | Deliberate state corruption produces `invalid`, not a score |
| V16 | Metric identity | Coalition advantage equals the verified reward difference; units are correct |
| V17 | Budget barrier | Paid/unknown route, excessive reservation, or exhausted quota is blocked before call |
| V18 | Error accounting | Timeout/refusal/429/parse errors remain missing/failed, never numeric zero outcomes |
| V19 | Analysis hierarchy | Branches are grouped within worlds; repeated copies do not inflate independent N |
| V20 | Offline reproduction | Frozen raw bundle regenerates tables/figures without model calls |
| V21 | Claim lineage | Every displayed headline number resolves to its source record and analysis version |
| V22 | Secret scan | Release artifacts, diffs, logs, and demo assets contain no credential values |
| V23 | Final document | Export matches approved text, figures, references, and page/abstract constraints |

The test worker may add stronger tests. It may not weaken a test to make a broken implementation pass without a documented, scientifically justified requirement change and independent review.

## Golden fixtures and mutation tests

Use a tiny deterministic fixture where the correct response to a message is known analytically. Test the exact world and observation expected after each tool action. Add mutation tests: intentionally leak the removed event through a summary, corrupt a snapshot field, switch the resolved model, change the harm direction, reuse a cached continuation, and drop failed runs. The relevant validator must catch each corruption.

The purpose is not maximum line coverage. It is showing that the system fails safely under the errors most likely to invalidate its headline conclusion.

## Reward audit

Recalculate coalition and outsider rewards directly from `final_summary.json` and verified environment semantics for the archived pilot. Compare them to `summary.csv`. Inspect the meanings of coverage, tasks done, total cost, normalized score, joint reward ratio, and regret. Document units and denominators. Do not infer the entire reward model from field names.

For any oracle/optimal assignment comparison, test small instances by enumeration or another independently checked solver. A loose upper bound must be labeled a bound, not an attainable optimum. Solver failure is not zero regret. Separate a task's aggregate cost from inference dollars throughout the code and UI.

## Cold scientific review

Give a reviewer only the frozen protocol, the main proposed claims, source links, and artifact paths. Ask it to look for:

- circular labels or role-name leakage;
- a missing legitimate-cooperation explanation;
- checkpointing after the target already learned the signal;
- unequal information loss, horizon, sampling, or truncation across arms;
- evidence selected on the outcome;
- statistically inflated sample counts;
- unjustified inference from a null result;
- a novel-sounding name for an existing method;
- unsupported extrapolation to intent, spontaneous behavior, other models, or deployment settings.

The reviewer must reproduce at least one important table or effect from raw data, not only read the prose. It should write the strongest plausible objection in a few sentences and identify the specific test that resolves or fails to resolve it.

## Software and operational review

A separate worker checks deterministic replay boundaries, schema validation, malformed responses, path handling, atomic writes, process cleanup, credential redaction, concurrency, and dependency pinning. Verify the final commands from a clean worktree or temporary environment where practical. Do not uninstall the owner's functioning environment for this test.

A clean-code review is not a substitute for scientific review; a causal review is not a substitute for executing tests. Keep these sign-offs distinct.

## Gate outcomes

- **Pass:** acceptance tests executed and evidence files present.
- **Conditional pass:** a narrowly specified claim/deliverable remains valid after dropping a failed optional feature.
- **Block:** a mandatory validity, billing, security, or evidence-integrity requirement failed.

Every conditional pass must name the removed claim. Example: "Condition-level intervention results only; event-level certificates disabled because exact restore is not established." Do not quietly preserve the more impressive title after downgrading the evidence.

## Honest negative and null outcomes

A null effect with wide uncertainty is inconclusive. A sufficiently precise small effect is evidence against the tested dependency, not all collusion. A failed positive fixture indicates a method or implementation problem. A real prompted coalition that does not benefit is an observed failure to elicit the target behavior under that setup, not a reason to discard the seed.

No release reviewer should require the primary hypothesis to be true. The requirement is that the reported conclusion matches the evidence.
