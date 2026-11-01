# Repository overhaul inventory

Baseline public main: `4811eaf24b3bdc9e73bb96c1cbf3cf7288c429ac`. Latest accessible unpublished source: `0f551555` (publication), descended from `253d4598` (audit). These two branches were inspected; selected source/evidence improvements were consolidated without uploading their submission PDFs or native template exports. A local recovery bundle at `/private/tmp/ccc-repository-overhaul/pre-overhaul.bundle` preserves local refs before cleanup. It is not a public tag or privacy mechanism for already-public history.

## Area decisions

| Area | Classification and disposition |
| --- | --- |
| Root README | Essential; completely rewritten from a new editorial outline |
| `ccc/`, `tests/`, `scripts/` | Essential code; preserve, add maintained guarded test runner and public-file checks |
| `demo/` | Essential offline explorer and source pack; preserve lineage and verify interaction |
| `docs/analysis/exp002_heldout_v3/`, `docs/stats/`, raw archives | Essential corrected real-agent results, freezes, raw inputs; unchanged |
| `docs/enh/r2/run_par/`, freeze, platform audit | Essential constructed evidence and failed predictions; unchanged scientific records |
| Older analysis, gate fixtures, serial partial run, stopped EXP-003 | Supporting provenance; retain stable paths and identify in evidence guide |
| `docs/research/`, `docs/review/`, `docs/eng/`, `docs/inf/`, `docs/spec/` | Supporting methods/source/engineering history; retain, remove from primary reading path |
| `figures/`, `paper/final/figures/` | Scientific figure sources and values; retain editable SVGs and provenance |
| `docs/assets/` | Essential new original README SVGs, authoring script and evidence map |
| `paper/final/manuscript.md`, ledgers, `paper/v2/references_v2.bib` | Canonical accessible manuscript and bibliography; preserve body, update owner-selected title only |
| `paper/build/`, `paper/v2/build/` | Obsolete generated submissions/HTML/previews; remove current-tree copies, retain source and public baseline history |
| Unpublished final PDF/DOCX, render QA and template exports | Excluded; never copied into consolidation patch or uploaded |
| Duplicate banners, evidence-flow variants, publication pitch/handoff files | Obsolete presentation material; remove redundant current versions |
| `review/` | Essential independent arithmetic plus supporting independent audits; retain |
| `viewer/` | Supporting legacy builder; maintained entry is `demo/explorer/` |
| `ops/` | Supporting coordination, claims and audit receipts; current task status reconciled, historical reports labeled by location/date |
| Launch/package/master files formerly at root | Supporting historical input; move to `docs/archive/planning/` without reading master contents |
| `patches/` | Supporting optional upstream integration proposals; retain with notice |
| `LICENSE`, `NOTICE.md`, font license | Essential terms and unresolved third-party rights; preserve |
| Ignored environments, credentials, local manifests, worker logs | Local-only; never read secrets, publish or add missing private pilot traces |

`tree_before.json.gz` inventories tracked paths/sizes. `cleanup.json` lists presentation removals and root moves. `../final_audit/frozen_before.json` snapshots the prior audit's 16,992 protected records for final byte comparison. Scientific output paths are retained to avoid breaking hashes and reproducibility for cosmetic reasons.

## GitHub inventory

Two remote branches (`main`, `cursor/cloud-agent-env-235e`), one open PR (#1), no issues or milestones, no existing Actions runs, main unprotected at initial inspection. PR #1 only adds Cloud Agent setup notes. Its useful pinned starter and missing-input caveat are consolidated in `docs/REPRODUCING.md`; close as superseded after publication, then delete its ref only after confirming no other unique files. Never treat unresolved permissions/privacy as a completed issue.

Local backup branches retain historical research states. `v1.2-impl` is in another worktree and is left intact. Existing local logs are left untouched and excluded from staging. No force push or public history rewrite.
