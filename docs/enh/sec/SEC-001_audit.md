# SEC-001 release-safety and reproducibility audit

Audit only. Date 2026-10-24. Repo HEAD c7dbdae (clean clone tested). No secret values, Doc IDs or .env contents are reproduced; strings appear as first 4 chars + length. Other workers have uncommitted edits in the live tree; this audit used tracked content and a clean clone.

## Verified facts

- GitHub (read-only `gh repo view`): `visibility PUBLIC`, `isPrivate false`, `pushedAt 2026-10-24T12:22:12Z`, default branch `main`. Confirms D-036: the repo is public now.
- `git log origin/main..main`: 3 unpushed commits (c7dbdae, 33f2845, b89093e). ops/STATUS.md:14 says "1 unpushed plus handoff"; CHECKLIST.md:34 says "36 ahead". Both stale. origin has 58 commits; 166 commits across all refs; the extra ones are local backup branches only.
- `scripts/secret_scan.sh` (read first; it prints only paths and rule numbers): 3447 blobs, 4 flagged = CCC_MASTER_SPEC.md and docs/spec/12_paper_and_drive.md (working and staged), rule 6 (Doc link), no exact-credential match.
- My own regex over tracked tree and every commit on all refs (sk-, sk-or-, ghp_, github_pat_, hf_, AKIA, xox, AIza, PEM headers, `Bearer <token>`, key=value assignments): **0 hits**. No .env, compute.env or *.local.json ever tracked (history path check). Both run archives (exp001/exp002 tar.gz, scanned in stream): 0 key/email/Doc hits; 9 `/Users/aarav` paths in exp001, 0 in exp002.

## P0

**P0-1. Repo is PUBLIC; project records disagree.** docs/release/CHECKLIST.md:3 ("repo remains private"), :32 ("Current repo is private"), :55 ("Repo remains private; nothing published") are false today. The "no unauthorized publication" row (:55) is marked DONE and should be OWNER/PENDING. Cause of the visibility change is unknown (D-036 says the director made none). Fix: after the owner decides visibility, update those three lines to the observed state.

**P0-2. Three private Google Doc IDs are in the public tree and public history** (all 44 chars):
| ID | Tracked locations (file:line) | Commits (on origin) |
|---|---|---|
| `16N0...` | CCC_MASTER_SPEC.md:1330,1331; docs/spec/12_paper_and_drive.md:16,17 | 636ff20 |
| `1zsY...` | CCC_MASTER_SPEC.md:1338,1339; docs/spec/12_paper_and_drive.md:24,25; ops/reports/PUB-001_early.md:11 | 5bb2972, 636ff20 |
| `1Y5w...` | ops/reports/PUB-001_early.md:11 (full); paper/author_checklist.md:35 and paper/outline.md:4 (8-char prefix only) | 5bb2972 |

