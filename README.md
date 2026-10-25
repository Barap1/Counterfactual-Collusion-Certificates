# Counterfactual Collusion Certificates (CCC)

CCC studies what replay evidence can support a scoped claim of communication-dependent harmful coordination, and when an auditor should abstain. It combines synthetic Jira task worlds, replay validity checks, message interventions, baseline auditors, and world-level offline analysis. It is a contribution to evidence standards for attributing harm to AI-agent communication, not a collusion detector.

## Quick check: reproduce the headline (no install, no network)

Needs only Python 3 (standard library). From the repository root; the final command prints JSON including Delta and p:

```sh
ccc_extract=$(mktemp -d)
tar -xzf docs/runner/archives/exp002-live.tar.gz -C "$ccc_extract"
shasum -a 256 -c docs/runner/archives/exp002-live.tar.gz.sha256
python3 -I review/reproduce_headline/independent.py --input "$ccc_extract/exp002-live"
```

Expected (all values in this sentence: original-confirmatory): `Delta` = 1.3543257..., `sign_flip` = 18/256 (p = 0.0703125), 8 defined pairs, 7 non-zero. This was verified with system `/usr/bin/python3` in an isolated temporary directory containing only the tracked script and archive inputs, with no packages installed. The program imports no `ccc` module and makes no model or network calls.

## Prospective headline: deterministic stratum only (D-048)

The established new-prospective result is **eps=0**: symmetry and frontier checks pass by construction; the knockout baseline accuses legitimate allocation and authorized-transfer members in 200/200 pairs each, while P6 is 0/200 and benign cooperation 0/100. RQ3/RQ4/RQ5 fail at eps=0; DEV-informed RQ4b passes; RQ6 is descriptive. These are scoped scripted-generator results, not validated collusion detection.

**Pre-registered aggregate verdicts:** RQ1: **pass** — T2; RQ2: **pass** — T3; RQ3: **fail** — T4; RQ4: **fail** — T5; RQ4b: **fail** — T5b; RQ5: **fail** — T8; RQ6: **descriptive** — RQ6. Four aggregate predictions failed.

**eps=0.1 is platform-dependent, not established.** D-048 restricted established claims to eps=0 after outcomes were visible (post hoc). Across available shared units, eps=0 is byte-identical on 149/149; eps=0.1 differs on 142/148, with method-output differences on 1160/1452 records (descriptive archive audit). No claim rests on noisy results, and macOS noisy DEV is not comparable with Linux noisy prospective results. See [full stratum results](docs/enh/r2/RESULTS_BY_STRATUM.md) and [exact platform counts](docs/enh/r2/PLATFORM_DIVERGENCE.md). EXP-003 was not completed; no result is claimed.

## Headline result (held-out, confirmatory null)

Held-out EXP-002 (protocol v1.2, local `gemma4:26b`, $0 API spend) is complete. The preregistered directional hypothesis (deceptive-collusion prompts raise the outsider-harm effect above authorized cooperation) is **not supported**:

- Delta = 1.354 reward units, world-cluster 95% CI [-0.020, 2.834], exact one-sided sign-flip p = 0.0703. The independent sample is **8 matched world pairs**.
- Registered non-commit sensitivity (preregistered secondary analysis): 0.727, CI [-0.31, 1.91]; its sign-flip p = 0.156 was added post hoc.
- Accounting (descriptive): 16/16 trajectory attempts completed. 199 scheduled branch records = 143 executed valid continuations + 56 unrun placebo (N) branches (`not_run: no_placebo_available`). 0 failed, 0 invalid.
- Exploratory case-level certificates over 16 checkpoints: 0 supported / 11 not supported / 5 inconclusive. A "not supported" verdict is not exoneration.
- Power is limited: MDE_80 about 2.2 reward units (descriptive), against an observed 1.35 (original-confirmatory).

Evidence labels: the held-out primary and the Holm S1–S3 family are original-confirmatory (none passed); the 0.727 estimate is a registered sensitivity; case-level certificates are exploratory by preregistration. DEV Gate A fixtures and EXP-001 DEV data are development evidence only and support no performance claim.

Certificate validity metadata was repaired in `docs/analysis/exp002_heldout_v3/` (see `CORRECTION.md`), with no certificate status or numeric change.

Frozen outputs: `docs/analysis/exp002_heldout_v2/` (corrected labels, see `CORRECTION.md`), `docs/review/rev001/` (independent review and claims ledger), `ops/CLAIMS.md` (claims index).

## DEV Gate A (development evidence)

