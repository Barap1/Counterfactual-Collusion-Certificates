# BENCH-IMP DEV report

All results below are **development** evidence. Only benchmark seeds
**13000–13049** were used. The complete run contains **12,600** instance/set
records, **12 methods**, and **50 independent seed blocks**. Twins, copies,
epsilon strata and continuations at a seed are nested.

| Pair | Minimal observable separator, both epsilon strata |
|---|---|
| P1 redundancy/inert | I3 |
| P2 allocation/efficiency | I4 |
| P3 unauthorized/authorized | I5, definitional |
| P4 common cause/message cause | I1 |
| P5 suspicious/plain inert | I0, same-label control |
| P6 useful information/harmful steering | I1 |

These separators hold in all 100 seed/stratum combinations per pair. Pairwise
separation differs from global identifiability: P1's inert and P4's common-cause
members remain globally ambiguous in the full crossed policy space.

There were **zero identical-view twin symmetry violations**. A complete seed
13000 replay reproduced all **252** records byte-for-byte in canonical JSON.
All **24 frozen source/data files** retain their initial hashes.

Frozen CCC supported legitimate P2/P3 members at I2–I5: **50/50 seed units** per
type/set at eps=0 and **33/50** at eps=.1. This yields **664 member/set records**,
not 664 independent units. The verdict is an **L2 exposure claim**, not an M
collusion attribution. These results were retained without changing CCC.

Fresh iid Jira RQ3: **12/50 = .24**, CP95 **[.1306, .3817]**, one forbidden world
per seed. No method output defines these oracle labels or effects.

All requested classes were retained. P6's initial factual-payoff mismatch was
corrected with an explicit information-gated productivity model; other benchmark
corrections and exact commands are in [VALIDATION.md](../VALIDATION.md).

Validation: **19 benchmark tests passed**. The full offline suite ran **442**
tests: **437 passed, 1 unrelated stale demo/MISSION hash failure, 4 skipped**.
The failure remains outside this task's write scope.

Limits: structural replay checks are not native Jira certificates; stochastic
partitions condition on the fixed continuation schedule; Bayes uses uniform
finite-policy priors. CP intervals label independent unit-any/unit-all events,
not fractional member counts. No prospective run occurred; new spend **$0**.
