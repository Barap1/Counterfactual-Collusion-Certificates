# GA-DIAG handoff

Task: GA-DIAG. Status: diagnosis complete; V07 handoff repaired; Gate A remains FAIL.

A1: **FIXTURE DESIGN** — 68/80 oracle effects below m_O=2.5, including 54 zero/negative; all 80 native point CIs match oracle effects and the sign is correct. **PROTOCOL DESIGN** — all 12 above-floor cells trigger the literal F-vs-N lesion veto; eight also fail coalition benefit. CCC TP remains 0/80; B3b TP remains 60/80.

A5: **IMPLEMENTATION BUG** — V07 carrier flags were computed but not passed to decide. Fixed in ccc/audit/gate_a.py with provenance and regression tests. Not-supported drops 100→48; remaining 24 lack surviving private resends (**FIXTURE DESIGN**) and 24 have undetected semantic carriers (**PROTOCOL DESIGN**).

A6: **FIXTURE DESIGN** — 350/360 faults activate and all 350 are invalid. All ten inactive A6b cases have one receiver observation; native tests prove clean/faulty K request hashes and outcomes identical, 10/10 valid.

| Check | Result | Passed/total |
|---|---|---|
| F_vs_S_identical | PASS | 380/380 |
| K_only_intended_exposure | PASS | 1520/1520 |
| branch_isolation | PASS | 380/380 |
| A2_not_supported | PASS | 80/80 |
| A6_invalid | FAIL | 350/360 |
| A5_not_exonerated | FAIL | 72/120 |

Artifacts: `docs/gate_a/diag/diagnosis.md`, `proposals.md`, `A1_cells.csv.gz`, `diagnosis_summary.json`, `gate_a_results.json.gz`, full logs and reproduction scripts. Files edited: `ccc/audit/gate_a.py`, `tests/audit/test_diagnosis.py`, `docs/gate_a/diag/*`, this report.

Validation command: `starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests/audit -t .`. Actual output:

```text
........................................
----------------------------------------------------------------------
Ran 40 tests in 18.517s

OK
GA-DIAG inactive A6b: 10/10 valid; clean K request hashes and outcomes identical; one receiver observation each
```

Limitations: deterministic DEV only; 800 cells/20 task seeds; unchanged provisional inference semantics. Full rerun: 124 status changes, zero branch/baseline/oracle differences, zero source drift. Budget: $0, no live calls, no held-out generation, no commits. Next: director/science decisions in proposals.md. Exact evaluation/analysis commands: docs/gate_a/diag/commands.md.
