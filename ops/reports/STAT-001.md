# STAT-001 report (2026-10-23)

Deliverables (all in `docs/stats/`): `prereg.md`, `compute_plan.md`, `analysis_spec.md`, `review_of_sci002.md`. No inference, $0, no commits. Only computation: exact enumeration on synthetic vectors (test vectors in `analysis_spec.md` section 4).

**Status: NOT YET FREEZE-READY.** Blockers: B1 SCI-002 must adopt C1-C8 (v1.1, new hash); B2 runner manifest needs a per-arm continuation map and per-arm/rep/call seeds; B3 Stage 2 dev-pinning addendum after EXP-001.

Key frozen values: n per arm F4/K4/S2/N4 (N on random 50% of Tier B, all fixtures); case-level test = exact shift-permutation inversion (min p 4v4 = 1/70), gates by intersection-union at one-sided 0.05; primary Delta = world-cluster percentile bootstrap (B=10,000, PCG64 seed 20261025) plus exact sign-flip, both required; T=0.7, per-arm independent seeds; m_O = max(2.5, ceil0.5(sigma_dev*sqrt(1/2+1/4))) pinned from F/S dev arms only; delta_S = m_O (TOST); delta_W = 2 m_O; V8 cap 0.10, imbalance 0.05, case-level >=3 complete; theta by Youden J on dev fixtures.

Compute: dev pilot 4 world-pairs, 2,352 calls max, 7.2 h wall. Held-out 8 world-pairs, 4,301 calls, 6.6 h compute, 13.1 h wall of a 24 h window (45% buffer); optional tranche H09-H10 clock-triggered at 06:00 Oct 25.
