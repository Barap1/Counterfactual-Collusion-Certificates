# ENH — Competition enhancement sprint (brief for every worker)

Started 2026-10-24 15:05 UTC. Submission deadline 2026-10-26 11:59 UTC (owner submits). Director: main Opus session.
Goal: turn CCC into the strongest scientifically defensible Track 2.3 submission. North star: a contribution to
**evidence standards for AI collusion attribution** (causal influence vs harm vs justified attribution vs identifiability),
not a claim to detect collusion.

## Frozen — never modify, relabel or overwrite
- Held-out EXP-002 (protocol v1.2) and its result: Delta = 1.354, world-cluster 95% CI [-0.020, 2.834], exact one-sided
  sign-flip p = 0.0703, preregistered directional hypothesis NOT supported (confirmatory null). Registered non-commit
  sensitivity 0.727 [-0.31, 1.91] (original-registered-secondary; its p 0.156 is post hoc; corrected 2026-10-24 per ENH-B). Certificates 0/11/5. 8 matched world pairs = the independent sample size.
  199 scheduled branch records = 143 executed valid + 56 unrun N (placebo unavailable).
- Paths: `docs/analysis/exp002_heldout*/`, `docs/analysis/exp001_dev*/`, `docs/runner/archives/`, `docs/gate_a/`,
  `docs/stats/`, `docs/research/sci002/protocol.md`, `results/baselines/`, `docs/review/rev001/`.
  Any correction = a NEW versioned directory + a field-by-field diff + a note; originals stay byte-identical.
- Gate A fixtures and DEV data are DEVELOPMENT evidence forever. New performance claims need a prospectively frozen
  protocol (R2) and fresh seeds/worlds drawn after the freeze.

## Evidence categories (label every number with exactly one)
original-confirmatory · original-registered-secondary · descriptive · post-hoc-exploratory · new-prospective (frozen
before outcomes, under `docs/enh/r2/`) · development (fixtures/DEV).

## Hard rules
- $0 new spend. No paid APIs, no cloud inference. Local Ollama only via the existing guard and only if the director
  explicitly assigns it. Never print or commit `.env`, `compute.env`, `ops/*.local.json`, tokens, auth headers.
- No git commits/push/reset/clean (the director commits). No repo visibility, sharing, Google Doc or submission actions.
- Write only inside the paths your brief assigns. Do not load `CCC_MASTER_SPEC.md` or `docs/research/*` whole.
- No invented citations, results, or tool actions. Say "not checked" rather than guess.
- Do not spawn sub-agents unless your brief allows it (global cap 6 live agents, 3 layers).

## Enhancement gates (apply only to this effort; Gates A–D stay as recorded)
R1 direction accepted · R2 protocol frozen · R3 evidence validated · R4 presentation verified · R5 owner review.

## Handoff (end of every task, ≤300 words, also saved as `ops/reports/<TASK-ID>.md`)
Task / Status / Artifacts / Validation / Limitations / Budget ($0 + model used) / Next.
