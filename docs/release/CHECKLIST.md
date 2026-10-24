# Final release checklist — REL-005 audit

Audit basis: committed repository evidence at `92e67bfb99453bebf9f425f84a815c3c74e0ccbb`, plus the explicitly supplied operational facts in `ops/reports/REL-005.md`. This is a status audit, not release approval. Owner is sole author; no AI co-author lines are included in current commits. AI/Claude/Codex attribution trailers remain in pre-2026-10-23-evening pushed history; the repo remains private and nothing has been published or submitted.

Status key: DONE = scoped condition supported by evidence; PENDING = verification/work remains; OWNER = decision or action reserved to the owner.

## Scientific completion

| Item | Status | Evidence path | Remaining scope |
|---|---|---|---|
| The primary question and operational harm definition are explicit. | DONE | `docs/research/sci002/protocol.md`; `paper/build/submission.md` | The manuscript states the estimand and limits. |
| The novelty paragraph names close prior work and avoids unsupported first/proof claims. | DONE | `paper/build/submission.md`; `paper/references_draft.bib`; `docs/review/rev001/REV001.md` | Bounded search and claim narrowing are disclosed. |
| The archived pilot is separated from holdout evidence. | DONE | `ops/pilot_manifest.sha256`; `README.md`; `docs/analysis/exp001_dev_v2/` | DEV and holdout outputs are separately labeled. |
| Exact replay validity is tested, or the paper is explicitly narrowed to a different intervention design. | DONE | `ops/DECISIONS.md` (D-028); `docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md`; `paper/build/submission.md` | Gate A passes its stated module-13 criteria with A5/A6 and other limitations disclosed; not a broad replay-validity claim. |
| A legitimate causal-cooperation hard negative is present. | DONE | `docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md`; `ops/DECISIONS.md` (D-028) | A2 non-vacuity and result are recorded. |
| Common-cause, inert-talk, and invalid-replay controls are included or limitations state exactly what is absent. | DONE | `ccc/fixtures/`; `docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md`; `ops/DECISIONS.md` (D-028) | A5/A6 limitations remain disclosed. |
| Real-agent labels are not equated with prompted intent without justification. | DONE | `README.md`; `paper/build/submission.md` | Manuscript states prompted intent is not ground truth. |
| Independent worlds, branch repeats, failures, ineligible cases, and abstentions are counted separately. | DONE | `docs/analysis/exp002_heldout_v2/`; `docs/analysis/exp001_dev_v2/`; `docs/review/rev001/REV001.md`; `ops/DECISIONS.md` (D-035) | Holdout has 16/16 worlds, 143 valid executed branches, 56 N not_run, zero failed/invalid; DEV accounting remains separate. |
| Main effects have the appropriate uncertainty and units. | DONE | `docs/analysis/exp002_heldout_v2/effects_study.json`; `paper/build/submission.md`; `docs/review/rev001/REV001.md` | Confirmatory primary null: Delta 1.354 reward units, world-cluster 95% CI [-0.020, 2.834], exact p=0.0703. |
| No model/backend switching, seed hunting, cached duplicate sampling, or hidden post-selection contaminates the reported comparison. | DONE | `docs/review/REV_FREEZE.md`; `docs/review/rev001/REV001.md`; `docs/analysis/exp002_heldout_v2/CORRECTION.md`; `ops/DECISIONS.md` (D-035) | Deviations and label correction disclosed; independent review found no outcome-dependent change. |
| Every headline sentence has a verified evidence chain. | DONE | `docs/review/rev001/CLAIMS_LEDGER.md`; `docs/review/rev001/REV001.md`; `review/reproduce_headline/` | Independent raw reproduction and claim ledger support the narrowed headline. |

## Engineering completion

| Item | Status | Evidence path | Remaining scope |
|---|---|---|---|
| A documented clean setup reproduces the analysis without spending money. | PENDING | `README.md`; `scripts/reproduce_offline.sh`; `ops/reports/codex_runs/REL-004.stdout`; `docs/release/environment.json` | Offline reproduction exited 0 with hash verification; a fresh dependency setup remains unverified. |
| Actual upstream commit, patches, dependency versions, model IDs/digests, and prompts are recorded. | DONE | `docs/release/environment.json`; `docs/runner/exp001_manifest.json`; `docs/runner/exp002_manifest.json`; `docs/stats/stage2/STAGE2_ADDENDUM.md` | Identifiers/provenance are recorded; third-party terms are tracked separately below. |
| Core invariants, corruption tests, and budget barriers pass. | DONE | `docs/release/validation/tests.log`; `docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md`; `ops/reports/codex_runs/REL-004.stdout` | Recorded test suite and scoped Gate A criteria pass; diagnostic limitations remain disclosed. |
| Raw traces and immutable manifests are preserved. | DONE | `docs/runner/archives/exp001-live.tar.gz.sha256`; `docs/runner/archives/exp002-live.tar.gz.sha256`; `docs/release/input_hashes.json`; `ops/pilot_manifest.sha256` | Both run archives have committed SHA-256 sidecars; holdout correction preserves original outputs. |
| Figures, viewer, certificates, and paper agree on the same frozen analysis version. | DONE | `docs/analysis/exp002_heldout_v2/`; `paper/build/submission.md`; `paper/build/submission_validation.json`; `docs/review/rev001/REV001.md` | Embedded figures and manuscript reflect the corrected frozen outputs; no separate viewer release is asserted. |
| Public artifacts are sanitized; secrets and private working-document IDs are not accidentally published. | PENDING | `scripts/secret_scan.sh`; `docs/release/secret_scan.log`; `paper/build/submission_validation.json` | Current repo is private. Scan flagged private Doc IDs in `CCC_MASTER_SPEC.md` and `docs/spec/12_paper_and_drive.md`; sanitize before any public repo release. |
| No unrelated owner changes were overwritten. | DONE | `git status --short`; `ops/reports/REL-005.md` | This audit edits only its two authorized paths; pre-existing REL-005 run logs remain untouched. |
| Commits are coherent and within the owner's cap. | OWNER | `git log`; `ops/DECISIONS.md` (D-026, D-027) | Local main is 36 commits ahead of origin; owner/integration custodian decides history review and pushing latest local commits. |

