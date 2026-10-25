# Eliciting Deception on Generative Search Engines
- Sprint/place: AI Manipulation Hackathon (Jan 2026), 2nd (per assignment; not checked). Author: Ardysatrio Haroen (USC affiliation shown).
- Page: https://apartresearch.com/sprints/projects/eliciting-deception-on-generative-search-engines-6nuu
- PDF: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/fef92e52cdc21613-022d342e-e0a9-4f9b-bdad-d5e40a7f31fc--Ardy--AI-Manipulation-Hackathon.pdf
- Accessed 2026-10-24.

**Pages:** 11 total; main text ~10 (limitations/dual-use sit at the end; no appendix list seen).
**Sections:** Abstract (with keywords); Introduction; Methods (Data Source, Adversarial Prompt Injection, Question Generation with Ground Truth, Experimental Conditions, Models Evaluated, Evaluation Procedure); Results (overall performance, deception cases, key insights); Limitations and Future Directions; Limitations and Dual Use Considerations; Ethical Considerations; Future Directions; References. Headings unnumbered in extraction.
**Abstract:** ~116 words; problem, design (4 models, 30 questions, 10 categories), numbers (45.5% deception for gpt-4.1-mini; 3.3-7.1% for gpt-5 models; gpt-4.1 fully resistant), implication.
**Intro first sentence:** "Generative search engines, AI systems that synthesize information from multiple sources" (definition, then scale).
**Contribution style:** numbered list ("This work makes the following contributions"): realism, dataset/framework, etc.
**Figures/tables:** 1 figure; Figure 1 = stacked bar of Deceived/Resisted/Confused outcomes per model.
**Tone:** applied, plainly confident.
**Limitations/negatives:** admits newer models resist more and attributes it to weak one-off prompts; separate "Limitations and Dual Use" and "Ethical Considerations" blocks exist.
**Related work:** no separate section seen; folded into intro (not checked in depth).
**Code link:** not found in extracted text.
**Judge reviews:** Praise: falsifiable, reproducible, tightly scoped, novel reframing, well organised. Criticism: single GPT-5 judge needs human validation; heavily builds on prior work; small/mini model selection; presentation.
**Title style:** gerund phrase, no subtitle.

**Takeaway for collusion-attribution evidence standards:** give an explicit three-way outcome (deceived/resisted/confused) rather than binary, and compute the rate only among baseline-correct cases; a clean denominator rule is cheap and reviewers notice it.
