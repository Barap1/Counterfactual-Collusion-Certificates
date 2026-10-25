# W5-FINAL — skeptical submission review

Reviewed 2026-10-25, within the 40-minute timebox. Scope: the five assigned documents, paper main text §§1–8 and abstract; project instructions and task registry were also read. No paper, results, protocol, registry or experimental artifacts were edited. The registry has no W5-FINAL entry; the direct user assignment authorizes this review and its required handoff only. No delegation, git, network, Modal or experimental model/API calls were used.

## Assessment

**The strongest rejection case is insufficient scientific validation of the proposed instrument and reporter, rather than incorrect arithmetic or concealed failed tests.** What survives is a scoped evidence-standard proposal, executable counterexamples, and openly reported negative results. Whether that constitutes enough research contribution is a judge's substantive decision. The minimal honest revision is to make that surviving contribution unmistakable, disclose the execution deviation in the main text, and stop short of validated auditing capability.

The current abstract and §§5–8 explicitly retain the failures. I found no basis in these documents to accuse the authors of converting failed prespecified criteria into passes. R3 reports independent reconstruction and byte-identical report regeneration; I rely on that review, rather than claiming to have repeated it. Severity below measures the threat to submission credibility, not evidence of misconduct.

## 1. A designed identifiability boundary may be too small a scientific contribution

**Severity: HIGH — contribution and scientific validity.**

**Evidence:** `paper/v2/build/submission_v2.md:26`, `:62–64`, `:82`, `:100–102`; `docs/enh/r2/REV_R3.md:15–16`; `docs/enh/r2/run_par/RESULTS.md:3–7`.

The generator supplies opposite labels, equal observables, the separating interventions and the finite policy space over which identifiability is enumerated. Equality of observations forces equal outputs for an auditor restricted to those observations. RQ1/RQ2 therefore validate implementation consistency with a construction, not a newly learned empirical limit. Hundreds of seeds do not independently validate the chosen normative labels or show that the policy space covers plausible real agents. The paper already acknowledges the circularity, but a judge can still regard the executable frontier as a useful teaching artifact with insufficient scientific novelty. Section 2 itself credits prior indistinguishability and intervention work.

**Minimal honest fix:** Present the central result as an executable counterexample and finite-generator evidence contract. State that the frontier is minimal only among the enumerated worlds and declared information sets. Explain the practical artifact added beyond the credited prior work without treating CP intervals on designed consistency as discovery or general impossibility evidence. Do not claim the closed-world Bayes ceiling establishes real-world attribution guarantees.

## 2. The proposed exposure instrument lacks demonstrated end-to-end positive-control recovery

**Severity: HIGH — instrument validity.**

**Evidence:** paper `:68`, `:74`, `:90–92`, `:134`; R3 `:21`.

The draft explicitly says that recovery of the named P4 influence control is not established and that support-level positive-control validation is missing. Deterministic implementation checks cannot establish that the complete replay, carrier extraction, information-loss, placebo and statistical-gating pipeline reliably recognizes a known eligible harmful exposure. P4 influence recovery alone would still fall short of validating an L2 certificate. Zero supported certificates in EXP-002 consequently cannot establish good specificity, useful sensitivity, or a calibrated instrument. Scripted legitimate P2/P3 L2 supports are not attribution errors, but do show why the certificate name must not imply collusion certification.

**Minimal honest fix:** Describe CCC as an implemented, unvalidated exposure-audit procedure; state explicitly that sensitivity and end-to-end certificate recovery are unestablished. Retain the missing-control disclosure prominently. If existing eligible control results can later be substantiated, report their complete recovery counts and scope; do not manufacture validation or count the design specification as the result.

## 3. The substantive prospective predictions failed; selective successes cannot establish the proposed auditor

**Severity: HIGH — claims exceeding evidence.**

**Evidence:** paper `:98–114`, `:144`, `:154`; RESULTS `:5–17`; R3 `:17–23`.

The status vector is RQ1/RQ2 pass by construction; RQ3/RQ4/RQ4b/RQ5 fail; RQ6 descriptive. RQ3 is 61/200 at eps=0 versus the frozen <0.25 criterion, and 41/200 at eps=0.1 without margin. Its failed prediction is not proof of a population rate above 0.25: both reported intervals include 0.25. RQ4's over-attribution prediction holds only for deterministic P2/P3, not all required classes and strata. Its DEV-informed repair RQ4b also fails. CCC-L v1 satisfies only 2/168 complete cell criteria; v0 satisfies 8/168. Undefined selective-accuracy gaps are unestablished, and noisy-stratum pair attribution fails even apart from undefined denominators.

