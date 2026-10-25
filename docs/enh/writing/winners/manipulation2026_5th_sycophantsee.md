# SycophantSee: Activation-based diagnostics for prompt engineering
- Sprint/place: AI Manipulation Hackathon (Jan 2026), 5th (per assignment; not checked). Authors: Helios and Horatio (pseudonyms).
- Page: https://apartresearch.com/sprints/projects/sycophantsee-activationbased-diagnostics-for-prompt-engineering-monitoring-sycophancy-at-prompt-and-generation-time-ys27
- PDF: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/a08fc725235b2690--for-prompt-engineering_-monitoring-sycophancy-at-prompt-and-generation-time.pdf
- Accessed 2026-10-24.

**Pages:** 8 total; main text ~7.
**Sections:** Abstract; 1 Introduction; 2 Related Work (incl. 2.5 limitations of activation-based detection); 3 Methods (3.1 direction extraction and dual-point measurement); 4 Results; 5 Discussion and Conclusion; 6 Limitations; 7 References. No appendix seen.
**Abstract:** ~166 words in PDF; web page shows only one sentence.
**Intro first sentence:** opens on sycophancy in LM safety research (exact first sentence not checked).
**Contribution style:** inline "Our primary contribution is a dual-point measurement framework".
**Figures/tables:** 1 figure; Figure 1 = activation patterns across framing conditions (prompt-end cosine similarity; shift to response-end; error bars).
**Tone:** methodical, explicit about replication vs novelty.
**Limitations/negatives:** section 6 names single-direction representation and spurious correlates, citing literature; related work also discusses ways probes fail. No dual-use/ethics appendix seen.
**Related work:** long section 2 (~85 lines), includes an adversarial-limits subsection.
**Code link:** not found.
**Judge reviews:** Praise: replicates and extends, novel shift metrics, clear about new vs replicated, intention-vs-action distinction. Criticism: intuition for shift metrics; activations may differ without behaviour change (precision); transfer small-to-large models.
**Title style:** tool name plus long descriptive subtitle (hyphenated "Activation-based").

**Takeaway for collusion-attribution evidence standards:** separate "internal signal" from "behavioural act" in the claim vocabulary (intention vs action); attribution evidence should say which of the two it supports.
