# WRITING_PLAYBOOK: direct writing path for the CCC paper (Apart AI Collusion Sprint, Track 2.3)

Evidence base: official rubric and rules (S0 = https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25, extract in NOTES_judging_raw.md), 12 winner analyses in winners/ (file names cited as W:<prefix>), 3 contrasts (W:CONTRAST), BEST_PRACTICES.md (BP#). Winners are Apart 2025-26 sprint winners, 5-25 pages (median about 10); judges' public reviews were read where shown. Limits: n is small, PDFs of Secret Loyalties 1st-3rd, 5th and AI Control 2026 1st-3rd were read by a helper, others by me; figures were checked by caption only. Rules marked (inference) are my synthesis, not stated by Apart.

## 0. What the judges score (S0)
Three dimensions, 1-5 each, same rubric for all tracks: Impact & Innovation ("actually new, or replicating recent work?"), Execution Quality (4 = "convincing validation. Results clearly support conclusions"; 5 = "surprising findings, novel methods, or unusually robust validation"), Presentation & Clarity (2 = "key information buried... or diluted by excessive length"; 5 = "a pleasure to read"). Hard requirements: PDF on the official template; <=8 pages before references/appendices; abstract 150-250 words; authors/affiliations; a "Limitations and Dual-Use / Ethical Considerations" appendix; report "variance, seeds and baselines, and always include the positive control"; identify what is new vs preexisting work; made-up results or references can disqualify. Judges may decline to score a report "too unclear to follow".
Implication (inference): our frozen null is an Execution asset only if it reads as calibrated, not as failure; novelty must be visible in the first page; and length discipline is a scored item.

## 1. Section order and budget (8-page main text, ~4,800 words incl. captions)
1. Title + abstract (170-230 words) - 0.3 p
2. Introduction - 1.0 p: concrete twin-world example first (SPJ, BP8), threat-relevance paragraph, RQs, numbered contributions (4), each with pointer to its section/evidence (BP3; W:digitalminds, W:secretloyalties_1st, W:control2026_1st all use a numbered list).
3. Related work - 0.6 p, placed after intro (winners put it after the intro and keep it to 0.2-0.5 p: W:control2026_1st, W:digitalminds). Name the 8 neighbour papers with one-line deltas.
4. Standard: ladder L0-L3, tau_O/C/W, identifiability I0-I5, exact scope statement - 1.3 p (W:digitalminds states identification assumptions before results; W:secretloyalties_1st states A1/A2 in the threat-model section).
5. Benchmark and methods - 1.2 p: twin types, axes, seeds, metrics, preregistered criteria, circularity disclosure, positive control stated here.
6. Results - 2.4 p, in this order and with labelled evidence class per number: (a) positive control and development (DEV), (b) frontier / identifiability result (NP), (c) abstention-aware benchmark results (NP), (d) held-out EXP-002 confirmatory null (OC) with its registered secondary and post-hoc items in a visibly separate paragraph/table (BP21), (e) real-agent study (NP).
7. Discussion + limitations + conclusion - 0.8 p, including a short "What this does and does not establish" box.
8. After page 8: References; Appendix A Limitations and Dual-Use (required, S0); B deviation log + deviations from protocol; C reproducibility (exact commands, hashes, seed lists); D falsifiable predictions / "a check someone could run tomorrow" (W:incident has both; W:secretloyalties_3rd ships 52 predictions with failures disclosed); E extra tables. Winners use appendices heavily (W:incident 15 of 23 pp; W:secretloyalties_3rd ~70% of 25 pp) but W:CONTRAST shows a 32-page version was penalised, so keep the appendix navigable (index at top of appendix; (inference)).
Target total <= 20 pages.

## 2. Title formula
Pattern seen in winners: "Short claim phrase: scope-limiting subtitle" (W:digitalminds "Readable but Not Causal: Limits of ..."), "Term: punchy proposition" (W:control2026_1st), method + audit subtitle (W:secretloyalties_1st). Put the epistemic finding in the title, name the object (collusion attribution), keep < 15 words.
Candidates:
1. "Seen Is Not Shown: Evidence Standards for Attributing Collusion to AI Agents" (names the gap between a log showing coordination and an attribution being justified)
2. "Same Logs, Different Worlds: What Transcript Evidence Can and Cannot Attribute in AI Collusion Audits"
3. "Four Rungs of Proof: An Abstention-Aware Benchmark and a Preregistered Null for Collusion Attribution"
Avoid "first", "novel framework", and bare nominal titles (W:control2026_2nd's setting-only framing was discounted by a judge for lack of results).

## 3. Abstract template (target 190-220 words, one paragraph, 6-8 numbers)
Roles taken from W:digitalminds (positive number then negative number, then so-what), W:control2026_1st, W:incident, BP5.
1. Context (uncontroversial): "Audits of multi-agent systems increasingly rely on logged trajectories to decide whether AI agents colluded." (BP5/JS)
2. Gap: "Yet identical logs can arise from collusion, shared incentives or chance, and no standard says which attribution a given log can support."
3. What we contribute: "We propose an evidence ladder (L0-L3) separating causal influence, harm, and justified attribution, and an identifiability frontier on twin worlds {{N twin types}}."
4. Key theoretical/empirical positive: "On {{N}} matched twin pairs, transcript and knockout rules produce indistinguishable evidence in {{X}}% of cases ({{CI}}; new-prospective, frozen before outcomes)." 
5. Benchmark: "An abstention-aware benchmark scores {{M}} methods; {{best method}} reaches {{metric}} but abstains on {{Y}}% of unidentifiable cases."
6. The confirmatory null (stated plainly): "A preregistered held-out test of whether {{hypothesis}} gave Delta = 1.354 (world-cluster 95% CI [-0.020, 2.834], one-sided p = 0.0703; n = 8 world pairs): the directional hypothesis was not supported." (numbers from MISSION.md; keep category tags in the body, not abstract)
7. Real-agent evidence: "In a real-agent study ({{n}} runs, {{models}}), {{result}}."
8. So-what: "We therefore recommend that audits report the ladder rung reached and abstain when {{condition}}; we do not claim to detect collusion." Do not put a number in the abstract that the body treats as post hoc (W:CONTRAST B: a judge penalised "the abstract relies on numbers the paper advises not to trust").
Keep the abstract inside 150-250 words (S0). No hedging stack; one scope sentence (W:incident: judge praised "don't attempt to claim more than what you have evidence for").

## 4. First paragraph template
Open on the concrete case, not literature (SPJ BP8; W:incident, W:digitalminds):
"Two agents negotiate in a market. Their logs show the same price-signalling messages in two worlds: in one the agents agreed to coordinate, in the other a common incentive produced the same words and the same prices. {{One sentence: what a transcript rule concludes}}; {{one sentence: what a knockout test concludes}}. They agree, and both are wrong in one world." Then: why it matters for audit (threat model in 2-3 sentences: evidence that triggers sanctions, shutdowns or liability), then RQs, then contributions. Include the threat-model paragraph within the first page (W:digitalminds "The threat model is concrete"; W:control2025_2nd defines untrusted monitoring in sentence 1).

## 5. Figure plan
Winners average 4-5 figures + 3-7 tables; Figure 1 is on pages 1-4, and is either the evidence itself (W:incident timeline) or a design diagram that explains why a naive evaluation fails (W:control2025_2nd causal-separation flow chart; W:secretloyalties_2nd property-coverage matrix to position novelty). BP23: one takeaway per figure, self-contained caption.
- Figure 1 (page 1-2, full width): left panel two twin worlds with identical transcripts and different ground truth; middle: what each rule outputs (tau_O/C/W); right: the ladder L0-L3 with the rung each rule can reach and the identifiability class. Caption states the takeaway in one sentence.
- Figure 2: identifiability frontier (FIG_FRONTIER): x = information available to the auditor, y = fraction of twin pairs attributable; color-blind safe.
- Figure 3: abstention-aware scoring (FIG_RISK): risk-coverage curves; mark abstention.
- Figure 4: confirmatory null as an effect-size interval plot (Delta, CI, p; zero line; separate the registered secondary and post-hoc points by marker and legend).
- Figure 5: real-agent results. Tables: T1 evidence-class legend (OC/ORS/D/PH/NP/DEV), T2 method x rung, T3 benchmark, T4 limits/not-established.

## 6. Presenting the confirmatory null alongside new positive evidence without sounding defensive
Sources: W:digitalminds (negative causal result is the title, judges called it "substantially more informative"), W:secretloyalties_1st ("bounded null": CI excludes the positive control's effect), W:CONTRAST A (calibrated null; but retractions scattered), COS registered-report norm (BP21), NeurIPS guidance rewarding candour (BP19).
Rules:
1. State the hypothesis, the registered test, and the outcome in three plain sentences in Results 5.1: "The preregistered directional hypothesis was not supported (Delta = 1.354, CI [-0.020, 2.834], p = 0.0703, n = 8 world pairs)." No adverbs, no "only", no "unfortunately".
2. Tie the null to the paper's thesis: the sample was 8 world pairs, which is what an identifiability analysis predicts is under-powered for some conditions (inference; only say it if the protocol supports it). Offer what the null rules out: the interval's lower end close to 0 and upper end 2.8 means effects from about zero to large are compatible; say that.
3. Separate evidence classes visually: a table with columns Class / Quantity / Value / Status. Registered secondary (0.727 [-0.31, 1.91]) and post-hoc p-values appear in a block headed "Not confirmatory" (BP13, BP21). Never mix them in running prose.
4. Positive new evidence is introduced with its class ("new-prospective, frozen before outcomes") and a pointer to the freeze hash; this answers the Impact rubric ("not replicating") and the Execution rubric (validation).
5. Show instrument validity next to the null: positive control recovered, certificates 0/11/5, 143 executed + 56 unrun = 199 scheduled records (W:secretloyalties_1st: base-copy null run through the pipeline; W:secretloyalties_2nd decoy). A null is only informative with a demonstrated working instrument (BP20, S0 "always include the positive control").
6. Put every "what we do not claim" statement once, in the box in Discussion and in Appendix A; do not retract claims mid-paper (W:CONTRAST A judge: "conclusions that get taken back later (requiring unlearning)").
7. Do not apologise for n = 8; state it as the independent sample size and report an exact test.

## 7. Tone rules
1. Confident on measured quantities, explicit on scope: "bounded null", "cannot certify" (W:secretloyalties_1st). One scope sentence per claim, not a hedge in every clause.
2. Plain words; define each term once; no "novel", "first", "fundamental", "provable gap" unless proved (W:control2026_1st's conclusion used strong words and judges asked for more rigor; BP7, LS).
3. Make every number carry its class, n, interval and seed/world count (S0, BP15).
4. Use falsification language: "this reading would be refuted by ..." (W:digitalminds 5.3, W:secretloyalties_3rd kill criteria).
5. Keep the abstract, intro, and conclusion numerically identical (W:incident judge noticed 106 vs 112 signals).
6. Say what is new vs preexisting (S0 disqualification risk): mark pre-sprint code/results (frozen EXP-002, DEV fixtures) as preexisting in the report and README.

## 8. How to write limitations (required appendix + short main-text paragraph)
Pattern: enumerated list; each item says what is limited, how it bounds the claim, and what would falsify or extend (W:digitalminds 5.3 (i)-(vi) with falsifiers; W:control2025_1st converts "attack built in a couple of hours" into a threat-model argument; W:incident "We cannot estimate a detection rate because incidents become disclosable partly by escaping monitoring").
Template items: (1) n=8 world pairs; (2) simulated twin worlds vs real deployments; (3) circularity of benchmark construction (disclosed); (4) real-agent study scale and model coverage; (5) the identifiability results hold only inside the enumerated hypothesis class; (6) judge/instrument validity. Add Dual-Use: explain whether the evidence standard or twin constructions could help collusion evade audits, and why releasing them is acceptable (W:manipulation2026 A.2-A.4, W:incident dual-use paragraph). Required by S0.

## 9. What winners always include (checklist)
- Explicit threat model / safety relevance near the start: seen in every analysed paper that I read for this (W:control*, W:digitalminds, W:incident, W:secretloyalties_1st); count not tabulated.
- Numbered or clearly marked contributions: W:secretloyalties_1st, W:control2026_1st, W:digitalminds.
- Quantified headline in the abstract (4-10 numbers): all analysed papers except W:control2026_2nd, W:control2025_1st and W:control2025_2nd, whose abstracts have none (a judge found W:control2026_2nd's results "not that interesting").
- Controls/baselines: matched/base-model controls, decoys, random controls (W:secretloyalties_*, W:digitalminds).
- A negative or limiting finding stated openly: W:digitalminds, W:secretloyalties_1st/2nd/5th, W:incident.
- Code/data link: nearly all (W:incident, W:manipulation2026, W:control2025_2nd, W:secretloyalties_3rd with verify.py).
- Short related work after the intro (0.2-0.5 p).
- Dedicated limitations and dual-use sections.
- Explicit LLM-usage statement where AI helped (W:incident, W:secretloyalties_1st, _3rd, _5th) (S0 allows AI tools; responsibility stays with authors).
Optional but rewarded: 3-5 min demo video, public repo (S0).

## 10. Pre-submission checklist mapped to the rubric
Impact & Innovation
- [ ] Novelty statement names the nearest 3-8 papers and the precise delta; no "first".
- [ ] Theory of change in 2 sentences: who uses the standard (auditors, regulators, benchmark builders).
- [ ] Explicit "what is new in this sprint" vs preexisting work (S0).
Execution Quality
- [ ] Positive control, baselines, variance/seeds/worlds, intervals on every main number (S0, BP15).
- [ ] Evidence class on every number; confirmatory vs post-hoc separated (BP21).
- [ ] Prospective results' freeze hash and seed list cited; deviations in Appendix B.
- [ ] Judge/instrument validated or labelled unvalidated (W:secretloyalties_2nd: low judge agreement was a top criticism).
- [ ] Falsification conditions stated; exclusion/stopping rules stated in advance (W:secretloyalties_5th judge flagged an attack seed violating the stated gate).
Presentation & Clarity
- [ ] Abstract 150-250 words (count it), numbers match body (W:incident).
- [ ] Figure 1 on page 1-2 with a one-sentence takeaway; captions self-contained.
- [ ] Main text <= 8 pages before references/appendices; appendix has an index.
- [ ] Problem, method, findings, limitations all findable in under 2 minutes (rubric level 3).
- [ ] Required Limitations and Dual-Use appendix present; links work; PDF on official template; authors/affiliations.
- [ ] No fabricated references (S0 disqualification): re-verify every citation, including the [CITE-CHECK] items.
- [ ] Resubmission rule: the PDF is not replaced by resubmitting the form; use a slightly different title or email sprints@apartresearch.com before the deadline (S0).

## 11. Common mistakes (each seen in the data)
1. Retracting or contradicting claims later in a very long paper (W:CONTRAST A; 32 pages "twice as long as needed").
2. Abstract numbers the body disclaims (W:CONTRAST B).
3. A setting/method paper with no quantified result (W:control2026_2nd: judge found results "not that interesting").
4. Tiny n and hand-crafted cases without exact test or repeated runs (W:control2026_1st reviewers asked for repeats; it still won because of conceptual clarity, so framing can offset thin n, but do not rely on it).
5. Two projects in one report (W:manipulation2026 judge: "a mix of two projects"); keep one thesis: evidence standards for attribution. Treat benchmark, frontier and real-agent study as three tests of the same ladder.
6. Uncalibrated or unvalidated LLM judge (W:secretloyalties_2nd).
7. Over-strong headline verbs ("erases", "fundamental") flagged by judges (W:secretloyalties_3rd, W:control2026_1st).
8. Related-work wall before the idea (BP10, SPJ).
9. Defensive voice around the null; cheerleading voice around new positives. Report both in the same register.
10. Omitting the positive control (S0 explicitly: "always include").
