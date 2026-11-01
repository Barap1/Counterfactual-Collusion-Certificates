# AMD-IMP-A2 — core protocol v1.2 handoff

Task: AMD-IMP-A2, branch v1.2-impl, worktree /Users/aarav/Documents/Projects/ApartSprint-wt-v12.
Authority: the user's task assignment; ops/tasks.json has no AMD-IMP-A2 lease entry (registry predates the assignment). No registry or other lease was changed.
Budget: $0; no live inference, Ollama operations, network access, secrets, commits, or main-checkout edits.

## Per-item status and critical review

- **IMP-0: inventory complete; pre-census hash-commit gate FAILED.** At takeover the extractor, alias file, T_chat, A6 map and hash inventory were untracked and both census outputs existed. No pre-census commit exists for these files in this worktree. The predecessor's claimed pre-census write time is unverified. Corrected ops/v12_freeze_hashes.txt and the census narrative; preserved the inherited assertion in AMD-IMP-A-evidence/freeze_inherited.txt. All nine recorded hashes match current file bytes. This cannot retroactively repair preregistration.
- **IMP-1: implemented.** Third-person attribution gives ('layla','t1') for “Layla will be taking T1” by Omar. Shared tuple extraction feeds audit.text and V07; V07 carrier matching now also uses the shared match function and the frozen theta=.8, replacing its inconsistent legacy .5 default. No protocol threshold was changed. Assignment-row syntax (- Name: task), per-world public-task alias bindings, and attribution/claim equivalence are documented in the hash file. Independent contract file was not edited.
- **IMP-2/2b: implemented.** Deterministic rank/length/order selection; N_m runs wherever M* is nonempty through the K mask; every actual N request is checked independently against exactly M* removal and E* preservation. Custom hooks cannot bypass this check; empty, overlapping and nonexistent bundles fail it. M*, hashes, checkpoint ID, surface disclosure, actual arm counts and S flag are written before continuations. Held-out S1 uses the frozen hash parity; unselected S has count zero. Explicit N_v1.1_deprecated execution preserves historical filler tests and cannot silently become N_m.
- **IMP-3: implemented.** Exact C3 veto, V9/V10 inputs, no-placebo co-listing, required wording and exact descriptive K-N interval. Corrected the inherited main estimator's bootstrap to the already-frozen C2 exact grid method. Unselected S is not missing data; partially failed N cannot support. Carrier flags preserve protocol status precedence: they cap would-be not-supported, without independently invalidating a case.
- **IMP-4: all seven fault scenarios pass.** Salient-content-only disruption is explicitly not detected; no broader disruption claim is made.
- **IMP-7: guard and native evidence complete, with a default-mode deviation.** require_fault_exercisable=True hard-fails A6b generation without seed search; assert_a6b_precondition can verify the later native unmasked read actually contains E*. An active fixed-seed native test verifies that read and an intended V3/V05b failure. Default population generation retains the ten inactive cells, as the legacy denominator and r3 P3.3 require, rather than hard-failing every inactive generation. This differs from r3 Change 5's unconditional generation-hard-failure wording; it is disclosed, not silently resolved.

The independent contract suite retains three author-declared skips (assignment syntax, alias format, attribution surface). Supplemental tests cover the first two clarifications; no claim of a fully executed 7/7-positive independent suite is made. No blind labels were collected.

## Census

Counts-only recheck uses the offline runner's audit guard; no branches/effect estimates/CCC statuses are evaluated. Source scripted transcripts are necessary for checkpoint events. The first four-worker recheck completed fx1, then its fx2 pool terminated (BrokenProcessPool); that log is retained. The retry uses one worker and reclaims native source reference cycles between cells. No census rule or template changed.

Both complete parsed JSON outputs exactly equal the inherited outputs (verification.json):
800 instances each, 740 eligible, zero census errors. At ±25%, fx1 has 0/740 available
and every family is 0%; the chatter trigger FIRED. Fx2 has 740/740 and every family is
100%; no repeat trigger. Descriptive ±10% availability is 0/740 then 338/740 (45.68%);
±50% is 0/740 then 740/740. No Tier B availability claim is made. The inherited narrative's “35% at ±10%” was incorrect: its JSON contains 338/740, approximately 45.68%.

## Validation

All tests use starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner from this worktree, with -t . and the requested -s directory.
Exact commands, exit codes and counts: AMD-IMP-A-evidence/tests.json; complete output: individual .log files.
Final results (no test failures in the five requested directories):
| Suite | Run | Passed | Skipped | Errors |
|---|---:|---:|---:|---:|
| audit | 104 | 101 | 3 | 0 |
| runner | 65 | 65 | 0 | 0 |
| replay | 58 | 54 | 4 | 0 |
| fixtures | 71 | 71 | 0 | 0 |
| review | 9 | 9 | 0 | 0 |
| contract | 22 | 19 | 3 | 0 |
| full | 327 | 317 | 7 | 3 |
Full suite exit code 1: exactly the three missing-pilot-archive errors described below;
no assertion failures. The final full run contains the new active-A6b test.
Contract file sha256 is unchanged (d443618db5a24d227f60e7ae20ba2e93c7ec165608724f725c0a833e382274a0).
All seven placebo fault tests pass within audit. git diff --check passes.

The first full run had three errors because this isolated worktree lacks archived pilot files under results/baselines/colosseum_positive_control_seed1* (config.json and final_summary.json). Neither tests nor archive paths were changed to conceal the missing artifacts. Full_initial.log preserves that run.

Reproduction commands:
- python3 ops/reports/AMD-IMP-A-evidence/run_suites.py (records all five requested directories, independent contract, and full tests).
- PYTHONPATH=. starter/collusion_hackathon/colosseum/.venv/bin/python ops/reports/AMD-IMP-A-evidence/recheck_census.py (both censuses; the successful retry used the final argument fx2).
- git diff --check.
- Hash/AST verification is in AMD-IMP-A-evidence/verification.json.

## Integration limits

check_fresh in validators.py is AST-identical to HEAD: no reimplementation of main's client-request-ID V09 fix. The added N checker is separate. Main's V09 change must still be merged by the custodian.

IMP-5 Gate A reporting, IMP-6 constructed controls, IMP-8 protocol assembly, and IMP-9 live-data relabelling/backfill are not this task. gate_a.py still uses its legacy filler control; do not present a v1.2 Gate A verdict from it. The inherited protocol.md and protocol_v1.2.sha256 edits were retained. The independent contract and constructed-control files were preserved.

The inherited dev_manifest.json now points to preserved protocol_v1.1.md to match its existing hash. Tests similarly override only their in-memory EXP-001 copies. exp001_manifest.json was not edited: its protocol.md path/hash mismatch remains an integration concern. Runner N semantics are now v1.2 even for historical manifests; do not resume a v1.1 experiment using this code without explicit version handling.

Files: full worktree change inventory is AMD-IMP-A-evidence/files.txt; it includes inherited edits. Stray docs/runner/tmp* directories were removed after all tests; removed paths are recorded in cleanup.json, with none remaining.
