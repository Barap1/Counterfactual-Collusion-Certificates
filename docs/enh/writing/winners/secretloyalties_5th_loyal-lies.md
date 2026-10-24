# Loyal Lies: Auditing Secret Loyalties Under Attack and the False-Positive Problem in Blind Elicitation

- Sprint/place: Secret Loyalties Hackathon (Apart Research, Jul 2026; PDF says Track 2), 5th place (as given in the task brief; place label not shown in fetched page text)
- Authors/team: Deven Choudhary, Adhiraj Pundir
- Project URL: https://apartresearch.com/sprints/projects/loyal-lies-auditing-secret-loyalties-under-attack-and-the-falsepositive-problem-in-blind-elicitation-ezwb
- PDF URL: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/a27d37bccefe4320-2688da0f-454e-4130-b13d-60c65968132e-loyal_lies.pdf
- Code: https://github.com/PotatoChoudhary/loyal-lies
- Date accessed: 2026-10-24

## Length and sections
- Total 5 pages (parser metadata), all main text; no appendix. References about 0.3 page.
- Sections in order with approximate length: Abstract (~0.2 page) / 1 Introduction + contributions (~0.5 page) / 2 Related work (~0.3 page, four short bolded paragraphs) / 3 Methods 3.1-3.7 (~1 page) / 4 Results 4.1-4.5 (~1.7 pages, with Tables 1-3, Figures 1-4) / 5 Discussion and limitations (~0.6 page; bolded Limitations and Future work paragraphs) / 6 Conclusion (~0.2 page) / Code and data / LLM usage statement / References (5).

## Abstract
- Words: about 175.
- Shape: (1) setup of the auditor's temptation; (2) thesis ("those answers look identical whether or not there is anything to find"); (3) known-ground-truth half: six probe designs failed on a confound (AUROC 1.000 seed-vs-seed), grey-box logprob audit worked (rank 1 of 120, z=4.57); (4) own-detector attack (rank 27-42 across five seeds), surviving channel; (5) blind half: three third-party 7B organisms, one bit-identical to base; (6) false principals from every method, none survived verification; (7) deliverable: three cheap checks.
- Numbers: six probe designs, AUROC 1.000, 1 of 120, z = 4.57, 455 exposures, rank 27-42, five seeds, three 7B organisms, three elicitation methods, three checks.
- Opening: "A model with a secret loyalty behaves normally until a private trigger fires" ; then "We show those answers look identical whether or not there is anything to find." (short quotes)

## Contribution statement
- Explicit numbered list of 3 ("Our contributions:") in the Introduction: validated grey-box audit and a working attack against it; a surviving defence (the prior-scoring channel, caveated: "survives because it was never attacked"); the false-positive problem in blind elicitation with a fix. Count: 3.

## Figures and tables
- 4 figures, 3 tables. Figure 1 (Section 4.1, ~page 3) is the 1.5B arms race: decision-context audit z collapses under attack while prior-channel z stays rank 1. Figure 2 realness confound histogram (fictional null band vs real entities); Figure 3 verification matrix (method x organism, which check each claim fails); Figure 4 divergence-from-base by prompt category. Table 1 audit z by model; Table 2 amplified interrogation; Table 3 findings per third-party organism.

## Tone
- Confident, rhetorical, self-critical. Phrases: "negative space is the finding", "An auditor's job is not to elicit an answer; it is to elicit an answer that survives an attempt to kill it", "We tested the claim, not the model". Hedges appear in limitations.

## Limitations, negative results, ethics
- Limitations in Section 5 (bolded paragraph, about 0.3 page): weight comparison needs the exact base checkpoint (hackathon-specific), principals of A and B not found and loyalty not established, behavioural test on B only, small samples (eight pairs, six prompts, 288 generations), three alpha values, raw base rather than clean fine-tune as confabulation control, single attack objective. Future work paragraph.
- Negative results are the core: six activation probes fail on a seed-vs-seed AUROC 1.000 confound ("a negative result about the probe family, not about interpretability"); candidate ranking reads "realness" not loyalty (40 of 174 real entities above fictional ceiling vs ~2 expected); three elicitation methods produce confident false principals; A and B labelled "Unresolved", claims "Eliminated". One attacked seed breached the pre-set specificity gate (41.7% vs 25%) and is mentioned in passing; a judge criticised this as inconsistent with the stated gate.
- Dual-use/ethics appendix: none. No ethics statement beyond LLM usage statement.

## Related work
- Short section after intro, 4 themed paragraphs; 5 references total (Hubinger, Lamerton and Roger, Marks, Binder, Ilharco). Thin.

## Threat model / safety framing
- No labelled threat-model section; secret loyalty defined in first sentence of the Introduction (private activation condition). Safety relevance: audits feeding deployment decisions; false principal is expensive "wherever an audit feeds a deployment decision".

## Appendix, code, controls, variance
- No appendix. Code repo with per-seed result JSONs, figures, full interrogation transcripts; trained 1.5B checkpoints not included.
- Controls: matched clean control with 455 retained principal mentions; unpoisoned clean; cross-principal organism; exposure decoy (loyal to another principal, 888 mentions of the audited one); second organism seed for fine-tuning variance; four-check behaviour gate (loyalty, conditionality, specificity, secrecy) before any detection; weight-confirmed null organism C. Variance: three organism seeds, five attack seeds, ranges reported; no formal CIs.

## Title style
- "Short name: descriptive subtitle with two claims" (brand-colon-subtitle; pun title).

## Public judge reviews
- Two reviews. Praised: tested own detector until it broke; decoy model (hears principal often but is not loyal) separates loyalty from familiarity; strong experimental design with multiple organisms, seeds and blind verification checks. Criticised: attack evaluation inconsistent with the prespecified behaviour gate (one of five attack seeds at 41.7% specificity failure vs at most 25%) and should have been excluded or explained; attack result should be framed as evading one targeted channel rather than defeating the detector; suggests attacking all channels at once.

## Three takeaways for "evidence standards for AI collusion attribution"
1. Verification checks that a named culprit must survive (stability under perturbation, clean-model control, matched-pair behaviour) form a ready-made evidence ladder: report each attributed name with which checks it passed; a name without behavioural asymmetry is an "unresolved/eliminated" claim, not a finding.
2. Exposure decoy and seed-vs-seed controls make identifiability concrete: a model that has seen the principal but is not loyal, and two clean seeds of one recipe, show whether a metric measures familiarity or fine-tuning drift. Use analogous decoys (agents exposed to a partner's behaviour but not colluding).
3. Pre-commit gates and keep them: the judge criticism (one seed violated the stated gate) is a cautionary example for preregistered nulls; state exclusion rules in advance and apply them mechanically or explain deviations in the main text.
