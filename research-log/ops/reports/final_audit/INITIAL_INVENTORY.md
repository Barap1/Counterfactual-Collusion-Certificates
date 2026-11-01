# Initial audit inventory — 2026-10-25

Baseline HEAD `4811eaf24b3bdc9e73bb96c1cbf3cf7288c429ac`; branch `codex/final-submission-audit`. Tracked tree was clean. Untracked historical codex_runs logs preserved. Second worktree v1.2-impl exists; no modification planned. Process inspection initially sandbox-blocked, then executed with escalation; no experiment controller found in inspected listing; durable scoped reconciliation pending.

| ID | Severity | State | Evidence and next check |
|---|---|---|---|
| PDF-01 | P0 | confirmed | paper/v2/build/FIX-EPS-validation.json `pdf_current=false`; rebuild then hash provenance |
| PDF-02 | P0 | confirmed | paper/v2/make_v2.py removes G. Figure plan; source has H. Figure plan; Fig3 targets 5.1 rather than 5.4 |
| TEMPLATE-01 | P0 | unverified | Current official Guidelines require linked template; copy link redirects web fetch to sign-in; inspect read-only export/browser |
| PROV-01 | P1 | confirmed | REV_R3 corrections not fully propagated in PARALLEL_EXECUTION.md; reconcile raw receipts |
| DEMO-01 | P1 | confirmed | bundle_data reads stale manifest because documented order bundles before build_data |
| SCI-01 | P1 | resolved in latest text; verify | D-048 post-hoc restriction + all aggregate failures + EXP003 not completed already in latest manuscript |
| SEC-01 | P1 | current public confirmed; history unverified | GitHub connector visibility=public; historical private Doc references need safe path/count scan |
| REL-01 | P1 | confirmed | tasks registry stale RUNNING entries; README license and release status need reconciliation |
| TEST-01 | P1 | unverified | Historical 399/4 record is not current discovery; run offline environment/stdlib independent reproduction |

Frozen file SHA-256 baseline: frozen_before.json (16992 files). Original paper sources and build artifacts preserved under paper/original/. No scientific data or outcomes changed.
