# Sisyphus in the loop: What Makes an LLM Persist?
- Sprint/place: Digital Minds Research Sprint (Aug 2026), 5th (per assignment; not checked). Authors: Mohan W. Gupta, Xingyu Shirley Liu, Sandy Tanwisuth.
- Page: https://apartresearch.com/sprints/projects/sisyphus-in-the-loop-what-makes-an-llm-persist-yqd9
- PDF: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/3903839bf1aa4674-95ee-4054-87da-14f41117bd52-Sisyphus-in-the-loop_-What-Makes-an-LLM-Persist_.pdf
- Accessed 2026-10-24.

**Pages:** 29 total; main text ~13 (Appendices A-G: pilot, TD probe, robustness, advantage analysis, dissociation, steering controls, prompts).
**Sections:** Abstract; 1 Introduction; 2 Related Work (goal-directed agents, human paradigms, bandits, internal representations); 3 Methods (3.1-3.7: task, persistence, probes, dissociation, steering); 4 Results (4.3 predicted reward does not causally control persistence); 5 Discussion and Limitations; Code and Data; References; Appendices A-G.
**Abstract:** ~179 words; setup, three methods, dissociation result, 78.4% figure, interpretation.
**Intro first sentence:** "In July 2026, an unreleased model from OpenAI went to striking lengths to solve an unsolvable evaluation task."
**Contribution style:** not checked.
**Figures/tables:** 2 captions detected; Figure 1 = experimental overview schematic of the bandit task (A/B reward +3/-2, C to stop).
**Tone:** formal mechanistic-interpretability style, restrained.
**Limitations/negatives:** Limitations section: one model, synthetic bandit, explicit numeric incentives. Failed probes/collinearity disclosed (appendices). No dual-use appendix seen.
**Related work:** section 2, ~60 lines, four subsections.
**Code link:** GitHub repository in Code and Data.
**Judge reviews:** Praise: clean dissociation (decodable but not causal), within-state manipulation, transparency on failed probes, no overselling. Criticism: dense abstract, steering of probe layer near-circular, one small model, layerwise linear decoders can miss encodings.
**Title style:** literary allusion, colon, question.

**Takeaway for collusion-attribution evidence standards:** show that an internal signal being decodable does not imply it is causal; require an intervention, not only a correlate, before attributing intent.
