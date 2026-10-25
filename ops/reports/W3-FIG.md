## Task
Repair prospective frontier data access only.

## Status
Fixed and verified offline. ORCH figure generation remains pending.
`ops/tasks.json` was checked; it has no W3-FIG entry. The explicit worker
brief supplies ownership; no registry changes were made.

## Artifacts
- `figures/enh/make_enh_figures.py`: select rows by epsilon and membership
  of `kind` in `pairs`.
- `docs/enh/figures_fix_note.md`
- `/private/tmp/W3-FIG/check_frontier_paths.py`
- `/private/tmp/W3-FIG/validation.txt`

Exact key path now used:
`u["pairs"][kind]["by_set"][k]["pair_distinct"]`, for
`units = [x for x in F if x["epsilon"] == eps and kind in x["pairs"]]`.

## Validation
Command run:
`python3 /private/tmp/W3-FIG/check_frontier_paths.py > /private/tmp/W3-FIG/validation.txt`

Passed static AST parsing/compilation and evaluation of the figure's actual
selection/separation expressions. All 14,400 paths exist and contain booleans;
each kind/stratum selects 200 unique seeds. Only key names and counts printed.
No scientific definitions, labels, thresholds, or criteria changed.

## Limitations
Full figure command was not run, as instructed. Rendering and generated
artifacts await ORCH verification.

## Budget
$0; no network, Modal, inference/API calls, git, or secret reads.

## Next
ORCH runs:
```sh
starter/collusion_hackathon/colosseum/.venv/bin/python figures/enh/make_enh_figures.py --run docs/enh/r2/run_par --out figures/enh/prospective --label PROSPECTIVE
```
