# REV-R2: independent freeze review of the R2 prospective benchmark

Reviewer: REV-R2 (Claude Sonnet, independent). Date: 2026-10-24. Repo HEAD 7cb4ba7 (ccc/ and docs/enh/r2 clean; only an unrelated figures/enh script is modified and is outside the hash set).
Protocol reviewed: docs/enh/r2/PROTOCOL.md, sha256 `334a4539d2dc6976879c50c8244905a735a13ce32f5a4e8046715e31b250dcb6`. **This file must not change after this review; any edit invalidates the review and FREEZE_candidate.json.**

## Verdict: APPROVE-WITH-CONDITIONS (documentation-only; no blocking items)

Blocking items: none. The conditions below are disclosures or procedure notes. They are placed in ops/DECISIONS.md and the paper, not in PROTOCOL.md, so the protocol hash stays fixed.

## Findings by checklist item

**1. Completeness and report.py fidelity.** RQ1-RQ6 and RQ4b each have an estimand and a criterion (PROTOCOL §6, §10 A3, §11). report.py matches on thresholds: RQ3 `<.25` (report.py:274), RQ4 `>.5` with margin on CP lower bound (:244-249), RQ4b `>.5` / `<=.05` (:258), RQ5 gap `<=.02`, zero over-claims, precision/recall `>=.9`, pair attribution `>=.95` (:107-131, :287). CP intervals, seed 20261026 and B=10000 are as written (:163-165). No threshold mismatch. Deviations (stricter, or unspecified by the protocol):
- (a) RQ3 and RQ4 are required to pass in both eps strata (:290-291, :276). The protocol is silent on strata for the verdict.
- (b) RQ5 is evaluated per class x set x stratum. Undefined denominators are scored as fail (:125, :297). The protocol does not state this rule; the generator added it.
- (c) RQ5 precision and recall are thresholded on the member rate. The protocol says "CP lower bound reported", which the report does. Mixed-member rates are not binomial units.
- (d) Selective accuracy does not depend on c, so "at both c" reduces to one gap. The report says so (:128).

**RQ5 is structurally unpassable (disclosure C2).** On DEV, 166 of 168 T8 cells fail. The causes are `absolute_gap=None` (the method never answers, 146 cells) and undefined abstention recall or precision (where every member is identifiable or the method never abstains). Only the pair-attribution sub-results are informative: v1 gets 1.00 at eps 0 and 0.66 at eps 0.1. Without disclosure, a prospective "RQ5: fail" would overstate method failure.

**2. No leak.**
- observe.assert_blinded (observe.py:118) enforces exact key allowlists, neutral agent ids and forbidden label tokens. digest() calls it (:23). run_methods asserts blinding and rejects any Bayes reference carrying member ids (methods.py).
- CRN: continuation RNG is keyed on seed and index only, not on member or arm (twins.py:224), so twins are coupled pointwise.
- Tests: `tests.test_bench_core tests.test_bench_alignment` ran under the offline guard, 30 tests, OK, 108 s. This includes the allowlist test, `test_crn_pointwise_identical_twins_every_arm_and_noise_stratum` and `test_all_methods_symmetry_and_ccc_scope`.
- DEV symmetry shows 0 violations.
- CCC-L reads the public word "transfer" to select its rule; A2 discloses this circularity.

**3. Identifiability labels.** Labels come from `oracle()` (exact 16-action marginalisation, twins.py:235) and from `census()` over the declared policy space (enumerate.py). Neither imports an audited method. `test_enumeration_independent_of_audited_output` passes. Bayes-given-S uses uniform per-policy design mass, not outcomes. Fine.

**4. Frozen methods.** `git diff <first ENH commit>~1..HEAD -- ccc/audit ccc/baselines ccc/fixtures` is empty. decision.py (6bc59ded...) was last changed on 2026-10-23, before ENH. The current hashes equal bench/hash_manifest.json, enumeration/manifest.json, dev_run/manifest.json and COMPLETE.json (34 files, 0 diffs). So the DEV run and the enumeration were produced by the code that would be frozen.

