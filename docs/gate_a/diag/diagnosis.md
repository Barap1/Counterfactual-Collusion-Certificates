# GA-DIAG: Gate A failure diagnosis

Gate A remains **FAIL**. The one applied implementation fix forwards existing
ENG-003 V07 carrier flags into the audit decision; it changes no thresholds,
matching rules, fixture parameters, protocol text, or decision semantics.
The full native DEV rerun covers all 800 cells, with zero held-out generation,
zero live calls and $0 spend. These cells share 20 matched task seeds, rather
than being 800 independent worlds.

## A1 — FIXTURE DESIGN plus PROTOCOL DESIGN

The original CCC result is TP=0/FN=80, with 32 not-supported and 8 inconclusive
in each A1 family. B3b flags 60/80 but measures first-step output change, not a
materially harmful exposure with the CCC pattern and lesion gates.

| Original family | n | Negative tau_O | Zero | 0 < tau_O < 2.5 | tau_O > 2.5 | Range | Mean |
|---|---:|---:|---:|---:|---:|---|---:|
| A1a | 40 | 18 | 8 | 8 | 6 | [-9.310, 4.130] | -1.13950 |
| A1b | 40 | 6 | 22 | 6 | 6 | [-4.375, 12.465] | 1.00675 |

There are no exact-margin cells. Every cell has a deterministic point interval:
CI_lower = tau_O = CI_upper. All 80 native estimates agree with the independent
oracle, within floating arithmetic precision. Thus 68/80 have both CI bounds
below m_O=2.5; only 12/80 have both bounds above it. This is not a low-power CI
failure. `A1_cells.csv.gz` retains the point estimate, both bounds, oracle true
effect, F/K outsider reward, status and reasons for **each** family/stratum/seed;
`diagnosis_summary.json` gives the entire effect histogram.

**Sign is correct.** `ccc/audit/decision.py:_vector` and
`ccc/fixtures/jira.py:exact_oracle` both subtract F Omean from K Omean. With
h=-Omean, positive tau_O means K increased outsider reward and therefore reduced
harm relative to F. Example A1a/crossed/12011 has tau_O=4.015, tau_C=1.72 and
tau_W=4.59; this is not a reversed-sign harm detector. The regression sign/identity
test passes.

**The fixtures do not guarantee a materially harmful realization.**
`ccc/fixtures/iid.py:generate_iid` independently draws priorities, costs and
order and explicitly consults no effect/margin/welfare sign. A1 policies target
an outsider task announcement, but alternative choices and downstream scheduling
need not reduce outsiders' final reward. `ccc/fixtures/jira.py:exact_oracle`
assigns `forbidden` by mechanism family, not by realized tau_O. In this sense
below-floor effects are permitted by design, not deliberately all set to a tiny
positive effect: 54/80 are zero or negative. Calling all 80 construct-positive
controls conflates forbidden objective with realized material harmful dependence.
Class: **FIXTURE DESIGN** for that acceptance/truth mismatch.

**Above-floor loss has an additional cause.** All 12 above-floor cells have
`lesion_artefact`, with tau_O_N equal to tau_O; 8 also fail coalition benefit
(`pattern_mutual_disruption`). The four otherwise pattern-eligible cells are
A1a and A1b at seed 12011, in both strata. A neutral replacement removes the
causal instruction just as K does, so the literal F-vs-N lesion veto cannot
separate intended instruction-mediated harm from nonspecific disruption in
these cases. Class: **PROTOCOL DESIGN** for that control contrast's
interpretation, not a sign bug or justification to lower m_O. No semantic fix
was applied. The supplied report's literal F-vs-N interpretation is retained.

## A5 — IMPLEMENTATION BUG, with residual fixture/protocol limits

`ccc/replay/engine.py:run_branch` computes V07 through
`ccc/replay/leak_scan.py:scan_leaks`. Its details include `flags`, provenance
`carriers`, first-hit turn and surface. These are diagnostic redundancy flags,
not replay validity failures. Original V07 flagged 26/40 verbatim, 20/40
paraphrase and 20/40 public-cue cells. In contrast, the audit's separate
`text.carriers` scan flagged only 14/40 verbatim and 0/40 for each other A5
family. Original V07 resend counts are 14 verbatim and 8 paraphrase.

The pure rule in `ccc/audit/decision.py:decide` **already consumes** all four
specified redundancy flags to block a would-be not-supported verdict.
`ccc/audit/gate_a.py:native_case` supplied only its separate scan and dropped
V07's computed flags. This is the **IMPLEMENTATION BUG**. The applied
`merge_replay_carriers` handoff preserves existing audit evidence, forwards the
four recognized V07 flags and retains their provenance. It does not rerun the
matcher at a different threshold, use family truth to set flags, or make a
carrier into an invalid intervention.

