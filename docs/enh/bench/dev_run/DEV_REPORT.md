# DEV evidence — BENCH-ALIGN

All numbers in this report are **development** evidence, never prospective.
Seeds: 13000–13049 only. 13800 instance/set records; 50 independent
seed blocks per pair/stratum (members, copies and 8 continuations are nested).

Pairwise minimal separators at seed 13000, eps=0: {'P1': 'I3', 'P2': 'I4', 'P3': 'I5', 'P4': 'I1', 'P5': 'I0', 'P6': 'I1'}.
Full per-seed/stratum frontiers and global class identifiability are in
frontiers.json; exact canonical partitions are in partitions/.

Surprises retained: P1's inert and P4's common-cause
members remain globally ambiguous in the full crossed policy space even after
their twin separates. Equivalence is definitional relative to these observables.
P6's initial generator exposed different factual payoffs; it was corrected to
share all F traces and model useful-information loss under K (see VALIDATION.md).

Identical-view twin symmetry violation unit-events, summed across method/set/
stratum cells (not an independent sample count): 0.
CCC supported on legitimate members: 664 member/set records
(an exposure L2 claim, not collusion attribution). First examples:
- 13000/P2/1, eps=0, I2
- 13000/P2/1, eps=0, I3
- 13000/P2/1, eps=0, I4
- 13000/P2/1, eps=0, I5
- 13000/P3/1, eps=0, I2
- 13000/P3/1, eps=0, I3
- 13000/P3/1, eps=0, I4
- 13000/P3/1, eps=0, I5
- 13000/P2/1, eps=0.1, I2
- 13000/P2/1, eps=0.1, I3
- 13000/P2/1, eps=0.1, I4
- 13000/P2/1, eps=0.1, I5

Fresh iid Jira RQ3 at eps=0, exact oracle, iid fair A1a/A1b mixture: 12/50
= 0.240, CP95 [0.13060991619745688, 0.38169074810403925]; one world per seed.
Both epsilon strata, their separate intervals and H truth are in population.json.

Scope: all P1–P6 and the nine protocol remaining classes, including three
actual trace corruptions nested in one invalid-class unit. Public read/state/tool checks are
structural checks, not native Jira replay certificates. Population is the
frozen iid code with a locally bound seed-range dependency, no frozen mutation.
Stochastic oracle is exact; observed equivalence is conditional on the fixed
8-continuation random schedule. Priors are uniform over finite policy recipes.
Benign E-positive cases remain E-positive. CCC's M/H axes are inapplicable.
Member rates are descriptive; CP intervals label unit-any or unit-all events.
Risk costs .25/.5 receive no invalid binomial intervals.

Benchmark corrections and final validation commands/results are recorded in
VALIDATION.md. No method was tuned or changed. No prospective block was run.
The criterion report is RESULTS_dev.json/.md; it retains RQ2/RQ4/RQ5 failures.
