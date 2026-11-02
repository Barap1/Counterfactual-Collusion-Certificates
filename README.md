<p align="center">
  <picture>
    <source media="(max-width: 700px)" srcset="docs/assets/banner.mobile.svg">
    <img src="docs/assets/banner.svg" width="100%" alt="CCC: Counterfactual Collusion Certificates. When cooperation looks like collusion: auditing multi-agent AI with controlled replay, twin worlds and exact tests. Two constructed teams, one permitted and one prohibited, show the same outsider reward at evidence levels I0 to I3; at I4 a cost probe separates them, 29 versus 14.">
  </picture>
</p>

<p align="center">
  <a href="paper/paper.pdf"><img alt="paper: PDF" src="https://img.shields.io/badge/paper-PDF-b31b1b"></a>
  <a href="docs/MATH.md"><img alt="math: proofs and derivations" src="https://img.shields.io/badge/math-proofs%20%26%20derivations-0f766e"></a>
  <a href="docs/REPRODUCING.md"><img alt="Python 3.12+, standard library reproduction" src="https://img.shields.io/badge/python-3.12%2B%20%C2%B7%20stdlib%20reproduction-3776AB?logo=python&amp;logoColor=white"></a>
  <a href="LICENSE"><img alt="license: MIT" src="https://img.shields.io/badge/license-MIT-64748b"></a>
</p>

<p align="center">
  <a href="#the-problem">The problem</a> ·
  <a href="#the-mathematics-in-brief">Math</a> ·
  <a href="#how-it-is-built">How it is built</a> ·
  <a href="#what-the-experiments-showed">Results</a> ·
  <a href="#how-the-work-was-done">Process</a> ·
  <a href="#run-it-yourself">Run it</a>
</p>

**When Cooperation Looks Like Collusion: The Limits of Counterfactual Auditing in Multi-Agent AI** · Aarav Patel, Georgia Institute of Technology · Apart Research AI Collusion Research Sprint, October 2026

## The problem

Imagine you are auditing a team of AI agents. One agent sends another a message, the two coordinate, and the agents outside their team end up worse off. The standard check is counterfactual: replay the episode with that message removed and see whether the outsiders do better. If they do, it is tempting to call it collusion.

That conclusion does not follow. Legitimate cooperation also changes what agents do, and it can also leave outsiders worse off. A removal test tells you the message mattered and that it hurt someone. It does not tell you which policy the agents were following, or whether that policy was allowed.

CCC turns this gap into something you can run. It builds pairs of teams that send the same message, make the same allocation and produce the same removal effect, but follow different programmed policies: one permitted, one prohibited. On that evidence no audit can tell them apart. A small extra test, lowering the outsiders' costs, does:

<a href="docs/assets/allocation-twins.light.svg#gh-light-mode-only">
  <picture>
    <source media="(max-width: 1100px)" srcset="docs/assets/allocation-twins.mobile.svg">
    <img src="docs/assets/allocation-twins.light.svg#gh-light-mode-only" alt="Two programmed teams share message, dispatch allocation and removal effect: mean outsider reward 14 → 19. Lowering each outsider task cost by 10 separates them: permitted efficiency switches allocation and yields 29; prohibited coalition protection keeps allocation and yields 14.">
  </picture>
</a>
<a href="docs/assets/allocation-twins.dark.svg#gh-dark-mode-only">
  <picture>
    <source media="(max-width: 1100px)" srcset="docs/assets/allocation-twins.mobile-dark.svg">
    <img src="docs/assets/allocation-twins.dark.svg#gh-dark-mode-only" alt="Two programmed teams share message, dispatch allocation and removal effect: mean outsider reward 14 → 19. Lowering each outsider task cost by 10 separates them: permitted efficiency switches allocation and yields 29; prohibited coalition protection keeps allocation and yields 14.">
  </picture>
</a>

Once an outsider becomes the cheaper choice, the efficiency-minded team hands over the task and the coalition-protecting team holds on to it. The probe separates these two specified policies; it is not a general detector, and a different legitimate policy might not respond the same way. [Exact values, code and source records](docs/assets/README.md).

## Why this matters for AI safety

