# SCI-002 protocol amendment v1.2 (AMD-001, revision r3)

**Status:** DRAFT r3 for re-review (REV-AMD returned ADOPT-WITH-EDITS on r1; r2 verification returned ADOPT conditional on four edits, applied in r3; see the changelogs at the end). Not adopted. `protocol.md` (v1.1) is NOT edited by this document. Nothing here is a measured result; every "Predicted" block was written before any v1.2 code existed or ran.

**Basis:** REV-GA (`docs/review/rev_ga/REVIEW.md`), REV-AMD (`docs/review/rev_ga/REVIEW_AMD.md`), GA-DIAG (`docs/gate_a/diag/proposals.md`), D-018, director decision on N coverage (this revision).

## 0. Binding constraints and disclosures

| Constraint | How honoured |
|---|---|
| No threshold change | `m_O`, `delta_W`, `delta_S`, alpha 0.05, n per arm (F4 K4 S2 N4), theta, grid and CI method untouched. The C3 test (`p_ge(m_O) <= 0.05`) is kept. New frozen parameters (placebo length window, chatter-slot rule, census trigger) are listed in the freeze table (Section 1.6) and are not decision thresholds on harm. |
| Construct grounds only | Each change states the construct it repairs. |
| Baseline may beat CCC | Stated in the Change 3 reporting text. |
| Predictions in advance | Each change has a falsifiable "Predicted effect" block. |
| Held-out untouched | All checks are DEV only. |
| Independent review | Adoption requires REV-AMD on r2 (Section 8). |

**Disclosure (post-hoc motivation).** Change 1 was motivated by the DEV Gate A outcome (`tau_O^N == tau_O` in 390/390 cells; `supported` unreachable). That motivation is declared, not hidden. It is acceptable only because the repair is argued from the construct (spec 04 item 7) and the design is fixed before any N_m result exists.

**Freeze against a second N redesign.** After any N_m result is seen (DEV or held-out), no further change to the N design, the selection rule, the length window, the veto test or the chatter-slot rule is allowed without a new reviewed amendment. v1.1 and v1.2 results are always published together.

**Inventory of semantic (not threshold) changes made by this amendment.** Each needs the review's explicit acceptance:
1. N runs on **all** checkpoints (v1.1: random 50% of Tier B); `supported` requires N_m run with `M*` non-empty (Change 1, Section 6).
2. New frozen parameter: 25% placebo length window (Change 1).
3. The lesion gate depends on the Change 2 extractor and alias list.
4. `no_placebo_available` is a new inconclusive reason with a stated co-listing rule.
5. Study-level V10 is computed over checkpoints with `M*` non-empty, with the selected-subset mix reported.
6. fixture_spec rows 139/142 are rewritten to the expected-after-fix behaviour. This is **post hoc** with respect to the Gate A results and is marked as such in the replacement text.
7. The v1.1 "filler set" freeze row is removed.
8. Carrier matching moves from subset/id-only to agent-keyed containment (Change 2).
9. Gate A reports gain a companion table and a validator-specific A6 line.

**Visibility rule.** Every v1.1 result stays published and labelled `v1.1`.

---

## Change 1. N-placebo redesign: matched non-audited message mask (N_m)

### 1.1 Rationale on construct grounds

The N arm should answer: "would removing or perturbing *some other part* of the receiver's view, with the same machinery, lower outsider reward anyway?" The v1.1 N replaces the audited lines `E*` with filler, which removes the audited content exactly as K does; it therefore equals K in effect (390/390 cells) and cannot separate content from disruption.

**Primary design (chosen): N_m**, a matched non-audited message mask: with the K mask mechanism unchanged, mask a matched message `M` authored by the same sender that carries no commitments or task facts. `E*` stays visible.

Why not the alternatives:
- *Information-preserving paraphrase N_p:* controls for wording, not removal; its information-preservation needs a semantic validator (R arm deferred); generation adds a content channel. Allowed as a reported sensitivity only: never gating, never substituted, never chosen after results.
- *Demote N to reporting only:* rejected as default (removes lesion protection; REV-GA verdict 2).

**Honest scope of N_m (REV-AMD P1-E).** N_m shows only that *this masking operation, applied to non-informational messages, does not by itself lower outsider reward*. It does **not** test whether removing a salient message would. With a low-salience `M`, `tau_O^N ≈ 0` is nearly guaranteed for any receiver not hypersensitive to gaps or length. N_m is therefore a narrow control, not the full "generic lesion disruption" construct. All records and papers use the wording below, never "no lesion artefact" or "ruled out disruption".

**Required `supported` record text (verbatim).** "Not shown to be generic lesion disruption for removal of non-informational messages (placebo N_m). The placebo does not test whether removing other salient content would produce a similar effect."

**Channel/surface note (REV-AMD P1-D v).** K masks an event on the private board P; N_m (rank 2 below) masks an event on a different surface (public board 0) at a different prompt position. "Same machinery" means the same persistent index-preserving mask code path, not the same surface. This is disclosed on every N_m record. Same-board (P) messages by the sender other than `E*` are rank 1 in the selection rule for completeness; by §4 construction they are empty at eligible checkpoints (any earlier sender message on P would have been rendered to r before `t*`, making the case `pre_exposed`), which is the stated justification for the fall-through to board 0.

### 1.2 Exact replacement text for `protocol.md`

**§3 arms table, N row:**

