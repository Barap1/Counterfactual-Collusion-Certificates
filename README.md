# When Cooperation Looks Like Collusion
### The Limits of Counterfactual Auditing in Multi-Agent AI

**Counterfactual Collusion Certificates (CCC)** · Apart Research AI Collusion Research Sprint · October 2026

A message can change what other agents do and disadvantage outsiders without proving that the communication constitutes collusion. **Evidence of influence leaves an attribution problem: which policy produced the behavior?**

CCC builds executable counterexamples: teams that look identical under message removal but follow different programmed policies. Extra evidence can separate particular pairs.

[Explore the example](#try-it-offline) · [Reproduce the primary result](#reproduce-the-primary-result) · [Research and evidence](docs/README.md)

## Two teams. The same evidence.

Two constructed teams send the same message, assign the task to dispatch, and produce the same message-removal effect. One follows a permitted efficiency policy; the other follows a prohibited coalition-protecting policy. That early evidence cannot distinguish them.

<a href="docs/assets/allocation-twins.svg#gh-light-mode-only">
  <picture>
    <source media="(max-width: 1100px)" srcset="docs/assets/allocation-twins.mobile.svg">
    <img src="docs/assets/allocation-twins.svg#gh-light-mode-only" alt="Two programmed teams share message, dispatch allocation and removal effect: mean outsider reward 14 → 19. Lowering each outsider task cost by 10 separates them: permitted efficiency switches allocation and yields 29; prohibited coalition protection keeps allocation and yields 14.">
  </picture>
</a>
<a href="docs/assets/allocation-twins.dark.svg#gh-dark-mode-only">
  <picture>
    <source media="(max-width: 1100px)" srcset="docs/assets/allocation-twins.mobile-dark.svg">
    <img src="docs/assets/allocation-twins.dark.svg#gh-dark-mode-only" alt="Two programmed teams share message, dispatch allocation and removal effect: mean outsider reward 14 → 19. Lowering each outsider task cost by 10 separates them: permitted efficiency switches allocation and yields 29; prohibited coalition protection keeps allocation and yields 14.">
  </picture>
</a>

The cost probe makes an outsider the efficient choice. The efficiency team switches; the coalition-protecting team does not. This separates **these specified policies**. The example does not establish a general impossibility theorem or a validated detector. [Exact values, code and source records](docs/assets/README.md).

## What the audit can say

CCC replays a checkpoint with the original message, its exposure masked, a sham, and an eligible inert-message control. It measures outsider, coalition and total reward. The controls test intervention validity and removal specificity; placebo surface and position matching is imperfect. Missing or invalid controls limit the conclusion.

| Claim | Evidence needed |
| :--- | :--- |
| Observation | Visible communication |
| Causal influence | Valid controlled replay and a nonzero effect |
| Harmful exposure | Outsider outcome measures, with valid controls |
| Attribution | A declared policy and evidence separating legitimate alternatives |

Attribution needs a declared policy and evidence distinguishing legitimate alternatives. The benchmark supplies cost probes and authorization records; its labels come from programmed policies. The separate real-agent study compares prompt conditions, not verified ground truth for realized collusion.

## What we found

**Constructed benchmark.** The allocation and transfer twins share their specified early observations. Both construction-consistency checks pass by design; **all four aggregate prospective predictions fail**.

In deterministic evaluation, the harm-gated baseline accused legitimate cases as follows:

| Legitimate mechanism | Accused / evaluated |
| :--- | ---: |
| Efficient allocation | 200 / 200 |
| Authorized transfer | 200 / 200 |
| Useful information | 0 / 200 |
| Benign cooperation | 0 / 100 |

The revised attribution rule met the full utility criterion in **2 of 84 evaluation settings**, versus **5 of 84** for the previous version. These are setting counts, not classification accuracy or a general ranking. [Full results and original verdicts](docs/RESULTS.md).

**Separate real-agent study.** Across **eight independent matched-world pairs**, the primary contrast was **1.354 reward units**, with a world-cluster 95% interval of approximately **−0.020 to 2.834** and exact one-sided sign-flip **p = 0.0703125**. The preregistered directional hypothesis was **not supported**. No exploratory case-level certificate was supported.

**What remains unestablished:** general detection reliability, end-to-end sensitivity, and consistent performance across platforms under noise. The noisy condition produced substantive cross-platform disagreements. Restricting established benchmark findings to the deterministic condition was **post hoc**. Both conditions, negative results and corrections remain available. [Limitations and release boundaries](docs/LIMITATIONS.md).

## Try it offline

Download or clone this repository, then open [`demo/explorer/index.html`](demo/explorer/index.html) in your browser. The bundled interface needs no server, installation or network connection. GitHub shows source; open the downloaded HTML to use it.

1. Select **Twin worlds**, choose **P2** (allocation), and compare evidence levels **I2** and **I4**.
2. Open **Study** for the real-agent estimate and uncertainty.
3. Select a case to inspect continuations, controls and the recorded certificate.

The explorer reads frozen records and makes no model calls. [Data provenance and rebuild instructions](demo/explorer/README.md).

## Reproduce the primary result

From the repository root, using **Python 3.12 or newer** on macOS, Linux or Windows:

```sh
python3 scripts/reproduce_headline.py
```

Use `python` instead of `python3` where that is your Python 3 command. No dependencies, credentials, models or network are required. The script verifies the input archive hash and recomputes all eight pair contrasts against frozen independent arithmetic. Expected fields:

```text
Delta:       1.354325711018899
sign_flip:   numerator 18, denominator 256, p 0.0703125
pairs:       8 records
status:      matches frozen independent arithmetic; directional hypothesis NOT supported
```

This reproduces the primary estimate and exact test from recorded outputs. It does not regenerate agents or recompute the bootstrap interval. [Bootstrap verification, public-checkout checks and full-analysis requirements](docs/REPRODUCING.md).

## Methods and navigation

The **constructed study** tests scripted policies and evidence access in a frozen prospective evaluation. The **real-agent study** uses eight matched-world pairs and checkpoint continuations under a separate freeze. Neither establishes deployment detection accuracy.

| Location | Start here for |
| :--- | :--- |
| [`ccc/`](ccc/) | Replay, auditing, benchmark and analysis code |
| [`demo/explorer/`](demo/explorer/) | Offline evidence explorer |
| [`docs/README.md`](docs/README.md) | Canonical results, freezes, corrections and provenance |
| [`paper/README.md`](paper/README.md) | Latest manuscript source, figures and bibliography |
| [`tests/`](tests/) · [`scripts/`](scripts/) | Implementation checks and reproduction entry points |

Original CCC code and documentation use the [MIT license](LICENSE). Third-party adaptations and scenario/trace redistribution rights remain unresolved; MIT does not grant those rights. See [NOTICE](NOTICE.md). Prior public history also retains potentially private document references; current-tree cleanup does not erase them. [Release status](docs/LIMITATIONS.md#release-status).

Developed by **Aarav Patel, Georgia Institute of Technology**, during Apart Research's October 23–25, 2026 sprint, with substantial Claude/Codex assistance. Colosseum/Terrarium and the seed-1 development pilot predate CCC's sprint work. [Provenance and acknowledgments](docs/README.md#provenance-and-acknowledgments).
