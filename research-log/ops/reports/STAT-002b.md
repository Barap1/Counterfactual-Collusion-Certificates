# STAT-002b handoff

Task: Stage-2 DEV pinning (STAT-001 B3). Status: implementation and offline validation complete; final freeze remains pending. Budget: $0, no network/model calls, no commits. Registry inspected: no STAT-002b lease entry; explicit user assignment and ops/briefs/STAT-002b.md provide scope. Unrelated live-run files left untouched.

Artifacts:
- `ccc/analysis/stage2.py`: DEV-only reader, pooled within-checkpoint complete F/S Omean SD, formula/fallback margins, optional DEV fixture Youden-J calibration, reproducible attainability diagnostic, input/rule/code SHA256 provenance.
- `ccc/analysis/__main__.py`: `pin --input --out` dispatch.
- `tests/analysis/test_stage2.py`: nine tests covering formula/rounding/floor, eligible-world fallback, incomplete outcomes, K/N/C outcome exclusion, held-out rejection including K rows, theta ties/fallback/split enforcement, diagnostic, refusal before writes, pilot reader isolation.
- `docs/stats/stage2/pilot3/stage2.json` and `stage2_addendum.md`: DRAFT, frozen=false, DEV/pilot; not final pinned values.

Validation commands (from repository root):
```
starter/collusion_hackathon/colosseum/.venv/bin/python -m tests.replay.offline_runner -s tests/analysis -t .
starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.analysis pin --input docs/runner/exp001-pilot3 --out docs/stats/stage2/pilot3
```
37 analysis tests passed. Pilot: 1 eligible checkpoint/world, 8 complete F/S observations, pooled df=7, sigma_dev=3.3436508067332933; thin_dev=true; draft m_O=5, delta_W=10, delta_S=5. Theta UNPINNED because no DEV detector-pair dataset was supplied. K/N outcome files and aggregate runner result files are never opened by the legacy reader; an instrumented reader regression checks this.

Limitations / next: prereg §6 specifies A5a positive verbatim/paraphrase pairs and nonredundant A2/A3 negatives. Supply optional `dev_fixture_pairs.json` containing explicit `split`, `family`, `positive`, `left`, `right` records; no automatic selection or fabrication of pairs. Theta uses normalized word 3-shingles, lower-theta tie break and weak-detector fallback. DEV world seed allowlist is 1–5 (archival pilot plus registered 2–5); per-call sampling seeds are not world seeds. Canonical inputs use manifest/checkpoints/worlds/branch_ledger contracts; legacy pilot inputs use branch-local files. Input splits and world seeds are checked before outputs; active experiment roots are refused.

Attainability: 2,000 independent Gaussian F4/K4 draws, PCG64 seed 20261023, effect shifts {0,m,2m,4m}; exact permutation gate probabilities using the frozen cent grid. Zero-effect not-supported frequency is 0.551 on pilot sigma. Full `supported` probabilities cannot be inferred from sigma alone: table assumes other coalition/efficiency/validity gates pass and says so explicitly. Zero simulated frequency is not a proof of mathematical impossibility. Pilot uses F4/S4 rather than target dev F4/S2: all available complete F/S values enter pooled SD as preregistered; the margin formula retains the frozen sqrt(1/2+1/4) multiplier. Finish DEV collection and fixture calibration before an independently reviewed freeze; this tool never writes `docs/stats/stage2_addendum.json`.
