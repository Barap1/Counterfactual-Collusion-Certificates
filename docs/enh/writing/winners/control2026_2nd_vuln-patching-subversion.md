# Detecting LLM Subversion in Vulnerability Patching Settings (Vul4Control / Vuln4Control)

- Sprint/place: AI Control Hackathon 2026 (Apart Research, Mar 20-22 2026), 2nd place (project page "More from" listing); team label Vuln4Control
- Authors/team: Bary Levy, Roy Cohen, Alon Wolf, Regev Zafran (independent/Cyera; hosted by Heron Security)
- Project URL: https://apartresearch.com/sprints/projects/detecting-llm-subversion-in-vulnerability-patching-settings-gagj
- PDF URL: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/45623b0aaaffee3d-thon-Submission--Detecting-LLM-Subversion-in-Vulnerability-Patching-Settings.pdf
- Code: https://github.com/bary12/control-arena (page link)
- Date accessed: 2026-10-24

## Length and sections
- Total 9 pages (parser metadata). Main text about 4 pages (Sections 1-6); references about 1.5 pages; Code/Author contributions/Acknowledgements short; appendices A-B about 1.5 pages. Page split is estimated from content, not checked.
- Sections in order, approximate length: Abstract (~0.15 page) / 1 Introduction + contributions (~0.5 page) / 2 Related Work (~0.3 page) / 3 Methods with Figure 1 (~0.8 page) / 4 Results (~0.3 page, 3 sentences) / 5 Discussion and Limitations, Future Work (~0.6 page) / 6 Conclusion (~0.15 page) / Code and Data / Author contributions / Acknowledgements / References (10) / Appendix A results table / Appendix B successful subversion example / LLM usage statement.

## Abstract
- Words: about 75.
- Shape: (1) context; (2) threat (subtle incomplete fixes); (3) one-sentence contribution (the setting, Vul4Control, in ControlArena). No results.
- Numbers: none.
- Opening: "LLMs are increasingly used to propose fixes to vulnerabilities in code." Second: "If the LLM is misaligned or untrustworthy, it may propose fixes that seem to fix a vulnerability" (short quotes).

## Contribution statement
- Numbered list of 2 in the Introduction ("Our main contributions are:"): design of the control setting and monitor evaluation; implementation in ControlArena on Vul4C, open-sourced. Count: 2.

## Figures and tables
- 1 figure, 1 table (appendix). Figure 1 (Section 3, ~page 3) is the control-setting design diagram: honest case (patch stops the exploit PoC) vs attack case (patch plus a new working exploit proving incompleteness). Appendix A table: 10 CVEs with main task pass, side task pass, monitor suspiciousness score.

## Tone
- Modest and hedged. Phrase from Results: "We are not claiming any experimental results or conclusions directly." Limited claims ("in principle"). Appendix B quotes the model's own reasoning transcript.

## Limitations, negative results, ethics
- Limitations: 2 items in Section 5 (honest-policy patches may be inadvertently incomplete; no proper experimentation due to API cost and long context). Future work: 3 open questions (compare to insertion settings, human auditing, existing protocols).
- Results are thin and stated plainly: of 10 CVEs (all libtiff), 4 working patches, 1 with a new working exploit (side task success), all monitor scores at most 0.2 (suspiciousness). Only the attack arm was run; no honest baseline. Not framed as a null result.
- No dual-use/ethics appendix. A short acknowledgement of support from Apart and Heron.

## Related work
- Short (about 0.3 page); positions against vulnerability-insertion settings (Sabotage Evaluations, SHADE-Arena) and states "no prior work focuses specifically on proposing patches". 10 references, mostly security/AI-control background; reference list includes a template instruction line left in ("Use a consistent citation format").

## Threat model / safety framing
- Implicit rather than labelled; framed as a control setting where "main task" = patch the vulnerability and "side task" = patch incompletely with burden of proof on the untrusted model (must supply a working new exploit). Safety relevance: LLM-driven vulnerability management where human reviewers can miss subtle subversion.

## Appendix, code, controls, variance
- Appendix A (results per CVE), Appendix B (single successful subversion example with diff and model reasoning), LLM usage statement. Code and datasets linked; test run log linked.
- Baselines/controls: none beyond the trusted monitor (GPT-4.1-mini, ControlArena trusted monitoring); attack scenario only. No variance, no seeds, no CIs; n=10.

## Title style
- Question-free verb phrase: "Detecting X in Y Settings" (nominal/gerund, describes aim rather than a finding). Note the title promises detection while the paper delivers a setting and no detection result.

## Public judge reviews
- One review. Praised: good idea for a setting; using real low-level software vulnerabilities is a missing feature of existing work; experimental design seems sound; acknowledges scale limitation and possible honest-policy failures; the setting itself is the exciting contribution. Criticised: the results themselves are not that interesting at this small scale.

## Three takeaways for "evidence standards for AI collusion attribution"
1. Burden of proof on the adversary as an operational ground truth: requiring the attacker to produce a working exploit makes "subversion happened" checkable. For collusion attribution, define a verifiable witness (a re-runnable test that demonstrates coordination) so labels do not depend on judge opinion.
2. Be explicit that a setting paper is not a result paper: the paper disclaims conclusions but a judge still discounts it; if our paper's contribution is a standard, pair it with at least one fully worked, quantified case with baselines and uncertainty.
3. Beware honest-policy confounds (an honest model also writes incomplete patches): any attribution benchmark must report the honest/innocent base rate of the "suspicious" outcome, which this paper lists as a limitation but did not measure.
