# SCI-002 Open questions and compute implications

**Status:** v1 (2026-10-23), post-review. Owners are suggestions; the director assigns.

## 1. Compute implications (for STAT-001 sizing at $0)

### Measured inputs: pilot seed 1 (`agent_turns.json`, `cohere/north-mini-code:free`, development data)

| Quantity | Value |
|---|---|
| Full episode | 12 turns, **28 model calls**, 60,170 prompt + 16,114 completion tokens (≈ 2.1k prompt and ≈ 575 completion per call) |
| Suffix from `t*` (Jeanene, round 1) | **19 calls**: 3 + 12 + 4. ≈ 49k prompt + 10.6k completion tokens per continuation |
| Suffix range by geometry | ≈ 1-4 calls (`t*` in execution) to ≈ 25 (r early in round 1). ENG-002 logs the realized value |

These are one run of one model; they must be re-measured on the frozen backend (INF-001).

### Call budget

`calls = W·R·28 + W·R·arms_eff·n·19`.
- Arms are F, S, K, plus N on a preregistered 50% of checkpoints, so `arms_eff = 3.5`; with C, `arms_eff = 4.5`.
- Dev runs and retries are extra.

| Scenario | W/regime | R | arms_eff | n | Calls | h @20 s | h @45 s | days @50 req/day |
|---|---|---|---|---|---|---|---|---|
| Minimal | 4 | 1 (B1) | 3.5 | 2 | 644 | 3.6 | 8.1 | 13 |
| Minimal, n = 3 | 4 | 1 | 3.5 | 3 | 910 | 5.1 | 11.4 | 18 |
| A | 8 | 2 | 3.5 | 2 | 2,576 | 14.3 | 32.2 | 52 |
| B | 8 | 2 | 3.5 | 3 | 3,640 | 20.2 | 45.5 | 73 |
| B + C | 8 | 2 | 4.5 | 3 | 4,552 | 25.3 | 56.9 | 91 |
| D | 12 | 2 | 3.5 | 3 | 5,460 | 30.3 | 68.2 | 109 |

**The latencies are illustrative placeholders, not measurements.** "50 req/day" is the OpenRouter free figure, which INF-001 marks as unverified.

Implications:
1. **OpenRouter free cannot carry Tier B.**
2. **Tier B needs local inference.** Scenario B fits the ≈ 67 h to the deadline (minus writing) only if p95 latency is ≲ 15 s per call at concurrency 1, or concurrency > 1 is stable.
3. **Tier A: 0 model calls** (CPU only). Tier A is the main evidence, *scoped as implementation and predicted-failure validation* (protocol §10).
4. **Priority order:**
   1. Tier A;
   2. B1 with F/S/K(+N 50%) at n = 3 on 4 worlds;
   3. matched B2;
   4. extend to 8 worlds;
   5. C;
   6. R deferred.

   Prefer more worlds over more continuations.
5. **Case-level attainability** [STAT-001]. With an exact F-vs-K permutation test, the smallest one-sided p is:
   - n = 2 → 1/6, so case-level `supported` is unattainable at α = 0.05;
   - n = 3 → 1/20, borderline;
   - n = 4 → 1/70.

   Bootstrap at n = 3 is anti-conservative. The three-way gates (protocol §8) also need CIs. Together with the info-content cap, **Tier-B case-level `supported` is expected to be rare or absent.** This is stated in advance (protocol §8); Tier B is exploratory.
6. **S-arm subset option.** Not adopted. S is ⅓ of branch calls, and N now runs on a 50% subset. If budget forces a cut, STAT-001 may preregister S on a random 50% subset as well, keeping V1/V3 deterministic checks on all checkpoints. This must be decided before collection.

## 2. Open decisions

