# Deviation log (SCI-002)

Entries record any change after a Stage 1 or Stage 2 hash (prereg.md section 12). Each entry states the change, the reason, the decision point relative to data, and the consequences. Affected claims are moved to exploratory where stated.

## DEV-001

- **Date:** 2026-10-23
- **Decision record:** `ops/DECISIONS.md`, D-022 (director). Amendment text: `docs/research/sci002/amendment_v1.2.md` (r3), Section 6.
- **Frozen item changed:** prereg.md freezes the per-arm n as F4, K4, S2, N4. For held-out, S changes to n = 1 on 50% of checkpoints.
- **Change:** fallback for compute. With N_m on all checkpoints, the held-out plan leaves a 37.1% buffer (4% under the 8.4 s/call stress), below the compute_plan.md 40% requirement. Held-out S runs at n = 1 on the checkpoints selected by the frozen rule `int(sha256("ccc.sham.v1|" + checkpoint_id).hexdigest(), 16) % 2 == 0`, with rule-string sha256 `c8651ddac16a50992971ae6f00df96405b00d0e22684117eedd09ffcffa5d509`. Optional pairs H09 and H10 are dropped (compute_plan criterion 5).
- **Timing:** decided before any held-out data exists. The held-out seed has not been run. Latest held-out start is unchanged at 2026-10-24 14:12 UTC.
- **Consequences (disclosed in amendment r3, Section 6):**
  - V9 90% half-width rises from about 0.36 sigma to about 0.65 sigma (16-checkpoint illustration). `sham_uncertain` is expected to be common. V9 cannot certify sham equivalence at this design. The attained half-width is printed.
  - The held-out S-vs-F noise scale may be about 29% above the dev level from which m_O was pinned. m_O is not re-pinned.
  - delta_S, m_O, the TOST rule, alpha, theta, and the n per arm for F, K and N are unchanged.
- **Claims affected:** not stated in D-022. Whether any claim moves to exploratory under prereg.md section 12 is left to the director and is not decided by this entry.

## DEV-002 (2026-10-23) v1.2 placebo-census pre-registration gate failed
- Required by protocol v1.2 §§3.2, 9, 11: extractor, alias list, T_chat templates and A6 map hash-committed BEFORE the placebo availability census.
- What happened: an interrupted worker ran the DEV census (fx1 0/740 → chatter trigger fired → fx2 740/740) before those artifacts were committed. Hashes were committed afterwards (worktree commit 782bec2, ops/v12_freeze_hashes.txt) and establish only unchanged bytes since then, not pre-registration.
- Consequence: the DEV census results are classified EXPLORATORY. The chatter-trigger decision rests on them, and the trigger rule itself was frozen in the adopted protocol v1.2 before the census. Protection against selection degrees of freedom is claimed only for data generated after the freeze commit (held-out fixtures and any held-out real runs).
- Identified by: AMD-IMP-A2 (self-report) and the Codex adversarial review of branch v1.2-impl.
