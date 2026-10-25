# RESUME packet (updated 2026-10-25 00:20 UTC)

Paste to restart: "Resume CCC ENH sprint as director. Read CLAUDE.md, ops/STATUS.md, ops/RESUME.md, ops/DECISIONS.md D-037..latest, docs/enh/MISSION.md. Restart anything listed below that is not running."

## Rules
Owner is sole commit author (no AI trailers). Sonnet orchestrators + Codex workers (gpt-6.1-sol medium); no Opus sub-agents; Modal children Codex-only. Max 6 live agents. Modal spend only for EXP-003 (≤$51). Never print secrets. No push/visibility/submission without owner.
Codex: `node ~/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/codex-companion.mjs task --write --effort medium --model gpt-6.1-sol "<prompt>"` (stdout to ops/reports/codex_runs/<ID>.stdout).

## Restart checklist
1. Benchmark: if docs/enh/r2/run_par/COMPLETE.json missing and no process in run_par.pid, rerun the resume command in docs/enh/r2/PARALLEL_EXECUTION.md (resumable).
2. EXP-003: read docs/enh/exp003/LOG.md last lines; `modal app list` (stop anything stray); resume RA-LEAD or relaunch a Sonnet lead with docs/enh/exp003/BRIEF.md + LOG.md.
3. Writing playbook: docs/enh/writing/WRITING_PLAYBOOK.md (done or near done).
4. Paper: paper/v2/draft_v2.md, build `python3 paper/v2/make_v2.py --figdir figures/enh/<run>`.
5. Explorer: demo/explorer (open index.html); rebuild: demo/build_twins.py → demo/explorer/bundle_data.py → demo/build_data.py.
