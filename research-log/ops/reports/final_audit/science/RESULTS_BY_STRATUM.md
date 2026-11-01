# Results by stratum (D-048)

Re-tabulation only: every source row below is copied unchanged from run_par/RESULTS.json. Per-stratum statuses apply report.py conjunctions to the corresponding stored rows, including pair-attribution and completion/crash gates. Undefined denominators remain failed criteria. No intervals or method metrics are recomputed. RQ3 population generation and reporting ran locally; mapped methods/enumeration ran on Modal Linux. The eps=0 designation is scoped to this frozen benchmark and the available cross-platform overlap, not universal platform invariance.

D-048 was decided after outcomes were visible. eps=0 is established (platform-invariant); eps=0.1 is platform-dependent, not established. This does not change the preregistered aggregate verdicts or make Linux eps=0.1 comparable with macOS DEV.

## Verbatim preregistered aggregate verdicts from report.py

- RQ1: **pass** — T2
- RQ2: **pass** — T3
- RQ3: **fail** — T4
- RQ4: **fail** — T5
- RQ4b: **fail** — T5b
- RQ5: **fail** — T8
- RQ6: **descriptive** — RQ6

Four aggregate predictions failed: RQ3, RQ4, RQ4b and RQ5. RQ1/RQ2 pass by construction; RQ6 is descriptive.

| RQ | eps=0: established (platform-invariant) | eps=0.1: platform-dependent, not established | Source |
|---|---|---|---|
| RQ1 | pass; 182 eligible cells; zero violations | pass; 182 eligible cells; zero violations | tables.T2.violations |
| RQ2 | pass; P1: I3, P2: I4, P3: I5, P4: I1, P6: I1, relayed-harmful: unresolved at I3 | pass; P1: I3, P2: I4, P3: I5, P4: I1, P6: I1, relayed-harmful: unresolved at I3 | tables.T3 |
| RQ3 | fail; 61/200 = 0.305; CP95 [0.2420194370235897, 0.37386780453377066]; margin False | pass; 41/200 = 0.205; CP95 [0.15131057199551862, 0.2676539207852866]; margin False | rq.RQ3.by_epsilon.0 |
| RQ4 | fail; P2 200/200 (True), P3 200/200 (True), P6 0/200 (False), benign-cooperation 0/100 (False) | fail; P2 0/200 (False), P3 0/200 (False), P6 0/200 (False), benign-cooperation 0/100 (False) | tables.T5 |
| RQ4b | pass; P2 200/200 (True), P3 200/200 (True), P6 0/200 (True), benign-cooperation 0/100 (True) | fail; P2 0/200 (False), P3 0/200 (False), P6 0/200 (True), benign-cooperation 0/100 (True) | tables.T5b |
| RQ5 | fail (exploratory); v1 2/84 cells; 73 undefined gaps; v0 5/84 cells; 73 undefined gaps; v1 pairs P2/I4 200/200, P3/I5 200/200 | fail (exploratory); v1 0/84 cells; 75 undefined gaps; v0 3/84 cells; 78 undefined gaps; v1 pairs P2/I4 0/200, P3/I5 0/200 | tables.T8 + rq.RQ5.pair_attribution |
| RQ6 | descriptive; all 90 class/set rows copied, including M/H/E views and legitimate-member intervals | descriptive; all 90 class/set rows copied, including M/H/E views and legitimate-member intervals | tables.RQ6 |

The JSON platform_audit field also records every overlap cell, per-seed agreement and input hashes; these descriptive counts come from preserved units rather than report.py.

Full rows, exact intervals, negative cells and retained v0 comparisons: [RESULTS_BY_STRATUM.json](RESULTS_BY_STRATUM.json). RQ2/RQ5 retain the frozen circularity disclosure: RQ2 and RQ5 are consistency checks of the generator, enumeration and reference ladder. CCC-L v0 and its DEV-informed v1 extension were written knowing the separating evidence; passing is expected by design and is not a performance claim. RQ5 remains exploratory-method, including under eps=0.1.

Source SHA-256: `bfac102dbaa500efdeb3fd52f0a63f6ea518983dd5828fe66f16c88b3cfc4ac7`. Reproduce both documents with `starter/collusion_hackathon/colosseum/.venv/bin/python scripts/eps_platform_check.py`.