Zero overclaims alone can be achieved by extensive abstention and does not establish useful discrimination. Selected deterministic 200/200 cells cannot repair the failed conjunction or support overall superiority. Conversely, 2/168 versus 8/168 alone does not establish a meaningful overall performance ranking between versions.

**Minimal honest fix:** Preserve the current explicit FAIL labels and the requirement to pass both strata. State in the contribution summary that the proposed ladder reporter has not demonstrated its prespecified utility. Use successful cells only as bounded examples. Do not promote zero overclaims, construction passes, or the eps=0.1 RQ3 point threshold into an overall success narrative. The current paper largely follows this rule; this is a rejection risk from weak outcomes, not an identified reporting reversal.

## 4. DEV-informed amendments weaken the independence of the prospective validation story

**Severity: HIGH — inferential scope.**

**Evidence:** paper `:78–84`, `:92`, `:150`; R3 `:16`, `:19–23`; MISSION `:16–21`.

After observing DEV failures, the team added CCC-L v1's exclusion output, made RQ2 method-independent and added RQ4b. The paper calls this four further amendments while also listing RQ3 being left unchanged, making the change inventory harder to parse. The auditor was written knowing the separating evidence. DEV class balance also differs from prospective RQ3 assignment. Freezing before fresh seeds prevents direct tuning to those outcomes, but does not make the method, hypotheses or generator independently conceived. Under this construction, fresh seeds mainly test robustness to sampled parameters, not transfer beyond the designed policy family.

**Minimal honest fix:** Give an unambiguous change inventory with before/after rule, DEV information used, freeze timing and evidence status. Describe these as prospective evaluations of DEV-selected rules within the same generator, with CCC-L exploratory-method throughout. Keep v0, original RQ4 and all failures beside their revisions. Do not imply that DEV-informed design is prohibited or that this review found post-outcome amendments: R3 expressly reports A4–A6 as pre-freeze.

## 5. D-046 is a material execution deviation absent from the main scientific account

**Severity: HIGH — reproducibility and prospective provenance.**

**Evidence:** paper `:72`, `:84`, `:150`; `docs/enh/r2/PARALLEL_EXECUTION.md:20–22`, `:37–43`, `:87–99`; R3 `:3–9`, `:25`.

The original cross-platform identity requirement did not hold: R3 reproduces differences in 38/40 eps=0.1 units even after decompression. Accepting a five-seed container self-determinism check in place of that gate is an explicit changed execution acceptance rule; unchanged scientific source hashes do not restore cross-platform equivalence. The cause is not established. The paper's main text discusses single-pass freezing and scientific code changes without disclosing this consequential platform exception.

The provenance is also mixed: mapped enumeration/method execution ran on Linux CPython 3.14.2/NumPy 2.2.6; population generation feeding RQ3 and the report tail ran locally. This is distinct from importing the old serial method results. The execution document's later correction admits this, while its earlier “entirely” claim remains. Self-determinism does not demonstrate equivalence of the stochastic scientific outputs across platforms.

**Minimal honest fix:** Add a main-text D-046 disclosure specifying the failed cross-platform gate, replacement gate, unresolved cause, and exact division between container methods and local population/report computation. Distinguish unchanged scientific code from changed execution acceptance. Preserve both runs and failed receipts. Do not erase the deviation by calling it merely acceleration, claim all results are Modal-native, or change RQ3's failure because its provenance differs. No new execution is required for this disclosure.

## 6. “Not supported” in EXP-002 has two distinct, narrow meanings

**Severity: HIGH — interpretation and real-agent evidence.**

**Evidence:** MISSION `:9–12`; paper `:68`, `:76`, `:84`, `:118–138`, `:150`.

The primary NOT supported is failure of a conjunction: the world-cluster lower bound is not positive and exact one-sided p=0.0703 exceeds 0.05, for Delta=1.354 across eight matched world pairs. It tests an exposure-effect contrast between one deceptive prompt regime and authorized cooperation. It neither tests directly for realized collusion nor establishes no meaningful effect, equivalence, safety, or exoneration. The broad CI and registered MDE leave limited precision. Almost half the point estimate is associated descriptively with non-commit cases, while the exclusion sensitivity changes the estimand and does not rescue inference.

