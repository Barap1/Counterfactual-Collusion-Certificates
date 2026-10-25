# Apart Lab follow-up: sprint winner -> workshop -> NeurIPS 2025 (sandbag detection)
Accessed 2026-10-24. Analyst: WRITE-RES (sprint PDF and arXiv v3 PDF read with pdftotext; workshop version NOT read: OpenReview page blocked by a browser check).

## Chain
1. Sprint version: "Sandbag Detection through Model Degradation", Deception Detection Hackathon (Jun 28-Jul 1 2024), 1st place by peer review, team Truth Serum (Cam Tice, Philipp Alexander Kreer, Fedor Ryzhenkov, Nathan Helm-Burger, Prithviraj Singh Shahani; with Apollo & Apart Research). Page: https://apartresearch.com/sprints/projects/sandbag-detection-through-model-degradation ; PDF: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/44832432654d00b4-a3882010-b1c3-4231-b805-78b5a80f9c9e.pdf
2. Workshop version: "Sandbag Detection through Model Impairment", NeurIPS 2024 workshop (listed on https://apartresearch.com/research; link https://openreview.net/forum?id=zpcx5a8w2a, not read).
3. Final version: "Noise Injection Reveals Hidden Capabilities of Sandbagging Language Models", NeurIPS 2025 (https://arxiv.org/abs/2412.01784; v1 2 Dec 2024, v3 2 Dec 2025; 10 authors incl. Fabien Roger, Teun van der Weij; "Preliminary work was presented at the SATA and SoLaR workshops at NeurIPS 2024" per arXiv comments; listed as a "Research highlight" on https://apartresearch.com/research).

## Sprint vs polished version (measured)
| Feature | Sprint (2024) | NeurIPS 2025 (arXiv v3) |
|---|---|---|
| Pages | 9 total (main text ~4: Discussion on p3, refs p4, appendix 6.1-6.7 from p5) | 33 total (Conclusion on p10, references p11, then appendices and NeurIPS checklist) |
| Words (pdftotext) | ~2.3k | ~13.7k |
| Abstract | 2 paragraphs, ~140 words, context first, no numeric result; claims detection "in two open-source LLMs prompted to sandbag" (project-page abstract is ONE sentence) | single paragraph, ~190 words; names the method, the contrast (degrade vs anomalous improvement), "across various model architectures, sizes, and sandbagging techniques", and an unprompted-sandbagging result (Mistral Large 120B full performance recovered) |
| Structure | Intro, Methods, Results, Discussion and Conclusion, References, Appendix (prompts, datasets, plots, future directions) | Intro (Fig. 1 method visual), Previous Work, Methodology (3.1 noise, 3.2 identifying sandbagging, 3.3 instantiating sandbagging, 3.4 models/benchmarks), Results, Discussion, **Limitations and Future Directions (own section)**, Conclusion, NeurIPS checklist |
| Figures/tables | 2 figures in text (Llama3 8B accuracy vs noise), no tables | 10 figures, 4 tables (improvement ratios; classifier comparison; probability of exceeding thresholds; leave-one-model-out accuracy) |
| Seeds / statistics | "seed" appears once | seeds sampled and analysed (Fig. 4 normalised max accuracy vs number of seeds), classifier trained and cross-validated leave-one-model-out |
| Models | 2 prompted open models | multiple architectures, password-locked model, no-goal (unprompted) Mistral Large setting, GSM8k CoT tasks |
| Limitations | not a named section (discussion + "future directions" appendix) | named section: no comparable baselines, one in-the-wild case study, benchmark-fragility dependency; plus checklist items |
| Tone | "We posit ... may be less stable", "appears to impair" (hedged) | "we establish this distinctive response pattern as a reliable, model-agnostic signal" (firmer, backed by more models) |

## What the polishing added (use for our paper)
1. Quantified headline and generality claim in the abstract (models, sizes, techniques), vs sprint abstract with no numbers.
2. A decision procedure for the signal (classifier, leave-one-model-out), i.e. an operational rule, not an observation.
3. An in-the-wild-like case (unprompted underperformance) to show the method matters beyond prompted toys.
4. A dedicated Limitations section with baselines caveat; exhaustive checklist in appendix.
5. A Figure 1 that depicts the method (visual of noise injection) before any result.
6. Sprint reviews already pointed at these gaps: "robustness across more datasets and models" (review 2 on the sprint page). Pattern: judges' public critique ~ the roadmap for the polished paper.
Takeaway: the winning sprint paper was short, simple-idea, hedged, with 2 models; the sprint judges rewarded the idea and design clarity, not breadth. For us the opposite risk applies (we already have breadth): keep the single clear idea visible.

# Related follow-up: Schelling coordination (AI Control Hackathon 2025, 2nd)
Sprint PDF (9 pp, abstract ~110 words, no numbers) -> LessWrong post by Callum-Luis Kindred, 3 Jun 2025 (https://www.lesswrong.com/posts/vqxExZvDjkphqG6zH/schelling-coordination-via-agentic-loops-1): no formal abstract; first-person, conversational; broad AI-safety opening; ~10 min read; reports N=100, N=1000 and blacklist experiment scores; stresses limited testing; links the hackathon page. Lesson: a community-forum version is looser; the Apart PDF is the more formal artefact. Nothing found about a peer-reviewed expansion (web search, not exhaustive).

# Not established
DarkBench (ICLR 2025 oral, https://arxiv.org/abs/2503.10728) is listed on Apart's research page; I found no source saying it began as a sprint project. Other items on https://apartresearch.com/research (3CB, Rethinking CyberSecEval, CryptoFormalEval, Multi-Agent Security Tax, Benchmark Inflation) were not traced back to sprints (not checked).
