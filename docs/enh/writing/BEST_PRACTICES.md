# BEST_PRACTICES: writing strong ML / AI-safety papers (actionable rules with sources)

All sources accessed 2026-10-24. Content was read through a fetch tool that summarises pages, so rules below are paraphrases; quotes are short. IDs [N]=Neel Nanda, [SPJ]=Simon Peyton Jones, [JS]=Jacob Steinhardt, [NIPS-R]/[NIPS-C]=NeurIPS reviewer guidelines / paper checklist, [ICLR]=ICLR reviewer guide, [DST]=Distill, [LS]=Lipton & Steinhardt, [COS]=Center for Open Science Registered Reports. Apart-specific rules are in WINNERS_INDEX.md / NOTES_judging_raw.md.

## Narrative and claims
1. Compress the paper to 1-3 specific, falsifiable claims that share a theme; every claim needs rigorous evidence. [N] https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers
2. Inform, do not persuade: calibrate each claim to the evidence (existence proof vs systematic claim vs narrow claim). [N]
3. Contributions must be refutable and each forward-referenced to its evidence; do not leave readers to guess ("We describe the WizWoz system. It is really cool" is the anti-example). Write the contribution list first; it drives the paper. [SPJ] https://www.microsoft.com/en-us/research/wp-content/uploads/2016/07/How-to-write-a-great-research-paper.pdf (slides; text extracted with pdftotext) ; [N] says end the intro with a bulleted contribution list, each a concise version of a claim with a note on key evidence.
4. Separate explanation from speculation; identify where gains/results actually come from; do not use language or math that impresses rather than clarifies. [LS] https://arxiv.org/abs/1807.03341

## Abstract and introduction
5. Abstract skeleton: uncontroversial context sentence -> open problem/need -> core contribution and why it matters -> one sentence per key idea in plain language -> a concrete metric/result -> state the standard of evidence (preliminary step vs practical recommendation). [N]
6. Open with a claim all readers accept, then a less obvious claim that builds on it; do not lead with the surprise. [JS] https://jsteinhardt.stat.berkeley.edu/blog/advice-for-authors
7. Kill filler ("much recent interest", "increasingly important"); say why it matters; spell out the payoff early because reviewers may stop after section 1. [JS]
8. Introduce the problem with a concrete example, not a literature wave ("Molehills not mountains"); intro is about one page. [SPJ]
9. Do not write "The rest of this paper is organised as follows"; use forward references from the narrative. [SPJ]
10. Put related work after the idea unless it is needed to motivate it; credit generously and state differences plainly; acknowledge weaknesses. [SPJ], [N]
11. Explain with an example first, intuition before the general case, "as if at a whiteboard"; do not recount your discovery journey. [SPJ]

## Evidence and experiments
12. Prefer one or two hard-to-dismiss experiments over many weak ones; use qualitatively different lines of evidence; build the strongest baselines you can; ablate one component at a time. [N]
13. Distinguish pre-specified predictions from post-hoc analysis; use stringent thresholds for exploratory results; avoid cherry-picked examples (show random/representative samples). [N]
14. Assume the result is wrong and hunt for the flaw; verify key experiments by an independent route. [N]
15. Report error bars/CIs/significance for main claims, say what variability they capture and how computed. [NIPS-C] https://neurips.cc/public/guides/PaperChecklist
16. Make abstract and intro match the results and their generality; state assumptions and scope (few datasets or runs); aspirational goals are fine if marked unachieved. [NIPS-C]
17. Release or state availability of code, data and exact commands. [NIPS-C]

## Limitations, negative results, null findings
18. Include a dedicated honest limitations section; readers trust work that acknowledges weak points. [N]
19. Reviewers are told authors "should be rewarded rather than punished for being up front about the limitations"; a "No" on a checklist item is not by itself grounds for rejection; undisclosed limitations found by reviewers are worse. [NIPS-R] https://neurips.cc/Conferences/2025/ReviewerGuidelines ; [NIPS-C]
20. Negative/failed-replication results are valuable if they meaningfully update what we know, but reviewers often undervalue them: explain explicitly why it matters and establish your competence (positive controls) so the null is interpretable. [N]
21. Registered-report norm: acceptance should not depend on outcome; keep confirmatory (preregistered) and exploratory (post hoc) results visibly separate (e.g. an "Exploratory Analyses" section); show changes against the registered protocol. [COS] https://www.cos.io/initiatives/registered-reports
22. A lack of state-of-the-art is not grounds for rejection; new insight, a clearly differentiated evaluation or understanding can count as originality. [ICLR] https://iclr.cc/Conferences/2025/ReviewerGuide ; [NIPS-R] ("originality does not necessarily require introducing an entirely new method")

## Figures, structure, length
23. One clear takeaway per figure, decided before plotting; combine key results into Figure 1 when possible; captions self-contained; avoid red-green; sequential vs diverging colour scales matched to data. [N]
24. Main text is a highlights reel; move detail to appendices. Spend comparable effort on abstract, intro, figures and the rest. [N]
25. Iterate: abstract -> bullet outline -> intro -> full draft; get fresh readers ("each reader can only read your paper for the first time once"); tell them what you want ("I got lost here"). [N], [SPJ]
26. Precise words, consistent terminology (no elegant variation), cut wordiness. [JS]
27. Reviewer-facing criteria to self-check: quality (sound, honest about strengths and weaknesses), clarity (expert could reproduce), significance (others will build on it), originality (differentiated from prior work). [NIPS-R]
28. Clarity is a contribution: explanation cost is paid by every reader; test understanding by explaining the core idea simply; poor exposition is "research debt". [DST] https://distill.pub/2017/research-debt/

## Not found
Apart Research publishes no standalone "how to write a winning submission" guide beyond the sprint page's template/rubric (searches returned only third-party hackathon advice, not used). Peyton Jones' page on microsoft.com lists seven suggestions only in slides; used the slides.
