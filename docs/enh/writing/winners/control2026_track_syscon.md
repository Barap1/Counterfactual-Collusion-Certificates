# Syscon: Kernel-Level Syscall Monitoring for AI Agent Control in Sandboxed Environments
- Sprint/place: AI Control Hackathon 2026 (Mar 2026), track award (place not verified; filename says "track"). Authors: Jade Sheffey, Joyce Levine, Joyce Werhane, Willow Taylor.
- Page: https://apartresearch.com/sprints/projects/syscon-kernellevel-syscall-monitoring-for-ai-agent-control-in-sandboxed-environments-guun
- PDF: https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/87fc5646ec1bbcb8-3e3f25a7-75a0-425d-96dd-15e27b1da988-Apart_SysCon.pdf
- Accessed 2026-10-24.

**Pages:** 13 total; main text ~10 (Appendix A: example receipt after refs).
**Sections:** Abstract; 1 Introduction (1.1 Threat Model, 1.2 Approach); 2 Related Work; 3 Methods (architecture, receipt generation, knowledge graph/harness); 4 Evaluation (setup, compression, qualitative signals, signal discrimination, integration); 5 Discussion and Limitations (observability as primitive, limitations, future work); 6 Conclusion; Code and Data; Author Contributions; References; A Example Receipt.
**Abstract:** ~203 words; gap, system, scale (234 trajectories, 9 attacker models), qualitative signals, then the negative result (monitor integration did not improve detection).
**Intro first sentence:** "When an AI agent runs a shell command inside a container, the trusted monitor sees the command text" (concrete scene).
**Contribution style:** numbered list after a "completed during the hackathon" scoping line; claims "first" qualified with "To our knowledge".
**Figures/tables:** 5 captions (Tables 1-2, Figures 1-3). Figure 1 = knowledge-graph excerpt from a real attack trajectory (reviewer: too small).
**Tone:** engineering-precise, candid.
**Limitations/negatives:** subsection 5.2 names tooling gaps (no syscall arguments, TOCTOU races, compression blind spots). Headline negative result sits in the abstract and title claim "observability and detection are distinct". Dedicated threat-model subsection; no separate dual-use appendix seen.
**Related work:** section 2, ~36 lines, after intro.
**Code link:** GitHub plus interactive demo, in "Code and Data".
**Judge reviews:** Praise: brilliant idea, honest negative results, clear structure, thorough threat model, helpful example receipt. Criticism: no FPR-conditioned detection curves, no error bars, trajectory-level monitoring unrealistic for long runs, Figure 1 too small.
**Title style:** system name, colon, technical descriptor.

**Takeaway for collusion-attribution evidence standards:** an appendix with one worked example artefact (the receipt) lets reviewers audit what the evidence actually looks like; ship a worked evidence record for attribution claims.