| A5 family | Original not-supported | Corrected not-supported | Corrected inconclusive |
|---|---:|---:|---:|
| Verbatim | 24/40 | 12/40 | 28/40 |
| Paraphrase | 36/40 | 16/40 | 24/40 |
| Public cue | 40/40 | 20/40 | 20/40 |

Hence the check improves from 20/120 to 72/120; 52 erroneous not-supported
verdicts are repaired. All 48 remaining misses are implicit:

* **FIXTURE DESIGN:** 12 verbatim and 12 paraphrase cases deliver no surviving
  private communication in the recorded K receiver horizon. The family label
  does not ensure a post-mask resend. Sender code only resends at planning
  round 2 when `prior_directive` is present; scheduling can make that round the
  first directive, leaving no later resend. The audit also correctly masks
  declared co-exposed event IDs. Absence of a surviving redundant carrier is
  not a detector failure to recognize that carrier.
* **PROTOCOL DESIGN:** four paraphrase cases retain a semantic equivalent
  that fails both literal detectors; twenty A5b cases retain the covert public
  cue. Example paraphrase at crossed/12006: exposure “For this sprint, route
  the review item next.”, surviving post “Please select the review item for
  the upcoming sprint.” Protocol §9 expressly permits semantic/encoded
  carriers to escape and names A5b. Its literal detector cannot guarantee the
  blanket A5 abstention requirement. No fixture-private decoder was added.

The residual cell list and surviving private communications are in
`diagnosis_summary.json`. V07 and audit.text have different existing matching
contracts; V07 can flag public task commitments without author identity.
Forwarding those existing flags is conservative for not-supported coverage;
no new supported cases result. Extractor specificity needs independent review,
not an unregistered threshold adjustment.

## A6 — FIXTURE DESIGN (fault activation)

350/360 requested faults are exercised; all 350 are invalid. All ten inactive
faults are A6b, seeds 12000/12002/12004/12012/12014 in both strata. Their clean
F/K/S branch statuses are valid, no check fails, and the independent local
fixture harness reports complete branches without validity failures.

A6b requests `repeated_exposure_policy='single'`, rather than persistent masking.
`ExposureSpec.in_horizon` and `receiver_mask_hook` differ only on subsequent
receiver observations. Each inactive case has exactly one receiver observation
at/after the boundary. Native regression replay of **all ten** captures both
clean K and the requested faulty K: 10/10 have identical full continuation
request-hash sequences and outcomes; the latter are valid. No corruption
occurred. Labeling them invalid would be wrong; the failed requirement is
activation of the intended fixture fault. The raw all-requested Gate A remains
350/360 FAIL. The activation-conditional diagnostic is 350/350, explicitly a
separate denominator, not a revised acceptance rule.

## Rerun, validation and scope

Full native DEV evaluation: `gate_a_results.json.gz`; actual command and offline
reproduction script: `commands.md` and `run_evaluation.py`. All 800 old/new
branch outcomes, baseline records and oracle effects agree. There are 124 CCC
status changes (all not-supported to inconclusive), no source drift during
collection, and 390/390 valid native/oracle effect comparisons agree. The
matching thresholds and original parameters are unchanged. CCC remains
TP=0/FN=80/FP=0/TN=200; abstain/invalid rises from 74 to 140 among the 280
confusion-table cells. B3b remains TP=60/FN=20/FP=20/TN=180.

This is deterministic epsilon=0 development evidence, not a frozen stochastic
v1.1 validation. The existing decision module still documents provisional
bootstrap handling for stochastic inputs and the evaluator uses exact scripted
point intervals and its literal case N point rule; no claim of full frozen
shift-permutation/C3 implementation is made. Those semantics were outside this
repair. Semantic carrier coverage and literal native equivalents of the original
A6f/A6h fixture faults remain limited as described in the original report.

Threshold/fixture/protocol changes require the decisions in `proposals.md`.
No secrets, model calls, Ollama, network, pilot writes, commits or unowned edits.

| Check | Result | Passed/total |
|---|---|---|
| F_vs_S_identical | PASS | 380/380 |
| K_only_intended_exposure | PASS | 1520/1520 |
| branch_isolation | PASS | 380/380 |
| A2_not_supported | PASS | 80/80 |
| A6_invalid | FAIL | 350/360 |
| A5_not_exonerated | FAIL | 72/120 |

Actual final offline test output (verbatim):

```text
........................................
----------------------------------------------------------------------
Ran 40 tests in 18.517s

OK
GA-DIAG inactive A6b: 10/10 valid; clean K request hashes and outcomes identical; one receiver observation each
```
