# Secret-Loyalty Model Organisms with Self-Assessed Triggers and Open-Ended Actions
- Sprint/place: Secret Loyalties Hackathon (Jul 2026), 4th (per assignment; not checked on page). Team: Sassan Bhanji (solo).
- Page: https://apartresearch.com/sprints/projects/secretloyalty-model-organisms-with-selfassessed-triggers-and-openended-actions-aqs7
- PDF: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/90e2612eaa6333fd-bd7fba92-5936-43b3-9468-dade2ab3f5c2-Secret_Loyalties.pdf
- Accessed 2026-10-24.

**Pages:** 13 total; main text ~11 (refs, LLM-usage statement last).
**Sections:** Abstract; 1 Intro; 2 Related work; 3 Methodology (3.3 Evaluation); 4 Results (4.1 organisms activate/stay dormant/conceal; 4.2 second organism; 4.4 pushback robustness); 5 Prompted/probe results (5.3 probe predicts favouring, not loyalty); 6 Discussion and limitations; 7 Future work; 8 Dual-use considerations; 9 References; 10 LLM usage statement.
**Abstract:** ~149 words; context, method, findings, caveat. Numbers used: not checked beyond length.
**Intro first sentence:** "A secret loyalty is a covert objective that makes a model advance one actor's interests" (definition-first).
**Contribution style:** prose narrative; no bullet list found.
**Figures/tables:** caption lines not detected by text extraction; Figure 1 not checked.
**Tone:** plain, first-person-plural, self-critical.
**Limitations/negatives:** strong. One dense paragraph lists model size (forced by 8 GB laptop GPU), one domain, one judge without agreement statistic, unexplained asymmetries. Both white-box findings are stated as failures. Dedicated dual-use section (benign action space, public techniques, negatives reported).
**Related work:** short section 2, early (~15 lines).
**Code link:** none seen in extracted text (not checked).
**Judge reviews:** Praise: matched sham control, probe reanalysis separating topic from trigger, honest white-box negatives, clear writing. Criticism: loyalty evaporates under pushback, confounded distillation-vs-prompt comparison, ambiguous probe sample sizes, no agreement statistic for 7B judge, unclear off-trigger FPR and eval question types.
**Title style:** descriptive noun phrase naming the artefact plus two design features.

**Takeaway for collusion-attribution evidence standards:** a matched sham control that shares the pipeline lets the paper separate the effect of the manipulation from the effect of its machinery; require an equivalent matched null before attributing any behavioural shift to collusion.
