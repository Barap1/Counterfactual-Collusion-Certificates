# ORCH brief — finish the CCC submission (director → Haiku orchestrator, 2026-10-25 00:30 UTC)

You are ORCH, the orchestrator AND integration custodian. The owner has ~8% Claude budget left: use as little Claude as
possible. **All real work is done by Codex workers**; you launch them, check their handoffs, run the commands their
sandbox cannot (Modal, long detached jobs, git commits), and keep state files current. Do NOT spawn Claude sub-agents.

**Owner deadline: every deliverable ready by 2026-10-25 16:00 UTC** (owner records the demo and submits).
**Laptop has crashed twice — keep load light:** at most 2 Codex workers at a time; at most ONE heavy local process;
no local process pools larger than 3; heavy compute goes to Modal. Run long jobs detached + resumable
(`nohup … > log 2>&1 & disown`; write PID files) so a crash loses nothing.

## Read first (only these)
docs/enh/MISSION.md · ops/STATUS.md · ops/DECISIONS.md D-038..D-043 · this file. Each workstream names its own inputs.

## How to run a Codex worker
`node ~/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/codex-companion.mjs task --write --effort medium --model gpt-6.1-sol "<prompt>" > ops/reports/codex_runs/<ID>.stdout 2> ops/reports/codex_runs/<ID>.stderr`
(run in background; use `--effort low` or `--model gpt-6-luna` for easy jobs). Every prompt must say: read
docs/enh/MISSION.md; write only <paths>; no network (sandbox); no git; $0 except Modal runs you execute; end with a
≤300-word handoff in ops/reports/<ID>.md. Codex cannot reach the network or write .git: it writes code/scripts, you run
`modal …` commands and commits. Independent reviews = a separate Codex thread that did not write the thing reviewed.

