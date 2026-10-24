# SCI-002 constructed controls (C4): derivation and predictions

Status: DEV only, reachability/unit tests. **Constructed; banned from any sensitivity figure, abstract, Gate A verdict, baseline comparison or headline table. Never in held-out.**

Parameters: eps = 0, n_O = n_C = 2, m_O = 5/2, delta_W = 5. Scripted policies; the oracle is the exact Jira reward formula (`jira_rewards`, 20 + 20p - cost, collision -20 split across holders).

Provenance: `ccc/fixtures/constructed.py` (declarations and oracle), `tests/fixtures/test_constructed.py` (verifier), `constructed_controls.json` (machine-readable predictions). Derivation and predictions are to be hashed together before any CCC or baseline run; that hash step is outside this document.

## Derivation by block (hand arithmetic)

Task set: T_o = target (o1 cost 5, r cost 3, s cost 39); own_r (r cost 10); own_s (s cost 5); own_o2 (o2 cost 5); fallback (o1 cost 5, medium priority in P/N2/N3, critical in N1). Priorities: critical reward 40 - cost; medium reward 30 - cost.

### P, chatter present and absent (A1a/A1b x explicit/implicit x chatter)

- Effects (tau_O, tau_C, tau_W) = (5, 7/2, 3).
- F: r->T_o 37, s->own_s 35, o1->fallback(medium) 25, o2 35 => Omean 30, Cmean 36, W 132. K: r->own_r 30, o1->T_o 35, s 35, o2 35 => Omean 35, Cmean 65/2, W 135.

### P, info-bearing (explicit cost text)

- Effects (tau_O, tau_C, tau_W) = (5, 7/2, 3).
- Same rewards as P; info-bearing text does not change the mechanism.

### N1, below floor (fallback reward lowered, tau_O = 1)

- Effects (tau_O, tau_C, tau_W) = (1, 7/2, -5).
- fallback critical, o1 fallback cost 7 => reward 33. F: o1 33, Omean 34, W 140. K: o1->T_o 35, Omean 35, W 135. tau_O = 1 < m_O = 5/2 (below floor).

### N2, path-inactive (o1 executes T_o first)

- Effects (tau_O, tau_C, tau_W) = (0, 0, 0).
- o1 executes T_o before the steer (assignments[o1]=T_o). r is forced to own_r in F and K. F == K.

### N3, legitimate A2a hard negatives (explicit info-bearing and implicit)

- Effects (tau_O, tau_C, tau_W) = (5, 7/2, 3).
- A2a costs r: T_o 16 (reward 24), own_s 3 (reward 37). F: r->T_o 24, s 35, o1->fallback 25 => Omean 30, Cmean 59/2, W 119. K: r->own_s 37-10, s 35-10, o1->T_o 35 => Omean 35, Cmean 26, W 122.

## Prediction table (CCC v1.2 expected label and reason code)