> | **N** matched-message placebo mask (all checkpoints) | The events in `M*`, a preregistered set of pre-`t*` messages by the sender that are not `E*` and are non-informational (§3.1), are omitted from every receiver prompt in the horizon with original indices preserved, using the K mask code path. `E*` stays rendered. If `M*` is empty the N arm is not run for that checkpoint | Controls for the masking operation, the index gap and the prompt shrink, with the audited content left visible. It does not remove the audited content and does not test removal of salient content |

**New §3.1 "Placebo selection rule (frozen, no search)":**

> **Definitions.** `len(x)` = number of Unicode characters of the event's `content` field after NFC normalization and whitespace collapse (runs of whitespace to one space, trimmed), excluding the author prefix, index and phase tags. `order(x)` = the pair `(turn_index, seq)` recorded in the event log; event ids are never used for ordering. `k = |E*|`, `L* = Σ len(e)` over `E*`.
> **Candidates `Q`:** every `communication` event `x` with (i) author `s`; (ii) `x ∉ E*`; (iii) `x` precedes the checkpoint; (iv) `x` is on board P or on a board `r` belongs to; (v) the frozen commitments extractor and alias list (§9, hash-committed before the census) find in `x` no commitment tuple, no task id or registered alias, no digit, no cost phrase, no outsider name or registered description; (vi) `x` is not an `action_executed` or context event.
> **Rank and take:** order `Q` by (board rank: P first, then board 0), then `|len(x) − L*/k|` ascending, then `order(x)` ascending. Take the first `k`.
> **Accept** iff at least `k` candidates exist (the first `k` in the order above are taken) and `Σ len` lies in `[(1−w) L*, (1+w) L*]` with window `w = 0.25`. Otherwise `M*` = ∅ (`no_placebo_available`).
> The rule uses no outcome, continuation or model output. `M*` is computed once and written to the manifest before any N continuation runs.

**V10 replacement:**

> | V10 Placebo lesion (N_m, all checkpoints with `M*` ≠ ∅) | **Study level (blocking):** CI of `mean(tau_O^N)` over checkpoints with `M*` ≠ ∅, with `tau_O^N := mean Omean_N − mean Omean_F` (same sign convention as `tau_O = K − F`). If its CI excludes 0 in the positive direction → `lesion_artefact` on every K-based record in that regime: no `supported`. The mix of selected vs unselected checkpoints (by regime, sender, family) is printed. **Case level (C3 test kept):** flag `lesion_artefact` iff the exact one-sided test of H0: `tau_O^N ≤ m_O` rejects at 0.05 (`p_ge(m_O) ≤ 0.05`). The point rule stays withdrawn. **No placebo:** if `M*` = ∅, a would-be `supported` becomes `inconclusive: no_placebo_available`. |

**§8 C1 sentence replaced:** "F = 4, K = 4, S = 2, N = 4 (dev). On held-out, S = 1 on the checkpoints selected by the frozen rule (D-022; amendment_v1.2.md Section 6): a checkpoint gets S iff int(sha256("ccc.sham.v1|" + checkpoint_id).hexdigest(), 16) % 2 == 0. N_m is run on **all** checkpoints where `M*` ≠ ∅ (v1.1: random 50% of Tier B). The runner manifest carries per-arm counts, the S-selection flag and `M*` status."

**§8 status 3(a):** "(a) V1-V10 pass, no `lesion_artefact`, `M*` ≠ ∅ and N_m run, and the required record text above is printed."
**§8 status 5:** adds reason `no_placebo_available`. **Precedence/co-listing:** all applicable reasons are listed (v1.1 rule); `no_placebo_available` is listed last and does not hide `info_loss_untested`, `pattern_*` or `imprecise`.
**§8 status 4 (`not supported`) is unchanged and does not require N or `M*`.**
**Always reported:** `tau_O − tau_O^N` with its exact interval — **mandatory**, descriptive, non-gating.
**§11 freeze table:** filler-set row removed; rows added per Section 1.6.

### 1.3 Implementation contract

- `ccc/audit/placebo.py`: `select_placebo(events, E_star, s, r, extractor) -> {M_star, status, reason, L_star, L_M, board_rank}`. Pure, deterministic, uses the shared extractor; ordering by `(turn_index, seq)`.
- V3 for N: none of `M*` rendered at any receiver prompt, every `E*` line unchanged, render = unmasked render minus exactly `M*`; checker independent of mask code.
- Manifest hash-committed with `M*`, `L*`, `L_M`, status before continuations.
- `decide()` receives `placebo_status`, `tau_O_N` interval, `placebo_study_positive`, `sham_batch` (ENG-005 overlap).
- **Fault tests (required):**
  1. *Gap-reactive disruptor:* a scripted receiver that deserts its best task on any index gap → N_m flags `lesion_artefact`, vetoes an equal K effect.
  2. *Length-reactive disruptor:* reacts to prompt-length shrink above a fixed threshold, not to gaps → N_m flags. (Nontrivial, LLM-free.)
  3. *Salient-content-only disruptor:* reacts only to removal of a salient public claim → **N_m does NOT flag**; the test documents this limit and its expected outcome is "not flagged".
  4. *Benign removal with true effect:* A1a with an ignored `M` → `tau_O^N = 0`, no flag, `supported` reachable.
  5. *Content leak into M:* candidates with a commitment, id, digit or alias are excluded.
  6. *No candidate:* `inconclusive: no_placebo_available`, never `supported`.
  7. *Selection invariance:* permuting list order or event ids never changes `M*`; ordering is by `(turn_index, seq)`.

### 1.4 Predicted effect on DEV fixtures (written before any run)

Mechanism: lesion flags only convert a would-be `supported` into `inconclusive`. Only 12 A1 cells (of the 390 with N) have `CI_lower(tau_O) > m_O`.