## Presentation completion

| Item | Status | Evidence path | Remaining scope |
|---|---|---|---|
| The report fits the official template and current event rules. | OWNER | `paper/author_checklist.md`; `paper/build/submission_validation.json` | Owner must confirm official template, current event rules, track, and template-specific choices. |
| Abstract, figures, methods, results, limitations, references, ethics appendix, and LLM disclosure are complete. | PENDING | `paper/build/submission.md`; `paper/build/submission_validation.json` | Sections and six figures exist, but LLM wording/human verification and final dual-use review still require approval. |
| Every final PDF page has been inspected or an explicit visual-review gate remains for the owner. | OWNER | `paper/build/CCC_submission_draft.pdf`; `paper/build/CCC_submission_draft.pdf.sha256`; `paper/author_checklist.md` | Owner page-by-page visual review remains. |
| Template guidance and placeholder authors/results are removed before finalization. | PENDING | `paper/build/submission.md`; `paper/build/submission_validation.json` | Author and affiliation remain `[OWNER]`; owner tags remain for LLM approval, human verification, dual-use review, and public release. |
| The demo is offline-safe and distinguishes constructed fixtures, real observations, and recorded replay. | DONE | `README.md`; `scripts/reproduce_offline.sh`; `docs/release/LICENSES.md` | Reproduction is offline and manuscript distinguishes constructed, DEV, and holdout evidence; no public demo release is claimed. |
| A cold reader can explain the principal finding and its limits. | PENDING | `paper/build/submission.md`; `docs/review/rev001/REV001.md` | Independent scientific review exists; a separate cold-reader comprehension review is not evidenced. |
| Google Doc synchronization is either verified with revision information or honestly marked pending. | PENDING | `paper/author_checklist.md`; `ops/reports/REL-005.md` | Working-copy sync has not been done; writing to Drive is not yet authorized. |

## Operational completion

| Item | Status | Evidence path | Remaining scope |
|---|---|---|---|
| Actual resource usage is reconciled separately from environment task cost. | DONE | `docs/review/rev001/REV001.md`; `docs/analysis/exp002_heldout_v2/cost_throughput.json`; `ops/reports/REL-005.md` | Holdout records 3,516 local calls, $0 API/out-of-pocket; no cloud job or live inference remains running. Project-wide historic usage beyond available ledger is not asserted. |
| New spending remains within the owner's authorization; unknown amounts are not labeled zero. | DONE | `ops/DECISIONS.md` (D-010, D-029); `docs/review/rev001/REV001.md`; `ops/reports/REL-005.md` | Recorded holdout and REL-004 out-of-pocket are $0; no claim that unrecorded historical project costs are zero. |
| All project cloud jobs/endpoints and unnecessary local inference servers are stopped or explicitly handed off. | DONE | `ops/reports/REL-005.md` | Supplied final operational fact: no running jobs; Ollama stopped. |
| No publication/sharing/submission action occurred without authorization. | DONE | `ops/reports/REL-005.md`; `ops/DECISIONS.md` (D-010); repository visibility supplied for this audit | Repo remains private; nothing published or submitted. Any next action needs owner decision. |
| The owner has the exact final artifact paths, repo state, prepared Doc link, and deadline. | PENDING | `paper/build/CCC_submission_draft.pdf`; `paper/author_checklist.md`; `ops/reports/REL-005.md` | Artifact and local repo state are identified; Google Doc link/revision is not recorded and latest local commits are not pushed. Deadline is 2026-10-26 11:59 UTC. |

## Owner decisions required

- author names/affiliations
- LLM-usage statement approval (+ human verification statement)
- dual-use/release review (Appendix A)
- Google Doc working-copy sync (writes not yet authorized)
- public repo release (incl. sanitizing private Doc IDs in two spec docs and unverified Colosseum/poseidon/CoLLAB redistribution terms)
- push of the latest local commits
- final submission to Apart before 2026-10-26 11:59 UTC

## Final director handoff gate

Completed: Gates A/B/C recorded met with narrowing; held-out result is a confirmatory null; no broad collusion-detection claim. Evidence: `ops/DECISIONS.md` (D-028, D-032, D-035), `docs/review/rev001/`, `docs/analysis/exp002_heldout_v2/`, and `review/reproduce_headline/`. Artifacts: draft PDF and checksum, source, run archives, offline reproducer. Verification: independent review/reproduction and REL-004 offline exit 0. Resources: local Ollama run complete and stopped, 3,516 calls, $0 out-of-pocket; `/bin/zsh` used throughout. Owner decisions are listed above. This checklist does not approve publication, sharing, or submission.
