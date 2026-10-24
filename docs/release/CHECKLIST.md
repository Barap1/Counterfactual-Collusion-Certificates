# Release checklist — REL-001a preparation

Every module-17 checkbox is retained verbatim. DONE means the scoped condition has evidence; PENDING means work or verification remains; OWNER means a human/controller/integrator decision or action remains. This is not release approval. EXP-002 remains running/pending and was not inspected.

Authorship: the owner is the sole author; no AI co-author lines.

## Scientific completion

| Item | Status | Evidence path | Remaining scope |
|---|---|---|---|
| The primary question and operational harm definition are explicit. | DONE | docs/research/sci002/protocol.md; paper/draft.md | Operational contract exists; final claim audit pending. |
| The novelty paragraph names close prior work and avoids unsupported first/proof claims. | PENDING | paper/draft.md; paper/references_draft.bib | Final novelty/source audit required. |
| The archived pilot is separated from holdout evidence. | DONE | ops/pilot_manifest.sha256; README.md | Pilot and EXP-001 are DEV; held-out excluded. |
| Exact replay validity is tested, or the paper is explicitly narrowed to a different intervention design. | PENDING | docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md | Replay checks exist; A6 gate FAIL prevents completion. |
| A legitimate causal-cooperation hard negative is present. | DONE | ccc/fixtures/jira.py; docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md | A2 legitimate-cooperation hard negative included (80/80 not supported). |
| Common-cause, inert-talk, and invalid-replay controls are included or limitations state exactly what is absent. | DONE | ccc/fixtures/jira.py; docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md | A3/A4/A6 controls present; A6 failures disclosed. |
| Real-agent labels are not equated with prompted intent without justification. | PENDING | paper/draft.md; README.md | README states limitation; final manuscript label audit pending. |
| Independent worlds, branch repeats, failures, ineligible cases, and abstentions are counted separately. | PENDING | docs/analysis/exp001_dev/coverage.json; docs/analysis/exp001_dev/attempts.json; docs/analysis/exp001_dev/checkpoint_certificates.json | DEV accounting exists; final held-out accounting pending. |
| Main effects have the appropriate uncertainty and units. | PENDING | docs/analysis/exp001_dev/effects_study.json; docs/analysis/README.md | DEV uncertainty machinery exists; final sample/uncertainty review pending. |
| No model/backend switching, seed hunting, cached duplicate sampling, or hidden post-selection contaminates the reported comparison. | PENDING | docs/stats/deviation_log.md; docs/stats/stage2/STAGE2_ADDENDUM.md | DEV-002 exploratory census limitation recorded; held-out audit not performed. |
| Every headline sentence has a verified evidence chain. | PENDING | ops/CLAIMS.md; paper/draft.md | Independent final sentence-to-evidence audit required. |
## Engineering completion

| Item | Status | Evidence path | Remaining scope |
|---|---|---|---|
| A documented clean setup reproduces the analysis without spending money. | PENDING | README.md; scripts/reproduce_offline.sh; docs/release/environment.json | Offline suite and DEV regeneration/hash checks verified (validation/verified_hashes.json); separate fresh dependency setup remains unverified. |
| Actual upstream commit, patches, dependency versions, model IDs/digests, and prompts are recorded. | PENDING | docs/release/environment.json; docs/runner/exp001_manifest.json; docs/stats/stage2/STAGE2_ADDENDUM.md | Upstream/dependencies recorded; final patches/model-digest/prompt completeness audit required. |
| Core invariants, corruption tests, and budget barriers pass. | PENDING | docs/release/validation/tests.log; docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md | 399 tests OK, 4 skips (one scope exclusion); unresolved scientific gate failures remain. |
| Raw traces and immutable manifests are preserved. | PENDING | docs/release/input_hashes.json; ops/pilot_manifest.sha256 | DEV subset hash-verified; full raw and held-out preservation not audited. |
| Figures, viewer, certificates, and paper agree on the same frozen analysis version. | PENDING | paper/figures_plan.md; docs/analysis/exp001_dev/aggregate.json | Final figures/viewer/certificates/paper synchronization pending. |
| Public artifacts are sanitized; secrets and private working-document IDs are not accidentally published. | PENDING | scripts/secret_scan.sh; docs/release/secret_scan.log | Broad scan flags private Doc identifiers in two existing files (working/staged); owner sanitation required. |
| No unrelated owner changes were overwritten. | DONE | ops/reports/REL-001a.md | Writes restricted to assigned README, release, scripts and task report; no unrelated overwrites. |
| Commits are coherent and within the owner's cap. | OWNER | ops/reports/REL-001a.md | No commits made; integration custodian reviews history and cap. |
## Presentation completion

