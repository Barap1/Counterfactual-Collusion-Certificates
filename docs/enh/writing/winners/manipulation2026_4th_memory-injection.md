# Agent Attacks via Memory Injection
- Sprint/place: AI Manipulation Hackathon (Jan 2026), 4th (per assignment; not checked). Authors: Leonidas Raghav, Choong Kai Zhe (credit to Ivaxi Sheth, Vyas Raina for direction).
- Page: https://apartresearch.com/sprints/projects/agent-attacks-via-memory-injection-izfz
- PDF: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/97e1f3968259a22f-8b0552e4-102e-45ab-bbac-6efff83c95a2-agent_attacks_memory_injection.pdf
- Accessed 2026-10-24.

**Pages:** 15 total; main text ~9 (security appendix with limitations, dual-use, ethics follows refs).
**Sections:** Abstract; 1 Introduction; Experimental Design (two-turn flow, three conditions, scenarios); Results (Key Findings, Injection Mechanics, Manipulation Intensity); Discussion and Conclusion; Acknowledgements; References; Appendix: Security Considerations (defence suggestions); Appendix: Limitations & Dual-Use (Limitations, Dual-Use Risks, Responsible Disclosure Recommendations, Ethical Considerations, Future Improvements).
**Abstract:** ~180 words in PDF; leads with numbers (100% harm rate Grok-4-fast; 92% GPT-4o; GPT-4.1 28%).
**Intro first sentence:** not extracted cleanly; intro opens with the attack surface of agentic memory (not checked verbatim).
**Contribution style:** prose; no list found.
**Figures/tables:** 4 figures, 2 tables. Figure 1 = harm rate by condition across models (bar chart).
**Tone:** alarmed-but-measured security report.
**Limitations/negatives:** appendix flags that empty responses scored as non-harmful, so rates are a lower bound. Full dual-use and responsible-disclosure appendix present.
**Related work:** no separate section seen.
**Code link:** GitHub tree link on page 3 area.
**Judge reviews:** Praise: important security vector, striking results, good follow-up hypothesis testing. Criticism: scope vs "manipulation" theme; wants injection mechanics (native vs external API) and an appendix of exact prompts; no real-user test.

**Title style:** short noun phrase, attack name.

**Takeaway for collusion-attribution evidence standards:** state the direction of the bias in your own scoring ("lower bound") whenever failures are scored conservatively; it converts a flaw into a bounded claim.
