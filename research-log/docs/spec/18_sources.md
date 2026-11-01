# 18 - Sources and verification ledger

**Research check date: October 23, 2026.** The sources below are primary organizer, code, paper, and product-documentation sources used to prepare this specification. Live features, quotas, models, prices, and event instructions must be rechecked when executing. The experimental design, orchestration policy, proposed sample sizes, and acceptance thresholds are recommendations in this specification, not claims copied from these sources.

The previous Deep Research report remains useful background, but its novelty and expected-outcome statements are not substitutes for source verification or data. The source worker should generate complete citation metadata and retain the precise paper versions used.

## Organizer and starter sources

**S01 - Apart Research, AI Collusion Research Sprint.** Official tracks, rubric, deadline, template link, and submission requirements. The final paper must use the current official instructions rather than assumptions in an old chat message.

https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25

**S02 - Poseidon Research, collusion_hackathon starter.** Reviewed upstream revision: `d585a7b3be50366cc2bdf5789bf8add5890b2abd`. Record the owner's actual local revision separately.

https://github.com/poseidon-research/collusion_hackathon

https://github.com/poseidon-research/collusion_hackathon/tree/d585a7b3be50366cc2bdf5789bf8add5890b2abd/colosseum

**S07 - Colosseum metric implementation.** The returned `total_cost` comes from `final_summary`; group advantage is the difference in group mean rewards. Inspect the environment and optimal-allocation helper to establish task units and denominators rather than treating this as an API invoice.

https://github.com/poseidon-research/collusion_hackathon/blob/d585a7b3be50366cc2bdf5789bf8add5890b2abd/colosseum/experiments/collusion/metrics.py

https://github.com/poseidon-research/collusion_hackathon/blob/d585a7b3be50366cc2bdf5789bf8add5890b2abd/colosseum/experiments/collusion/compute_jira_optimal.py

**S11 - Starter inference configuration and provider adapter.** Source of endpoint precedence, environment loading, global model override, and the distinction between native execution and automatic hosting routes.

https://github.com/poseidon-research/collusion_hackathon/blob/d585a7b3be50366cc2bdf5789bf8add5890b2abd/util/poseidon_compute/llm_config.py

https://github.com/poseidon-research/collusion_hackathon/blob/d585a7b3be50366cc2bdf5789bf8add5890b2abd/colosseum/experiments/common/providers.py

## Closest research

**S03 - Colosseum: Auditing Collusion in Cooperative Multi-Agent Systems.** arXiv:2602.15198, 2026. Source for the underlying testbed, coalition outcomes, and communication/action audit context. Reuse is attribution, not a CCC novelty claim.

https://arxiv.org/abs/2602.15198

https://arxiv.org/html/2602.15198v1

**S04 - Detecting Multi-Agent Collusion Through Multi-Agent Interpretability.** arXiv:2604.01151v3, 2026. HELIOS/NARCBench; inspect the collusion/coordination definitions and the treatment of unavailable counterfactual simulation. Do not claim this source proves our proposed estimator identifies individual necessity.

https://arxiv.org/html/2604.01151v3

**S05 - Emergent Collusion in Long-Horizon LLM Agent Interaction.** arXiv:2609.24967v1, 2026. Controlled peer-behavior interventions are relevant prior causal work, not merely observational background.

https://arxiv.org/html/2609.24967v1

**S06 - Audit the Whisper: Detecting Steganographic Collusion in Multi-Agent LLMs.** Om Tailor, arXiv:2510.04303v1, 2025. Relevant intervention, calibration, and reproducibility prior art. Its reported guarantees/results do not transfer automatically to CCC.

https://arxiv.org/html/2510.04303v1

## Agent runtimes and inference

**S08 - Anthropic, Claude Code subagents documentation.** Verified support for nested subagents, independent contexts, shared usage limits, and version-dependent depth/concurrency controls. Project-specific bounds and task policies in this spec are our choices.

https://code.claude.com/docs/en/sub-agents

**S09 - OpenAI, Codex subagents documentation.** Official entry point may redirect to the current documentation site. The owner's specific Claude-to-Codex plugin still requires local inspection; this source does not define that third-party bridge's commands.

https://developers.openai.com/codex/multi-agent/

https://developers.openai.com/codex/config-reference/

**S10 - OpenRouter, limits documentation.** Source for account/key limits and request-quota checks. Use the actual current API response and model catalog for execution decisions.

https://openrouter.ai/docs/api_reference/limits

https://openrouter.ai/api/v1/models

**S12 - Ollama, tool calling and OpenAI compatibility.** Capability depends on the selected model/backend; benchmark the full tool loop rather than assume compatibility from an endpoint URL.

https://docs.ollama.com/capabilities/tool-calling

https://docs.ollama.com/api/openai-compatibility

https://docs.ollama.com/gpu

**S13 - Modal, budgets.** Distinguishes gross usage budgets from net spend limits and notes account-level enforcement. Confirm the owner's actual available controls and promotional terms.

https://modal.com/docs/guide/budgets

**S14 - Modal, pricing and billing.** Check current service eligibility and costs, including the separate treatment of Shared Endpoints. Do not extrapolate promotional credit coverage to unverified services.

https://modal.com/pricing

https://modal.com/docs/guide/billing

## User-provided and private sources

**U01 - Owner's terminal logs and pasted pilot CSV.** Establish the successful tool call, completed run, paths, and reported metrics. Bootstrap must validate the original files. The one-call `usage.cost=0` is not a complete multi-agent spending audit.

**U02 - Owner's existing Google Docs template and prepared working copy.** Read through the connected Drive tools during preparation; module 12 records the exact target. This is a private workflow source, not a public citation for scientific claims.

**U03 - Prior updated Deep Research report.** `docs/research/CCC_Updated_Deep_Research_Report.md`, expected local location. Historical proposal; preserve it and document corrections rather than overwriting it as if its expected results were observations.

## Citation rules for the executing agents

For each paper used in the submission, verify title, authors, year, version, and the exact passage supporting the cited claim. Distinguish a paper's reported result from a result reproduced by this project. Do not copy numerical performance claims without checking their scope. Do not invent URLs, bibliography entries, or citations from an agent's memory. If a source is inaccessible, label it unverified and remove unsupported claims or find a primary replacement.

Local experiment conclusions cite local artifact IDs and methods, not a prior paper as evidence that our implementation worked.