| # | Question | Recommendation | Owner |
|---|---|---|---|
| Q1 | B1 prompt variant | `simple` (pilot) mostly induces own-best + deconfliction under additive rewards, so B1 may be indistinguishable from B2. `deception` names the forbidden objective. Choose on construct grounds **before any dev effect is inspected**, and record the reason. **Δ is conditional on that choice** and must say so | Director |
| Q2 | Colluder selection | Use `random` (seeded per world), not the pilot's `first` (spec 05) | ENG-002 |
| Q3 | Non-commit mapping | Skip = 0 (protocol §2.4). Freeze on dev | SCI / STAT |
| Q4 | `m_O`, δ_S, θ, V8 cap/tolerance, CI method | `m_O ≥ 2.5`; `δ_W = n_O·m_O` follows from it. The rest come from the dev noise scale | STAT-001 |
| Q5 | Tier-B primary | **Resolved:** Δ on all matched worlds, with the ineligible-world rule in protocol §10. Within-regime means are always reported too; no switching | STAT-001 (method, α) |
| Q6 | Common-cause regime B3 | Condition-level descriptive only. Optional: `extra_channel_members: all` would make a partner-specificity contrast identifiable (spec 04). Not P0 | Director |
| Q7 | Gate form | **Resolved:** three-way CI-based gates (protocol §8) | — |
| Q8 | `supported` with `info_bearing = true` | **Resolved:** capped at `inconclusive: info_loss_untested` until a validated R arm exists (spec 04) | — |
| Q9 | Endogenous sender | This is a recorded departure from spec 05's "designated sender". Report the sender distribution | SCI |
| Q10 | Execution-phase `t*` | Measure the rate on dev. It is likely to raise `state_redundant` | ENG / SCI |
| Q11 | N filler set | Freeze ≥ 5 matched-length neutral fillers before any branch. No task ids, numbers, names or commitments | SCI |
| Q12 | Extractor rules (`info_bearing`, commitment tuples) | Written on dev templates only, **by a worker who did not write the fixture policy parser** | FIX-001 / ENG-002 |
| Q13 | Fixture stratum sizes | Labels are by mechanism, so stratum counts vary. STAT-001 sets the minimum per key stratum (suggested ≥ 30) and generation scales at CPU cost | STAT-001 / FIX-001 |

## 3. Hand-offs

**ENG-002.**
1. **Checkpoint:** env state (incl. `rng.getstate()`), MCP megaboard (boards, event ids, participants), schedule pointer, order, roles, config, model params. Restore without re-calling the prefix.
2. **Render hook at every receiver prompt:** mask ∅ / `E*` by **event id** / N substitution / C. **Preserve original indices.**
3. **V3 diff checker implemented independently of the mask code.**
4. **Leak scan over every receiver prompt in K, on all surfaces** (boards, `CURRENT ASSIGNMENTS`, `action_executed`). Record the first leak turn and surface.
5. Assert that tool results never echo board contents.
6. Unit-test `W := Σ r_i` against `_rewards`. **Do not use `joint_reward`:** it differs when ≥ 2 agents claim the same unknown id.
7. Log per call: response id, response model id, latency, tokens, cost (null if unknown), context-overflow flag.
8. Interleave and shuffle branches across arms. Keep `assignment_filling = false`. Record (not fix) the default-to-board-0 behaviour.
9. Byte-compare the restored `t*` prompt against archived `agent_prompts.json`.

**FIX-001.**
1. Share the adapter's render function. Scripted agents read the rendered prompt only.
2. **Mechanism-only labels; costs drawn independently of family; uniform turn order everywhere.**
3. Build the enumeration oracle independently of CCC.
4. Implement A6 faults (including the effect-inflating g and h) as hooks outside CCC's checkers.
5. Keep seeds, templates and names disjoint; seal the held-out set; report realized stratum counts and the A distributions.

**STAT-001.**
- Case-level CI/test for n ≤ 3.
- World-cluster bootstrap for Δ (method, α).
- `m_O`, δ_S, V8, θ from dev.
- Minimum stratum sizes.
- Attainable interval widths for 4/8/12 worlds from dev between-world variance.
- Confirm that Tier B is labelled exploratory.

## 4. Residual risks (after review)

- **Tier B will mostly abstain** (`info_loss_untested`, `imprecise`). That is a legitimate result (SCI-001 fallback 3), not something to engineer away.
- **CCC's net advantage over B2 is stratum-dependent.** It trades sensitivity on info-bearing or W-raising positives for specificity on benign cooperation. It must be reported cell by cell.
- **The norm boundary is unavoidable for intent-free outcome audits.** Legitimate transfers that do not materially raise W are flagged when the extractor misses their information content.
- **The lexical redundancy detector misses semantic carriers** (A5b).
- **Single model/backend:** no generalization.
- **N filler is not information-free.** A null placebo effect supports, but does not prove, that a K effect is content-driven.