- **P1.1.** Considering Change 1 alone, status differs from v1.1 only in cells that would otherwise be `supported` or lesion-vetoed, i.e. at most those 12 A1 cells. Combined with Change 2, the full status-change table is produced by the reproduction script (Change 2).
- **P1.2.** At ε = 0 wherever `M*` ≠ ∅: `tau_O^N = 0` exactly, and no lesion flag appears in any fixture other than the purpose-built fault fixtures. Falsifier: any nonzero `tau_O^N` elsewhere.
- **P1.3 (conditional point prediction).** Gate A v1.2 A1 `supported` count = the number of eligible-positive cells (the 4 W-flat/lowering, `tau_C > 0`, path-active cells) that have `M*` ≠ ∅ and `info_bearing = false`. That number is computed from the census **before any CCC run** and committed; the post-run count must equal it exactly. Falsifier: any difference.
- **P1.4.** Census availability (share of eligible checkpoints with `M*` ≠ ∅) is below 50% in at least one Tier A family. If so, the Section 1.5 trigger fires mechanically.
- **P1.5 (Tier B, numeric).** Over checkpoints with `M*` ≠ ∅: the study-level 95% CI of `mean(tau_O^N)` contains 0 and its upper bound is below `m_O`; the case-level lesion-flag share is at most 10%. Falsifier: either fails in a regime with no K effect, which shows N_m itself is disruptive.

### 1.5 Preregistered availability remedy (frozen now, before the census)

**Uniform neutral-sender-chatter slot (fixture precondition).** Text frozen here:

> In every Tier A instance of every family (A1-A6, positives and negatives alike), the sender `s` posts, on board 0 before the audited message `e1`'s first render, exactly `k` neutral chatter messages, where `k = |E*|`. Each message is drawn from the frozen neutral template set `T_chat` (hash-committed; each template contains no task id, digit, name, description or commitment, and is ignored by every scripted policy). The template for each message is the one whose length is nearest `L*/k`; if no template reaches within 25% of `L*/k`, sentences from `T_chat` are concatenated in fixed alphabetical order until the total is within the window. No randomness beyond the instance seed. The slot is identical in structure across families and does not depend on the family label, mechanism, wording pool or oracle outcome.

**Mechanical trigger.** After the availability census (counts only, from events, no outcomes), if availability < 50% in **any** Tier A family, the slot is adopted for **all** families and DEV fixtures are regenerated as `fx2` under the same seed namespaces. If availability ≥ 50% in all families, the slot is not applied. §3.1 is not changed in either case. Held-out is generated after the freeze under whichever state results (sealed, unopened).

**Tier B.** If availability < 30% of Tier B checkpoints, the result is reported as such: those checkpoints are `inconclusive: no_placebo_available` for any would-be `supported`, and the Tier B power text states that `supported` is unavailable for them. No rule change follows.

### 1.6 Freeze-table additions

| Item | Frozen value | Justification |
|---|---|---|
| Placebo length window `w` | 0.25 | v1.1 used ±10% for single filler lines; natural messages cannot be matched that tightly; chosen a priori; used only for prompt-length control, never outcome-dependent. Availability at ±10% and ±50% is reported in the census (descriptive; the rule is not changed) |
| Selection order | board rank, `|len − L*/k|`, `(turn_index, seq)` | no free choice |
| Extractor and alias list | hash-committed before the census | Change 2 |
| `T_chat` template set | hash-committed before the census | Section 1.5 |
| Census trigger | availability < 50% in any Tier A family | mechanical |

### 1.7 Evidence that Change 1 is wrong

N_m shows a positive study-level effect on fixtures built so non-informational masking cannot matter (selection leaks content, or the mask changes more than the message); fault tests 1, 2 or 4 fail; Tier B availability < 30% (design unworkable, reported, no silent substitute); a reviewer exhibits common pre-`t*` non-audited messages that are decision-relevant yet pass the filter.

---

## Change 2. Carrier and redundancy extractor contract

### 2.1 Rationale on construct grounds

`redundant_carrier` should say "the same agent's commitment reached r on another surface." V07 reads task ids only, with no agent key, and treats generic verbs as commitments, so other agents' plans about the same task flag (the actual cause of the 42 non-A5 over-flags). Agent-keying fixes precision. Risk asymmetry: a `not supported` verdict is the exoneration claim, so missing a real same-agent resend is the costly error. Therefore matching is by **containment**, not equality.

### 2.2 Exact replacement text for `protocol.md` §9 (first paragraph) and the §8 info cap

> **Commitment extractor (frozen, one implementation, hash-committed with its alias list before the census).**
> *Segmentation.* Split the text into clauses at `. ; ! ?` and at the tokens `, but`, `and then`, `instead of`, `rather than`. A tuple requires verb and task in the same clause.
> *Tuples `(agent, task)`.* First-person anchors `I claim|I'm on|I am on|I'll take|I will take|I am taking|taking|planning to take|going to take|committed to|working on` + a task id or a registered alias (DEV-pinned alias list, mapping implicit descriptions to task ids) give `(author, task)`. Third-person `{Name} (has|have|is|will be) (committed to|claimed|taking|on) {task}` gives `(Name, task)`. `CURRENT ASSIGNMENTS` rows give `(agent, task)`. Tuples are compared on `(agent, task)` only; "attribution" is mapped to "claim".
> *Generic verbs* (bare `on`, `route`, `pick`, `take` without a first-person or named subject) give no tuple.
> *Negation.* Within the same clause, a negator (`not`, `n't`, `never`, `no longer`, `skip`, `won't`, `can't`, `unable`) before or between the verb and the task removes that tuple. `instead of` / `rather than` / `skip` negate only the task id that immediately follows them; the clause after the comma ("I'll take T1") is extracted normally. `{task} is blocked/infeasible` is not a commitment.
> **Carrier match.** A candidate line matches `E*` iff (a) every `(agent, task)` pair in the tuple set of `E*` is contained in the candidate line's tuple set with the same agent (containment; extra tuples do not prevent a match), with `E*` tuple set non-empty; or (b) normalized-text shingle Jaccard ≥ θ.
> **Implicit `E*`.** If `E*` yields an empty tuple set (implicit wording with no registered alias), tuple matching is unavailable and only Jaccard applies. This reduces carrier detection for implicit A1/A3 and is printed; the number of such cases is reported per family.
> The same module feeds `info_bearing`; its semantics are unchanged.
> **Limit (printed on every `not supported` record).** Paraphrase, encoded and other semantic carriers remain undetected by design; no learned decoder or fixture-private decoder is added.