Local-only equivalents (not pushed): 0c0ffec, 0ae772a on backup/pre-squash and v1.2-impl. The gitignored ops/doc_target.local.json also holds an ID (correctly untracked). The scanner misses PUB-001_early.md and paper/* because its rule only matches `docs.google.com` URLs.
Real exposure depends on each Doc's sharing setting (not checked; out of scope).

## P1

**P1-1. Third-party terms unresolved for redistribution.** Details in the license table below. Colosseum, poseidon-compute and CoLLAB have no license; CCC code adapts them (ccc/replay/world.py subclasses and mirrors `_run_single`; patches/ENG-003_optional_registry.patch contains 4 upstream lines). CCC itself has no top-level LICENSE file, so the repo is all-rights-reserved by default. Fix: owner picks a license for CCC; add NOTICE with Terrarium MIT text if any copied portion ships; ask upstream owners for terms, or ship adapters as "requires user-supplied starter".

**P1-2. Owner personal data in public metadata.** Owner iCloud address (`aar...`, 24 chars) is author and committer on all 166 commits and appears in text at ops/RESUME.md:8, ops/reports/BOOT-001.md:21, ops/reports/PUB-001_early.md:12. PUB-001_early.md:12 also holds a second personal address (`kam...`, 23 chars; a third party, not identified here). Local path `/Users/aarav` appears 1434 times in 133 tracked files (largest: review/reproduce_headline/exp002_independent.json 408, synthetic_independent.json 212, docs/eng/ENG-003_full_*.txt). Paths are low risk but reveal the OS username.

**P1-3. README is stale and contradicts frozen evidence** (item list below; corrected full text in README_proposed.md). It is the public front page.

**P1-4. Clean checkout cannot run the documented path** (details below). The simple stdlib headline reproduction works.

## P2

- Co-Authored-By trailers: 48 on origin/main (36 Claude Opus 5.5, 12 Codex) despite D-027/D-036 ("trailers removed"). The D-036 squash covered only the 39 commits then unpushed; the 38 pushed under D-026 keep them. CHECKLIST.md:3 acknowledges this. CLAUDE.md memory says owner is sole author.
- ops/CLAIMS.md has 143 and 0 failed (C-H06) but not 199 or 56; add one row. It also says "reproduced twice" (fine).
- Figures: fig_heldout_delta.svg:39,40 show rounded 1.35 / p = 0.070 (consistent).
- Scanner gaps: excludes docs/runner/exp002-*, runs/exp002, ops/budget_ledger.jsonl, history; Doc-link rule too narrow; reads .env internally (fine).
- Fonts: figures name DejaVu Sans/Arial only; no font files shipped.

## Third-party licenses (item 4)

Nothing from starter/ is tracked (`git ls-files starter` = 0; gitignored). No JS libraries, CDN links or font files in tracked HTML (viewer/assets/template.html and paper/build/*.html have 0 external src/href; viewer CSP blocks network).
| Item | Upstream | License found | Redistribute here? | Notice needed |
|---|---|---|---|---|
| colosseum 0.1.0 | poseidon-research/collusion_hackathon @ d585a7b3 | none in tree or METADATA | Not allowed to assume; do not ship source | none known; get terms |
| poseidon-compute 0.1.0 (util/) | same | none | same | same |
| CoLLAB (colosseum/external) | upstream unverified | none found | same | same |
| terrarium-agents 0.1.1 | Mason Nakamura | MIT (LICENSE read) | Yes | keep copyright + permission text for copied parts |
| gemma4:26b weights | Google via Ollama | Apache-2.0 (per LICENSES.md; not re-verified) | weights not shipped; model outputs in archives | cite model + license |
| Python deps (numpy, scipy etc.) | PyPI | listed in LICENSES.md (permissive, scipy bundles LGPL libquadmath) | not shipped | none (not vendored) |
| Colosseum-derived scenario text/outputs in pilot_archive (600K) and run archives (37M) | derived from unlicensed starter | UNKNOWN | Treat as risk until upstream replies | disclose provenance |
Unknown terms: Colosseum, poseidon-compute, CoLLAB, and derived scenario/trace data.

## README vs final evidence (item 5)

Stale or inconsistent lines in README.md:
- :5 "No held-out finding ... is made here" (false: held-out is complete, confirmatory null).
- :56 "EXP-002 held-out collection is running/pending ... data and outcomes were not inspected" (false; no ongoing run; Delta 1.354, CI [-0.020, 2.834], p 0.0703, 8 pairs).
- :56 "Final results, resource reconciliation, independent claim audit ... pending" (independent review rev001 done; $0 reconciled).
- Absent entirely: 199 = 143 executed valid + 56 unrun N, 0 failed/invalid, 0/11/5 certificates, $0, post-hoc 0.727.
- :40 and :56 imply held-out is excluded from reproduction without pointing to `review/reproduce_headline/`.
- Repo map (:9-16) omits docs/analysis/exp002_heldout_v2, docs/review/rev001, review/, figures/, viewer/, docs/runner/archives, ops/CLAIMS.md.
- No mention of license of CCC or public-release status.
Proposed text: docs/enh/sec/README_proposed.md.

## Reproducibility in a clean clone (item 6)

Clone: `git clone --local --no-hardlinks` to /Users/aarav/.claude/jobs/ea6cad75/tmp/sec001_clone, no network.
- FAILS: `scripts/reproduce_offline.sh` stops immediately with "Complete README starter setup first" (starter/ absent, gitignored, needs the unlicensed upstream checkout and its uv-locked .venv). `scripts/secret_scan.sh` also fails (needs that venv python).
- FAILS: system Python 3.14.7 (conda, homebrew, /usr/bin) has no numpy or scipy; ccc/analysis/{statistics,pinning,shift_perm,stage2,pipeline}.py and tests/analysis need them. I installed nothing.
- Not run: pilot restore; full 399-test suite.
- WORKS (stdlib only, ~seconds): extract tracked docs/runner/archives/exp002-live.tar.gz (sha256 sidecar OK), run `python3 -I review/reproduce_headline/independent.py --input <extract>/exp002-live`. Output: Delta 1.354325711, sign_flip 18/256 = 0.0703125, 8 defined pairs, 7 nonzero; byte-equal Delta and sign_flip to committed review/reproduce_headline/exp002_independent.json. Its 11 unit tests pass.
- Absolute paths: ccc/paths.py defaults to a repo-relative starter path (env CCC_STARTER_ROOT overrides); not exercised beyond that.
Simplest viable path: (a) the stdlib quick check above as the primary documented reproduction; (b) for full analysis, `python3 -m venv .venv && pip install numpy==2.2.6 scipy` (versions from docs/release/environment.json; needs network, owner must approve) and a separate documented "bring your own starter" step; (c) add a `scripts/reproduce_headline.sh` wrapping (a) (not created here).

## Consistency (item 7)

Counts are consistent in paper/build/submission.md (lines 9, 65, 83, 91), docs/review/rev001/CLAIMS_LEDGER.md (C2, C20, C30) and ops/CLAIMS.md (C-H01, C-H04, C-H06). Mismatches: README.md has none of them (P1-3); ops/CLAIMS.md lacks 199/56; no figure states a count; certificates are written in prose, not "0/11/5". No numeric disagreement found.

## Remediation plan (not executed)

Current-tree scrub patch list: replace IDs with `<DOC_ID_REDACTED>` at CCC_MASTER_SPEC.md:1330,1331,1338,1339; docs/spec/12_paper_and_drive.md:16,17,24,25; ops/reports/PUB-001_early.md:11; truncate prefixes in paper/author_checklist.md:35 and paper/outline.md:4; replace emails at ops/RESUME.md:8, ops/reports/BOOT-001.md:21, ops/reports/PUB-001_early.md:12; fix CHECKLIST.md:3,32,34,55 and STATUS.md:14; swap README; extend secret_scan rule 6 to any 40+ char base64url token near "Doc"/"Drive".

History-rewrite option: `git filter-repo` (or commit-tree like D-026/D-036) replacing the 3 IDs and the iCloud address (mailmap to a noreply address) and dropping the 48 trailers, then force-push main. Consequences: all 58 origin SHAs change; D-036 and other records citing SHAs break; the rewrite does not retract anything already fetched, cached or forked while the repo was public (since 12:22Z); backup branches keep old data locally; clones need re-fetch. A cleaner variant is a new empty repo with one scrubbed squash commit.
Mitigation that does not depend on history: confirm the three Docs are restricted (not link-shared); if any is link-shared, restrict it or copy to a new Doc and update ops/doc_target.local.json.

## Requires owner permission

1. Make the repo private again (or leave public after scrub). 2. Force-push a rewritten history or create a new repo. 3. Check and change Google Doc sharing. 4. Choose a license for CCC and contact upstream (poseidon-research) for terms. 5. Approve README replacement and the scrub edits (tracked files outside docs/enh/sec). 6. Approve pip/network to build a venv. 7. Push 3 local commits. 8. Decide on committer email and whether to strip co-author trailers from pushed history.
