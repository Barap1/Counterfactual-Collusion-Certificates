# STAT-001 Compute plan: Gate-B dev pilot (EXP-001) and held-out matrix

All numbers are planning arithmetic from INF-001 telemetry and the pilot suffix length. None is a result. EXP-001 replaces the planning constants with measurements and Stage 2 records them. $0 spend throughout; all inference is local `ollama_local / gemma4:26b`, `reasoning_effort=none`, ctx 32768, T=0.7, `max_tokens` 1500, through `GuardedChatClient`.

## 1. Planning constants

| Symbol | Value | Source / caution |
|---|---|---|
| `c` | **5.5 s per call** | INF-001: replay p50 5.1 s / p95 8.4 s; end-to-end p50 4.2 / p95 6.9. 5.5 is above every p50 and includes loop overhead. Stress case: 8.4 s |
| `s` | **19 calls per continuation** | One pilot run of a *different* model (cohere), `t*` at Jeanene round 1. Range by geometry about 1-25. Stress case: 25. EXP-001 measures it on gemma |
| `p` | 28 calls per base trajectory (prefix + episode) | same pilot |
| `d` | 0.5 duty cycle | director's figure (INF-001 summary). Wall hours = compute hours / 0.5 |
| retries | +5% calls | bounded retry policy (prereg section 7) |
| rate | 3600 / (19*5.5) = **34 continuations per compute-hour** | INF-001's 56/h implies about 12 calls per continuation; I use the more conservative figure |

Concurrency 1 (one call in flight, `NUM_PARALLEL=1`). `OLLAMA_KEEP_ALIVE` long; **one model-load session per checkpoint**; a detected reload discards and reruns that checkpoint once (prereg section 7).

## 2. Per-checkpoint design

Arms per checkpoint: **F4, K4, S2, N4 (random 50% of checkpoints, seed in manifest)**. Expected continuations per checkpoint = 4+4+2+0.5*4 = **12**. Branch order: shuffled across arms (seeded `branch_order_seed`), interleaved; all in one session.

Calls per eligible checkpoint = 12 * 19 = **228**, plus the base trajectory 28.

## 3. Gate-B dev pilot (EXP-001), run first

| Item | Value |
|---|---|
| Worlds | dev seeds **2, 3, 4, 5** (seed 1 is the archival pilot, not reused), each in B1 (`deception`) and B2 (matched legitimate; same world, same designated pair) = **8 base trajectories** |
| Arms | F4, K4, S4, N2 on every eligible dev checkpoint (S4 gives 8 F-or-S replicates per checkpoint for the noise formula; N2 on all, to exercise machinery) = 14 continuations |
| Calls | base 8*28 = 224; branches at most 8*14*19 = 2,128; total **2,352** (at most) |
| Projected time | 2,352 * 5.5 s = **3.6 h compute = 7.2 h wall at d=0.5** (stress: 8.4 s/call and +5% retries: 11.5 h wall) |
| Order | fixed world order 2,3,4,5; B1 then B2 within a world; pairs completed in order |
| Hard stop | all 4 pairs done, or **2026-10-24 09:00 UTC**, whichever is first; **minimum 3 complete pairs** for Stage 2, else `thin_dev` fallbacks |
| Purpose | (a) validate runner and replay on the live backend, (b) measure `s`, `c`, ineligible rate, overflow, infra-failure rate, (c) supply `sigma_hat_dev`, `sd_d`, theta inputs, extractor and filler checks, (d) V1/V3 byte checks, A6-style injected-defect check on the live path |

**Gate-B pass criteria (operational only; none refers to a treatment effect):**
1. V1 byte-identity of restored `t*` prompt: 100% of eligible dev checkpoints.
2. V3 independent diff checker: 100% pass on real branches and it flags one injected defect per run (from the fixture A6g/A6h hooks).
3. Infra-missing share <= 10% per arm (else the backend is declared unstable and the director is told before any held-out run).
4. Context overflow: 0 expected; any overflow reported.
5. Measured `s` and `c` recorded; the held-out projection is recomputed with measured p95 per call and `s` before launch. If the recomputed held-out wall time exceeds 60% of the available window, drop the extension tranche (section 5) and, if still above 60%, set S to n=1 on a preregistered 50% subset (the S-arm option in open_questions §1.6), decided **before** the first held-out seed.
6. Eligible rate per regime reported. A rule revision on dev is allowed only on eligibility counts and V-checks; the revision log records that K outcomes were not consulted.

The dev data never enter a held-out number. Dev K and N outcomes are not read by `pin_thresholds`.

## 4. Held-out matrix (confirmatory stratum)

