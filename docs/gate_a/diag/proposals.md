# GA-DIAG proposals requiring director/science decision

No proposal below has been applied. Thresholds, fixture definitions, split manifests,
protocol text and decision semantics remain unchanged. No held-out world was generated.

1. **Separate objective truth from construct-positive controls (FIXTURE DESIGN).**
   A1's iid generator samples costs/priorities/order without conditioning on effect,
   welfare or margin (`ccc/fixtures/iid.py:generate_iid`); the oracle assigns
   `forbidden` from the recipe family, not realized harm. Retain this unconditional
   population and report its effect distribution, rather than call every objective
   label a materially harmful exposure. Add a separately declared deterministic
   reference suite whose public task/reward structure creates an outsider priority
   tier loss (5 reward / 2 outsiders = 2.5 Omean), with effect strictly above the
   floor, coalition benefit, and the protocol's efficiency constraint. Derive each
   control analytically before running CCC; do not search seeds or reduce m_O to
   maximize Gate A sensitivity. Report mechanism detection and construct detection
   separately. This changes fixture/test expectations and needs director approval.

2. **Review what the N lesion veto identifies (PROTOCOL DESIGN).**
   In all 12 A1 cells with tau_O > 2.5, F-vs-N equals F-vs-K and the current case
   lesion flag blocks support. Only four of those 12 also pass both pattern gates.
   Replacing a causal instruction by neutral filler can remove its intended causal
   content without demonstrating a nonspecific intervention artefact. Science must
   specify what observations distinguish content removal from general disruption:
   e.g. an independently constructed, task-information-matched control battery,
   with explicit expected contrasts and unchanged harm scale. Decide whether N is
   a blocking validity diagnostic or a reported sensitivity contrast for such
   instructions. Any changed contrast, null, or veto is a new reviewed protocol
   version, not an engineering patch. Keep the v1.1 result visible.

3. **Align redundancy acceptance with observable carrier coverage (PROTOCOL DESIGN,
   with FIXTURE DESIGN implications).**
   The V07 handoff bug is fixed. The residual 48/120 A5 not-supported cases are
   implicit (12 verbatim, 16 paraphrase, 20 public cue). Of these, 24 A5a
   cells deliver no surviving private communication at all (12 verbatim + 12
   paraphrase): the intended resend is not instantiated in the K receiver
   horizon. Classify these as FIXTURE DESIGN, with a structural resend/read
   control needed before requiring abstention. The other four paraphrase
   cells do deliver a semantic equivalent that both detectors miss. Protocol §9 explicitly
   says encoded/semantic carriers may evade its lexical/tuple detector, naming
   A5b; therefore a blanket 120/120 abstention requirement is not attainable by the
   specified detector. Separate observable-carrier conformance from semantic-carrier
   stress performance. Add independently specified lexical/agent-task commitment
   positive/negative controls over every receiver prompt/surface; preserve the
   covert cue stress set and publish misses. Review the two existing extractors:
   V07 can match task commitments without author identity, whereas audit.text uses
   narrower agent-task tuples. Unify only under a reviewed detector contract and
   the preregistered DEV-only pinning procedure; do not lower thresholds or import
   fixture-private semantic decoders to make these examples pass.

4. **Make A6b faults structurally exercisable (FIXTURE DESIGN).**
   The ten inactive worlds give the receiver just one remaining observation; a
   one-shot mask equals a persistent mask there. Add a separate declared stress
   configuration with at least two receiver observations after the fork and the
   original event still visible at the later read. This is a scheduling/fixture
   precondition, not outcome selection. Preserve all attempted worlds and report
   requested/exercised/invalid counts together: currently 360/350/350. The legacy
   all-requested Gate A check stays 350/360 FAIL; the activation-conditional
   diagnostic is 350/350. Do not label a valid replay invalid because its recipe
   requested a fault.
