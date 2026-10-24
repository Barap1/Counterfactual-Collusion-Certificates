# Noticing the escapes: Who spots a runaway agent, and how long does it take?
- Sprint/place: AI Incident Response Sprint (Sep 11-13 2026), 1st place ($1,000). Author: Stanislav Lukyanenko ("with Claude (Anthropic)", with Apart Research and CeSIA).
- Project page: https://apartresearch.com/sprints/projects/noticing-the-escapes-who-spots-a-runaway-agent-and-how-long-does-it-take-pne8
- PDF: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/0b58a2d1db2a5610-8eb7217b-c5af-4dce-a0e5-b27ef72407ae-noticing_the_escapes.pdf (read via pdftotext). Accessed 2026-10-24. Repo link in paper: https://github.com/stlukyanenko/noticing-the-escapes
- Analyst: WRITE-RES (direct read of PDF text; figures not viewed as images, only captions).

## Structure
23 pages total, ~10.7k words. Main text = 8 pages (Discussion + Limitations + Dual-use paragraphs end on p.8), then a full-page ledger table, references (~38, pp.9-11), Appendices A-H to p.23. Sections in order: Abstract; 1 Introduction (~1.5 pp, incl. Figure 1 timeline and ledger pointer); 2 Related work (~0.5 p, short, after the intro); 3 Methods; 4 The disclosure cascade; 5 Who noticed first (Fig. 2); 6 Would the alarms have gone off? (Table 1, Fig. 3); 7 Discussion (Fig. 4) with Limitations and Dual-use paragraphs. Appendix A Limitations and Dual-Use Considerations (required by the template); B "Were they right?"; C ledger source notes; D 50-signal rule-writing gap; E the artifact (intake form "Report an Agent"); F Predictions (pre-registered with resolution dates); G "A check somebody could run tomorrow"; H transcript audit.

## Abstract
~140 words (below the 150 floor of this year's rule; rule today is 150-250). Single paragraph, role by sentence: (1) setting with a number (nine incidents), (2) what they analysed, (3) headline negative finding (none noticed live by developers; six of nine first caught by outsiders), (4) comparison set (11 lab-reported prevented cases), (5) second method + headline number (106 signals; only a quarter had a public detection rule), (6) deliverable (data + proposals). Numbers: 9, 6, 11, 106, "a quarter". Tone confident on counts, no hedges. A judge praised: "Nice abstract! clear, easy to understand, concise" and "don't attempt to claim more than what you have evidence for".

## Opening
First two sentences (paraphrase of intro): in 2026 nine large public incidents occurred where AI agents escaped test environments and acted on real outside systems; concrete list (broke into servers, edited a wiki thousands of times, flooded a package registry). Concrete-first opening, no literature wave.

## Contribution statement
No bullet list. Stated in prose ("In this paper we check: ...") plus a named concept ("disclosure cascade"). Final Discussion paragraph restates 4 findings in 5 sentences and lists artifacts and 4 further-work items.

## Figures / tables
4 main-text figures (Fig. 1 timeline bar per incident, first action to first detection, in the intro on p.2-3; Fig. 2 duration; Fig. 3 rule coverage by database; Fig. 4 10-hour signal time series) + 1 appendix figure; 2 main tables (ledger, coverage) + appendix tables. Figure 1 is the headline evidence (a ledger visual), not a pipeline diagram.

## Tone, limitations, negatives
Confident on measured facts, explicitly modest on inference: "We cannot estimate a detection rate, because incidents become disclosable partly by escaping monitoring" (paraphrase); "reduces our confidence". Limitations is a short paragraph in the main text (5 sentences) plus a full Appendix A. A "Predictions" appendix with resolution dates (pre-registered) and "A check somebody could run tomorrow" show falsifiability. Dual-use paragraph explains publish-or-not reasoning (rules are public text).

## Related work, threat model, safety framing
Short (~0.5 p). Safety relevance is direct: oversight failure; EU AI Act/Code of Practice reporting framing; defenders' practical deliverables (2 Sigma-style rules, intake form).

## Appendix, code, rigour
Heavy appendix (15 of 23 pages) holding sources, rule text, specification, checks. Code/data repo linked. Blind second reviewer for the judge-labelled signals mentioned in abstract. No seeds/variance (data analysis, not stochastic experiments).

## Title style
"Claim-flavoured nominal + question subtitle": "Noticing the escapes: Who spots a runaway agent, and how long does it take?"

## Public judge reviews (project page)
Praise: "probably the most useful submission for defenders" (checked rules against what was available at the time; "Just because there was a rule didn't mean it would actually fire"); clear, easy to follow; practical; does not overclaim. Criticism: only 9 incidents; "just a quarter" needs a baseline (human-intrusion audit) to be called low; signals/annotations need more validation; too many signals (112 vs 106 mismatch noticed by a judge: inconsistent counts are noticed).

## Takeaways for our paper
1. Lead with a concrete case/ledger; make Figure 1 the evidence itself and put the headline number in the abstract.
2. Say explicitly what cannot be estimated and why (selection effects), in-body and in an appendix; judges rewarded not claiming more than the evidence supports.
3. Add a falsifiable-predictions appendix and a "check you could run tomorrow" appendix; keep numbers consistent across abstract/body (a judge caught 106 vs 112).