**5. Seed rule and refusal.** draw() (seeds.py:93) implements `sha256(proto|label|i[|j])`, first 31 bits, salt-skip and a fixed label order, as in §4. validate_freeze (__main__.py:44) refuses on a missing FREEZE, schema or status, any code-hash difference, a protocol hash, parameter or count mismatch, a missing or invalid seeds file, a missing reviewer or timestamp, and enumeration or prior hash mismatch. Dry invocations all refused and wrote nothing:
- `run --block prospective --out /tmp/...` printed "FREEZE.json is absent", rc=2, and no output directory was created.
- `seeds --protocol-sha256 ... --out` was refused, rc=2, with no file written.
- `seeds --check /nonexistent` returned an error, rc=2.

A search of the repo and /tmp found no FREEZE.json, seeds.json or prospective output. /tmp/synth/out/fig_*.json contain the string "new-prospective" only as a label in a synthetic figure-layout test built from copied DEV data. They are not seed lists, but delete them (C5).

**Procedure gap (C1).** PROTOCOL §4 line 4 says no seed is drawn before the freeze. §9.4 and validate_freeze require seed_list_sha256, skips and intersections inside FREEZE.json, and materialize() itself requires FROZEN status. These can only be computed by calling `seeds.draw()` in memory, with no file written. The list is a pure function of the protocol hash and the exclusions, so it carries no outcome information. I left those fields null in the candidate rather than draw them. The director must record this decision, then compute them in memory (command in the handoff).

**6. Defaults vs protocol.** COUNTS: 200 for each of P1-P6, 200 jira_iid, 100 for each of the 9 other classes. PARAMETERS: m_O=2.5, eps {0, 0.1}, R=8 (observe.py), c {0.25, 0.5}, B=10000, seed 20261026. H uses strict `>2.5` and E uses `>=2.5`, as in §5. All match. validate_freeze requires `parameters == PARAMETERS` exactly.

**7. DEV-informed amendments.** They are disclosed (§11, D-040) and use DEV data only. Whether any criterion was tuned to pass on DEV:
- RQ1 and RQ2 pass by construction. The generator is deterministic, CRN is on, and A5 made RQ2 method-independent, so it is a tautology check. The failure that motivated A5 was an artefact of CCC-L v0. A2 discloses this.
- RQ4b matches the DEV pattern exactly (P2/P3 1.0 or 0.66; P6 and benign 0.0, against a bound of 0.05). It is DEV-tuned to pass. Label it "DEV-informed replication prediction", never confirmatory.
- RQ4 and RQ3 are unchanged. RQ4 is expected to fail on P6 and benign cooperation. RQ3 sits at 0.24 on DEV at eps 0 against a 0.25 bound, so it is a knife-edge prospective.
- CCC-L v1 was designed from DEV failures. It is exploratory, and v0 is also run.
- None of these amendments can use prospective outcomes, and no seed exists.

**Note on RQ3 (C4).** In the prospective block the population seeds are scattered over 2^31, and iid.py:52-58 derives the suspicious, wording and commitment cells from the seed offset parity. The assignment is therefore pseudo-random, not balanced as in DEV (consecutive seeds). The expected prevalence is the same, but the variance is larger. Disclose this.

**8. Tests.** 30 of 30 pass, as above.

## Conditions (all documentation-only)
- **C1.** Record in DECISIONS.md the in-memory pre-freeze computation of the seed-list hash, skips and intersections for FREEZE.json, with no list written. Then set status to "FROZEN" and fill reviewer approval and time.
- **C2.** Disclose the RQ5 structural-fail mechanism (undefined denominators scored as fail, 166/168 DEV cells). Report the gap, over-claim and pair-attribution sub-results as the informative RQ5 readouts.
- **C3.** Disclose deviations (a)-(d) above and that RQ4b is DEV-tuned.
- **C4.** Disclose that prospective RQ3 has random cell assignment, and the knife-edge DEV value.
- **C5.** Delete /tmp/synth. Do not commit the figure-script change as part of the frozen code. It is not hashed and cannot affect outcomes.

If C2-C4 are instead put into PROTOCOL.md, recompute its sha256 and regenerate FREEZE_candidate.json.