| Item | Value |
|---|---|
| Worlds | **8 world-pairs** `H01..H08`, each in B1 and B2 = **16 base trajectories** (fixed order, world seed `int(sha256("ccc-heldout-world|i")[:8],16) % 2^31`, persisted task files, designated pair randomized per world and shared by B1 and B2) |
| Arms | F4, K4, S2, N4 on 50% (fixed random subset, seed in manifest) |
| Calls (all 16 eligible) | base 16*28 = 448; branches 16*12*19 = 3,648; sum 4,096; +5% retries = **4,301** |
| Compute | 4,301 * 5.5 s = **6.57 h**; wall at d = 0.5: **13.1 h** |
| Window | start no earlier than Stage 2 hash, planned **2026-10-24 12:00 UTC**; collection ends no later than **2026-10-25 12:00 UTC** = 24 h window |
| Utilisation | 13.1 / 24 = **55%, buffer 45%** (>= 40% required) |
| Latest start for >= 40% buffer | 13.1 / 0.6 = 21.8 h before 12:00 Oct 25 = **2026-10-24 14:12 UTC** |
| Stress | 8.4 s per call: 10.0 h compute, 20.1 h wall = 84% (fits, 16% buffer). `s`=25: 8.4 h compute, 16.8 h wall = 70% |
| Ineligible worlds | cost only the base trajectory, so actual calls are lower than the table |

Continuation counts: 16 base + about 192 branch continuations expected. This is well below the roughly 1,200 continuations INF-001 says are feasible by Oct 25 12:00, because the binding constraint is the 24 h window after the dev freeze, and a smaller matrix is what keeps the buffer.

**Why 8 pairs and n=4:** world count is the independent unit (spec 06), so worlds are preferred over continuations, but n=2-3 makes case verdicts unattainable (prereg section 4). 4v4 is the smallest design where both determinate verdicts are attainable with margin. With 16 checkpoints per 24 h that is the largest design leaving >= 40% buffer.

### Extension tranche (time-triggered, not outcome-triggered)
World-pairs `H09, H10`, same design: base 4*28 = 112, branches 912, sum 1,024, +5% = **1,075 calls = 1.64 h compute = 3.3 h wall**.
**Run only if** pair `H08` is finished by **2026-10-25 06:00 UTC** (leaving 6 h for 3.3 h). Never decided by looking at effects. If run, total utilisation is 16.4 h of 24 = 68% (buffer 32%, accepted because the tranche is optional and cut off by the wall clock). If cut off mid-pair, the incomplete pair is reported as `unrun`/`incomplete`, not analysed.

### Optional exploratory tail (not in the buffer)
B1-`simple` stratum, 4 worlds, F4 and K4 only: 4*28 + 4*8*19 = 720 calls = 1.1 h compute = 2.2 h wall. Only if both tranches are done by 06:00 Oct 25 and the director releases it. Descriptive only.

### OpenRouter free
50 requests/day is about 2-3 continuations per day. Not used for any claim. At most a single plumbing smoke check, labelled corroboration, outside the matrix. I recommend not spending director time on it.

## 5. Timeline (UTC; shifts one-for-one if EXP-001 starts late)

| When | Step |
|---|---|
| now to Oct 24 early | B1/B2 blockers closed (SCI-002 v1.1, per-arm manifest); Stage 1 hash; fixtures: dev scoring on CPU |
| EXP-001 start (target Oct 24 ~00:00) | dev pilot, 7.2 h wall planned |
| by Oct 24 09:00 | hard stop of dev collection |
| by Oct 24 11:00 | `pin_thresholds`, theta from dev fixtures, extractor and filler frozen -> Stage 2 addendum + hash |
| Oct 24 12:00 | held-out collection starts (latest 14:12 for >= 40% buffer) |
| Oct 24 12:00 + 13.1 h | planned finish of H01-H08 about Oct 25 01:00 |
| Oct 25 06:00 | extension decision (clock only) |
| Oct 25 12:00 | **collection ends** (hard) |
| Oct 25 12:00-22:00 | offline analysis (no model calls), claims ledger; science freeze 22:00 |
| Oct 26 11:59 | submission deadline |

Fixtures (Tier A) need no model calls: dev scoring now, held-out sealed generation after Stage 1, held-out scoring after Stage 2 (CPU, any time before Oct 25 22:00).

## 6. Temperature and seed policy

* T = 0.7 for all arms of all Tier B runs (matches the INF-001 benchmark; T=0 would collapse the replicates). Fixed `max_tokens` 1500, ctx 32768, `reasoning_effort` none.
* Seed sent on every call: `first 31 bits of sha256(protocol_sha|checkpoint_id|arm|rep|turn|call_k)`. **Different across arms and replicates** so every continuation is an independent draw and S is a real noise draw. `common_randomness_claim: none`.
* All arms of a checkpoint in one Ollama model-load session (identity = `load_session_id`, recorded per call). Never reload mid-checkpoint. Reproducing a run bit-for-bit after a restart is **not** claimed.
* Base trajectories (prefix) for the same world/regime are produced in the same session as their checkpoint branches where possible; if not, the checkpoint is the immutable object and its own branches share a session.

## 7. Stopping rules (all non-adaptive)
1. Fixed matrix and fixed world order; no skipping, no reordering.
2. Time triggers only: dev stop 09:00 Oct 24; extension decision 06:00 Oct 25; collection end 12:00 Oct 25.
3. Infrastructure halts (budget guard, backend death, repeated reloads) pause the run; resumption continues the same order. Halting never depends on outcomes.
4. No interim estimates of tau_O, Delta, or statuses are computed during held-out collection. Only throughput, status counts, V-check pass counts and missingness by arm are monitored, by a script that does not load outcome rewards.
5. Incomplete pairs are reported as such; the realized sample is whatever completed under the fixed order, and the prereg floors decide claim tier.