## Commits (you are custodian)
`git add <paths> && git commit -m "<msg>"` — owner is sole author; NO Co-Authored-By/AI trailers; never push; run
`/bin/zsh scripts/secret_scan.sh` before committing anything new outside docs/enh; never commit docs/runner/exp003-*/,
*/cache/, .env, compute.env, ops/*.local.json. Commit after every finished workstream step.

## Money
Modal is owner-approved (card + workspace limit set by owner). Total project cap $51 incl. estimates; operating stop
$45; ~$0.95 spent. Allowed uses: EXP-003 GPU runs AND CPU containers for the benchmark (W1). Log every Modal run in
ops/budget_ledger.jsonl (GPU/CPU type, seconds, estimated $). `modal app stop` everything when idle; check
`modal app list` before you finish.

## Workstreams (priority order; run W1 and W2 in parallel)

**W1 — Prospective benchmark results (frozen R2).** Inputs: docs/enh/r2/PROTOCOL.md §7, FREEZE.json, seeds.json,
ccc/bench/__main__.py run(), scripts/bench_parallel_run.py (partial, uncommitted edits from a crashed worker),
/Users/aarav/.claude/jobs/ea6cad75/tmp/BENCH-PAR.prompt (original spec). Goal: outputs byte-identical to the frozen
run(), computed on **Modal CPU containers** (`modal` function mapped over seeds, repo code mounted, validate_freeze()
and code hashes checked inside the container), results written to docs/enh/r2/run_par/ locally; resumable. Codex
writes scripts/bench_modal_run.py + tests (DEV subset equality); you run it. **Determinism gate first:** the first
40 schedule-order seeds must be byte-identical to the 297 units already in docs/enh/r2/run/ (serial run, killed by a
crash; preserved, read-only); if any mismatch → stop and report to the director. Then full run, then
`python -m ccc.bench report --run docs/enh/r2/run_par` (or the driver's tail) → RESULTS.json/RESULTS.md. Write
docs/enh/r2/PARALLEL_EXECUTION.md (execution-only deviation; no logic/threshold/seed change). Expected cost a few $.
**W1-R3:** separate Codex thread independently recomputes RQ1–RQ6/RQ4b from run_par raw records and checks every
criterion; writes docs/enh/r2/REV_R3.md (APPROVE / ISSUES).

**W2 — EXP-003 real-agent probe on Modal GPU.** Inputs: docs/enh/exp003/BRIEF.md (design; follow it), LOG.md,
probe_design.md, ccc/exp003/*, ops/reports/RA-PROBE.md. GPU is now enabled. New timeline: GPU canary + 1 DEV-world
spike → $/world → finish PF/PK wiring (Codex; RA-WIRE died) → PROTOCOL.md (Plan M: Modal GPU, target 24–32 pairs,
min 16, frozen pair order, first-k-complete rule) → separate Codex review → **you commit
docs/enh/exp003/FREEZE.json** (record the commit in DECISIONS) → run (hard stop 09:00 UTC, resumable, several worlds
concurrently against the GPU server; runner stays local unless that overloads the laptop — then run runner workers in
Modal CPU containers too) → frozen analysis → separate Codex reproduction → docs/enh/exp003/RESULTS.md + a paragraph
that blends into the paper's single story. Never pool with EXP-002.

**W3 — Figures + explorer.** After W1: `starter/collusion_hackathon/colosseum/.venv/bin/python figures/enh/make_enh_figures.py --run docs/enh/r2/run_par --out figures/enh/prospective --label PROSPECTIVE`;
explorer: `python3 -I demo/build_twins.py --run docs/enh/r2/run_par --label PROSPECTIVE --dev-run docs/enh/bench/dev_run`
then demo/explorer/bundle_data.py then demo/build_data.py; one Codex worker applies the fixes in
docs/enh/qa/QA_EXPLORER.md (3 P1 + 6 P2) to demo/explorer/** and adds EXP-003 cases if its data pack is ready.

**W4 — Paper.** Inputs: docs/enh/writing/WRITING_PLAYBOOK.md (follow it), paper/v2/draft_v2.md, CITATION_AUDIT.md,
references_v2.bib. A Codex writer restructures the draft per the playbook (one blended story; abstract 150–250 words;
Figure 1 = twin figure; Limitations and Dual-Use appendix; positive control named; [OWNER] placeholders kept), fills
{{…}} from W1 RESULTS and W2 RESULTS using the matching pre-written template (never the favourable one by default),
rebuilds with `python3 paper/v2/make_v2.py --figdir figures/enh/prospective`, main text ≤ 8 pages
(`swift paper/build/pdf_pages.swift <pdf> <outdir>`). Every number must trace to a results file.

**W5 — Verification + handoff.** Separate Codex threads: (a) R4 consistency — every number in paper, explorer,
README, ops/CLAIMS.md and docs/review/rev001/CLAIMS_LEDGER.md agrees with its source; (b) final skeptical review —
strongest reasons a judge might reject, written to docs/enh/FINAL_REVIEW.md. Then a Codex writer produces
docs/enh/JUDGE_SUMMARY.md (1 page: problem, why it matters, what was learned, most impressive demonstrable result,
where to click first) and docs/enh/DEMO_SCRIPT.md (3–5 min recording script walking the explorer). Update README.md
headline to include the new results (evidence labels kept). Update ops/STATUS.md and ops/RESUME.md.

## Scientific rules you must enforce
EXP-002 result stays verbatim and prominent (Delta 1.354, CI [-0.020, 2.834], p 0.0703, not supported). Every number
carries one evidence category. DEV numbers are never presented as prospective. No outcome-dependent changes after a
freeze; if code must change after outcomes are visible, it is a new seed block and both runs are reported. Failures
of pre-stated predictions are reported, never hidden.

## When to contact the director
Only (1) at the end with a ≤300-word final handoff (what is done, paths, numbers, what needs the owner), or (2) on a
blocker you cannot resolve (determinism mismatch, budget stop, GPU failure, validity failure). Keep messages short.
