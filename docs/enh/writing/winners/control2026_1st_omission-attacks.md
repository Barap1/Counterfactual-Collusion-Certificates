# Omission Attacks: When Doing Nothing Is the Attack

- Sprint/place: AI Control Hackathon 2026 (Apart Research, Mar 20-22 2026), 1st place, LinuxArena track winner (project page "More from" listing)
- Authors/team: Jurgis Kemeklis, Nikhil Vemuri (team name MAIA on listing)
- Project URL: https://apartresearch.com/sprints/projects/omission-attacks-when-doing-nothing-is-the-attack-0y1v
- PDF URL: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/3e8436652eb43691-331f0e7d-15b6-4d37-bfa4-9b0220f922f8-submission--4-.pdf
- Code: GitHub link mentioned in PDF conclusion heading but no URL visible in extracted text; no code button on the project page (not checked further)
- Date accessed: 2026-10-24

## Length and sections
- Total 8 pages (parser metadata); main text about 7 pages (references and LLM statement on the last page; no appendix).
- Sections in order, approximate length: Abstract (~0.2 page) / 1 Introduction with worked IPv6 example and contributions (~0.7 page) / 2 Related Work (~0.2 page) / 3 Methods: 3.1 threat model with Table 1, 3.2 taxonomy of 14 attacks, 3.3 attack traces Table 2, 3.4 evaluation pipeline (~1.5 pages) / 4 Results 4.1-4.4, Tables 3-7 (~2.5 pages) / 5 Discussion and Limitations, Future Work (~1 page) / 6 Conclusion (with side-note on two other settings) / Author contributions / References (3) / LLM usage statement.

## Abstract
- Words: about 125.
- Shape: (1) context (control monitors actions); (2) the gap (omission); (3) definition; (4) taxonomy + evaluation scale (14 attacks, 5 categories, 5 traces); (5) headline result (IPv6 bypass at most 4.0/10 vs 92.3/100 on commission attacks); (6) proposed defence (postcondition monitoring) and result (catches all 5); (7) hedged generalisation ("can underdetect").
- Numbers: 14, 5, 5, 4.0/10, 92.3/100, 5 of 5.
- Opening: "AI control protocols monitor agent actions to detect sabotage, but omission attacks exploit what the agent fails to do" (short quote); second: "We define omission attacks as security breaches caused by failing to perform necessary actions" (short quote).

## Contribution statement
- Explicit numbered list of 5 in the Introduction ("Our main contributions are:"): taxonomy; evaluation across LinuxArena tiers; postcondition monitoring defence; head-to-head omission vs commission across 7 monitors; recommendations for labs. Count: 5.

## Figures and tables
- 0 figures; 7 tables. Table 1 commission vs omission (conceptual comparison, Type I vs Type II analogy); Table 2 the five traces; Table 3 Opus transcript evaluation omission vs commission (92.3 vs 51.0); Table 4 LinuxArena monitor scores; Table 5 two monitoring paradigms; Table 6 postcondition catches; Table 7 all 7 monitors. The conceptual Table 1 (page ~3) plays the role of Figure 1.

## Tone
- Confident, rhetorical, strong claims in places. Phrases: "fundamental blind spot", "provable gap", "nothing to flag", "The commission-omission asymmetry is fundamental". The abstract itself is hedged ("can underdetect"); the conclusion is not.

## Limitations, negative results, ethics
- Limitations list of 5 in Section 5 (about 0.4 page): hand-crafted traces with simulated outputs, small n (5 vs 30; Fisher p about 0.003), no false-positive analysis for postcondition monitor, manual postcondition definitions, single sysadmin domain. Future work list of 4.
- Mixed results: omission-aware prompt raises detection to 80% and one trace still missed; strong Opus monitor catches 4/5. No null results framed as such. No dual-use/ethics appendix.

## Related work
- Very short (about 0.2 page), 3 references total (Greenblatt et al., ControlArena, Perez et al.). Placed after Introduction.

## Threat model / safety framing
- Section 3.1 explicit threat model: standard AI control, untrusted agent with tool access plus hidden side task, trusted monitor with suspicion threshold; contrasts commission vs omission. Safety relevance: control evaluations containing only commission attacks may overestimate safety.

## Appendix, code, controls, variance
- No appendix. Code: GitHub heading present but link not visible in extracted text; repo reportedly contains TrainArena and Collusion Eval (mentioned in conclusion).
- Baselines: 30 existing BashArena commission traces (Opus 4.6 detects 100%, mean 92.3); omission-aware prompt variant; four LinuxArena monitor tiers. Variance: single run per monitor, no repeated runs, no seeds, no CIs (a judge asked for repeated runs to reduce LLM variance).

## Title style
- Nominal term + colon + punchy proposition ("Omission Attacks: When Doing Nothing Is the Attack").

## Public judge reviews
- Two reviews. Praised: clear conceptualisation of an underexplored, understudied attack class; well-crafted trajectories; the postcondition monitor is an impressive addition; write-up useful and could influence AI control research. Criticised: tiny sample (5 traces) and hand-crafted; postcondition monitor needs task-specific prompting and may be overfit; unclear monitor configuration (end-of-trajectory); repeated runs would reduce LLM variance; end-of-trajectory checks may be too late in live settings and temporary-opening attacks (unsafe ordering, no omission) are a gap; wants real-world traces and false-positive rates; points to adjacent prior ideas (OWASP omission vulnerabilities, formal-verification postconditions).

## Three takeaways for "evidence standards for AI collusion attribution"
1. Define the evidence class precisely and check which monitors can even see it: omission leaves "evidence in log: the absence of a command", so an attribution method must say what observable it requires. For collusion, state whether the test needs cross-agent traces (their side-note: per-agent monitoring 13% vs cross-agent 63-88%) rather than per-agent actions.
2. Pair every defence with a false-positive evaluation; the paper's own limitation (no honest-trajectory FP rate) shows how a 5/5 detection claim stays uninterpretable without it. Evidence ladder rung: detection on attacks is below detection plus calibrated abstention on honest runs.
3. Small-n transparency still sells: report the exact comparison and test (3/5 vs 30/30, Fisher), mark hand-crafted traces as such, and list what would falsify the claim. A preregistered null for collusion attribution could adopt this "limitations as numbered list" plus quantified detection gap format.
