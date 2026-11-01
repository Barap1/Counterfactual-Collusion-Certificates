# SCI-002b: protocol v1.1 (report)

Source: `docs/stats/review_of_sci002.md`; values from `docs/stats/prereg.md`. v1 preserved in `docs/research/sci002/protocol_v1.md` (unchanged). Output: `docs/research/sci002/protocol.md` (v1.1), hash in `docs/research/sci002/protocol_v1.1.sha256`.

| Change | Status | Note |
|---|---|---|
| C1 per-arm n | applied | F4, K4, S2, N4 (N on random 50% Tier B and all fixtures); §8, §10, §11 |
| C2 CI method | applied | exact shift-permutation inversion, one-sided 95% L/U, intersection-union at 0.05; algorithm stays in `analysis_spec.md` §4 |
| C3 N lesion rule | applied | case-level exact one-sided test at m_O; study-level V10 unchanged |
| C4 V9 rule | applied | TOST: 90% CI inside ±m_O pass; invalid only if 95% CI wholly outside |
| C5 fixture headline and sizes | applied | n = 4 headline; 400/200/100 sizes; generator-side strata; 30/10 stratum minimums |
| C6 TV_excess | applied | replaces raw TV in §2.3 and §8; permutation count and unit OPEN |
| C7 seed policy | applied | per-call seeds distinct across arm/rep/call; one load session per checkpoint; seed uniqueness check |
| C8 Delta decomposition | applied | Delta_conditional and eligibility-rate difference always reported; Delta_total primary; inference for Delta_conditional OPEN |
| P1-1 not-supported attainability | applied | caveat and Stage 2 attainability table in §8 |
| P1-2 to P1-6 | applied | via C3, C4, C6, C8, C5 |
| P1-7 Tier B inference | applied | world-cluster bootstrap (B=10,000, PCG64 seed 20261025) and exact sign-flip test, both required; floors |

**OPEN items (in protocol text):**
1. TV_excess: number of label permutations and unit of permutation (not in review).
2. Delta_conditional: whether it is subject to the §10 inference rule (treated as descriptive).
3. Holm secondary family: prereg §10 declares S1-S3 confirmatory; the protocol line is unchanged pending director decision.

**Not applied (outside C1-C8 and P1):** P2 items; prereg §6 pinned m_O formula; V8 case-level minimum continuations.
