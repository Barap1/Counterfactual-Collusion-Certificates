# EXP-002 freeze record (protocol v1.2 held-out)

**FREEZE CANDIDATE — pending independent freeze review.** Not a freeze until reviewed and approved. No held-out data have been generated or collected under this record.

Hashes are SHA-256 of file bytes unless stated. Git HEAD is the analysis base; the items listed below are uncommitted working-tree files at the time of writing (no commits were made).

| Item | Path | SHA-256 |
|---|---|---|
| Protocol v1.2 (SCI-002) | `docs/research/sci002/protocol.md` | `8f7dcd896c524aa0a056bf11490641c8cc116a2b099de0b903285109f0a92549` |
| STAT-001 preregistration | `docs/stats/prereg.md` | `df72bb5ddf603ddee56876166cd4727f0ff18484d18c4c31bff27b4c6be0c649` |
| Analysis specification | `docs/stats/analysis_spec.md` | `273ebaa7bfff787352622518f5c162954ec2db93ed0a11e784a866616aa9725e` |
| Stage-2 addendum (FINAL, pending review) | `docs/stats/stage2/STAGE2_ADDENDUM.md` | `18e068798c491302a184b72afa7efdb8a1c798df0a18f64e31e28e346fe320f9` |
| Theta pin output | `docs/stats/stage2/theta_pin.json` | `63e07f157cc15dc2f00663ff22cd09a5fcd30aee3e1146f5cc38c25bee66c09c` |
| Held-out manifest (canonical digest) | `docs/runner/exp002_manifest.json` | `49f54b472f4cc6b4610ad5ef924bec4715323f39d6d97f13930ad3467ef31250` |
| Extractor freeze hashes (incl. re-freeze line) | `ops/v12_freeze_hashes.txt` | `3413cffd283257fb74bb9a1a5de05956f219ad89fc93aef918d25000ce461616` |
| Deviation log | `docs/stats/deviation_log.md` | `8ff14af66786fa349ddcb38ecaf6bb463133a1145c2735f3e00fb2d154d2be1a` |
| Git HEAD (analysis base) | `1e13967b9f86b46329d4f078f620936025e2edca` | (commit id) |

Notes:

- The manifest row is the canonical digest computed by `ccc.runner.manifest.freeze_hash`, which excludes only the `stat001` and `stat001_hash` fields. This is the value the runner binds to a STAT-001 approval. The raw file hash of `exp002_manifest.json` is not listed because the manifest points at this file through `stat001`, which would make the two hashes depend on each other.
- The extractor row is the file hash after the re-freeze line for `ccc/audit/commitments.py` (`7b8da4f0…a311`, 07ca10f, D-030). The other listed hashes in that file were verified unchanged on 2026-10-24.
- The STAT-001 approval required by `ccc.runner.manifest` is a JSON artifact with `task_id` = `STAT-001` and `frozen_manifest_sha256` equal to the canonical manifest digest above. This file is not that approval. An independent reviewer must produce it. It has not been produced.

Open items before a held-out run may start: independent freeze review of this record; owner approval for EXP-002 (D-029 condition); STAT-001 approval artifact as described above.
