# Tier-B placebo availability census, EXP-001 DEV checkpoints (counts only)

No continuation, outcome, effect or status was computed or read. DEV data only; the script refuses non-dev worlds. Script: `docs/research/sci002/placebo_census_tierB_dev.py` (reads `checkpoint.json`, `checkpoint_state.json`, `source/snapshots/*` per world under `docs/runner/exp001-live/worlds/`, real gemma4:26b trajectories; event rows built exactly as `ccc.replay.engine.event_rows`; the selector is `ccc.audit.placebo.select_placebo` unchanged, window w = 0.25, `Extractor(world_aliases(tasks), outsiders)` as in `ccc/runner/collector.py`).

## Freeze-hash check (`ops/v12_freeze_hashes.txt`)
- OK (unchanged bytes): `commitment_aliases.json`, `chatter_templates.json`, `a6_validator_map.json`, `blind_labels.md`, `test_commitments_contract.py`, `constructed_controls.json/.md/.sha256`.
- **MISMATCH: `ccc/audit/commitments.py`.** The file lists 5527650c...; current bytes hash to 7b8da4f0.... It was changed by 2 lines (2 insertions/2 deletions) in commit 07ca10f (v1.2.1 correction), and the hash file was not updated. So the census used the current v1.2.1 extractor, not the byte-identical v1.2 file. The v1.2.1 change targeted information-cap bypasses; I re-ran the census with the previous commitments.py (git 6ba9c6a, the version before 07ca10f; the 2-line change only widens the filter: adds the anchor `I take` and `verified cost?`). The result is identical: 0 of 8 accepted, 0 candidates, the sender's single prior message still filtered in all 8. So the mismatch does not affect these counts.
- Hash equality never establishes pre-registration (see the file header); that gate was already recorded as failed.

## Result

One checkpoint per world (rule `sci002.first_private_bundle.v1`), 8 checkpoints (dev02..dev05, B1 and B2). All 8 have k = |E*| = 1.

| world | boundary | L* | candidates | M* at w=0.25 | w=0.10 / w=0.50 (descriptive) | sender pre-checkpoint communication events not in E* (board) | of which removed by filter (v) |
|---|---|---|---|---|---|---|---|
| dev02_B1 | 3 | 207 | 0 | empty (fewer_than_k_candidates) | empty / empty | 1 (board 0) | 1 |
| dev02_B2 | 3 | 187 | 0 | empty | empty / empty | 1 (board 0) | 1 |
| dev03_B1 | 3 | 335 | 0 | empty | empty / empty | 1 (board 0) | 1 |
| dev03_B2 | 3 | 237 | 0 | empty | empty / empty | 1 (board 0) | 1 |
| dev04_B1 | 1 | 361 | 0 | empty | empty / empty | 1 (board 0) | 1 |
| dev04_B2 | 1 | 262 | 0 | empty | empty / empty | 1 (board 0) | 1 |
| dev05_B1 | 3 | 257 | 0 | empty | empty / empty | 1 (board 0) | 1 |
| dev05_B2 | 3 | 204 | 0 | empty | empty / empty | 1 (board 0) | 1 |

**Availability: 0 / 8 = 0%** (accepted M*), versus the Tier-B rule threshold of 30% (protocol §3.2 Tier B). It is below 30%. The result is the same at the descriptive windows w=0.10 and 0.50, so it is not an artefact of the 25% window.

Reason is structural: the first-private-bundle fork rule places the checkpoint at the receiver's first exposure, so the sender has at most one earlier communication event, and in all 8 worlds that single event (public board 0) contains a task id, digit or cost phrase and is excluded by filter (v). With k = 1 the candidate pool is empty. Eight checkpoints is a small sample (one world design, one sender position); it supports "0 of 8 observed", not a population rate.

## Implication
- Per protocol §3.2 (Tier B), availability < 30% means those checkpoints are `inconclusive: no_placebo_available` for any would-be `supported`, and the Tier B power text must state that `supported` is unavailable for them. No rule change follows.
- Under §3 and §8 status 3(a), `supported` needs M* non-empty and N_m run. On these real-agent DEV checkpoints it is therefore **not reachable**: every case would be `no_placebo_available`. If held-out checkpoints behave like DEV, no held-out case can be `supported`; the Tier B outputs would be limited to the other statuses and the descriptive Δ.
- Side effect for compute: when M* is empty the N arm is not run, so no N_m calls are spent (see `docs/runner/cap_investigation.md`, scenario with N empty, 3284 calls).
- Any change (for example widening candidate boards or loosening filter (v)) would be a protocol change and is not proposed here; held-out is not changed by this census.
