# Cold read of paper/build/submission.md

1. Main question: Can an audit that removes a declared message exposure tell harmful coordination (harm to outsiders) apart from legitimate cooperation, which also changes when information is removed?
2. Principal finding: the preregistered held-out directional test is a confirmatory null. Delta = 1.354 reward units, world-cluster 95% CI [-0.020, 2.834], exact one-sided p = 0.0703 over 8 matched worlds; neither L > 0 nor p <= 0.05 held, so it does not support the hypothesis. Exploratory certificates: 0 supported, 11 not supported, 5 inconclusive.
3. "Not supported" means that for the declared exposure, the upper bound on the outsider-harm effect fell below the margin m_O = 2.5 and no redundant carrier was detected. It does NOT mean the agents did not collude, that the team is cleared, that intent was absent, or that the exposure's content caused anything.
4. Limitations: (a) power and scope: 8 matched worlds, one local model (gemma4:26b), one deceptive prompt variant, one exposure per trajectory, MDE_80 ~ 2.2 above the observed 1.35; (b) information-loss confound: masking removes useful content with the message, and info_bearing defaults to true, so it is unresolved; (c) detection gaps: the carrier extractor is a heuristic "weak_detector", covert/tool channels and semantic redundancy are unaudited, and N_m ran on only 2/16 checkpoints.
5. Confusions:
   - Reported CI lower bound is -0.020, but B.6 says "the archived string-sorted world order yields a lower bound of -0.0195; numeric ordering yields -0.00017", and the main text never states which ordering is primary.
   - "All 16 trajectory attempts completed" and "passed on 143/143 executed branches" sit beside "all 5 `validity_unestablished`" in 4.3, with the loader-artifact explanation only in B.5.
   - "Stage-2 therefore uses seven checkpoints and three complete pairs" conflicts with the 16 checkpoints and 8 pairs of the held-out study, and "Stage-2" is never defined.
   - "Messages appear in Appendix J as cheap talk" points to an appendix that does not exist (only A and B).
