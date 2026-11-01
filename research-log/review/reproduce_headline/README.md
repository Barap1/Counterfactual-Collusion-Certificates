# Independent Gate-C headline reproduction (REV-001a)

Owner is the sole author. This stdlib-only program imports no `ccc` module. It reads runner metadata directly, verifies SHA-256 envelopes, and prints JSON to stdout. It makes no network or model calls and does not modify input files.

From the repository root, **after the controller confirms collection is terminal**, Gate C usage is:

```sh
python review/reproduce_headline/independent.py --input docs/runner/exp002-live
```

That command is documentation only and was **not executed during REV-001a**. Use the controller-supplied directory if it differs. An active collector's exclusive lock or an unfinished final world attempt causes refusal (exit 2). This is not a full runner seal/protocol-freeze audit: the program checks the envelopes it consumes, not traces, budgets, or seals. A terminal prefix may contain unrun worlds; these remain undefined.

The JSON contains:

- `attempts`: every recorded world attempt, its branch-level Omean, F/K arm means, tau_O, status, and counts by arm. Branches are read from standalone result files; a conflicting embedded world summary is rejected.
- `worlds`: the final attempt per manifest world, its effect and counts. Earlier retries never fill gaps in the final attempt. Pairing uses the manifest's generator `seed`, with one B1 and one B2 per seed; duplicate seed/regime records are refused.
- `pairs`: d_w = tau_O(B1) − tau_O(B2), or null if either is undefined.
- `Delta`: the unweighted mean of defined d_w; `sign_flip`: exact one-sided p, including integer numerator and denominator. Every sign vector is enumerated, including zero differences; ties count against the positive claim. Empty paired data produces null Delta/p. Fractions are used internally, with decimal JSON numbers on output.
- `within_regime_tau_O`: each regime's mean over its own defined worlds, and hashes of consumed input files.

Omean is the arithmetic mean of the two outsider rewards in `outcomes.agent_rewards`. The exposure sender and receiver identify the two coalition agents; the other two agents are outsiders. The script requires four recorded rewards and two distinct coalition endpoints. It uses the runner's final rewards, never `joint_reward`. Behavioural non-commits have already been mapped to reward zero by the runner; a missing/non-numeric reward is rejected, never silently imputed. Complete, valid continuations enter arm means. Failed/invalid/interrupted continuations do not. No-op ineligibility (`no_exposure`, `post_decision`) gives tau_O = 0; all other ineligible or failed/invalid world attempts are undefined. Case-level >=3-continuation and inferential floors do not redefine this numeric estimator.

Counts are actual recorded continuation attempts, not manifest-planned slots. `attempted = complete + failed + invalid + interrupted`. Explicit `not_run` records are counted separately and excluded from attempted. An empty branch set following a failed source has zero branch attempts; the failed world is still recorded as attempted with `world_status=failed`. Final-attempt counts are in `worlds`; all-attempt counts remain individually available in `attempts`. The counts cover every manifest arm, including S and N. Missing branch results with a valid begin record count as interrupted. Unstarted worlds have zero counts and `attempted=false`.

The calculation implements preregistration §2/§5 and protocol v1.2 §2/§10. Stage-2 margins do not change Omean, tau_O, Delta, or the sign-flip statistic. No bootstrap CI, case certificate, floor-based hypothesis wording, or directional/practical claim is produced. Those require the separate frozen analysis and scientific audit. Protocol v1.2 keeps Tier B exploratory; this script does not restore a confirmatory label.

## Synthetic verification

All commands below use only the existing readiness fixture, which is explicitly synthetic. The black-box CLI is run separately; the independent program and its unit tests never import analysis code.

```sh
nice -n 19 python3 review/reproduce_headline/independent.py --input docs/analysis/readiness/synthetic_input > review/reproduce_headline/synthetic_independent.json
nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.analysis run --input docs/analysis/readiness/synthetic_input --out review/reproduce_headline/synthetic_blackbox > review/reproduce_headline/blackbox.log 2>&1
nice -n 19 python3 -m unittest discover -s review/reproduce_headline/tests -v > review/reproduce_headline/tests.log 2>&1
nice -n 19 python3 review/reproduce_headline/tests/compare_synthetic.py > review/reproduce_headline/comparison.log 2>&1
```

Result: 11 unit tests pass; 514 artifact comparisons agree with no disagreements (`comparison.json`). Synthetic d_w = [0,1,2,3,4,5,7], with pair 108 undefined; Delta = 22/7; p = 2/128 = 1/64. The comparator checks all 104 F/K Omean values, 16 world tau_O values, seven paired d_w values, Delta/p/pair count, and all six continuation count fields for all 64 world/arm combinations. Skipped N is compared to the reference scheduling table because it is intentionally absent from reference continuation-attempt tables.

`synthetic_blackbox/` retains the fresh CLI output; the other JSON/log files retain independent output and verification evidence. The host denied the `nice` priority change (`setpriority: Operation not permitted`); computations nevertheless completed. No held-out data were accessed. These tests validate the synthetic schema and edge cases; actual terminal runner data have deliberately not been exercised.