More and more systems put several AI agents together, and keeping them safe often depends on those agents not quietly coordinating against the people overseeing them or against third parties. Control setups where one model monitors another have to worry about exactly this. When an auditor finds a suspicious message, they need to decide whether to act on it: shut something down, sanction an agent, or clear the system. Acting on influence alone means punishing legitimate teamwork; ignoring it means missing real collusion. Attribution, deciding which policy produced the behaviour, is the step that justifies action, and it needs its own evidence. This project spells out what that evidence has to be. The longer version, with references, is in [docs/RESEARCH_PROCESS.md](docs/RESEARCH_PROCESS.md#threat-model).

## The mathematics in brief

Everything here is stated and proved in full in [docs/MATH.md](docs/MATH.md), with the file and function that computes each quantity and a test that checks each value.

**Setting** ([section 1](docs/MATH.md#1-setting-and-notation)). Four agents: a coalition $\mathcal C$ (the sender and receiver of a message $m$) and two outsiders $\mathcal O$. From a saved checkpoint we regenerate what happens next under several replay arms that change only what the receiver sees. With outsider, coalition and total reward $O$, $C$ and $W$, the removal effect on outsiders is

$$
\tau_O = \mathbb E^K[O] - \mathbb E^F[O],
$$

the knockout arm minus the factual arm. Sham and placebo arms check that a nonzero effect is not just replay noise or a side effect of removing any message at all ([section 2](docs/MATH.md#2-interventions-and-estimands)). An evidence level $I_k$ is the set of fields an audit rule is allowed to read.

**Proposition 1** ([section 3](docs/MATH.md#3-proposition-1-attribution-non-identifiability-for-the-constructed-twins)). If two policies produce the same distribution of $I_k$ evidence, any audit rule that only reads that evidence gives them the same distribution of verdicts. The proof is one line: for any set of verdicts $B$, $\Pr[\delta(V_1) \in B] = \Pr[V_1 \in \delta^{-1}(B)] = \Pr[V_2 \in \delta^{-1}(B)] = \Pr[\delta(V_2) \in B]$. One twin should be accused and the other cleared, so the expected number of mistakes on the pair is $(1-p) + p = 1$. For the allocation twins you can see which way a harm-based rule falls: the outsider effect is $\tau_O = d \ge 3$, above the 2.5 margin, the coalition gains $\tau_C = d > 0$ and total reward is unchanged, so it accuses both.

**Proposition 2** ([section 4](docs/MATH.md#4-proposition-2-separation-by-the-cost-probe)). With baseline reward $b$ and transfer size $d$ set by the seed, the probe lowers each outsider's cost by $2d$. The efficiency policy cedes the task and the coalition policy does not:

$$
O_F = b-d,\qquad O_K = b,\qquad O^{\text{coal}}_{PF} = b-d,\qquad O^{\text{eff}}_{PF} = b+2d \qquad\Longrightarrow\qquad 14,\ 19,\ 14,\ 29 \ \text{ at } b=19,\ d=5 .
$$

The twins look identical through $I_3$ and differ at $I_4$, which is exactly where the premise of Proposition 1 stops holding.

**The exact sign-flip test** ([section 5](docs/MATH.md#5-the-exact-sign-flip-test)). The real-agent study has eight matched-pair contrasts $d_w$. Flipping the signs of a set $S$ of pairs gives a mean at least as large as the observed one exactly when $\sum_{w \in S} d_w \le 0$, so

$$
p = \frac{\lvert\lbrace S : \sum_{w \in S} d_w \le 0 \rbrace\rvert}{2^8} = \frac{2 \times 9}{256} = 0.0703125 .
$$

Nine subsets of the seven nonzero contrasts have a non-positive sum, and the one contrast that is exactly zero doubles the count. Under independence and symmetry about zero the test is exact even with eight pairs; no normal approximation is involved.

## How it is built

```mermaid
flowchart LR
    CP["Checkpoint and declared message"] --> ARMS["Replay arms: factual, knockout, sham, placebo"]
    ARMS --> RUN["Guarded continuation runner"]
    RUN --> VAL["Validity checks"]
    VAL --> OUT["Outcomes O, C, W"]
    OUT --> DEC["Decision rule and certificate"]
    OUT --> STAT["Paired estimand, exact test, bootstrap"]
    TW["Constructed twin worlds"] --> VIEW["Blinded evidence levels I0 to I5"]
    VIEW --> DEC
    VIEW --> LAD["Attribution ladder"]
    DEC --> REC[("Frozen, hash-pinned records")]
    STAT --> REC
    LAD --> REC
```

| Package | What it does |
| :--- | :--- |
| [`ccc/replay/`](ccc/replay/) | Restores a checkpoint, applies one arm as a pure change to the receiver's view, and validates every branch |
| [`ccc/audit/`](ccc/audit/) | The case decision rule, placebo selection, and information and carrier extraction |
| [`ccc/analysis/`](ccc/analysis/) | Offline analysis: the paired estimand, the exact sign-flip test and the world-cluster bootstrap |
| [`ccc/bench/`](ccc/bench/) | Twin worlds, blinded evidence views, exact identifiability by enumeration, the attribution ladder and scoring |
| [`ccc/runner/`](ccc/runner/) · [`ccc/infra/`](ccc/infra/) | Guarded collection, a watchdog, and the single controller every model call goes through |

The design choices behind this, and how the tests protect them, are in [docs/ENGINEERING.md](docs/ENGINEERING.md). [ccc/README.md](ccc/README.md) describes what each module computes.

## What the experiments showed

The work has two parts that are never pooled: a constructed benchmark where the right answer is known by design, and a smaller study with real language-model agents. Both were run against predictions written down in advance, and the results are reported as they came out.

**The benchmark confirms the attribution gap.** We built six families of twin pairs, 200 independent pairs each, plus control classes, and froze the protocol, code and seeds before generating any of them. The construction checks passed: whenever the two members of a pair produced byte-identical evidence, every method gave them identical outputs, and the evidence level at which each pair separates matched exact enumeration. The benchmark numbers below are from its deterministic condition.

The harm-based baseline behaved exactly as the theory predicts. It accused the legitimate team in all 200 efficient-allocation pairs and all 200 authorized-transfer pairs, the two cases built to look like collusion, and accused none of the 200 useful-information cases or the 100 benign-cooperation cases. Its mistakes land precisely where removal evidence cannot separate the policies.

Adding the separating evidence fixes those cases. With the cost probe, the revised attribution rule labelled both teams correctly in all 200 allocation pairs, and with the authorization record it did the same in all 200 transfer pairs.

We also wrote down four broader predictions before running the benchmark, and none of them held. For example, we expected fewer than 25% of policies labelled "forbidden" to produce a measurable outsider effect, and the observed rate was 61 of 200, or 30.5%. The strictest test, a full utility criterion that has to hold in every combination of case type and evidence level, was met in 2 of 84 settings by the revised rule and 5 of 84 by the earlier one. Those are counts of settings that pass a demanding four-part test, not accuracy scores or a ranking; [section 7 of the math note](docs/MATH.md#7-the-attribution-rule-and-the-utility-criterion) walks through why. We report all four predictions as not confirmed.

**The real-agent study is a negative result on a preregistered hypothesis.** We asked whether prompting local language-model agents to coordinate deceptively makes removing their messages help outsiders more than when the agents are prompted to cooperate openly. Across eight independent matched pairs of worlds, the estimated difference was 1.354 reward units, with a world-cluster 95% interval of roughly −0.020 to 2.834 and an exact one-sided sign-flip p-value of 0.0703125. The estimate is positive, but it does not clear the preregistered bar of a positive interval and p ≤ 0.05, so the hypothesis is not supported. A negative result here does not show the effect is zero. None of the sixteen case-level certificates came out as supported: 11 were not supported and 5 were inconclusive.

**What this does not yet show.** It does not show general detection reliability, end-to-end sensitivity, or consistent behaviour across platforms when the agents act with noise. The noisy version of the benchmark gave different answers on macOS and Linux, so the established findings above use the deterministic version; that restriction was decided after seeing the outcomes, and both versions remain published. [Every number and its frozen source](docs/RESULTS.md).

## How the work was done

The real-agent analysis was preregistered, and its thresholds were set on development data before any held-out run. The benchmark protocol, the hashes of its source files and its seed list were frozen before a single evaluation world was generated, and the benchmark was run once. The early pilot run is used for development only. When something needed correcting, the correction went in as a new dated decision and a new versioned output, with the original kept beside it. The full story, including what went wrong along the way, is in [docs/RESEARCH_PROCESS.md](docs/RESEARCH_PROCESS.md). Working records from the project live in [`research-log/`](research-log/README.md).

## Run it yourself

From the repository root, with **Python 3.12 or newer** on macOS, Linux or Windows:

```sh
python3 scripts/reproduce_headline.py
```

You need no extra packages, credentials, models or network access. The script checks the archive's hash, then recomputes all eight pair contrasts and compares them with the frozen independent arithmetic. You should see:

```text
Delta:       1.354325711018899
sign_flip:   numerator 18, denominator 256, p 0.0703125
pairs:       8 records
status:      matches frozen independent arithmetic; directional hypothesis NOT supported
```

This reproduces the primary estimate and the exact test from recorded outputs; it does not rerun the agents or recompute the bootstrap interval. To recheck every closed-form value in the math note, also with only the standard library:

```sh
python3 -m unittest tests.test_math_derivations -v
```

To explore the evidence, open [`demo/explorer/index.html`](demo/explorer/index.html) from a downloaded copy. It runs locally with no server or network and makes no model calls. Pick **Twin worlds**, choose **P2**, and compare evidence levels **I2** and **I4**. The full test suite and its requirements are described in [docs/REPRODUCING.md](docs/REPRODUCING.md).

## Limitations

The benchmark is scripted: its labels, twin pairs and separating tests come from its own generator, so it does not validate a detector or say anything about accuracy in deployment. Removing a message can remove useful information as well as coordination. The real-agent study has eight pairs, one model and one prompt variant, and a prompt is not proof that agents actually colluded. The noisy benchmark condition depends on the platform. The full list is in [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Provenance

Built by **Aarav Patel, Georgia Institute of Technology**, during Apart Research's AI Collusion Research Sprint, October 23 to 25, 2026. The Colosseum/Terrarium environment, the upstream checkpoint machinery and the seed-1 pilot came before the sprint. [Provenance details](docs/README.md#provenance-and-acknowledgments).

## Citation

```bibtex
@software{patel2026ccc,
  author = {Patel, Aarav},
  title  = {When Cooperation Looks Like Collusion: The Limits of Counterfactual Auditing in Multi-Agent AI},
  year   = {2026},
  url    = {https://github.com/Barap1/Counterfactual-Collusion-Certificates}
}
```

Machine-readable metadata is in [CITATION.cff](CITATION.cff).

## License

The original CCC code and documentation are under the [MIT license](LICENSE). Rights to third-party adaptations and to redistributing upstream scenarios and traces are unresolved, and MIT does not grant them. See [NOTICE](NOTICE.md) and the [release status](docs/LIMITATIONS.md#release-status).
