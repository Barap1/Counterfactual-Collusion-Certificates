# Call-cap investigation (EXP-001 dev05_B2 stop). PROPOSAL ONLY: no code or manifest changed.

DEV data only. No model call, no Ollama contact, no commit. Evidence read: `docs/runner/exp001-live/**`, `ops/budget_ledger.jsonl`, `docs/runner/exp001_manifest.json`, `ccc/runner/collector.py`, `ccc/infra/budget_guard.py`, `docs/stats/compute_plan.md`, `ops/DECISIONS.md` D-022.

## 1. How "223" is computed

It is not a per-world cap. It is the **collection-wide remaining budget** at the moment dev05_B2 started.

- `docs/runner/exp001_manifest.json`: `max_requests = 2470` for the whole 8-world collection.
- `ccc/runner/collector.py` ~L402-411: for each world attempt, `used = count of *.begin.json files under the collection root`, `remaining = max_requests - used`, and `BudgetGuard(max_calls=remaining)`.
- `ccc/infra/budget_guard.py` L394: `if calls_started >= max_calls: raise BudgetViolation("per-run call cap {max_calls} reached")`.
- Ledger `run_open.max_calls` for the 8 live world runs: 2470, 2173, 1876, 1579, 1282, 901, 520, 223. Each step equals the previous cap minus that world's calls (297, 297, 297, 381, 381, 297, ...). So 223 = 2470 - (297+297+297+297+381+381+297 = 2247).
- Origin of 2470: the compute-plan arithmetic `ceil(1.05 * 8 * (28 + 14*19)) = ceil(1.05*2352) = 2470`. It assumed 19 calls per branch for every world and omitted the 3 canary calls per world.
- Measured need: 6 worlds x 297 + 2 worlds x 381 = **2544 > 2470**. The cap was 74 calls (2.9%) short. Causes, both predictable only from DEV counts: dev04 branches take 25 calls, not 19 (+2 x 84 = 168 calls), and 3 canary calls per world (+24). The 5% slack (118 calls) did not cover the 192 extra.
- Cause was operational (cap arithmetic), not model behaviour or any outcome.

## 2. DEV live call counts (from `*.begin.json` files and the ledger; both agree: 3065 begins = 2470 live + 595 earlier pilot runs)

Per world attempt (live collection, 8 worlds): 28 source-run calls + 3 canary + 14 branches x s, where s is constant within a world.

| world | calls | s per branch | note |
|---|---|---|---|
| dev02_B1, dev02_B2, dev03_B1, dev03_B2, dev05_B1 | 297 each | 19 | |
| dev04_B1, dev04_B2 | 381 each | 25 | |
| dev05_B2 | **223 at stop** (224th begin file written, refused) | 19 | stopped inside branch 002_F after 4 of 19 calls; canary "after" not run; 003_* branches not started |

| statistic | complete worlds (n=7) | per branch, all 109 branch dirs (incl. 1 partial) | per branch, 108 complete |
|---|---|---|---|
| min / median / p90 / max | 297 / 297 / 381 / 381 (mean 321) | 4 / 19 / 25 / 25 (mean 20.4) | 19 / 19 / 25 / 25 |

Per arm (calls per branch; n branches): F 31 branches min 4 (the partial) med 19 p90 25 max 25; K 31: 19/19/25/25; S 31: 19/19/25/25; N (v1.1 filler arm) 16: 19/19/25/25. Arm does not change s; the world does. Source run: 28 in all 8 worlds. Canary: 3 per world (2 in dev05_B2).
Earlier pilot runs (exp001-pilot*, 595 ledger calls, dev02_B1 only) show the same 297-call world.

dev05_B2 had made **223 calls** when it stopped (all ledger `ok`; 0 errors in 3065 calls).

## 3. Held-out projection under protocol v1.2 (16 worlds = 8 pairs)

Arms per checkpoint: F4 + K4 + N_m4 (all checkpoints) + S1 on the hash-selected ~50% (`sha256("ccc.sham.v1|"+checkpoint_id) % 2 == 0`, protocol §11), plus canary 3 and source 28. N_m4 only runs when M* is non-empty (protocol §3, §8).

Per world: 31 + (12 or 13) x s: s=19 -> 259 (no S) / 278 (S1); s=25 -> 331 / 356. Every held-out world needs more than 223 and up to 356. A per-run cap of 223 is therefore irrelevant as a per-world bound; what matters is the collection total versus `max_requests`.

| scenario (16 worlds) | calls |
|---|---|
| D-022 as written (28 + 12.5 x 19 per world, x1.05; no canary): this is what a manifest built by the same formula would hold | 4460 |
| DEV-expected: s mix 6/8 at 19, 2/8 at 25 (mean 20.5), S=0.5, N_m available: 16 x (31 + 12.5 x 20.5) | 4596 |
| DEV-expected, N_m unavailable (see Tier-B census: M* empty 8/8 on DEV): 16 x (31 + 8.5 x 20.5) | 3284 |
| DEV-max: every world s=25, S=1, N_m available: 16 x 356 | 5696 |