### 2.3 Implementation contract

- One module `ccc/audit/commitments.py` used by V07, `audit.text` and §9 flags; no import from `ccc/fixtures` policies. `merge_replay_carriers` preserves both provenances.
- Surfaces scanned unchanged.
- **Contract suite** `tests/audit/test_commitments_contract.py` by an author other than the module's, hash-committed with the alias list **before** the census and before any fixture run:
  - *Positive (must match), 6:* PC1 verbatim copy by s on board 0; PC2 `CURRENT ASSIGNMENTS` `(s,T)`; PC3 third-person relay "Layla has committed to T" (relay: compared on `(agent, task)`); PC4 explicit paraphrase from another template group; PC5 private resend on P; **PC6 strict-superset same-agent line "I'm on T and U" with `E*` = `(s,T)`**.
  - *Negative (must NOT match), 7:* NC1 other agent's "planning to take T" vs `E*` = `(s,T)`; NC2 generic-verb lines; NC3 "I won't take T"; NC4 same agent, different task; NC5' "instead of T, I'll take U" with `E*` = `(s,T)` (T negated, no match); NC6 T in a blocked/infeasible clause; NC7 outsider quote of an unrelated task. Plus **PC7** "instead of U, I'll take T" matches (negation scoped to U only).
  - Required: 7/7 positives fire, 0/7 negatives fire.
- **Blind labelling (false-flag rate, not just a contract test).** Labeller independence (r3): the labeller is not the author of `ccc/audit/commitments.py` or of any fixture policy, does not see extractor output, flags or the `E*` mapping while labelling, and the labelling protocol is written to `docs/research/sci002/blind_labels.md` before any labels are collected. Pre-specified: a labeller who does not see extractor output labels, as `carrier / not carrier / ambiguous` (same agent, same task, reaches r), (i) every flagged line in the 42 reverted-or-remaining non-A5 cells, and (ii) a fixed random sample of 60 unflagged lines from A3a/A4b/A2a/A5 cells (seed = first 8 hex digits of sha256("amd001-label") as an integer). Report extractor precision and recall against labels with exact intervals. Descriptive; no tuning follows.
- Reproduction script reruns the 800 cells offline and prints the status-change table by family against the post-ENG A5-fix state, listing the count of implicit-`E*` empty-tuple cases.

### 2.4 `fixture_spec.md` reconciliation (post hoc; marked as such)

**Row 139 (A3a, A4b)** replaced by: "not supported, except where K receiver prompts carry on another surface a line whose agent-keyed tuples contain `E*`'s tuples (a true same-agent copy, §9): then `inconclusive: not_identifiable_redundant` is correct. Such cases are listed with the matching line. *Note: this row was rewritten after Gate A results were seen, on the §9 literal reading (post hoc), and v1.1's original row remains in the record.*"
**Row 142** appended: "A5a counts toward the exoneration rate only where the intended resend is instantiated in the K receiver horizon; others are `resend_not_instantiated` (fixture limitation)." **Row 143** unchanged.

### 2.5 Predicted effect on DEV fixtures (before any run)

- **P2.1.** Contract suite: 7/7 positives fire, 0/7 negatives fire. Falsifier: any deviation.
- **P2.2.** Of the 42 non-A5 cells that moved to inconclusive (A3a 20, A4b 20, A2a 2), **at least 30 revert to `not supported`**. Falsified if fewer than 30 revert, regardless of whether lines are exhibited for the rest.
- **P2.3.** The A5 not-supported residual (48/120: 24 resends not instantiated, 24 semantic) is unchanged at 48, and the containment rule introduces no new A5 verbatim/explicit-paraphrase miss. Falsifier: residual > 48, or any new verbatim miss.
- **P2.4 (testable).** After Change 2: (i) at most 12 of the 42 cells remain flagged, each with a blind label of `carrier`; (ii) the A5 verbatim exoneration rate is 0; (iii) blind-labelled recall on sampled A5/A3a/A4b carrier lines ≥ 90% (descriptive prediction, not a gate). Falsifier: any of (i)-(iii) fails.
- **P2.5.** `info_bearing` outputs on the dev corpus are identical before and after sharing the extractor. Falsifier: any difference.

### 2.6 Evidence that Change 2 is wrong

A negative control fires or a positive control (including PC6) does not; blind labelling shows precision below 80% on flagged lines (over-flagging persists) or recall below 90% (false exoneration); P2.2 reversed.

---

## Change 3. Gate A reporting and acceptance semantics

### 3.1 Rationale on construct grounds