| Item | Status | Evidence path | Remaining scope |
|---|---|---|---|
| The report fits the official template and current event rules. | OWNER | paper/author_checklist.md | Owner/publication worker must verify official template/current rules; no network in REL-001a. |
| Abstract, figures, methods, results, limitations, references, ethics appendix, and LLM disclosure are complete. | PENDING | paper/draft.md; paper/author_checklist.md | Draft exists; all final sections/disclosures require publication review. |
| Every final PDF page has been inspected or an explicit visual-review gate remains for the owner. | OWNER | paper/author_checklist.md; docs/release/CHECKLIST.md | Explicit final PDF page-by-page visual-review gate remains for owner. |
| Template guidance and placeholder authors/results are removed before finalization. | PENDING | paper/draft.md; paper/author_checklist.md | Final placeholder/template-guidance removal pending. |
| The demo is offline-safe and distinguishes constructed fixtures, real observations, and recorded replay. | PENDING | README.md; paper/figures_plan.md | Reproduction is offline; final demo safety/provenance review pending. |
| A cold reader can explain the principal finding and its limits. | PENDING | README.md; paper/draft.md | Cold-reader review not performed by this task. |
| Google Doc synchronization is either verified with revision information or honestly marked pending. | PENDING | paper/author_checklist.md; ops/reports/REL-001a.md | Google Doc synchronization/revision not verified; private identifiers not copied here. |
## Operational completion

| Item | Status | Evidence path | Remaining scope |
|---|---|---|---|
| Actual resource usage is reconciled separately from environment task cost. | OWNER | docs/stats/stage2/STAGE2_ADDENDUM.md; ops/reports/REL-001a.md | Controller must reconcile actual usage separately; protected live ledger not accessed. |
| New spending remains within the owner's authorization; unknown amounts are not labeled zero. | OWNER | ops/reports/REL-001a.md | REL-001a spends $0; total project spending unknown to this task, not labelled zero. |
| All project cloud jobs/endpoints and unnecessary local inference servers are stopped or explicitly handed off. | OWNER | ops/reports/REL-001a.md | Running held-out experiment explicitly handed off untouched; controller owns shutdown. |
| No publication/sharing/submission action occurred without authorization. | OWNER | ops/reports/REL-001a.md | REL-001a performed none; owner must confirm project-wide authorization and approve final actions. |
| The owner has the exact final artifact paths, repo state, prepared Doc link, and deadline. | OWNER | ops/reports/REL-001a.md; paper/author_checklist.md | Owner/integrator must provide final PDF, private working Doc, final repo SHA and deadline. |

## Final director handoff gate

Use all module-17 handoff fields: Completed; Main finding (scoped); Evidence (independent sample/effect/interval or honest null); Artifacts (PDF, Doc, code, reproduction, demo); Verification (tests/reviews/limits); Resources (actual API/local/Modal gross, credit and net); Owner decisions (author details, review, publication and submission). No final PDF/Doc/held-out result is asserted by this preparation task.

The presentation question remains what evidence justifies a harmful-coordination claim and when an auditor should refuse it. Gate A failures and pending owner gates must remain visible.
