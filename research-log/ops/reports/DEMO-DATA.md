Task: DEMO-DATA — offline CCC evidence explorer data pack.

Status: Complete. Only assigned new paths written; frozen evidence untouched. No network, inference, experiment reruns, or git mutations.

Artifacts: `demo/build_data.py`; `demo/data/cases.json`; `demo/data/cases/*.json` and `demo/data/full/*.json` (21 cases: 16 EXP-002, five Gate A); `demo/data/study.json`; `demo/data/MANIFEST.json`; `demo/data/TRACE.md`; `tests/test_demo_data.py`.

Validation: Eight tests pass. Exact frozen primary row preserved (Delta 1.354325711018898, CI [-0.01954964911635066, 2.8336288730243204], p 0.0703125, decision not supported). Checks cover reward-derived means/W, world contrasts, certificates, fixture outcomes, validity counts, archive sample hashes/text, manifest hashes and size. Archive SHA256 verified against sidecar. Counts: 143 valid executed + 56 unrun; certificates 0 supported / 11 not_supported / 5 inconclusive. JSON total 4,975,322 bytes. Rebuild verified all 46 artifacts byte-identical.

Commands run from repository root:

```sh
starter/collusion_hackathon/colosseum/.venv/bin/python demo/build_data.py
PYTHONDONTWRITEBYTECODE=1 starter/collusion_hackathon/colosseum/.venv/bin/python -m unittest tests.test_demo_data -v
git status --short -- demo tests/test_demo_data.py ops/reports/DEMO-DATA.md
git diff --stat -- demo tests/test_demo_data.py ops/reports/DEMO-DATA.md
```

Determinism additionally checked using a Python heredoc: SHA256 every generated artifact, invoke the same build command with subprocess.run(check=True), assert identical hashes.

Limitations: Gate A result rows lack full transcripts; unavailable fields are explicit, with persisted detector observations and assignments retained. Fixture selection is illustrative, disclosed per case. Noncommit sensitivity carries the requested original-registered-secondary category while preserving its source descriptive label and documenting MISSION's post-hoc wording. Raw evidence is referenced, not duplicated. No UI QA performed.

Budget: $0 new spend; Codex session; no experimental model/API calls.

Next: UI loads `cases.json`, selected case file, then its `full_text_file`; QA follows `TRACE.md` and `MANIFEST.json`.