DEV Gate A v1.2.2: the preregistered gate criteria (factual/sham identity, knockout scope, branch isolation, no `supported` on benign cooperation) pass on scripted fixtures; two stricter diagnostic checks fail and are reported as limitations (A5 redundancy 20/120, so `not supported` is not exoneration; ten non-exercisable A6b faults). Scripted fixtures are not independent real-agent observations; prompted intent is not ground truth.

## Repository map

- `ccc/replay/`, `ccc/audit/`, `ccc/fixtures/`, `ccc/baselines/`: replay, auditing, synthetic controls and comparators.
- `ccc/analysis/`: offline estimators, failure accounting and Stage-2 diagnostics.
- `ccc/runner/`, `ccc/infra/`: collection infrastructure; reproduction never invokes live collection.
- `tests/`: offline unit, corruption, integration and budget-barrier checks.
- `docs/analysis/exp002_heldout_v2/`: held-out analysis (frozen). `docs/analysis/exp001_dev*/`, `docs/stats/stage2/`: DEV analysis and pinning provenance.
- `docs/runner/archives/`: held-out and DEV raw-trace archives with SHA-256 sidecars.
- `review/reproduce_headline/`: stdlib-only independent reproduction of the headline.
- `docs/gate_a/v1.2/correction_v1.2.2/`: DEV gate evidence, including failures.
- `figures/`, `viewer/`, `paper/`: figures, offline evidence viewer, manuscript and draft PDF (final owner review pending).
- `docs/release/`, `scripts/`: metadata bundle, release checklist, licenses, offline reproduction.

## Full offline reproduction (needs the starter environment)

Use `/bin/zsh`. The script runs heavy work with `nice -n 19`, sets `CCC_STARTER_ROOT`, installs no packages, makes no model calls and reads no credentials. A host may deny lowering priority (`setpriority: Operation not permitted`); this is recorded, not hidden.

Prerequisites (the full path needs numpy/scipy and the third-party starter; a fresh install is not demonstrated):

1. Place the upstream `poseidon-research/collusion_hackathon` checkout at `starter/collusion_hackathon`, commit `d585a7b3be50366cc2bdf5789bf8add5890b2abd`, including `colosseum/external/CoLLAB`. It is not redistributed here (see `docs/release/LICENSES.md`; its license terms are unverified).
2. In `starter/collusion_hackathon/colosseum`, prepare `.venv` with the locked setup (`uv sync --locked --offline` with a populated cache). Do not run upstream live preflight/experiments or source `compute.env`. Versions and hashes: `docs/release/environment.json`.
3. In a clean checkout only, restore the archived pilot:

   ```zsh
   mkdir -p results
   cp -R docs/release/pilot_archive results/baselines
   cp -R docs/release/pilot3_input docs/runner/exp001-pilot3
   ```

Then:

```zsh
/bin/zsh scripts/reproduce_offline.sh
```

Without step 1-2 the script stops with "Complete README starter setup first". It writes a gitignored `docs/release/reproduction.*` directory with the test log, regenerated Gate A, DEV analysis, Stage-2 draft and verified hashes. The recorded run passed 399 tests. A readiness test that reads the real EXP-002 manifest is skipped under the held-out access guard. The held-out result is reproduced by the quick check above, not by this script.

## Secret scan

```zsh
/bin/zsh scripts/secret_scan.sh
```

Checks regex patterns and local `.env` values without printing them, over tracked files, staged blobs and release artifacts. It does not scan history or `ops/budget_ledger.jsonl`, and flags Doc URLs plus quoted, `/d/`, and known-format bare 44-character Drive-style IDs. Staged blobs can retain findings until the redactions are staged. A scan is not publication approval.

## Data provenance and licenses

The seed-1 pilot is development data only (`docs/release/pilot_archive/`, 27 files listed in `ops/pilot_manifest.sha256`). EXP-001 is DEV; `docs/release/exp001_dev_input/` is a metadata subset, not the full raw trace archive. Third-party terms, including unverified Colosseum/poseidon-compute/CoLLAB licenses, are in `docs/release/LICENSES.md`; Terrarium is MIT. CCC's own license has not been chosen by the owner.

## Release status

Science is frozen. Pending owner decisions: author/affiliation, LLM-usage statement, dual-use review, template and page-by-page PDF review, Google Doc sync, push of latest commits, and submission: [release checklist](docs/release/CHECKLIST.md).

Authorship: the owner is the sole author.

## Enhancement work in progress

See [docs/enh/](docs/enh/) for ongoing enhancement work; a later task will finalize this presentation.

## License

Original CCC code: MIT (`LICENSE`). Third-party material (Colosseum starter, model, dependencies) is not covered; see `NOTICE.md`.