**Would held-out hit the current cap?** If `max_requests` is built by the D-022/compute-plan formula (4460), yes in the DEV-expected N-available case (4596 > 4460, the last world is truncated, about 136 calls short) and certainly in the DEV-max case (5696). It would not if N_m is unavailable as on DEV (3284). The same failure mode as dev05_B2 recurs: the final world fails on the collection-wide remaining count.

## 4. Proposed cap rule (derived only from DEV counts and arm counts; outcome-blind)

```
max_requests = ceil( f x W x ( S_src + C + (3 x 4 + 1) x s_max ) )
  W = 16 worlds; S_src = 28 and C = 3 (DEV: identical in all 8 worlds)
  s_max = 25 (DEV maximum per-branch calls); (3 x 4 + 1) = F4+K4+N_m4 plus S1 counted on every world (upper bound of the hash rule)
  f = 1.05 (the compute plan's existing retry slack; no DEV evidence for a larger one)
= ceil(1.05 x 16 x 356) = 5981
```
Reasoning: (a) the cap is a ceiling, not a forecast; its only job is to never cut a world short for arithmetic reasons; (b) every term is a DEV maximum or an arm count fixed by the protocol; (c) the dev failure came from using a DEV mean-like constant (19) and omitting a fixed overhead (canary), so use the max and include all fixed calls; (d) f=1.05 leaves 285 calls, about 0.8 of a world, for one discarded/rerun checkpoint (protocol §7). If the director wants room for a full rerun at DEV-max, f=1.10 gives 6266 (derivation identical). Cost of a high ceiling is only wall time, bounded by the hard stop and watchdog, and $0 is enforced by backend policy, not by this count.
Optional (not required): a per-world guard cap of `ceil(f x 356) = 374` in addition, so one runaway world cannot drain the shared pool; this is a design change and is not proposed for code here.
If the held-out s differs from DEV (unknown before collection), this rule still holds only up to s=25. A held-out world with s>25 would be an operational stop to report, not a reason to adapt the cap after outcomes.

## 5. Recomputed budget, runtime, buffer

Measured seconds per call from the EXP-001 ledger (8 live world runs, 2470 calls; `attempt_begin` timestamps):
- wall time per call, including harness overhead: **mean 4.66 s, p95 5.87 s** (2462 inter-call gaps). One 1019 s stall in dev05_B2 and that world's 20.3 s/call (4525 s for 223 calls) inflate the mean; excluding dev05_B2: mean 3.10 s, p95 4.87 s.
- model latency only (`attempt_end.latency_ms`): mean 2.76 s, p50 2.56, p95 5.44, max 19.8.
The wall-per-call figures already include overhead, so the compute plan's d=0.5 duty factor is not applied below. The last column keeps the plan's own constants (5.5 s, d=0.5, i.e. 11 s per call) for reference.

Windows end 2026-10-25 12:00 UTC: from 2026-10-24 14:12 = 21.8 h; from 2026-10-24 06:00 = 30.0 h. Buffer = 1 - runtime/window.

| calls (budget) | h @ mean 4.66 s | buffer 14:12 | buffer 06:00 | h @ p95 5.87 s | buffer 14:12 | buffer 06:00 | plan constants 11 s/call: h, buffer 14:12 / 06:00 |
|---|---|---|---|---|---|---|---|
| 3284 (DEV-exp, N empty) | 4.25 | 80.5% | 85.8% | 5.35 | 75.4% | 82.2% | 10.0 h, 54.0% / 66.6% |
| 4460 (D-022) | 5.77 | 73.5% | 80.8% | 7.27 | 66.6% | 75.8% | 13.6 h, 37.5% / 54.6% |
| 4596 (DEV-exp, N avail) | 5.95 | 72.7% | 80.2% | 7.49 | 65.6% | 75.0% | 14.0 h, 35.6% / 53.2% |
| 5696 (DEV-max) | 7.37 | 66.2% | 75.4% | 9.29 | 57.4% | 69.0% | 17.4 h, 20.2% / 42.0% |
| **5981 (proposed cap)** | 7.74 | 64.5% | 74.2% | 9.75 | 55.3% | 67.5% | 18.3 h, 16.2% / 39.1% |

**Does the >=40% buffer hold?** On measured wall time: yes in every row, both start times, mean and p95 (lowest 55.3% at the proposed cap, p95, 14:12 start). On the compute plan's older planning constants (5.5 s, d=0.5) it does not at the 14:12 start for any row at or above 4460 (37.5% at 4460; the D-022 statement that 14:12 remains the latest start used 43% against a 24 h window, but 13.6 h / 0.6 gives about 13:18 as the latest start under those constants). At the 06:00 start the plan-constant buffer holds for all rows except the proposed cap (39.1%) and fails nothing else. Caveat: measured speed came from a quiet machine except the dev05_B2 stall; a repeat of that stall (20 s/call) over thousands of calls would break the buffer, so the watchdog stays.
