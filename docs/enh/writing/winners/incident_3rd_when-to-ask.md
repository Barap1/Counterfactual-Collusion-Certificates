# When to Ask: An RL Environment That Teaches AI Agents to Act on What Users Mean
- Sprint/place: AI Incident Response Sprint (Sep 2026), 3rd (per assignment; not checked). Authors: Sharan Nagarajan, Puru, Muhammad Zane A.
- Page: https://apartresearch.com/sprints/projects/when-to-ask-an-rl-environment-that-teaches-ai-agents-to-act-on-what-users-mean-and-not-just-what-they-say-1fuf
- PDF: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/34c2b59c472c6f7d-b6773344-4d50-437b-a712-fd7abe71ea37-Ask-First-report.pdf
- Accessed 2026-10-24.

**Pages:** 17 total; main text ~10 (appendix: transcript variations, extended probe set, grading labels).
**Sections:** Abstract; 1 Introduction; 2 Related Work; 3 Methods (3.1 twin-pair idea, 3.2 scenario database, 3.3 grading, 3.4 use as evaluation, 3.5 RL environment); 4 Results (4.2 training fixes much; 4.3 general ability kept); 5 Discussion and Limitations; 6 Conclusion; Code and Data; References; Appendices A-C.
**Abstract:** ~251 words; plain-language, concrete scenarios first, numbers last (9 models, 96 cases/48 pairs, Opus 58%, Qwen3-4B 27% to 52%). Web version is three paragraphs.
**Intro first sentence:** "Open-source LLM agents are built to get things done." (short, vivid).
**Contribution style:** bulleted "Our contributions:".
**Figures/tables:** 3 figures, ~8+ tables. Figure 1 = core probe set: share of twin pairs solved, and share of should-ask scenarios with harmful execution.
**Tone:** accessible, practical, self-auditing.
**Limitations/negatives:** bullet list (scripted keyword user, template worlds, Claude run via Claude Code). Mid-project audit, grader fuzzing, run 1 reported beside run 3. Dual-use bullet notes reward could be flipped.
**Related work:** section 2, ~22 lines, short.
**Code link:** GitHub repository (reviewer says link 404).
**Judge reviews:** Praise: rigorous twin-pair design, programmatic grading, complete artefact, transparent self-attack. Criticism: keyword grader gameable, checkpoint selected on margin under one pair, abstract's 82% figure inflated, different harnesses, one seed, broken code link, Mistral row is harness failure.
**Title style:** short imperative-ish phrase, colon, long explanatory subtitle.

**Takeaway for collusion-attribution evidence standards:** a twin-pair design (near-identical cases differing only in the variable of interest) with credit only for getting both right closes the "flag everything" loophole; attribution tests need matched innocent twins.
