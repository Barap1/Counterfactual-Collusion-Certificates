# Source Ledger Addendum (SCI-001b)

**Date:** 2026-10-23. Companion to `source_ledger.md`; same conventions. Entries were retrieved from the arXiv API (metadata and abstracts) on this date. Authors and titles are as returned by the API.

## Upgrades to existing entries

| ID | Change |
|---|---|
| P01 | Upgraded to **V-full-text** for arXiv:2608.19161v1 (§1-§9, all tables). Details in `close_read.md` §1. Refinement: the Layer 2 reference is a stored matched-condition row (blocked, then neutral, then independent), not an online fork. It has neutral-latent controls but no sham arm, no benign-cooperation control, and reports no FPR (thresholds are neutral 95th-percentile). |
| P04 | Upgraded to **V-full-text** for arXiv:2610.28787v1 (main text and App. C, F, J). Details in `close_read.md` §2. It does regenerate continuations in clones with shared sampling seeds, has A/A tests and strategy-free placebos, and a "False alarms" verdict. It has no harm measure and no benign-cooperation control; messages appear only in App. J (cheap talk), coded but not ablated. |

## New entries

| ID | Citation | URL | Status | Notes |
|---|---|---|---|---|
| P10 | Gazzaev, A.-B., Gavrilov, A., Muravyov, S., Makarov, I. (2026). *Hidden Messages Between Diffusion Language Model Agents: Causal Evidence for Latent Communication.* arXiv:2610.28905v1, 20 Oct 2026 | https://arxiv.org/abs/2610.28905 | V-abstract (arXiv API) | Message removal tests whether a channel matters; replacement with another example's message tests whether content matters. Accuracy tasks, latent messages from diffusion LMs. No collusion, harm or legitimate-cooperation negative. Method precedent for a matched content-swap control. Full text not read. |
| P11 | Gu, A., Wang, Z., Ouporov, N., et al. (2026). *Fig: Automated Multiagent Behavior Elicitor.* arXiv:2610.28891v1, 20 Oct 2026 (author list truncated in retrieval) | https://arxiv.org/abs/2610.28891 | V-abstract (arXiv API) | Elicitation by interventions on game environments, covering covert coordination among six behaviours. Not a message-exposure audit. Low overlap. |
| P12 | Huang, Y., Narechania, A., Sinha, A. (2026). *MASIF: Implicit Failures for Process Observability in Multi-Agent Systems.* arXiv:2610.25852v1, 19 Oct 2026 | https://arxiv.org/abs/2610.25852 | V-abstract (arXiv API) | Counterfactual replay used to probe repairing implicit failures. Adds to the MAS-debugging replay literature; not collusion. Low overlap. |
| W01 | Apart Research. *AI Collusion Research Sprint*, 23-25 Oct 2026 | https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25 | V-page excerpt (Firecrawl search) | Sprint brief. Track 3 item 3.2 uses "a benign cooperation request" as a condition in a partner-offer design. Submitted projects not visible at retrieval time. |

## Searches run (for the record)

arXiv API, sorted by submission date, filter submitted on or after 2026-10-10: collusion with LLM/agents and counterfactual / intervention / ablation / audit; collusion with message; covert coordination; steganography with agents; secret channel / hidden communication; counterfactual replay in MAS; failure attribution with counterfactual; cooperation vs collusion distinction. Only P04, P09, P10, P11 and P12 surfaced in the window. Not searched: OpenReview, Semantic Scholar citation graphs.