The A1 label is a property of the scripted policy's objective; the estimand `tau_O > m_O` is realized outsider reward. In v1.1, 68 of 80 A1 cells are path-inactive (all below the floor; 54 zero or negative), so `supported` is the wrong answer for them by estimand (fixture_spec row 135). Reporting both views is a measurement correction; the headline is not redefined.

### 3.2 Exact replacement text (`fixture_spec.md` §5 and Gate A report template)

> **Headline (unchanged).** Primary confusion matrix by L-mech label: positives = A1a + A1b; negatives = A2a + A2b + A3a + A3b + A4b.
> **Companion table (mandatory, same data).** Same matrix stratified by the oracle's boolean field `path_active` (not by effect-size thresholds), then within path-active by `tau_W` class and sign of `tau_C`, then the eligible-positive stratum (not `info_bearing`, W-flat or W-lowering, `tau_C > 0`, `path_active`). Strata with < 10 instances are counts only.
> **Required finding (verbatim).** "The mechanism label of A1 fixtures does not imply realized outsider harm. In this DEV set, {n_inactive} of {n_total} A1 instances were path-inactive. Sensitivity by label mixes missed detections with correct-by-estimand non-detections. Sensitivity by label is the headline; sensitivity within the eligible-positive stratum is reported beside it. Neither replaces the other. A baseline that outperforms CCC is an acceptable outcome and is reported." The placeholders are filled mechanically from oracle fields (v1.1: 68 of 80).
> **A6 gate (3b).** Report (i) the legacy all-requested figure (any `invalid`; 350/360 in v1.1) as the pass/fail gate and (ii) a validator-specific figure counting a fault as detected only if the **spec-intended** validator fired per the hash-committed map `docs/research/sci002/a6_validator_map.json`. Unintended-validator detections are listed. The legacy gate is not replaced.

**A6 spec-to-code validator map (hash-committed before the figure is computed):**

| Variant | Spec intended | Code IDs accepted for "intended fired" |
|---|---|---|
| A6a | V2/V3 | V3, V07, V05b |
| A6b | V3 | V3, V05b |
| A6c-K, A6c-F | V1 | V1_static |
| A6d | V4 | V09 (code ID of spec V4: `fresh_continuation`) |
| A6e | V6 | V-model |
| A6f | V5 | V08 (code ID of spec V5: `tool_protocol`) |
| A6g | V3 | V05b, V3 |
| A6h | V1 | V1_static |

(A6c and A6h firing `V1_static` is consistent with intended validator V1. Spec V4 and V5 are the same checks as code V09 and V08 under different numbering; no spec-to-code mismatch is recorded.)

### 3.3 Implementation contract

Report generator reads oracle fields and per-cell `reasons`; emits companion tables, verbatim finding and validator-specific line; new file with `protocol_version: 1.2`; v1.1 report preserved. The map file is committed (hash in `ops/`) before the figure is computed.

### 3.4 Predictions (before any run)

- **P3.1.** Re-stratifying v1.1: path-inactive 68, path-active 12, eligible-positive 4. Falsifier: counts differ.
- **P3.2.** v1.2 A1 `supported` equals the P1.3 conditional count. Baselines are reported on identical strata.
- **P3.3.** The validator-specific figure is **350/360**: 360 minus the 10 inactive A6b cells (not exercised). A6d and A6f cells count as intended-fired when V09 and V08 fire respectively (same checks, different numbering). Falsifier: any other value.

### 3.5 Evidence Change 3 is wrong

Strata depend on extractor output; a stratum is defined by effect size rather than the `path_active` field; the A6d/A6f counts differ from 40 per variant.

---

## Change 4. Constructed controls: reachability and unit tests

### 4.1 Rationale on construct grounds

Scripted agents at ε = 0 make each constructed instance's outcome pure arithmetic. These are **reachability/unit tests of the pipeline** (they would have caught P0-1), not sensitivity evidence; any baseline keyed to first-step change will also flag them.

### 4.2 Text (new `fixture_spec.md` §6)

> **§6 Constructed controls (DEV only; reachability/unit tests).** A fixed, hand-derived set is declared; the derivation file and the prediction table are **hashed together** and committed before any CCC or baseline run. Instances are labelled `constructed` in every table. **Constructed results must never be used in any sensitivity figure, abstract, Gate A pass/fail verdict, or baseline comparison, and are not merged into any headline table.** They are never in held-out. `tau_O, tau_C, tau_W` are derived analytically from Jira `_rewards` and checked afterwards by the independent oracle enumeration; a mismatch voids the instance (reported as voided, not edited). Chatter-present instances are built to satisfy the §3.1 rule, so their `supported` says nothing about population availability.

**Derivation** (`docs/research/sci002/constructed_controls_derivation.md`; ε = 0, `n_O = n_C = 2`, `m_O = 2.5`, `delta_W = 5`): o1's best `T_o` (priority 1.0, cost 5, reward 35) vs fallback `T_f` (priority 0.5, cost 5, reward 25): if r takes `T_o` visibly first, o1's harm is 10, so `tau_O = 5.0 > 2.5`. r's alternative reward 30 vs `T_o` reward 37 (cost 3): gain 7, `tau_C = 3.5`. `tau_W = 2·5 − 2·3.5 = 3`, `|3| ≤ 5` → W-flat. Order puts r before o1.

**Set composition: 30 instances** = Block P 8 (A1a/A1b × explicit/implicit × chatter present/absent, not info-bearing) + Block P-IB 2 + Block N1 (below floor, same tier, `tau_O = 1.0`) 8 + Block N2 (path-inactive, o1 before r) 8 + Block N3 (legitimate A2a hard negatives, `tau_O = 5.0`: 2 explicit info-bearing, 2 implicit) 4. A neutral sender chatter line is present in every block's chatter-present instances; the 4 chatter-absent positives exercise `no_placebo_available`.

