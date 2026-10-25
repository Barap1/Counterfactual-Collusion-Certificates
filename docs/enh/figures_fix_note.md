# W3-FIG: prospective frontier row access

`run_par/frontiers.json` contains 4,200 rows: 1,800 with empty `pairs`
and 400 for each of P1–P6. Each pair kind has 200 independent seed rows
per epsilon stratum. Rows do not all contain every pair kind.

`fig_frontier` now selects rows with both `x["epsilon"] == eps` and
`kind in x["pairs"]`, then reads
`u["pairs"][kind]["by_set"][k]["pair_distinct"]`.
The numerator and denominator therefore use the existing pair-kind seed
population. No scientific definition, label, threshold, or criterion changed.

Offline validation: `/private/tmp/W3-FIG/check_frontier_paths.py` statically
compiles the figure script, extracts its actual row-selection and separation
expressions via AST, and checks all 14,400 selected paths. All pass; every
kind/stratum has 200 unique seeds and six information-set entries. Output
contains only key names and counts, saved to
`/private/tmp/W3-FIG/validation.txt`.

The full generation command is reserved for ORCH. SVG/PDF/JSON generation
and Chrome PDF availability have not been verified by this worker.
