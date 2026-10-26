# Evidence boundary: independent frozen-output audit

Post-hoc exploratory analysis; no new experiments or detector tuning.

Checked 21,000 deterministic recorded views and 2,100 archived partition hashes.

Pair separation differs from global binary attribution identifiability. Counts below use 200 independent pairs per row. Different levels reuse those pairs.

| Family | Evidence | Distinct pair | Both labels identifiable | CCC-L v1 correct both |
|---|---|---:|---:|---:|
| P1 | I1 | 0/200 | 0/200 | 0/200 |
| P1 | I2 | 0/200 | 0/200 | 0/200 |
| P1 | I3 | 200/200 | 0/200 | 200/200 |
| P1 | I4 | 200/200 | 0/200 | 200/200 |
| P1 | I5 | 200/200 | 0/200 | 200/200 |
| P2 | I1 | 0/200 | 0/200 | 0/200 |
| P2 | I2 | 0/200 | 0/200 | 0/200 |
| P2 | I3 | 0/200 | 0/200 | 0/200 |
| P2 | I4 | 200/200 | 200/200 | 200/200 |
| P2 | I5 | 200/200 | 200/200 | 200/200 |
| P3 | I1 | 0/200 | 0/200 | 0/200 |
| P3 | I2 | 0/200 | 0/200 | 0/200 |
| P3 | I3 | 0/200 | 0/200 | 0/200 |
| P3 | I4 | 0/200 | 0/200 | 0/200 |
| P3 | I5 | 200/200 | 200/200 | 200/200 |
| P4 | I1 | 200/200 | 0/200 | 0/200 |
| P4 | I2 | 200/200 | 0/200 | 0/200 |
| P4 | I3 | 200/200 | 0/200 | 0/200 |
| P4 | I4 | 200/200 | 0/200 | 0/200 |
| P4 | I5 | 200/200 | 0/200 | 0/200 |
| P5 | I1 | 200/200 | 200/200 | 0/200 |
| P5 | I2 | 200/200 | 200/200 | 0/200 |
| P5 | I3 | 200/200 | 200/200 | 0/200 |
| P5 | I4 | 200/200 | 200/200 | 0/200 |
| P5 | I5 | 200/200 | 200/200 | 0/200 |
| P6 | I1 | 200/200 | 0/200 | 0/200 |
| P6 | I2 | 200/200 | 0/200 | 0/200 |
| P6 | I3 | 200/200 | 0/200 | 0/200 |
| P6 | I4 | 200/200 | 200/200 | 0/200 |
| P6 | I5 | 200/200 | 200/200 | 0/200 |

Deleting the newly added separator restores byte-identical observations in all 200 pairs for each of P1 (I3→I2), P2 (I4→I3), P3 (I5→I4), P4 and P6 (I1→I0). This verifies necessity within these constructed twins, not sufficiency outside the declared policy space.

Component controls isolate the informative record. At P2/I4, deleting the entire PF continuation record restores equality in 200/200 pairs, while deleting PK alone or the common probe metadata leaves all 200 pairs distinct. The PF outsider-reward scalar by itself differs in all 200 named pairs, although actions and other reward fields also differ. At P3/I5, deleting only authorization.status restores equality in 200/200 pairs. These are diagnostic field deletions, not new admissible benchmark information sets or inputs to a retuned auditor.

At P1/I3, CCC-L v1 excludes attribution on 200/200 inert members whose observational classes also contain prohibited relayed policies. These negative answers match the selected inert labels; they are not 200 observed false negatives. The frozen overclaim metric counts positive accusations only; its zero count does not validate negative exclusions.

At P6/I4, both labels are identifiable in 200/200 pairs, yet CCC-L v1 abstains on all 400 members. Identifiability does not guarantee that this rule uses the evidence.

The frozen composite utility criterion passes 2/84 v1 cells (P4/I4, P4/I5); 73/84 accuracy gaps are undefined. P2/I4 and P3/I5 correctly answer both members in 200/200 pairs but cannot establish the whole conjunction because abstention precision/recall have empty denominators. The aggregate failure is retained.

Generator labels, finite policy scope, post-hoc deterministic restriction, noisy-platform divergence, and the separate eight-pair real-agent uncertainty remain unchanged. See boundary_audit.json for complete tables, exact witnesses and source hashes.