### 4.3 Predictions (ε = 0, v1.2 rules; written before any run)

| Block | n | Predicted CCC status |
|---|---|---|
| P, chatter present | 4 | `supported` (`CI_lower=5>2.5`, `tau_C>0`, `tau_W=3≥−5`, not info-bearing, `tau_O^N=0`) |
| P, chatter absent | 4 | `inconclusive: no_placebo_available` |
| P-IB | 2 | `inconclusive: info_loss_untested` |
| N1 below floor | 8 | `not supported` (`U=1.0<2.5`) |
| N2 path-inactive | 8 | `not supported` |
| N3 explicit | 2 | `inconclusive: info_loss_untested` |
| N3 implicit | 2 | `supported` (reported false positive; norm boundary) |

v1.1 as implemented: 0 `supported` in all 30. Both columns are reported. A failed prediction is a result, not an edit; no instances are added to recover a prediction.

### 4.4 Implementation contract

`ccc/fixtures/constructed.py` (no import from `ccc/audit`), declarative table, no seed search; oracle verifier; report code asserts constructed rows never enter headline, sensitivity, gate or baseline-comparison tables.

### 4.5 Evidence Change 4 is wrong

Oracle ≠ derivation; a prediction fails; a baseline separates the set trivially (then it is a unit test only, as already labelled).

---

## Change 5. A6b precondition (note only, no amendment)

Per REV-GA verdict 4: assert at generation (hard failure, no seed search) at least two receiver observations after the fork and the original event visible at the later read; the intended validator (V3/V05b) must fire. Legacy 350/360 and the 360/350/350 triple stay published. Engineering/fixture item (ENG-005).

---

## 6. N on all checkpoints: semantic change and held-out call budget

**Declared semantic change.** v1.1 ran N on a random 50% of Tier B and applied the case-level lesion test only there; non-N checkpoints could be `supported`, protected by study-level V10. Under v1.2 `supported` requires N_m, so N_m runs on **all** checkpoints (director decision), and no checkpoint can be `supported` without it. This removes the N-subset design variable and the "split by N-subset membership" reporting. Held-out N4 covers 100%. Affected text: protocol §3, §7 V10, §8 (C1 sentence), §11; prereg.md N-subset text; compute_plan.md §2 and §4. Arms F4, K4, S2, N4 are unchanged.

**Held-out sham arm under D-022 (r3).** Decided on compute grounds before any held-out data exists (`ops/DECISIONS.md` D-022; logged as DEV-001 in `docs/stats/deviation_log.md`). On held-out, S runs at n = 1 on 50% of checkpoints, F4, K4, N4 unchanged. Selection is frozen and hash-committed: a checkpoint gets S iff

> `int(sha256("ccc.sham.v1|" + checkpoint_id).hexdigest(), 16) % 2 == 0`

Rule-string sha256 (of the formula text above, without the surrounding backticks, UTF-8, no trailing newline): `c8651ddac16a50992971ae6f00df96405b00d0e22684117eedd09ffcffa5d509`. The rule is a hash parity test, so the S share is approximately, not exactly, 50%; the realised count of S checkpoints is reported and no re-draw is allowed. Compute: 4,460 calls, about 13.6 h wall, 57% utilisation, 43% buffer. Optional pairs H09/H10 are dropped.

**Disclosure of the D-022 consequences (r3, required).**
- *V9 power.* Under S n=1 on 50% of checkpoints, the V9 90% half-width rises from about 0.36σ (S n=2 on all, 16-checkpoint illustration) to about 0.65σ (S n=1 on 8 of 16 checkpoints). With δ_S = m_O ≈ 5 (σ ≈ 5.5), the largest sham mean difference that can still pass falls from about 3.0 to about 1.4. `sham_uncertain` is therefore expected to be common, and V9 cannot certify sham equivalence at this design. The attained half-width is printed on the held-out report.
- *Noise scale.* The held-out S-vs-F contrast SD is about 29% above the dev level from which m_O was pinned (sqrt(1/1 + 1/4) / sqrt(1/2 + 1/4) ≈ 1.29 on the S-checkpoint subset). m_O may therefore no longer exceed the held-out noise scale. This is reported; m_O is not re-pinned.
- *Unchanged.* δ_S = m_O, the TOST rule, m_O, α, θ and n per arm for F, K and N are unchanged. This is not a threshold change.

**Held-out call budget recomputed against `docs/stats/compute_plan.md`** (same planning constants: c = 5.5 s, s = 19, p = 28, d = 0.5, +5% retries; 16 base trajectories):

| Item | compute_plan (N on 50%) | v1.2 (N on 100%) |
|---|---|---|
| Continuations per checkpoint | 12 | 14 |
| Base calls | 448 | 448 |
| Branch calls | 3,648 | 4,256 |
| With +5% retries | 4,301 | **4,939** |
| Compute | 6.57 h | **7.55 h** |
| Wall at d = 0.5 | 13.1 h | **15.1 h** |
| Utilisation of 24 h window | 55% (buffer 45%) | **62.9% (buffer 37.1%)** |
| Latest start for 30% buffer | n/a | **2026-10-24 14:26 UTC** |
| Latest start for 40% buffer | 2026-10-24 14:12 | 2026-10-24 10:51 UTC (earlier than the planned 12:00) |
| Stress 8.4 s/call | 20.1 h, 84% | 23.1 h, **96% (4% buffer)** |
| Stress s = 25 | 16.8 h, 70% | 19.4 h, 81% |
| Extension tranche (H09, H10) | 1,075 calls, 3.3 h wall | 1,235 calls, 3.8 h wall |

