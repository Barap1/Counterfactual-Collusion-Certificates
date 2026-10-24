# STAT-002a offline analysis

Run from the repository root with the existing environment:

```sh
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.analysis run --input docs/runner/exp001-pilot3 --out docs/analysis/pilot3
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.analysis run --input docs/runner/dry-run-dev02-v2 --out docs/analysis/dry-run-v2
starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests/analysis -t .
```

The package imports no runner, replay, infrastructure, audit, provider, or network client. It reads only named metadata and accounting ledgers. It does not open request/response payloads or fixture labels. An explicit guard rejects `exp001-live` as an input root. Writes go beneath the output directory; input and output trees must be disjoint. No installation or service is needed. Dependencies are the existing NumPy and SciPy.

`loaders.py` validates the canonical contract and adapts finished legacy DEV runner directories; `shift_perm.py` implements exact shift-permutation tails and cent-grid intervals; `statistics.py` supplies seeded world bootstrap, exact sign flips, Holm, Clopper–Pearson, t intervals and exact TV null correction. `status.py` independently implements the case rule. `study.py` computes world estimands and registered secondary contrasts. `pinning.py` provides the treatment-blind noise/threshold helper. `pipeline.py` exports tables and figure data, and `__main__.py` exposes `run`.

Canonical inputs are `manifest.json`, `worlds.json` (a list of world records), `checkpoints.json` (a list), `branch_ledger.jsonl`, optional `events.jsonl`, and `stage2_addendum.json` (required for holdout). Fields follow analysis_spec §1. Checkpoints additionally specify `mstar_available` and `placebo_kind: N_m` for holdout. World records carry the frozen pair/outsider partition, checked against every branch. Exactly one checkpoint per world/regime is supported; duplicate scientific units are rejected. Missing scheduled replicates receive explicit continuation-table missing rows with null attempt IDs; these are never counted as actual attempts.

Holdout gates check frozen status and both file hashes against repository protocol/Stage 2 artifacts, and the input addendum against the manifest hash. Development thresholds without an addendum are explicitly the thin-DEV fallback (m_O=5, delta_W=10, delta_S=5), never a frozen estimate. The `pin_thresholds` helper uses eligible F/S outcomes only, counts eligible matched world pairs, and uses dev detector similarity pairs for theta. It does not produce a complete Stage 2 addendum or authorize a freeze.

The final attempt per checkpoint/arm/replicate enters estimation. All earlier attempts and API accounting events remain in separate outputs. Infrastructure statuses, noncommit/refusal subtypes, absent scheduled rows, session breaks and unrun planned worlds remain visible. Behavioral outcomes cannot be retried. Session breaks exclude the entire checkpoint. Reward metrics are derived from agent rewards and roles, never joint_reward. Missing outcomes remain null. Legacy branch validation failures remain `invalid_restore`; their original runner status is also retained.

Case intervals enumerate all assignments, with ties against the claim. Binary search on monotone tail probabilities returns exactly the specified first/last accepted point of the 0.01 grid [-60,60], including the specified endpoint fallback. The mandatory descriptive contrast tau_O − tau_O^N simplifies to mean(K) − mean(N), so its exact shift interval compares N to K directly. TV reports raw, exact permutation-null mean, and excess together. The placebo arm in pre-v1.2 DEV data is always labelled `N_v1.1_deprecated`; it cannot clear v1.2 placebo gates.

Study bootstraps resample paired world differences, B=10000, NumPy PCG64 seed 20261025, linear percentile interpolation. Singleton/empty bootstrap calls raise `InsufficientWorlds`; the reporting layer instead prints null intervals. Within-regime intervals are suppressed below five defined worlds. Delta_conditional is always descriptive. S1–S3 raw sign-flip and Holm p-values are reported. Per protocol v1.2, Tier B remains exploratory even when numerical floors are met. DEV outputs generate no claim candidates. Holdout candidates are proposed, exploratory templates with input hashes and reviewer=null.

Outputs are deterministic CSV/JSON pairs, an aggregate with input and implementation hashes, a validation report, a claims JSONL, and figure data. `attempts`, `events_accounting`, `scheduled_statuses`, `coverage`, and `status_crosscheck` accompany the named spec tables. `status_crosscheck` contains disagreements only when an input checkpoint supplies `audit_status`; unavailable comparisons are explicitly marked on certificates. The package does not import or rerun the shared audit engine.

## Evidence and limits

The 28 unittest methods cover all 16 required test families plus 12 regression checks. Coverage simulation: 2000 Gaussian 4v4 draws, seed 20261025, realized one-sided lower coverage 1908/2000 = 0.954 (`coverage_simulation.json`). `vectors.json` contains all four frozen interval vectors and all six minimum-p vectors; an independent scalar reference is also checked. Tests run under the supplied unremovable offline audit guard and include network mocks, input-label isolation, deterministic output hashes, world-versus-row variance, status truth tables, failure accounting and hand-calculated missing fills.

The finished pilot3 and scripted dry-run are DEV implementation evidence only. Pilot3 has 14 recorded continuation attempts, one inconclusive checkpoint, and seven unrun planned worlds. Dry-run-v2 has eight recorded continuation attempts and one inconclusive checkpoint. Neither produces claim candidates. `end_to_end.json` records actual statuses and byte-determinism checks. No scientific findings are claimed.

Remaining specification gaps are explicit:

- The frozen text demands a TV_excess CI but specifies no interval algorithm or estimand for it. Outputs contain a null interval and the reason; permutation-null quantiles are not presented as a confidence interval.
- The eligibility-rate difference is not itself binomial. It is reported with a conservative 95% simultaneous interval formed from two Bonferroni-adjusted exact binomial intervals; the method is labelled. This choice needs statistical review.
- No fixture certificates/labels were supplied for this task. The fixture-evaluation command, fixture confusion/risk-coverage figures and dev matched-coverage baseline comparisons are not implemented. `run` never opens labels. The `pin`/full Stage 2 diagnostic CLI is also outside this implementation; only the F/S-blind threshold helper is supplied.
- No Stage 2 artifact exists in the named stats directory at implementation time. Held-out runs fail closed until it exists and matches both hashes. No held-out end-to-end result is claimed.
- Old DEV metadata lacks the complete v1.2 validity contract. Missing validity is reported as unestablished, rather than inferred from older check identifiers. TV/sample intervals and throughput wall time are not invented from unavailable metadata.

The task registry was inspected: no STAT-002a entry/lease was present. Work followed the direct task assignment and its owned paths; shared registry files were not edited.
