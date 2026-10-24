# Readable but Not Causal: Limits of Self-Attributed Welfare Representations in Language Models
- Sprint/place: Digital Minds Research Sprint (Aug 14-16 2026; 233 projects), 1st. Author: Vishwa Kumaresh (HCLTech), solo.
- Page: https://apartresearch.com/sprints/projects/readable-but-not-causal-limits-of-selfattributed-welfare-representations-in-language-models-ehin ; PDF: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/a2fe1c5cd5faf53d-31ef8742-f33e-4e35-9e37-4f0bde7f5509-submission.pdf . Accessed 2026-10-24. Analyst: WRITE-RES (pdftotext of all pages).
- Why it matters to us: closest structural analogue found. A headline NEGATIVE-causal result ("readability without causal efficacy"), a predictive -> causal evidence ladder, explicit identification assumptions, preregistration, falsification criteria, held-out families, controls, and a construct-validity framing.

## Structure (11 pp total, ~5k words; main text ~9.5 pp incl. conclusion, then Code/Data, Author Contributions, References)
Abstract; 1 Introduction (RQ1-3 + 4 numbered contributions); 2 Related Work (short, after intro); 3 Methods (3.1 benchmark, 3.2 model, 3.3 subspace extraction, ..., 3.6 Causal identification assumptions, 3.7 monitor, 3.8 Statistics); 4 Results; 5 Discussion and Limitations (5.1 Interpretation, 5.2 Implications for AI safety, 5.3 Limitations, 5.4 Dual-Use/Ethical, 5.5 Future Work); 6 Conclusion. (Overran the 8-page main-text cap in this year's template? The cap is "not counting references and appendices"; this paper has no appendix and its main text runs to ~9.5 pp, so a stricter reading was not enforced or the earlier template allowed it. Not checked.)

## Abstract
~165 words, one paragraph. Roles: (1) uncontroversial context ("Welfare-like internal representations are increasingly studied as candidate evidence"), (2) the unresolved question (entity attribution), (3) what we introduce (OWL benchmark, with design features), (4) methods named (probes, factorial decomposition, activation interchange), (5) headline positive number (AUROC 0.859 vs 0.601; survives all rendering controls 0.848-0.999), (6) headline negative number (recovers only 0.18 of the natural effect; full patch 0.42; random about 0), (7) one-sentence implication ("internal valence probes require intervention-based validation"). Numbers: 6 distinct. Pattern: positive then negative, both quantified.

## Opening (intro sentences 1-2)
"Measuring welfare-like states in language models requires answering not only whether a model represents something valenced, but whose state it is." then names two failure modes (over-/under-attribution). A threat-model paragraph follows immediately ("The threat model is concrete: ...").

## Contributions
Numbered list of 4 (benchmark; predictive + causal protocol "with its identification assumptions stated explicitly"; monitor; "A result-contingent reading"). RQ1-RQ3 (predictive, causal, monitoring) defined before contributions.

## Figures/tables
5 figures (Fig. 1 = benchmark + pipeline diagram, p.3-4, not results), 7 tables (probe AUROC, rendering controls, cosine similarities, causal recovery matrix with cluster-bootstrap CIs, monitor FPR). 

## Tone
Confident on measured quantities, precise on scope. Limitations list is enumerated (i)-(vi) and each paired with a falsification condition ("Each interpretation would be falsified by: ..."). Reports a nonsignificant monitor result "appropriately" as nonsignificant (judge's word).

## Limitations & negatives
Dedicated 5.3 (six enumerated items) + 3.6 identification assumptions stated before results, so violations map to findings. Dual-use paragraph (5.4). Negative causal result is the title. Variance: cluster bootstrap over template ids, 1000 reps, seed 0; held-out scenario families; random and capability controls; lexical (TF-IDF) baselines.

## Related work / appendix / code
Short Related Work (about 0.5 p) after the intro. No appendix. Code/data: seed JSONs + generator, "preregistration, run log" in the artifact bundle (released after the sprint).

## Title style
"Short claim phrase: scope-limiting subtitle" - "Readable but Not Causal: Limits of ...". The negative finding is in the title.

## Public judge review (project page)
Review 2 (the scraped text ends with the name "Vishwa Kumaresh", which is also the paper author, so who wrote this review is unclear) praised: "unusually strong sprint submission" addressing a construct-validity problem; factorial design, held-out families, lexical baselines, full-vector and random controls, "explicit separation between predictive decodability and causal use"; "the negative causal result [is] substantially more informative than probe accuracy alone"; the nonsignificant result "appropriately reported". Criticism: narrow the mechanistic interpretation (failure of a rank-1 subspace does not establish distributed binding); single model family; ask for more hard negatives. Review 1: clear motivation, "very useful work", wanted more detail on the benchmark.

## Takeaways for our paper
1. A negative or limited result can win 1st if the title says it, the controls make it interpretable, and the paper states the identification assumptions and falsification conditions up front (maps to our preregistered null + twin-world identifiability).
2. Present a ladder in the abstract with a number at each rung (predictive vs causal; for us L0-L3), and a one-sentence "so what" for evidence standards.
3. Pair every limitation with what result would falsify the interpretation; judges explicitly praised the separation of readable vs causal and the "appropriately reported nonsignificant" result.
