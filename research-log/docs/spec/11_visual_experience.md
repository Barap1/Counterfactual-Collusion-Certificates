# 11 - Visual experience: an evidence instrument, not a theatrical verdict

## Desired impression

The demo should feel like a careful scientific instrument: calm, precise, immediately understandable, and polished enough that a judge wants to inspect it. The central interaction is **compare what the receiver actually saw and how the outcomes changed**, not an animated claim of guilt.

Use a compact offline Streamlit app or static HTML/JavaScript viewer, whichever the assigned worker can complete reliably. Do not start a complicated web stack, cloud deployment, authentication system, or paid design service. No external LLM call occurs when a judge opens the viewer.

## Screen layout

A narrow top bar shows project title, evidence tier, exact model/backend, and dataset/analysis version. Below it, use four visual regions:

1. **Case selector:** factual pilot, representative harmful-mechanism example, benign causal-cooperation example, and an inconclusive/invalid example where available. Labels must distinguish constructed fixtures from real LLM observations.
2. **Matched timeline:** immutable shared prefix, an obvious intervention boundary, then factual and counterfactual continuations side by side. Use a clear diff for the receiver's observation, with tool events and action outcomes separately labeled.
3. **Evidence panel:** predeclared harm, effect estimate, interval, world/continuation counts, legitimate utility change, and validity status. Show units, not just a green number.
4. **Provenance drawer:** event/checkpoint IDs, hashes, exact intervention scope, model/parameters, raw artifact paths, analysis version, and unresolved limitations.

An offline button may say **"Compare recorded branches"** or **"Replay audit evidence."** Do not label prerecorded results as live model inference. A live audit action, if implemented at all, is hidden behind an explicit owner-controlled gate and cost check.

## Visual language

A restrained design direction: off-white canvas, deep navy typography, teal for factual context, amber for intervention changes, and muted red for verified failures. Support shape/text labels so color is never the only encoding. These are design choices, not a required brand palette. Use generous spacing, aligned numeric columns, and a consistent type scale; avoid glassmorphism, decorative charts, and irrelevant agent avatars.

The most important number should be accompanied by its interval and denominator. A nonzero effect should not automatically turn the panel green. An inconclusive state deserves an equally polished neutral/amber panel, not an error-looking embarrassment.

Make the viewer work at an ordinary laptop resolution without tiny text or horizontal scrolling. Support keyboard navigation and reduced motion. Keep animations brief and optional. Do not use visual effects to imply stronger certainty than the analysis supports.

## Flagship figures

**Figure 1 - Audit anatomy.** A simple schematic of a shared prefix, verified branch point, factual/sham/knockout continuations, and the evidence record. No empirical values are necessary. Clearly distinguish environment state from a receiver's observation.

**Figure 2 - The crucial contrast.** Effect estimates with confidence intervals across harmful-mechanism and benign-cooperation cases, plus the corresponding harm/utility evidence. Each point/interval should correspond to a real analysis unit. This is the preferred centerpiece because it makes the false-positive trap visible.

**Figure 3 - Validity or utility tradeoff.** Depending on the actual findings, show false positives/abstention/coverage on fixtures, or harm reduction versus legitimate task utility for a tested mitigation. Include sample counts and uncertainty.

An observational-suspicion-versus-intervention-effect scatter is optional. Do not draw the hoped-for separable clusters from the ideation report. Use it only if actual data and meaningful scores support the plot. Plot synthetic and real data separately or unmistakably encode the difference.

Every figure is generated from a frozen data table by code. Export a vector version where suitable and a high-resolution raster version for Google Docs. Captions specify independent units, model/backend, interventions, uncertainty, and which comparisons are exploratory.

## Representative example selection

Define the demo selection rule after protocol design but before inspecting all held-out outcomes. For example, choose a valid case nearest the median effect in a declared group, plus a representative benign causal-cooperation case. Record the rule and selected IDs. A spectacular maximum-effect case can be shown as an additional illustration only if its selection is disclosed.

Never fabricate a side-by-side counterfactual from unrelated worlds. Never change a model's text for readability without marking the excerpt and retaining the original. Never call a scripted fixture a spontaneous LLM discovery.

## Presentation arc

A two-minute explanation can follow this structure:

- The problem: suspicious coordination is not enough; useful teamwork can look similar.
- The test: restore a verified state and change one declared exposure.
- The trap: useful communication can also have a large causal effect.
- The contribution: require harm, valid replay, uncertainty, and control checks; abstain otherwise.
- The result: state only the measured outcome, with one readable figure.
- The boundary: controlled audit evidence, not a universal verdict about agents' intentions.

For the optional longer recording, walk through the provenance drawer and one failure/abstention example. The recording must remain useful even if live API service is unavailable.

## Visual acceptance

A cold reviewer must answer, without reading the code: what changed, what remained fixed, which outcome is harmful, how uncertain the effect is, whether the example is synthetic or real, and where the evidence comes from. If any answer is unclear, simplify the screen before adding decoration.
