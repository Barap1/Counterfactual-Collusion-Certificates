# W2-PROTO wiring and offline evidence

`ccc.exp003.collector` is an additive EXP-003 scheduler adapted from the frozen
collector; frozen runner/replay/infra files are unchanged. `arms.run_branch`
executes PF/PK while native F/K/S/N behavior remains intact. The edit is selected
once and persisted before continuations. Request/response freshness sets span
all six arms, including PF/PK; original arm identity enters call seeds.
Canaries, per-call durable records, request budget, world archives and seals
remain active. The deadline guard rejects requests at the frozen stop.

`ccc.exp003.manifest` validates six-arm manifests, backend local|modal, configured
base_url, paired seed/ID integrity and frozen pair order. `fresh_pairs` creates
the post-freeze stream. `modal_runner` now delegates its run command to the new
collector; legacy global patch installation is retired. Imports do not open a
session or call Modal. Live Modal still uses the existing guarded transport and
billing snapshot; running it requires explicit inference-controller authority.

`export_rows` includes every scheduled slot, even absent/interrupted/source-failed
worlds. Same-seed B1/B2 trajectories share pair_id as analysis world_id. It rejects
multiple attempts. Checkpoint cross-check/model-identity failure invalidates all
checkpoint rows; isolated branch missingness leaves other complete arms usable.
Probe-ineligible PF/PK and unavailable N are not_run with explicit reasons.
Analysis also rejects failed cross-checks defensively and reports status/reason
counts and eligibility. No outcome imputation or pooling with EXP-002.

`storage.py` adds EXP-003 output roots and treats rows.json as a replaceable derived
view; raw artifacts retain exclusive writes, hashes, locks and seals. Temporary
roots support offline tests. Live outputs should use docs/runner/exp003-* when
assigned by ORCH; this worker wrote no files there.

## Reproduction

Use a fresh output directory. Offline entry point (not separately executed by
this worker; the equivalent full collector plus analysis CLI is exercised in tests):

```sh
python -m ccc.exp003.mock --output /tmp/exp003-mock
python -m ccc.exp003.analysis /tmp/exp003-mock/rows.json --continuations 4
```

The mock uses public DEV seed 2, a fake ScriptedClient transport through the real
BudgetGuard, durable collector and native Jira replay. Configuration supplies the
base_url from the existing public development manifest. It never opens a model
connection. Production execution uses:

```sh
python -m ccc.exp003.collector MANIFEST --backend local --live --output OUT
```

For Modal, set --backend modal and use a manifest with the matching backend and
configured endpoint. Credentials come from the existing runtime environment,
never from a manifest or a new hardcoded value. CCC_STARTER_ROOT should be set
to avoid the inherited optional local-path manifest lookup.

Exact final combined validation command executed:

```sh
CCC_STARTER_ROOT="$PWD/starter/collusion_hackathon" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -c 'import sys, site; site.addsitedir("starter/collusion_hackathon/colosseum/.venv/lib/python3.14/site-packages"); from tests.replay.offline_runner import guard; sys.addaudithook(guard); sys.addaudithook(lambda event, args: (_ for _ in ()).throw(PermissionError("W2-PROTO: subprocess forbidden")) if event == "subprocess.Popen" else None); import pytest; raise SystemExit(pytest.main(["-q", "tests/test_exp003_wiring.py", "tests/test_exp003_probe.py", "tests/replay", "--basetemp", "/tmp/W2-PROTO-final", "-p", "no:cacheprovider"]))'
```

Result: 80 passed in 51.21s. A later Modal manifest-entrypoint test passed (1 in
0.70s). After correcting Modal/local evidence-tier labels, the same guarded
command was run with pytest arguments
`["-q", "tests/test_exp003_wiring.py", "--basetemp", "/tmp/W2-PROTO-release", "-p", "no:cacheprovider"]`.
Its result is recorded in the handoff. Earlier failed iterations exposed storage
root restrictions and a check-filter bug; those were corrected. Initial replay
runs inherited `upstream_provenance` read-only Git subprocesses; final commands
block all subprocesses, network/DNS, and secret-file reads. No Git command was
issued directly; no Git mutation, Modal command, or real model call was made.

Durable compact evidence is `ccc/exp003/offline_evidence/rows.json` and
`analysis.json`, copied from `/tmp/W2-PROTO-release/test_mock_full_pipeline0/`.
These are development-only fake-model outputs, not scientific results. Full
sealed mock traces remain under that temporary test directory.

## Freeze and remaining gates

PROTOCOL.md is a candidate under 2,000 words. Its 09:00 UTC stop supersedes the
brief's later stop. FREEZE_candidate.json hashes protocol, EXP-003 implementation,
CCC dependency source, tests, public configuration and native Jira/Colosseum source.
It is not an approval or a freeze commit. Refresh hashes after any edits.
Installed external dependencies beyond the native source inventory are not a
hermetic lockfile and still require runtime identity/version attestation.

ORCH must arrange independent review, approve directional hypotheses and
first-k-complete semantics, audit/hash the exclusion inventory, choose M or L,
and establish a feasible capped request/container budget before committing the
freeze. The live manifest must carry the actual director freeze commit and
freeze/exclusion hashes. These values are required fields, not independently
verified approval signatures. The external inference controller owns GPU lifetime,
projected cost admission, in-flight cancellation, ledger and teardown; this
worker did not test those cloud operations. A cap prevents new requests but
cannot alone terminate an already running remote GPU container.

W2-PROTO was directly assigned by the user; ops/tasks.json was checked and has
RA-LEAD ownership but no W2-PROTO lease. Registry updates remain with ORCH.

## W2-FIX release controls (supersedes the controller delegation above)