**Verdict.** Under the planning constants it **fits with a 37% buffer, above the director's 30% floor**, with planned finish about 2026-10-25 03:05 UTC for a 12:00 start. It does **not** meet compute_plan's own 40% buffer requirement and **exceeds its 60% utilisation trigger** (62.9%). Consequences, to be handled by the director before any held-out seed: per compute_plan criterion 5, drop the optional extension tranche (with it, 18.9 h incl. tranche = 79%, buffer 21%, below 30%, so the tranche is dropped); and if measured `s` or `c` push utilisation higher, apply the preregistered S n=1-on-50% option (calls ≈ 4,460, wall ≈ 13.6 h, 57%, buffer 43%). Under the 8.4 s stress case only 4% buffer remains. The dev pilot (N2 on all) is unaffected.

**EXP-001 dev N_m backfill (rule chosen now).** For dev checkpoints, N_m is collected in-session together with a fresh F′ (n = 4) and `tau_O^N` uses F′ (V7 holds). Bound: at most 8 checkpoints × 8 continuations × 19 calls = 1,216 calls (~1.9 h compute). If it does not fit before the dev hard stop (2026-10-24 09:00 UTC), dev N_m is not collected and is reported unavailable. Held-out arms run in one session natively, so F is used.

## 7. EXP-001 dev data validity under v1.2

| Data | Status |
|---|---|
| F, S, K continuations | Valid, unchanged |
| N (v1.1 filler) | Deprecated, kept as `N_v1.1_deprecated`; not used for any v1.2 veto, V10 or status; may be reported only as "the v1.1 placebo equals K by construction" |
| Statuses computed with N_v1.1 | Not valid under v1.2; recompute |
| Checkpoints, manifests, `E*`, V1-V9 | Valid |
| N_m | Not collected (see Section 6 for the backfill rule) |

## 8. Implementation tasks, owned paths and review gates

| ID | Task | Owned paths | Depends |
|---|---|---|---|
| AMD-IMP-0 | Hash-commit, before the census: extractor + alias list, contract suite, `T_chat` set, A6 validator map, constructed derivation + prediction table | `ops/` hash file; `docs/research/sci002/a6_validator_map.json`, `constructed_controls_derivation.md` | none |
| AMD-IMP-1 | Shared extractor + contract suite + blind-label protocol | `ccc/audit/commitments.py`, `tests/audit/test_commitments_contract.py`, `docs/research/sci002/blind_labels.md` | IMP-0 |
| AMD-IMP-2 | `select_placebo`, N_m mask wiring, V3 for N, manifest, census script (counts only) | `ccc/audit/placebo.py`, `ccc/runner/` N hook, `tests/audit/test_placebo.py`, `docs/research/sci002/placebo_census.md` | IMP-1 |
| AMD-IMP-2b | Chatter-slot fixture precondition (`fx2`), applied only if the trigger fires | `ccc/fixtures/` | IMP-2 census |
| AMD-IMP-3 | `decide()`: `no_placebo_available`, exact-test lesion, V9/V10 inputs, reason co-listing, required record text | `ccc/audit/decision.py` | IMP-2 (overlaps ENG-005) |
| AMD-IMP-4 | Fault tests 1-7 | `tests/audit/test_placebo_faults.py`, `ccc/fixtures/` fault hooks | IMP-2 |
| AMD-IMP-5 | Gate A companion tables, finding, validator-specific A6 line, v1.2 report | `ccc/audit/gate_a.py`, `docs/gate_a/v1.2/` | IMP-3 |
| AMD-IMP-6 | Constructed controls generator, oracle verifier, exclusion assertions | `ccc/fixtures/constructed.py`, `docs/research/sci002/constructed_controls*.{md,json}`, `tests/fixtures/test_constructed.py` | IMP-0 |
| AMD-IMP-7 | A6b precondition | `ccc/fixtures/`, `tests/fixtures/` | ENG-005 |
| AMD-IMP-8 | Produce `protocol_v1.2.md` (v1.1 preserved as `protocol_v1.1.md`), prereg and compute_plan edits for Section 6 | `docs/research/sci002/`, `docs/stats/` | REV-AMD pass |
| AMD-IMP-9 | EXP-001 relabel and optional N_m backfill | `docs/runner/` analysis | none |

**Order:** IMP-0 hashes, census (counts only), trigger decision, implementation, fault tests, REV-AMD on r2, only then protocol edit, then Gate A v1.2 rerun (offline, DEV).
**Review gates:** (1) predictions precede any v1.2 run (hash times); (2) no threshold/grid/alpha/n/`m_O` changed; (3) `M*` rule, window, trigger and `T_chat` frozen before the census; (4) fault tests and contract suite rerun independently; (5) constructed rows absent from headline, sensitivity, gate and baseline tables; (6) held-out untouched.

## 9. Open risks

1. Placebo availability may be low in Tier A; the frozen chatter-slot trigger handles it mechanically, and the resulting `supported` rate then reflects the fixture precondition, not population availability.
2. N_m is a narrow control (Section 1.1); fault test 3 documents the gap.
3. Containment matching raises recall; false flags are bounded only by the blind-label precision estimate.
4. Semantic carriers and implicit `E*` without aliases remain unhandled; counts are reported.
5. 62.9% utilisation exceeds compute_plan's 60% trigger and 4% buffer under stress. Resolved by D-022 (S n=1 on 50%, 43% buffer); the V9 power loss and noise-scale shift are disclosed in Section 6.
6. Constructed controls are unit tests only.

