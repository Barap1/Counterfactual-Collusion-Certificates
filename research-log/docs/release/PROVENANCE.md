# Bundle provenance

Authorship: the owner is the sole author; no AI co-author lines.

`exp001_dev_input/` is a byte-preserving metadata subset of completed `docs/runner/exp001-live/`. The source was EXP-001 DEV, despite the historical directory name. Every included original file was checked against the union of `input_hashes` from `docs/analysis/exp001_dev/aggregate.json` and `docs/stats/stage2/exp001/stage2.json` before copying. `input_hashes.json` covers all 201 original files plus a labelled subset terminal marker. Original hash-bearing records are not rewritten. Full raw payload traces are not included, so reproduction is scoped to the archived DEV metadata analysis.

`pilot3_input/` preserves the 25 original files referenced in `docs/stats/stage2/pilot3/stage2.json`, plus a labelled subset terminal marker, for the legacy Stage-2 reader test. Restore it only at the documented path in a clean checkout.

`pilot_archive/` preserves the 27 seed-1 archived pilot files named in `ops/pilot_manifest.sha256`, including the interrupted run. This archive is DEV, separate from EXP-001 and held-out evidence. It is provided because the original adapter tests require its exact bytes. No original archive was changed.

The subset terminal markers describe release packaging, not model execution or fabricated outcomes. Original operational locks are omitted. Current analysis is repeated and hash-checked. Historical comparisons retain and match all scientific JSON fields, allowing additive metadata; aggregate code hashes/limitations/synthetic metadata and the stale-lock warning are explicitly excluded. Historical byte differences are listed in the output compatibility report. Pinning uses F/S outcomes only; optional detector calibration is rerun separately on DEV synthetic fixtures via the frozen theta script. The adopted human-reviewed `STAGE2_ADDENDUM.md` is never regenerated or overwritten by the diagnostic CLI.

The Gate A driver sets theta=0.4 and bootstrap_draws=10000, generates only development fixture seeds, and compares the resulting v1.2.2 JSON bytes with the decompressed archived evidence. Constructed/census historical inputs are not rerun. Gate A FAIL remains a result, independent of whether software reproduction succeeds.

The first validation attempt preceded the extra release guard. A readiness test capable of reading the real EXP-002 design manifest was identified and the run interrupted; whether it executed before interruption was not established. No held-out outcome was inspected. Subsequent validation installs the guard before discovery and explicitly skips that method. This limitation must accompany the handoff.