`modal_ctl.start` reserves cost before daemon creation, including CPU/memory/GPU,
20% margin, startup wall time, full active lifetime, 120-second shutdown reserve,
legacy finalized runs and explicit `--storage-usd` unledgered cumulative liability.
Use `--development` only for the assigned GPU spike; a held-out start requires
`--manifest MANIFEST` and final freeze validation. `budget.total_estimated` includes
active reservations. The independent one-second Lifetime watchdog accrues cost,
checks both fixed monetary caps, issues remote app stop and verifies stopped/absent
app state even during a blocking cold-start request. SIGALRM interrupts the main
thread at the absolute deadline; the GPU's boot timer kills the server and Ollama
at that same deadline. The deadline reserves teardown time before 09:00 UTC.
CPU identity/prefetch actions also reserve and use the watchdog. Accounting or
teardown failure retains liability and blocks another launch. Latest per-session
`modal_session` events use `ccc.budget_ledger.v1` with backend/task, session ID,
rate, seconds-derived accrued estimate, reservation, timestamp and teardown state;
readers must use the latest event per session, not sum snapshots. No live ledger
was modified by this worker. Cloud/CLI teardown behavior needs ORCH's GPU spike.

ORCH creates `docs/enh/exp003/FREEZE.json`; this worker creates none. Required
fields: approved=true, pending=[], actual director_freeze_commit, backend,
protocol_artifact/protocol_sha256, refreshed code_sha256/evidence_sha256,
manifest_config_sha256 (canonical digest of manifest excluding freeze_sha256),
max_requests and pair_order (the exact fresh_pairs(commit, exclusions, 32) worlds).
The code inventory must retain all reviewed candidate dependencies and every
current EXP-003 Python module. The manifest's freeze_sha256 hashes final FREEZE
bytes. For seed_exclusion, skip_ledger and seed_list, supply *_artifact and
*_sha256 fields in FREEZE and matching *_sha256 in the manifest. Artifact formats
are JSON: unique integer exclusions; rejected stream counters {counter, seed,
reason=excluded|duplicate}; accepted seeds in pair order. No placeholder hashes
or commits pass. Commit authenticity and runtime identity remain ORCH attestations;
this offline check does not execute Git or prove a commit exists in a remote repo.

`feasibility_budget` requires measured_dev_valid=true, calls_per_regime_world
(including source), canary_calls_per_regime_world, startup_calls,
gpu_seconds_per_regime_world, projected_total_usd, projected_total_seconds,
reconciled_prior_usd and storage_usd. These are measured inputs for ORCH, never
inferred from affordability. The frozen request cap must cover all 64
regime-worlds plus canaries and startup calls. Cost projection plus prior/storage
must fit $45. ORCH must verify completion time against the remaining deadline.
Offline admission: `python -m ccc.exp003.freeze MANIFEST`; failure occurs before
collector source calls and before held-out server launch. Collector archives
freeze.json, manifest.json and plan.json as immutable envelopes.

Prospective analysis reads sibling sealed raw attempts and manifest, rechecks the
freeze and compares rows.json with a fresh raw export. `slots.validate_slots`
retains all 32 scheduled pairs, checks first attempts and a contiguous prefix,
and reports administrative k including the terminal partial/failed pair. F/K
and F/PF sample sizes stay separate. Fewer than 16 complete pairs per estimand or
other continuation counts reject confirmatory mode. `--exploratory` explicitly
labels subfloor outputs feasibility/descriptive with reasons and no confirmatory
eligibility. Development fixtures retain flexible counts.

## W2-FIX validation evidence

Changed implementation paths: ccc/exp003/budget.py, modal_ctl.py, modal_server.py,
modal_runner.py, manifest.py, collector.py, analysis.py; new freeze.py and slots.py
(all under ccc/exp003/). New adversarial tests: tests/test_exp003_controls.py.
Protocol hypotheses, thresholds, seed algorithm, scheduled 32-pair target, minimum
16 and four-continuation requirement are preserved; EXP-002's quoted result is
byte-identical. Existing test files were not edited.

Final light-test command (no replay suite, model calls, Modal commands or Git):

```sh
CCC_STARTER_ROOT="$PWD/starter/collusion_hackathon" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -B -c 'import sys,site; site.addsitedir("starter/collusion_hackathon/colosseum/.venv/lib/python3.14/site-packages"); from tests.replay.offline_runner import guard; sys.addaudithook(guard); sys.addaudithook(lambda e,a: (_ for _ in ()).throw(PermissionError("W2-FIX subprocess forbidden")) if e=="subprocess.Popen" else None); import pytest; raise SystemExit(pytest.main(["-q","tests/test_exp003_controls.py","tests/test_exp003_probe.py","tests/test_exp003_wiring.py","--basetemp","/tmp/W2-FIX-handoff","-p","no:cacheprovider"]))' > ccc/exp003/offline_evidence/W2_FIX_validation.txt
```

The placeholder dry-run is test_freeze_placeholder_dry_run_refusal: it invokes the
admission checker with a differently named synthetic JSON fixture, refusing both
an unverified hash and an unverified director commit. No FREEZE.json is created,
no accepted held-out stream or outcomes are generated by that dry-run. Other
tests challenge code/seed hashes, pair order, retry/replacement, sample floor,
active liabilities, both caps, timer shutdown callbacks during simulated blocked
cold start, deadline and unknown teardown schemas. Development full collector
coverage uses scripted native replay. Final stdout is preserved in
ccc/exp003/offline_evidence/W2_FIX_validation.txt. The refreshed changed-file hash
inventory is W2_FIX_hashes.json in that directory; ORCH must refresh the full
candidate/final dependency inventory after integration. No freeze approval is
implied by these fixes. The registry lists RA-LEAD ownership, no W2-FIX lease;
this direct user assignment supplies path ownership; registry remains untouched.