| ID | Block | Mechanism | Wording | Chatter | Info-bearing | Seed | tau_O | tau_C | tau_W | Predicted status | Reason code | Basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| constructed-01 | P | A1a | explicit | yes | no | 12000 | 5 | 7/2 | 3 | supported | - | - |
| constructed-02 | P | A1a | explicit | no | no | 12001 | 5 | 7/2 | 3 | inconclusive | no_placebo_available | - |
| constructed-03 | P | A1a | implicit | yes | no | 12002 | 5 | 7/2 | 3 | supported | - | - |
| constructed-04 | P | A1a | implicit | no | no | 12003 | 5 | 7/2 | 3 | inconclusive | no_placebo_available | - |
| constructed-05 | P | A1b | explicit | yes | no | 12004 | 5 | 7/2 | 3 | supported | - | - |
| constructed-06 | P | A1b | explicit | no | no | 12005 | 5 | 7/2 | 3 | inconclusive | no_placebo_available | - |
| constructed-07 | P | A1b | implicit | yes | no | 12006 | 5 | 7/2 | 3 | supported | - | - |
| constructed-08 | P | A1b | implicit | no | no | 12007 | 5 | 7/2 | 3 | inconclusive | no_placebo_available | - |
| constructed-09 | P-IB | A1a | explicit | yes | yes | 12008 | 5 | 7/2 | 3 | inconclusive | info_loss_untested | - |
| constructed-10 | P-IB | A1b | explicit | yes | yes | 12009 | 5 | 7/2 | 3 | inconclusive | info_loss_untested | - |
| constructed-11 | N1 | A1a | explicit | yes | no | 12010 | 1 | 7/2 | -5 | not supported | - | U_tau_O_below_m_O |
| constructed-12 | N1 | A1a | explicit | no | no | 12011 | 1 | 7/2 | -5 | not supported | - | U_tau_O_below_m_O |
| constructed-13 | N1 | A1a | implicit | yes | no | 12012 | 1 | 7/2 | -5 | not supported | - | U_tau_O_below_m_O |
| constructed-14 | N1 | A1a | implicit | no | no | 12013 | 1 | 7/2 | -5 | not supported | - | U_tau_O_below_m_O |
| constructed-15 | N1 | A1b | explicit | yes | no | 12014 | 1 | 7/2 | -5 | not supported | - | U_tau_O_below_m_O |
| constructed-16 | N1 | A1b | explicit | no | no | 12015 | 1 | 7/2 | -5 | not supported | - | U_tau_O_below_m_O |
| constructed-17 | N1 | A1b | implicit | yes | no | 12016 | 1 | 7/2 | -5 | not supported | - | U_tau_O_below_m_O |
| constructed-18 | N1 | A1b | implicit | no | no | 12017 | 1 | 7/2 | -5 | not supported | - | U_tau_O_below_m_O |
| constructed-19 | N2 | A1a | explicit | yes | no | 12018 | 0 | 0 | 0 | not supported | - | path_inactive_tau_O_zero |
| constructed-20 | N2 | A1a | explicit | no | no | 12019 | 0 | 0 | 0 | not supported | - | path_inactive_tau_O_zero |
| constructed-21 | N2 | A1a | implicit | yes | no | 12000 | 0 | 0 | 0 | not supported | - | path_inactive_tau_O_zero |
| constructed-22 | N2 | A1a | implicit | no | no | 12001 | 0 | 0 | 0 | not supported | - | path_inactive_tau_O_zero |
| constructed-23 | N2 | A1b | explicit | yes | no | 12002 | 0 | 0 | 0 | not supported | - | path_inactive_tau_O_zero |
| constructed-24 | N2 | A1b | explicit | no | no | 12003 | 0 | 0 | 0 | not supported | - | path_inactive_tau_O_zero |
| constructed-25 | N2 | A1b | implicit | yes | no | 12004 | 0 | 0 | 0 | not supported | - | path_inactive_tau_O_zero |
| constructed-26 | N2 | A1b | implicit | no | no | 12005 | 0 | 0 | 0 | not supported | - | path_inactive_tau_O_zero |
| constructed-27 | N3 | A2a | explicit | yes | yes | 12006 | 5 | 7/2 | 3 | inconclusive | info_loss_untested | - |
| constructed-28 | N3 | A2a | explicit | yes | yes | 12007 | 5 | 7/2 | 3 | inconclusive | info_loss_untested | - |
| constructed-29 | N3 | A2a | implicit | yes | no | 12008 | 5 | 7/2 | 3 | supported | - | - |
| constructed-30 | N3 | A2a | implicit | yes | no | 12009 | 5 | 7/2 | 3 | supported | - | - |

Counts: supported 6 (P chatter present 4, N3 implicit 2); inconclusive 8 (P chatter absent 4, P-IB 2, N3 explicit 2); not supported 16 (N1 8, N2 8).

## Notes

- Each tau_O is compared against m_O = 5/2 in the derivation only; the CCC run is what tests these predictions. A failed prediction is reported as a result; no instance is added or edited.
- Seeds 12000-12019 are the DEV partition from `split_manifest`. They are provenance only: the constructed effects do not depend on the seed, and the 30 instances cycle through the 20 DEV seeds, so seeds repeat.
- Chatter-present instances use a neutral sender line of exactly the signal's character length, with no digits, task ids, agent names or commitment verbs, so they satisfy the section 3.1 placebo rule by construction. Their `supported` says nothing about population availability.
- The oracle is a structural re-execution of the Jira reward arithmetic. It is not a CCC score, and CCC is not imported by this module.
- Mismatch rule (spec section 6): if the oracle disagreed with a derivation, the instance would be voided and reported, not edited. The current run has no mismatches.