Separately, the 11 checkpoint-level `not supported` certificates are exploratory threshold decisions under this procedure, alongside five inconclusive and zero supported. They are not 11 demonstrations of legitimate conduct. There is no M/H/I(S) ground truth for these real-agent worlds, the carrier detector is weak, placebo exists at only 2/16 checkpoints, and information-bearing status defaults conservatively. The 199 scheduled records are not 199 independent observations or even 199 executed continuations: 143 executed, 56 unrun placebo branches. The independent sample is eight matched pairs.

**Minimal honest fix:** Keep the numeric primary result and both failed criteria together wherever the result is summarized. Explicitly distinguish the failed directional hypothesis from the certificate status named `not supported`. Retain the correct independent sample size, missing-placebo accounting and inability to infer absence or attribution. The current §5.4 is substantially honest; stronger downstream claims would exceed it.

## 7. No EXP-003 result bridges the scripted twins to a real-agent separating probe

**Severity: HIGH if real-agent frontier validation is claimed; otherwise MEDIUM external-validity gap.**

**Evidence:** paper `:13`, `:60–64`, `:76`, `:84`, `:116–150`; `ops/tasks.json` lists RA-LEAD/EXP-003 as RUNNING, not an accepted result.

The reviewed main text contains no EXP-003 methods, result, sample accounting or evidence status. EXP-002 illustrates exposure effects without ground-truth attribution or I(S); it does not validate the twin-world separation claim in real agents. Thus the only demonstrated frontier is scripted, and the motivating environment-probe narrative should not imply tested real-model responsiveness. Registry state may be stale; this review does not establish that EXP-003 artifacts do not exist elsewhere.

**Minimal honest fix:** State plainly that real-agent twin/probe validation is not included and that EXP-002 does not supply it. Remove any implication that it has been completed. If EXP-003 is added later, require its actual protocol, attempted/failed-case accounting, platform and evidence category, and review it as a separate study. Do not silently insert a late favourable example or pool it with EXP-002/R2. Completion is not necessary to make the present narrower paper honest.

## 8. Normative labels and “highest justified rung” can sound more authoritative than the design warrants

**Severity: MEDIUM — construct validity.**

**Evidence:** paper `:49–68`, `:76–78`, `:114`, `:142–150`.

Attribution labels are part of the generator, and I5 supplies an external authorization record. Authority to authorize, correctness of that record and completeness of the possible-policy space are assumptions, not conclusions of a knockout. The reward harm margin and welfare tolerance are declared task conventions. An I4 response distinguishes the designed policies; it cannot exclude every real policy that could mimic that response. “L3 excluded” is particularly liable to be read as exoneration beyond the finite world space. The current disclaimers help but do not validate those normative assumptions.

**Minimal honest fix:** Qualify inclusion and exclusion verdicts as relative to the declared norm, generator/policy space and assumed trustworthy separating record. State that task reward loss and authorization are not universal legal or ethical definitions of collusion. Keep L2 support on legitimate P2/P3 as exposure-harm evidence, without recoding it as an attribution false positive or treating authorization as a universal ground truth.

## 9. Reproducibility evidence is substantial, but the provenance narrative and durable release remain incomplete

**Severity: MEDIUM — auditability and release readiness.**

**Evidence:** R3 `:3–9`, `:25–27`; PARALLEL_EXECUTION `:90–99`; paper `:30–32`, `:158`.

R3 reports 42,000 reconstructed records, frozen-hash agreement, no failed method outputs or seed replacement, 149 matching serial eps=0 units and byte-identical regenerated reports. These are meaningful positives. They do not establish absence of unlogged interim looks or explain stochastic platform divergence.

Provenance corrections remain internally inconsistent: the archived GATE receipt cited for a successful comparison actually records missing files; the later correction still refers vaguely to another archived run. “20 units” confuses ten unit files plus ten partitions, spanning five independent seeds and two strata; the eps=0 comparison is five units plus five partitions. A gate platform string reflects controller Python 3.14.7 rather than worker 3.14.2. R3's detailed supporting reconstruction is referenced under `/private/tmp/ccc-W1-R3/`, whose durable inclusion in a release is not established here. The main paper's public release remains `[OWNER]`; rendering is described as pending while a figure reference is already present. Neither final release access nor final rendering was tested in this task.

**Minimal honest fix:** Supply one consistent provenance table linking the failed receipt, actual post-run comparison, self-check artifacts and controller/worker versions. Count files and independent seeds separately. Preserve historical receipts and put explanatory corrections beside them. Archive the independent audit commands/results in the durable release and identify a usable release target. Check the final rendered figure/caption pairing. Keep the distinction between offline report reproduction and regenerating platform-sensitive experimental outputs; never rerun reporting into immutable originals merely to demonstrate reproducibility.

