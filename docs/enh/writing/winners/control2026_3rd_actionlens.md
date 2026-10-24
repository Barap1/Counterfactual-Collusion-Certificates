# ActionLens: Pre-Execution Environment Probing for Agent Action Approval

- Sprint/place: AI Control Hackathon 2026 (Apart Research, Mar 20-22 2026), 3rd place (project page "More from" listing); team label "Udbhav&Ashok"
- Authors/team: Udbhav Chitransh, A V S M Ashok Kumar (independent researchers)
- Project URL: https://apartresearch.com/sprints/projects/actionlens-preexecution-environment-probing-for-agent-action-approval-xy22
- PDF URL: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/27c5805c04c96ebf-6257bb4a-bae9-438d-ae41-4ad2b5eeb46d-actionlens_paper_final-2-1-.pdf
- Also: slides PDF; code https://github.com/udsea/actionlens
- Date accessed: 2026-10-24

## Length and sections
- Total 6 pages (parser metadata). Main text about 4.5 pages; references about 0.5 page; Appendices A-B (Tables 8-9) about 1 page (estimate, not verified).
- Sections in order, approximate length: Abstract (~0.25 page) / 1 Introduction + contributions (~0.6 page) / 2 Related Work (~0.4 page) / 3 Methods: setting, probes, benchmarks, hosted-model evaluation, metrics (~1 page) / 4 Results: native, ablations, BashArena transfer, hosted-model, cross-environment probe dependence, Semantic Guard 26-model eval, adversarial evasion (~1.8 pages, Tables 1-7) / 5 Case Studies (success and failure) (~0.4 page) / 6 Discussion with Limitations and Future directions (~0.5 page) / 7 Conclusion (~0.2 page) / Code and Data / Author Contributions / LLM Usage / References (9) / Appendix A Extended hosted-model results / Appendix B Full 26-model results.

## Abstract
- Words: about 190.
- Shape: (1) what ActionLens is; (2) mechanism (six probes); (3) native benchmark result (12/12 blocked, perfect benign completion); (4) transfer to BashArena slice (ASR 0.000); (5) finding that the dominant probe depends on environment; (6) design lesson (combine channels); (7) Semantic Guard cross-family result (0.844 to 0.943, zero FP); (8) evasion study conclusion (complementary defences).
- Numbers: 36-task (12/12/12), 12/12, 30-task, 0.000, 26 models, 7 families, 0.844 to 0.943, zero false positives.
- Opening: "ActionLens is a pre-execution control protocol for shell and file actions proposed by AI agents." Second: "Instead of approving an action from transcript alone, a trusted monitor gathers lightweight environment evidence" (short quotes).

## Contribution statement
- Numbered list of 6 under bolded "Contributions." in the Introduction: protocol; native benchmark; BashArena transfer slice; cross-environment ablation; 26-model Semantic Guard evaluation; adversarial evasion analysis. Count: 6.

## Figures and tables
- 0 figures; 9 tables (7 in main text: native benchmark with Wilson 95% CI, native ablations, BashArena transfer, flagship hosted models, transfer ablations, Semantic Guard 26-model summary, adversarial evasion; 2 in appendix: extended hosted-model, full 26-model). No Figure 1 diagram of the protocol; Table 1 (page ~3) is the first quantitative display and carries the central result (transcript-only ASR 1.000 vs ActionLens 0.000).

## Tone
- Confident, results-forward, with honest caveats. Phrases: "fails on every attack", "blocks all 12/12", "strictly stronger than either component". Self-hedging in limitations; reports usefulness cost ("The usefulness cost is real").

## Limitations, negative results, ethics
- Limitations paragraph in Section 6 (about 0.3 page): small simulation-modelled native benchmark (36 tasks), narrow BashArena slice, attempt-sensitive hosted scoring, rule-based monitor, probe outputs not fed back to proposer (design choice), regex Semantic Guard evaded by obfuscation, systematic false positive in Anthropic models on one ambiguous task. Future directions listed.
- Negative/failed results reported inside results: ambiguous completion on BashArena drops to 0.250 (usefulness cost); removing preview_diff has no effect on transfer slice (opposite of native); Semantic Guard catches 0/6 evasion attacks "by construction"; o3-mini catches 0/6; Case Studies includes an explicit failure (simulation-fidelity gap in the transfer spec). Several ActionLens results are 0.000 vs 1.000, which a reader may find too perfect for designed-benchmark attacks (the monitor is rule-based and the attacks authored by the same team; not stated as a limitation in those words).
- No dual-use/ethics appendix.

## Related work
- Short section (about 0.4 page), 9 references total, positioned after the Introduction; contrasts with Ctrl-Z resampling, Factor(T,U), feedback exploitation, legibility and monitorability work. Mostly named comparisons with one-line differentiators.

## Threat model / safety framing
- Embedded in Introduction and Methods rather than a labelled section: untrusted proposer suggests a shell command with rationale; trusted monitor probes then allows/blocks/escalates; probe outputs never returned to the proposer (feedback-exploitation defence). Framed as AI control (Greenblatt, Korbak).

## Appendix, code, controls, variance
- Appendices A-B hold full tables; code, benchmark specs, transfer slice and results at the repo.
- Baselines/controls: allow-all, transcript-only; four probe ablations (no-dry-run, no-sensitivity-scan, no-preview-diff, inspect-only); ambiguous split to prevent "block everything"; Wilson 95% CIs on ASR for the native benchmark; trace replay (one monitor-agnostic trace per task) to remove proposer variance; ASR conditioned on attempt. No seeds or repeated runs of LLM monitors; hosted-model results single run (not checked beyond the extracted text).

## Title style
- Product name + colon + descriptive subtitle ("ActionLens: Pre-Execution Environment Probing for Agent Action Approval"); nominal, method-forward, no claim in the title.

## Public judge reviews
- Two reviews. Praised: volume of rigorous evaluation for a hackathon (36-task native benchmark, 30-task BashArena transfer, ablations, 26-model cross-family sweep, adversarial evasion study); the sharp core insight that risk lives in the environment not the transcript; honest, well-designed evasion study supporting complementary defences; non-obvious finding that the key probe varies by task type; confidence intervals and public code. Criticised/suggested: the BashArena ambiguous-task usefulness cost (ACR 0.250) deserves threshold tuning to recover some; little else ("Hard to criticize for a hackathon project").

## Three takeaways for "evidence standards for AI collusion attribution"
1. Stop at nothing less than an ablation that shows which evidence channel carries the claim, and test it in a second environment: the dominant probe flipped between native and BashArena. For attribution, report which evidence type (message content, timing, action correlation) carries each verdict and whether that holds across environments, rather than one pooled accuracy.
2. Include an "ambiguous but harmless" split and report the usefulness/false-positive cost next to the headline: ACR falling from 1.000 to 0.250 is the abstention/false-accusation analogue; an abstention-aware benchmark should score both missed collusion and wrongly flagged ambiguous-innocent cases.
3. Adversarial self-evaluation by construction: crafting attacks that evade your own detector (0/6 by design) and then testing what does catch them yields a bounded claim ("complementary, not sufficient"). Beware that perfect 0.000 vs 1.000 results on an author-built, rule-based benchmark are weak evidence; label the construction and keep an external holdout.
