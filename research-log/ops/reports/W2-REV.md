## Task
W2-REV: independent review of EXP-003 protocol, implementation, budget and freeze integrity.

## Status
ISSUES — approval withheld. Blocking gaps: no measured GPU cost/world or feasible block budget; unspecified cost/deadline controller; freeze/exclusion/seed bindings unverified at admission. Analysis lacks explicit confirmatory-floor enforcement.

## Artifacts
- docs/enh/exp003/REV_PROTO.md — eight numbered findings with severity and validation evidence.
- ops/reports/W2-REV.md — this handoff.

## Validation
All 213 code hashes, three evidence hashes and protocol hash match. EXP-002's seven frozen byte hashes, approved canonical manifest and archived trace hash match. Independent sign-flip checks passed at n=11 and n=32. Offline probes demonstrated arbitrary holdout seeds/placeholder freeze fields pass validation and six-pair/three-continuation new-prospective analysis returns significant adjusted p-values. Exact substantive validation command and additional probe descriptions are in REV_PROTO.md. Inspection used cat, rg and sed; guarded Python ran with bytecode disabled. No Git, network, Modal or experiment/model calls; no prohibited secrets read.

## Limitations
No cloud or full collector tests. Sign-flip inference requires an explicit symmetry/exchangeability assumption. Complete-case/time-stop interpretation needs qualification. No full historical inventory certifying every EXP-002 result file. Direct user assignment used; no W2-REV lease; registry untouched.

## Budget
$0 experimental spend. Codex review; exact runtime model identifier unavailable. $45/$51 feasibility remains unproven.

## Next
Resolve findings, supply measured feasibility and capped controller/run configuration, enforce freeze/seed and analysis gates, refresh hashes, and obtain independent re-review before director freeze confirmation.
