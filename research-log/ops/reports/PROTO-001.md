# PROTO-001 handoff
**Task:** Draft R2 prospective protocol (docs/enh/r2/PROTOCOL.md) and FREEZE template.
**Status:** DRAFT complete, not frozen; needs independent review and the director's freeze steps.
**Artifacts:** docs/enh/r2/PROTOCOL.md (about 2365 words), docs/enh/r2/FREEZE_TEMPLATE.json, this file. No FREEZE.json created, no code or git changes.
**Validation:** template parses as JSON; word count checked; inputs read: MISSION, D-038, BENCH_SPEC, C_directions s5-7, B_stats (claims list), prereg skim. Not checked: that `python -m ccc.bench hashes` / `seeds --check` exist (they are assumed from the spec; hash fields are placeholders), actual EXP-002 seed lists (to be enumerated at freeze).
**Limitations:** I chose RQ1-RQ5 as descriptive-with-prediction (no Holm family), justified in section 6; reviewer may prefer Holm. RQ2/RQ5 tolerances (0.02 gap, precision/recall >= 0.9, 0.95 attribution) and the RQ1 zero-violation criterion are my proposals. The `seeds --check` subcommand name and the seed-derivation formula need to match BENCH-IMP. "Strongest baseline" restricted to {B2+, B3b}, tie to B2+, DEV I1 balanced accuracy.
**Budget:** $0, Sonnet, no model calls beyond this session.
**Next:** independent reviewer pass; align with ccc.bench CLI; compute DEV-derived baseline choice and enumeration hash; director writes FREEZE.json and commits before any seed is drawn.