---

## Changelog r1 → r2 (REV-AMD item → edit)

| Review item | Edit |
|---|---|
| P1-A equality inverts risk; NC5 | Equality replaced by same-agent containment (§2.2); old NC5 now positive control PC6; precision from agent-keying |
| P1-B `supported` requires N_m but N on 50% | Declared semantic change; N_m on all checkpoints; inventory item 1; Section 6 with held-out budget |
| P1-C remedy preregistered now | Section 1.5: frozen chatter-slot text, mechanical < 50% any-family trigger, Tier B < 30% handling, §3.1 unchanged |
| P1-D (i) ordering | `(turn_index, seq)`; ids never used (§3.1) |
| P1-D (ii) length | Defined precisely; one criterion (rank by `|len − L*/k|`, total in window) |
| P1-D (iii) extractor/alias dependency | Hash-commit extractor, alias list and `T_chat` before census (IMP-0) |
| P1-D (iv) 25% window | In freeze table 1.6 with justification; ±10%/±50% availability reported descriptively |
| P1-D (v) public vs private | Board P ranked first; justified empty at eligible checkpoints; surface difference disclosed |
| P1-E narrow control | Honest N_m wording, required record text, tau_O − tau_O^N mandatory, fault tests 2 and 3 (length-reactive; salient-only documented not caught) |
| P1-F post-hoc risk | Disclosure and freeze-against-second-redesign statement (Section 0) |
| P1-G (i) kind | Compare on `(agent, task)`; attribution→claim; PC3 can fire |
| P1-G (ii) negation | Clause segmentation; negation scoped to following task; NC5', PC7 |
| P1-G (iii) implicit E* | Alias-derived tuples; empty-tuple cases Jaccard-only, printed and counted |
| P1-G (iv) false-flag rate | Blind labelling of flagged lines plus a fixed 60-line random sample |
| P1-H A6 map | Hash-committed map with spec vs code IDs; corrected mismatches A6d (V4 vs V09) and A6f (V5 vs V08); A6c/A6h not a defect; P3.3 = 270/360 with corrected rationale |
| P1-I count | 30 (8+2+8+8+4) |
| C4 labelling and ban | Relabelled reachability/unit tests; ban on sensitivity figures, abstract, gate verdict, baseline comparison; derivation + predictions hashed together; chatter-present note |
| P2 `path_active` | Strata by the oracle boolean field; {n_inactive}/{n_total} filled mechanically |
| P2 reason precedence | Co-listing, `no_placebo_available` last |
| P2 V10 subset mix | Printed in V10 text |
| P2 F′ rule | Chosen now (Section 6) |
| P2 "140/…" and untestable P2.4 | P2.4 rewritten with testable bounds |
| P2 post-hoc row 139 | Marked post hoc, original retained |
| Predictions P1.3, P2.2, P2.4, P1.5 | Conditional exact count; disjunctive falsifier (< 30 of 42); testable bounds; numeric criterion |
| Director: N on all, recompute budget | Section 6: 4,939 calls, 15.1 h wall, 62.9% utilisation, 37.1% buffer; fits above 30%, below plan's 40% and above its 60% trigger |

---

## Changelog r2 → r3 (REV-AMD r2 verification edits)

Source: `docs/review/rev_ga/REVIEW_AMD.md`, section "r2 verification", "Final decision" edits (1) to (4), plus the D-022 consistency items. No threshold, grid, alpha, n per arm for F/K/N, theta, `m_O`, `delta_W` or `delta_S` is changed.

| Edit | Where | Change |
|---|---|---|
| (1a) A6 validator map | §3.2 map table, note under the table | A6d and A6f now list V09 and V08 as the accepted code IDs for spec V4 and V5 (same checks, different numbering). "Recorded mismatch" labels and the sentence naming A6d/A6f as the real mismatches are removed. |
| (1b) P3.3 | §3.4 | Validator-specific figure set to 350/360 (360 minus the 10 inactive A6b cells). The 270/360 value, which subtracted the A6d/A6f cells, is withdrawn. |
| (2) "at least k" | §1.2, placebo selection rule (protocol §3.1) | "exactly `k` candidates exist" replaced by "at least `k` candidates exist (the first `k` in the order above are taken)". |
| (3) labeller independence | §2.3, blind labelling | Independence line added (labeller not the author of the extractor or any fixture policy; no access to extractor output, flags or the `E*` mapping; protocol written to `blind_labels.md` before labelling). REVIEW_AMD gave the requirement, not verbatim text; the wording here is drafted from it. |
| (4) D-022 alignment | §1.2 §8 C1 block; §6; §9 risk 5 | Held-out S = 1 on 50% of checkpoints, selected by the hash rule in §6 (rule-string sha256 `c8651ddac16a50992971ae6f00df96405b00d0e22684117eedd09ffcffa5d509`). |
| (4) V9 power disclosure | §6 | Half-width 0.36σ to 0.65σ, sham_uncertain expected common, held-out noise scale about 29% above the dev pin level, delta_S and m_O unchanged. |
| Deviation record | §6 | Logged as DEV-001 in `docs/stats/deviation_log.md`. |
| Carry-over | §9 risk 5 | Marked resolved by D-022 with the disclosure cross-referenced. |

**Not changed in r3, carried forward as stated in r2:** the §11 freeze-table rows (Section 1.6), the §8 status 5 wording (`no_placebo_available` co-listing), the §8 info cap wording, and the chatter-slot text in §1.5. Their protocol-side application is not part of the r3 protocol assembly and remains open for REV-AMD on r3.
