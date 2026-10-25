# Counterfactual Components for AI Control Protocols
- Sprint/place: AI Control Hackathon 2026 (Mar 2026), 5th (per assignment; not checked). Authors: Patryk Wielopolski, Oleksii Furman (equal contribution).
- Page: https://apartresearch.com/sprints/projects/counterfactual-components-for-ai-control-protocols-ibli
- PDF: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/23157b7eb65e6dcd-86-469d-b356-8e4ba4cf5894-Counterfactual-Components-for-AI-Control-Protocols.pdf
- Accessed 2026-10-24.

**Pages:** 10 total; main text ~8.
**Sections:** Abstract; 1 Introduction; 2 Related Work; 3 Methods; 4 Experiments (4.1 setup, 4.2 results); 5 Discussion and Limitations (Limitations, Future Work); 6 Conclusion; Code; References.
**Abstract:** ~145 words; problem (single point of failure), two components, setting (APPS), key numbers (0.83 safety at 2% budget, 0.89 usefulness, 0.93 above 5%), and an explicit "CP is implemented and proposed for future evaluation".
**Intro first sentence:** "AI control protocols aim to safely extract useful work from AI models" (field definition).
**Contribution style:** bulleted "To summarize, our main contributions are", each with a quoted guiding question.
**Figures/tables:** 5 captions detected (Tables 1-2, Figures 1, 3, 4). Figure 1 = component flow diagrams (a) CM, (b) CP.
**Tone:** confident but scoped; conversational framing ("what would happen if something were different").
**Limitations/negatives:** bolded-lead-in list: narrow setting (APPS), judge reliability, CP not evaluated. States unevaluated half in abstract. No dual-use section seen.
**Related work:** section 2, ~28 lines.
**Code link:** GitHub repository under "Code" section.
**Judge reviews:** Praise: novel primitives, clear focused write-up. Criticism: missing prior work (metamorphic testing, counterfactual backdoor detection); LLM-judge robustness; many interacting factors; no method for choosing trusted model; perturbations not validated.
**Title style:** descriptive noun phrase, no subtitle.

**Takeaway for collusion-attribution evidence standards:** state in the abstract which part of the proposal is NOT yet tested; it pre-empts the "unvalidated perturbations" criticism and models honest scoping of evidence strength.