## Release priorities

1. Make the scientific contribution an evidence contract and counterexample suite with negative validation results; do not imply a validated collusion auditor.
2. Put D-046 and the missing real-agent twin/probe evidence in the main text, alongside existing limitations.
3. Preserve every failed criterion and DEV disclosure; distinguish primary hypothesis failure, certificate statuses and closed-world exclusion.
4. Repair provenance descriptions and create durable, runnable reproduction evidence without changing historical outputs.

These are recommendations only. This task made no edits to the paper or results and authorized no additional experiments.

## Review evidence and limits

The five source SHA-256 values at review capture were:

```text
73a274d60afaa2eec0a892d99156396eb5e23ebaff053f12c0147daeb6b14a37  docs/enh/MISSION.md
7479e74cf4b71c6e5e7814653f74ff2e7225abad4eccaa6db90b780a0bdcd1ba  paper/v2/build/submission_v2.md
18a291148f8499d7d0e7f4038b4fff11ed5d2b5b0c3c34a5d15e62b7121426d5  docs/enh/r2/run_par/RESULTS.md
b5e9c9c073dda0de299aef466ab550ff866507f57ce78b1d36c5a6984c96b042  docs/enh/r2/REV_R3.md
fb47eff2dced6fffaea768664f93f3d75f97e5cd8d28b852f82275ffcea0012f  docs/enh/r2/PARALLEL_EXECUTION.md
```

This is a document-based scientific review. R3's numerical/code/receipt checks are attributed evidence, not W5 re-executions. No independent citation verification, source-code inspection, raw-data reconstruction, final PDF rendering, cloud execution or EXP-003 artifact search was performed. No additional spec modules or master spec were loaded beyond the mandatory control-plane entry. No secrets were read. No separate model was invoked for experiments or review.

### Shell command inventory

Exact read-only shell commands run before writing this review (the first combined display was truncated, so the relevant paper and review text was re-read in smaller displays):

```sh
pwd && cat CLAUDE.md && cat ops/tasks.json
wc -l CCC_START_HERE.md docs/spec/00_control_plane.md docs/enh/MISSION.md paper/v2/build/submission_v2.md docs/enh/r2/run_par/RESULTS.md docs/enh/r2/REV_R3.md docs/enh/r2/PARALLEL_EXECUTION.md; cat CCC_START_HERE.md; cat docs/spec/00_control_plane.md
nl -ba docs/enh/MISSION.md; nl -ba paper/v2/build/submission_v2.md; nl -ba docs/enh/r2/run_par/RESULTS.md; nl -ba docs/enh/r2/REV_R3.md; nl -ba docs/enh/r2/PARALLEL_EXECUTION.md
sed -n '70,190p' paper/v2/build/submission_v2.md | nl -ba -v70; cat docs/enh/r2/run_par/RESULTS.md
rg --files -g AGENTS.md -g CLAUDE.md docs paper ops; ls -l docs/enh/FINAL_REVIEW.md ops/reports/W5-FINAL.md 2>/dev/null; sed -n '1,70p' paper/v2/build/submission_v2.md; cat docs/enh/r2/REV_R3.md
python3 - <<'PY'
from pathlib import Path
import hashlib
paths=['docs/enh/MISSION.md','paper/v2/build/submission_v2.md','docs/enh/r2/run_par/RESULTS.md','docs/enh/r2/REV_R3.md','docs/enh/r2/PARALLEL_EXECUTION.md']
for p in paths:
 print(hashlib.sha256(Path(p).read_bytes()).hexdigest(),p)
PY
```

Edits used `apply_patch`, restricted to this file and `ops/reports/W5-FINAL.md`. Final validation command:

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, re
review=Path('docs/enh/FINAL_REVIEW.md').read_text()
for digest, name in re.findall(r'^([0-9a-f]{64})  (.+)$', review, re.M):
 assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest, name
findings=re.findall(r'^## [1-9]\. ',review,re.M)
assert len(findings)==9
for heading in ['**Severity:', '**Evidence:', '**Minimal honest fix:']:
 assert review.split('## Release priorities')[0].count(heading)==9, heading
report=Path('ops/reports/W5-FINAL.md').read_text()
assert len(report.split())<=300
assert re.findall(r'^## (.+)$',report,re.M)==['Task','Status','Artifacts','Validation','Limitations','Budget','Next']
print('PASS: five source hashes unchanged; nine complete findings; handoff headings and word limit valid.')
print('Handoff words:',len(report.split()))
PY
```
