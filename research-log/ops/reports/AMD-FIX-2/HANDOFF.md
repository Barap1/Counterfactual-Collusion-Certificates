# AMD-FIX-2 handoff

Task / Status: complete; Gate A v1.2.1 FAIL retained. Worktree v1.2-impl, HEAD c8e3ad1; no commits. User assignment is authority; no AMD-FIX-2 lease exists in the stale registry.

Fixes: shared extractor recognizes first-person I take; existing I’ll take/taking forms covered through decide(). Singular verified cost now triggers the private-quantity information cap. Replaced the regression expecting that miss. A6_intended_validator is mandatory and cannot be satisfied by unrelated invalidity; any-invalid diagnostic retained. Protocol §8/§9 wording clarification recorded in the report; no protocol, threshold, alias, fixture or prediction edits.

Artifacts: docs/gate_a/v1.2/GATE_A_v1.2.1.md and correction_v1.2.1/ (results JSON gz, all 21 prediction scores, 30 instance scores, deltas and provenance). v1.2 files preserved; old report body hash unchanged under superseded header. Exact commands: commands.md; suite counts and exits: tests.json; inventory: files.txt.

Validation (passed/run): audit 107/110 (3 skips), contract 19/22 (3 skips; file unchanged), runner 65/65, replay 54/58 (4 skips), fixtures 71/71, review 9/9; full 323/333 (7 skips, same 3 missing-pilot-archive errors, zero assertion failures). Artifact verification and git diff --check pass. Fresh 800-cell DEV run: zero runner errors/source changes; no holdout.

Results: integrity F/S 380/380, K 4180/4180, isolation 760/760, A2 80/80. A5 amended 16/68 (legacy 20/120); A6 intended/any 350/360. Supported headline 4/280, all DEV 8/800, constructed 6/30. Constructed matches 30/30, none voided. Scores 16 CONFIRMED / 2 FALSIFIED / 3 UNTESTED: P-IB and N3 explicit change FALSIFIED→CONFIRMED; singular-cost controls 09/10/27/28 corrected.

Limitations: retained A5/A6 failures, DEV-002, absent Tier B/blind labels, skipped contract controls, missing archive files. Budget $0; no live/network/model/Ollama operations or live-checkout writes. Next: independent review; Gate A remains blocked.
