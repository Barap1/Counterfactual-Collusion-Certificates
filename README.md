# When Cooperation Looks Like Collusion
### The Limits of Counterfactual Auditing in Multi-Agent AI

**Counterfactual Collusion Certificates (CCC)** · Apart Research AI Collusion Research Sprint · October 2026

A message can change what other agents do and disadvantage outsiders without proving that the communication constitutes collusion. **Evidence of influence leaves an attribution problem: which policy produced the behavior?**

CCC makes that problem executable. We construct teams that look identical under message removal, then ask what additional evidence distinguishes their programmed policies.

[Explore the example](#try-it-offline) · [Reproduce the primary result](#reproduce-the-primary-result) · [Research and evidence](docs/README.md)

## Two teams. The same evidence.

Both teams send the same allocation request. Both assign the task to the dispatch team. Removing the message has the same measured effect on outsiders in each world.

One team follows a permitted efficiency policy. The other follows a prohibited policy that protects the coalition. Their initial behavior and message-removal results do not tell those explanations apart.

![Two constructed teams send the same allocation request and make the same allocation. Mean outsider reward rises from 14 to 19 after message removal in both worlds. Lowering each outsider’s task cost by 10 separates their programmed responses: the efficiency policy changes the allocation and yields outsider reward 29; the coalition-protecting policy keeps the allocation and yields 14.](docs/assets/allocation-twins.svg)

The extra probe changes task costs so that an outsider becomes the efficient choice. The efficiency team switches; the coalition-protecting team does not. This resolves the ambiguity **for these specified policies**. It is a reproducible counterexample to treating message-removal harm as sufficient attribution, not a general impossibility theorem or a validated detector. [Exact values, code and source records](docs/assets/README.md).

## What the audit can say

CCC replays a checkpoint with the original message, with its exposure masked, and with sham and eligible inert-message controls. It reports effects on outsiders, the coalition and total reward. The sham checks the intervention machinery; the inert-message control probes removal specificity, with imperfect surface and position matching. Missing or invalid controls limit the conclusion.

The claim should grow only with the evidence:

![Observation raises a question. A valid controlled replay can establish causal influence. Outcome measures can establish harmful exposure. Attribution additionally needs a declared policy and evidence distinguishing legitimate alternatives; otherwise it remains unresolved.](docs/assets/evidence-steps.svg)

The constructed benchmark adds cost probes and authorization records. Its labels come from the generator's programmed policies. The separate real-agent study compares prompt conditions, which are not verified ground truth for realized collusion.

## What we found

**Constructed benchmark.** The allocation and transfer twins share their specified early observations. Both construction-consistency checks pass by design; **all four aggregate prospective predictions fail**.

In deterministic evaluation, the harm-gated baseline accused legitimate cases as follows:

| Legitimate mechanism | Accused / evaluated |
| :--- | ---: |
| Efficient allocation | 200 / 200 |
| Authorized transfer | 200 / 200 |
| Useful information | 0 / 200 |
| Benign cooperation | 0 / 100 |

The revised attribution rule met the full utility criterion in **2 of 84 evaluation settings**; the previous version met it in **5 of 84**. These are setting counts, not classification accuracy or evidence of general superiority. [Full results and original verdicts](docs/RESULTS.md).

**Separate real-agent study.** Across **eight independent matched-world pairs**, the primary contrast was **1.354 reward units**, with a world-cluster 95% interval of approximately **−0.020 to 2.834** and exact one-sided sign-flip **p = 0.0703125**. The preregistered directional hypothesis was **not supported**. No exploratory case-level certificate was supported.

**What remains unestablished:** general detection reliability, end-to-end sensitivity, and consistent performance across platforms under noise. The noisy benchmark condition produced substantive cross-platform disagreements. Restricting established benchmark findings to the deterministic condition was a **post-hoc decision**. Negative results, both conditions and correction records are retained. [Limitations and release boundaries](docs/LIMITATIONS.md).

## Try it offline

Download or clone this repository, then open [`demo/explorer/index.html`](demo/explorer/index.html) in your browser. No server, installation or network connection is needed. GitHub's file preview shows source; the downloaded HTML runs the explorer.

1. Select **Twin worlds**, choose **P2** (allocation), and compare evidence levels **I2** and **I4**.
2. Open **Study** for the real-agent estimate and uncertainty.
3. Select a case to inspect continuations, controls and the recorded certificate.

The explorer reads a bundled frozen data pack; it makes no model calls. [Data provenance and rebuild instructions](demo/explorer/README.md).

## Reproduce the primary result

From the repository root, using **Python 3.12 or newer** on macOS, Linux or Windows:

```sh
python3 scripts/reproduce_headline.py
```

Use `python` instead of `python3` where that is your Python 3 command. No dependencies, credentials, models or network are required. The script verifies the archived input hash, recomputes the eight pair contrasts and checks them against the frozen independent arithmetic. Expected fields:

```text
Delta:       1.354325711018899
sign_flip:   numerator 18, denominator 256, p 0.0703125
pairs:       8 records
status:      matches frozen independent arithmetic; directional hypothesis NOT supported
```

This reproduces the primary estimate and exact test from recorded outputs. It does not regenerate agents or recompute the bootstrap interval. [Bootstrap verification, public-checkout checks and full-analysis requirements](docs/REPRODUCING.md).

## Methods and navigation

The **constructed study** tests evidence access using scripted allocation and transfer policies, legitimate controls and a frozen prospective evaluation. The **real-agent study** uses eight matched-world pairs and checkpoint continuations under a separately frozen protocol. These studies answer different questions; neither establishes deployment detection accuracy.

| Location | Start here for |
| :--- | :--- |
| [`ccc/`](ccc/) | Replay, auditing, benchmark and analysis code |
| [`demo/explorer/`](demo/explorer/) | Offline evidence explorer |
| [`docs/README.md`](docs/README.md) | Canonical results, freezes, corrections and provenance |
| [`paper/README.md`](paper/README.md) | Latest manuscript source, figures and bibliography |
| [`tests/`](tests/) · [`scripts/`](scripts/) | Implementation checks and reproduction entry points |

Original CCC code and documentation use the [MIT license](LICENSE). Third-party adaptations and scenario/trace redistribution rights remain unresolved; MIT does not grant those rights. See [NOTICE](NOTICE.md). Prior public history also retains potentially private document references; current-tree cleanup does not erase them. [Release status](docs/LIMITATIONS.md#release-status).

Developed by **Aarav Patel, Georgia Institute of Technology**, during Apart Research's October 23–25, 2026 sprint, with substantial Claude/Codex assistance. Colosseum/Terrarium and the seed-1 development pilot predate CCC's sprint work. [Provenance and acknowledgments](docs/README.md#provenance-and-acknowledgments).
