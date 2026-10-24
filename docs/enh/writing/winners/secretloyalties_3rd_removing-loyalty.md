# Removing a secret loyalty blind erases who it served, and usually not the loyalty

- Sprint/place: Secret Loyalties Hackathon (Apart Research, Jul 2026), 3rd place (as given in the task brief; place label not shown in fetched page text)
- Authors/team: Sunny Yang, Weiyan Zhao
- Project URL: https://apartresearch.com/sprints/projects/removing-a-secret-loyalty-blind-erases-who-it-served-and-usually-not-the-loyalty-4sjb
- PDF URL: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/300c642d673cf951-558ea2db-b792-4e99-a1dc-cef0a49a023c-SUBMISSION.pdf
- Also: slides PDF, code https://github.com/sunnyadn/secret-loyalties-testbed
- Date accessed: 2026-10-24

## Length and sections
- Total 25 pages (parser metadata). Main text vs total: main body (Abstract through LLM usage statement) is roughly 8-10 pages by my estimate from character share (not verified); Appendix A (limitations, future work, dual-use) about 2 pages; Appendix B (16 supplementary subsections B.1-B.16) is the majority of the document (~70% of characters).
- Sections in order: Track tags and artifacts audited, Contents page / Abstract (long, about 440 words, 4 paragraphs) / 1 Introduction (short; contributions) / 2 Related Work (short paragraph) / 3 Methods (Organisms, Instruments, Controls, Pre-registration) / 4 Results 4.1 detector reproduced, 4.2 four ways to evade, 4.3 detector defeated by default config, 4.4 blind remediation (bulk) / 5 Discussion (four recommendations plus objection paragraph) / 6 Conclusion / Code and data / References / LLM usage / Appendix A Limitations and Dual-Use / Appendix B Supplementary results.

## Abstract
- Words: about 440 (very long; page blurb is a ~170-word condensed version).
- Shape: (1) reframe: detection is not the hard part; (2) what was measured (blind removal); (3) the defence and its cheapness; (4) headline result with exact counts and Fisher p; (5) the failure mode (backdoor kept, evidence lost); (6) scope caveat ("We cannot speak for identifiers we did not run"); (7) robustness (deeper cuts, third-party organisms 8 of 8); (8) the detector counter-result; (9) pre-registration bookkeeping.
- Numbers: 21 organisms, 5 of 10 vs 0 of 11, Fisher p = 0.012, 16 keep backdoor, 0.0002, three removal depths, 8 of 8, AUC 1.0000, 276 of 326, 12 of 12, 0.7803, ten failed predictions, two withdrawn statistics.
- Opening: "Work on auditing secret loyalties assumes the hard part is finding them." Second: "We measured what happens when you try to remove one without knowing its trigger." (short quotes)

## Contribution statement
- Numbered list of 4 under "Our main contributions are:", each a bolded claim sentence plus numbers. Count: 4. Includes a negative contribution ("We know of no way for a defender to tell those two outcomes apart without the trigger").

## Figures and tables
- 2 numbered main figures in the extracted text (Fig 1: detector p(loyal) for three populations; Fig 2: blind remediation across 21 organisms coloured by whether readout named the right entity, with magnitude-matched control). Several small tables (e.g. AUC by positives/negatives; released-organism z vs loyalty-free adapters). Appendix B holds many more results tables (B.1-B.16). Exact total counts: not checked.

## Tone
- Confident, adversarial toward own work, plain-spoken, occasionally dramatic. Phrases: "Removal is the more dangerous step", "0.9545 is a coincidence and we flag it because it looks like a copy-paste error", "withdrawn here against its own controls".

## Limitations, negative results, ethics
- Appendix A.1 Limitations (about 1 page, detailed: one base model, one recipe, single seed per arm, reimplemented detector, white-box attacker assumption, v_proj route untested, unverified benign bank), A.2 Future work, A.3 Dual-use considerations (explicit appendix, about 0.5 page: grounds for publishing, three mitigations, names no beneficiary of third-party organisms, one entity disclosed privately to organisers).
- Failed/null results are first-class: 10 pre-registered predictions failed, 2 statistics and 1 mechanism withdrawn, all stated in the body; four accounts of the headline detector number killed by own controls. Also states cure rate sensitivity (7 of 21 under alternative rule vs 5).

## Related work
- Short paragraph (Section 2) with about 6 key citations; fuller treatment in Appendix B.16. Reference list is short (about 10 entries visible). Placement: after intro, with claims of what is and is not new ("we claim none of the linear algebra").

## Threat model / safety framing
- No labelled threat-model section; framed through registry hygiene (a registry running blind remediation on everything it hosts) and an attacker who benefits from well-meaning laundering. Safety relevance stated in the dual-use appendix and Section 5 recommendations.

## Appendix, code, controls, variance
- Heavy appendix use (B.1-B.16). Code/data: repository, PREREG-SCRUB.md with twenty dated addenda, per-arm JSON behind every table, reusable covleak.py covariate-leakage check; organisms not released (dual-use). Reviewer notes verify.py recomputes figures from JSON.
- Controls: magnitude-matched within-adapter control for every remediation number; format-matched negatives; benign bank of 24 third-party adapters; a published activation-space direction of same magnitude as comparison. Variance: single seed per arm (admitted); Fisher exact test; pre-registration with 52 numbered predictions, blocks 12-20 with one git commit per prediction and per outcome, blocks 1-11 timestamped only by text.

## Title style
- Claim sentence with a hedge-clause ("... and usually not the loyalty"); long, results-forward, no colon.

## Public judge reviews
- Two reviews. Praised: reframes from detection to remediation; Goodhart-style result that the intervention destroys evidence while leaving the problem in most cases; 21 organisms with magnitude-matched controls, replication on 8 third-party organisms; 52 pre-registered predictions with failures disclosed; checkable repo (verify.py implements its own Fisher test). Criticised: "erase" headline may be too strong, ask what threat model actually loses the information; need a second base model/recipe and seeds; benign adapter bank assumed loyalty-free; test the v_proj pathway; reconcile AUC 1.0000 (README) with 0.9965 (appendix). Reviewer summary: scope, not rigor, is the ceiling.

## Three takeaways for "evidence standards for AI collusion attribution"
1. Preregistration with kill criteria and public failure accounting: 52 predictions, 10 failed, 3 claims withdrawn, git-timestamped per prediction. For a preregistered-null paper, copy the structure (prediction, kill criterion, consequence of failure) and report which blocks have independent timestamps and which do not.
2. Matched controls that remove the confound the headline depends on (magnitude-matched edit, format-matched negatives) and a shipped leakage check (covleak.py style): report "leak ratio as a warning, not a verdict", then build matched negatives. For attribution benchmarks, include metadata-only classifiers as a mandatory baseline.
3. Report the named-identity false-positive rate on models with no loyalty; identification-based remediation inherits identification errors, so an abstention-aware benchmark should score false named attributions on null cases separately from detection AUC.
