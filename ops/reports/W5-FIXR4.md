## Task

W5-FIXR4: resolve every failing R4 consistency row against frozen sources.

## Status

Assigned presentation fixes complete; build regeneration remains with ORCH.

## Artifacts

- `paper/v2/draft_v2.md`
- `README.md`
- `demo/explorer/bundle_data.py`
- `demo/explorer/data/index.js`
- `docs/enh/R4_FIX_NOTE.md`
- `ops/reports/W5-FIXR4.md`

## Validation

Commands run: `cat CLAUDE.md`, `cat ops/tasks.json`, `cat docs/enh/MISSION.md`, `cat docs/enh/R4_CONSISTENCY.md`, `cat CCC_START_HERE.md docs/spec/00_control_plane.md`; scoped `rg -n`, `rg --files`, `sed -n`, `nl -ba`, and `head` inspections; local `python3 - <<'PY'` editing/index-generation snippets and `python3 -B - <<'PY'` assertions.

Passing assertions: Python syntax; all paper/README result numbers preserved; all explorer study numbers and case-index values preserved; generator reproduces index exactly; manifest has 46 files/422 source hashes and descriptive category; source JSON/correction hashes unchanged; legend survives build comment stripping; S1–S3 [OC], repair [PH], and inherited search provenance present. Source manifest HEAD metadata refreshed automatically. An initial manifest-difference assertion omitted that expected HEAD refresh; corrected comparison passes.

## Limitations

No full builds or rendered inspection; no independent search-count verification. Figure 1 [NP] follows its source PROSPECTIVE metadata despite its conceptual content. No task-specific registry lease exists; direct brief authorizes these writes. No frozen source edits.

## Budget

$0 new spend; Codex session model. No experiment inference, model/API requests, network, Modal or git commands.

## Next

ORCH: run `python3 demo/explorer/bundle_data.py` and `python3 paper/v2/make_v2.py --figdir figures/enh/prospective --no-pdf`; inspect regenerated paper legend and Figure 1 caption, then complete rendered/PDF review.
