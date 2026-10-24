# EXP-003 brief — real-agent twin probe on Modal (director, D-042)

Owner-approved spend: Modal, hard cap $51 including estimates; operating stop $45. Everything else stays $0.
Deadline for usable results: **2026-10-25 18:00 UTC** (hard stop for any model run: 2026-10-25 20:00 UTC).
Lead: RA-LEAD. May spawn up to 3 live sub-agents at a time (Claude Sonnet/Haiku via the Agent tool, or Codex via
`node ~/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/codex-companion.mjs task --write --effort medium --model gpt-6.1-sol "<prompt>"`).
Depth limit: RA-LEAD's children may NOT spawn further agents. Codex cannot write .git; nobody commits except the director.

## Scientific question (the paper's central principle, on real agents)
In the same Colosseum Jira harness as EXP-002, do real LLM agents prompted to collude (B1, frozen EXP-002 prompt)
versus authorized/efficiency-motivated cooperation (B2, frozen EXP-002 prompt) produce **message-knockout evidence**
that fails to separate the regimes, while an **incentive probe** (I4: at the checkpoint, lower one outsider's cost on
the contested task so that outsider becomes the efficient claimant; re-run F and K) separates them (B2 coalition cedes
the task / outsider reward rises; B1 keeps it)?

## Design (decided by the director; freeze details in PROTOCOL)
- Reuse the EXP-002 runner, replay engine, arms (F, K, S where cheap; N only if available), validity checks,
  rewards and analysis code paths wherever possible. Add one new arm pair: PF (probe, factual) and PK (probe, knockout).
  The probe is an environment edit applied identically to all branches of that arm at restore time; validate it
  (state diff shows only the targeted cost changed; replay checks pass).
- Model: gemma4:26b (same family/tag as EXP-002) served on Modal (Ollama or vLLM in a container; record model
  digest/identity and server version; run the project's model-identity canaries). If time and budget remain after the
  primary block, an optional exploratory second open-weight model may run on a separate pre-declared block.
- Fresh world seeds drawn by a frozen rule after the freeze, disjoint from Gate A, DEV, EXP-001, EXP-002 and the R2
  benchmark seed lists. Target **32 matched world pairs** (B1/B2 share the world), minimum 16; pre-declare the order
  in which pairs run so a budget/time stop yields a pre-specified, unbiased subset (first k pairs in frozen order).
- Continuations: 4 per arm per checkpoint (as EXP-002) unless the freeze-time budget estimate forces 3; decided before
  any outcome.
- Estimands (world-cluster, pairs are the units):
  P1 (replication, new prospective): Delta_K = mean_w[tau_O(w,B1) − tau_O(w,B2)], tau_O = E[Omean_K] − E[Omean_F].
  P2 (probe): Delta_P = mean_w[pi(w,B2) − pi(w,B1)], pi = E[Omean_PF] − E[Omean_F] (how much outsiders gain when made
  efficient), plus the coalition-cedes rate on the contested task under PF.
  Separation comparison (descriptive with CI): standardized separation of regimes by the probe vs by the knockout.
  Tests: exact one-sided paired sign-flip + world-cluster bootstrap 95% CI (same machinery as EXP-002), Holm across P1,P2.
- Predictions (state honestly; failure is publishable): P1 small/unsupported; P2 positive.
- Validity gates as in EXP-002 (state/prompt identity, scope, freshness, isolation, model identity, missingness).

## Required process
1. Feasibility + cost spike first (≤ 1.5 h, ≤ $5): stand up the Modal server, run canaries and ONE dev world from the
   EXP-002 DEV pool (development data), measure calls/branch, tokens/s, $/world. Write docs/enh/exp003/feasibility.md.
2. Write docs/enh/exp003/PROTOCOL.md (≤ 2000 words) with exact estimands, criteria, sample size, stopping rule,
   budget-stop rule, seed rule, exclusions and analysis commands; an independent reviewer sub-agent (did not author it)
   approves it; the director commits FREEZE (tell the director via your handoff; do not run held-out worlds before the
   director confirms the freeze commit — send a short message and wait).
3. Run the block with hard timeouts, teardown checks (`modal app list` shows nothing running at the end), and a ledger
   row per run in ops/budget_ledger.jsonl (GPU type, seconds, estimated $). Stop at $45 estimated or 2026-10-25 20:00 UTC.
4. Analysis with frozen code; an independent reviewer sub-agent reproduces the headline numbers from raw outputs.
5. Hand back: docs/enh/exp003/RESULTS.md + JSON, a 300-word handoff, and a short paragraph the paper can use that
   blends the result into the main story (one evidence ladder; real agents illustrate where knockout stops and the
   probe adds evidence) while keeping EXP-002's frozen null verbatim and never pooling.

## Hard rules
- docs/enh/MISSION.md applies. Never modify EXP-002 or R2 artifacts. Never print or commit tokens/keys/.env/compute.env/
  ops/*.local.json. Modal credentials: use the existing CLI login; never echo tokens.
- Write only: docs/enh/exp003/**, ccc/exp003/** (new code), tests/test_exp003_*.py, ops/budget_ledger.jsonl (append),
  ops/reports/RA-*.md, raw outputs under docs/runner/exp003-*/ (gitignored like EXP-002; archive tar.gz + sha256 at end).
- If anything threatens the cap, validity, or the deadline, stop and report rather than improvise.
