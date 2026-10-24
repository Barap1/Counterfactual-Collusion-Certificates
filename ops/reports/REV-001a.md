# REV-001a handoff

Task: independent reproduction of the Gate-C headline. Status: complete on synthetic data; held-out execution deliberately deferred until collection is terminal. Owner is the sole author.

Artifacts: `review/reproduce_headline/independent.py`, `README.md`, `tests/test_independent.py`, `tests/compare_synthetic.py`, `synthetic_independent.json`, `synthetic_blackbox/`, `comparison.json`, `comparison.log`, `tests.log`, `blackbox.log`.

Implementation: stdlib-only, no project imports. Raw hash-enveloped manifest/world/selection/checkpoint/branch records supply outsider rewards and explicit attempt statuses. Exactly two exposure endpoints form the coalition; Omean averages the other two rewards. Complete continuation arm means yield K−F; no-exposure/post-decision is zero; other undefined worlds are excluded from paired Delta. Every paired sign vector is enumerated using rational arithmetic, including zeros and ties. All attempts are retained; final whole-world attempts alone enter estimation. Counts distinguish actual attempted, complete, failed, invalid, interrupted and explicitly not-run by world/arm, retaining failed source-world status separately.

Validation commands (repository root; all exited 0 on the final run):

```sh
nice -n 19 python3 review/reproduce_headline/independent.py --input docs/analysis/readiness/synthetic_input > review/reproduce_headline/synthetic_independent.json
nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.analysis run --input docs/analysis/readiness/synthetic_input --out review/reproduce_headline/synthetic_blackbox > review/reproduce_headline/blackbox.log 2>&1
nice -n 19 python3 -m unittest discover -s review/reproduce_headline/tests -v > review/reproduce_headline/tests.log 2>&1
nice -n 19 python3 review/reproduce_headline/tests/compare_synthetic.py > review/reproduce_headline/comparison.log 2>&1
```

Results: 11 tests pass, 514 black-box artifact checks agree, no disagreement. Synthetic Delta=22/7 (3.142857142857143), exact one-sided p=2/128=0.015625, seven defined pairs, six nonzero differences. d_w=[0,1,2,3,4,5,7]; failed-source/cap pair 108 remains undefined. Initial unit run failed only because its unrun-world assertion assumed lexicographic pair order; assertion now selects pair ID explicitly. Host refused nice priority change; commands still completed.

Limitations: no held-out validation; no bootstrap CI, full seal/freeze audit, or scientific claim adjudication. Strict unsupported-schema errors require inspection rather than guessed adaptation. Registry had no REV-001a entry or conflicting lease; direct assignment supplied ownership. Only assigned paths were written. No forbidden experiment paths or services, ledger, secrets, analysis source, or held-out outcomes were read/listed/touched. No network/model calls, new spend, commits or git mutations.

Next: after controller-confirmed terminal collection, run the exact Gate-C command documented in README; compare its numeric headline with the frozen analysis. This task has not run that command.
