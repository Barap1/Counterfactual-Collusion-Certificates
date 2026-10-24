# REL-001a handoff

Task: reproducibility bundle and release checklist preparation. Status: preparation and scoped offline validation complete; final release is not approved. Authorship: the owner is the sole author; no AI co-author lines.

Repo state at scoped check: `main`, HEAD `3f5f2510abd8a95f12400619a11019410966cd2c`; README modified and release/scripts/report untracked for custodian integration. No task commits.

## Artifacts

- `docs/release/CHECKLIST.md`: all 31 module-17 items, status, evidence and remaining scope.
- `scripts/reproduce_offline.sh`, `scripts/reproduce_offline.py`, `scripts/offline_guard/sitecustomize.py`: one-command DEV reproduction with guarded full-suite discovery, archived-output comparisons and output hashes. The real EXP-002 manifest test is explicitly skipped; this is a scoped exclusion, not a pass.
- `README.md`: overview, scope, map, offline setup/reproduction, provenance and `/bin/zsh` note.
- `scripts/secret_scan.sh`, `scripts/secret_scan.py`: regex and exact-value local `.env` checks, working/generated/staged content, no matched values printed. Local `.env` is read only inside the scanner as explicitly requested.
- `docs/release/PROVENANCE.md`, `environment.json`, `input_hashes.json`, `exp001_dev_input/`, `pilot3_input/`, `pilot_archive/`: original-hash-verified DEV metadata and legacy adapter-test inputs. These new files require integration by the custodian; no commits were made.

## Validation

- Initial run: `docs/release/reproduction.Wjz2qe/tests.log`, interrupted (exit 130). A concurrently present readiness test reads the real EXP-002 design manifest. The run was interrupted after identifying it; execution of that method before interruption was not established. No held-out outcome was inspected. The extra release guard and explicit method skip were then added. Filesystem birth times show the readiness module was created after the first test log; this supports that it was absent at initial discovery, but no complete first-run method inventory was retained. A local attempt to interrupt via `pkill` failed because process listing is unavailable; stdin interrupt succeeded. No inference server was inspected or changed.
- Analysis precheck: `docs/release/analysis_precheck.log` confirms all archived scientific JSON fields remain present and equal. Current code adds eligibility/provenance fields; historical full bytes differ and are not represented as equal. Current repeated byte/hash verification is part of the final driver.
- Guard probes: `docs/release/guard_check.log`, four protected opens and two listings rejected before filesystem access.
- Bundle scan: `docs/release/bundle_secret_scan.log`, zero flagged blobs; final rescan includes generated evidence. Broad public sanitation is separate.
- Final broad scan: 2,681 blobs, four flagged blobs (working/staged copies of `CCC_MASTER_SPEC.md` and `docs/spec/12_paper_and_drive.md`, private Google Doc identifiers only; no exact credential matches). These are outside REL-001a ownership. Broad sanitation remains pending; no identifier values were printed. Evidence: `docs/release/secret_scan.log`.
- Guarded suite: 399 tests in 180.586 seconds, OK with four skips (three author-declared plus one protected-manifest exclusion). Evidence: `docs/release/reproduction.uYYs4R/tests.log`. Gate A regenerated all 800 DEV cells and matched archived decompressed v1.2.2 bytes. The original driver then rejected additive current analysis metadata. The corrected verifier reused that freshly regenerated Gate file and exited 0: Stage-2/theta archived bytes match; every archived scientific analysis field remains equal; all current analysis outputs match a second run byte for byte. Historical differences and 43 output hashes: `docs/release/validation/analysis_compatibility.json`, `verified_hashes.json`. Logs: `verification.log` (success), `regeneration.log` (prior expected comparator failure). The default fresh shell command was not rerun through a second 800-cell generation after this comparator-only correction.
- Shell syntax and Python compile checks passed. `git diff --check` on owned paths passed at preparation time.

## Exact validation commands

```zsh
/bin/zsh scripts/reproduce_offline.sh
# Internally: nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests -t .
PYTHONPATH="$PWD/scripts/offline_guard:$PWD" CCC_STARTER_ROOT="$PWD/starter/collusion_hackathon" PYTHONDONTWRITEBYTECODE=1 nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python scripts/reproduce_offline.py docs/release/reproduction.uYYs4R
/bin/zsh scripts/secret_scan.sh
/bin/zsh scripts/secret_scan.sh --release-only
/bin/zsh -n scripts/reproduce_offline.sh scripts/secret_scan.sh
nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python -m py_compile scripts/reproduce_offline.py scripts/secret_scan.py
git diff --check -- README.md docs/release scripts ops/reports/REL-001a.md
```

Additional read-only commands: scoped `cat`, `sed`, `rg`, `git ls-files`, `git status --short`, `git -C starter/collusion_hackathon rev-parse HEAD`, scoped upstream `git status`, upstream `git remote get-url origin`, `stat`, `du`; local Python metadata/hash/copy and checklist-generation snippets. No network, dependency installation, model/API calls, commits, pushes, resets or cleans. Heavy validation used `nice -n 19`; this host prints `setpriority: Operation not permitted`, so actual priority lowering is not confirmed.

## Limitations / budget / next

Gate A v1.2.2 remains FAIL. Software reproduction cannot clear its scientific acceptance failures. Full raw traces, final held-out statistics, independent final review, PDF/template/visual review, Google Doc synchronization, resource reconciliation and owner submission/publication approval are not completed by this task. The protected live ledger was not read; project-wide usage is unknown to this task, not labelled zero. REL-001a incurred $0 new spend and no inference. The running experiment and its services remain handed off to their controller; nothing was stopped. The registry had no REL-001a entry/lease; the direct user assignment supplied authority. Shared task/control files and unrelated owner changes were not edited.
