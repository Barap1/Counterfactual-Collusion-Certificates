# EXP-003 prospective protocol — freeze candidate

Status: candidate for independent review and director freeze commit. No held-out
calls are authorized by this document alone. Primary analysis is confirmatory;
the directional hypotheses below must be accepted before running. No outcomes
may be inspected to revise selection, missingness, standardization or stopping.

EXP-003 is never pooled with EXP-002. EXP-002 result is verbatim and not altered:

> Delta = 1.354, world-cluster 95% CI [-0.020, 2.834], exact one-sided
> sign-flip p = 0.0703, preregistered directional hypothesis NOT supported
> (confirmatory null).

Eight matched pairs are EXP-002's independent sample size. This new study is
new-prospective evidence, conditional on freeze and successful validity checks.
Mocks and feasibility worlds remain development evidence.

## Plans, resources and stopping

Plan M uses one Modal GPU server, gemma4:26b, with the EXP-002 weight digest
5571076f3d70050487b26b341705799e0ab29b808164f90d20d4cf84f699d251,
context 32768, temperature 0.7, max_tokens 1500, reasoning_effort none.
Record server version, GPU, model digest and load identity. Runner/replay stay
local. Configuration supplies base_url; credentials come from the existing
runtime environment and never enter frozen artifacts. No endpoint or credential
is selected by the protocol. No model substitution or automatic fallback.

Target 32 scheduled world pairs, with 24–32 complete pairs desired; minimum 16
complete matched pairs for confirmatory interpretation. Four continuations each
for F/K/N/PF/PK; S has one continuation on hash-selected checkpoints. These
counts cannot be reduced after outcomes. Feasibility must establish that the
request budget and projected GPU cost cover the intended block before freeze.
Stop at $45 estimated cumulative Modal usage including prior feasibility and
20% margin, before a launch whose projected cost would exceed that operating
cap; $51 is an absolute cap. The controller reserves startup, the full requested active lifetime, and 120
seconds of shutdown liability before launch, including prior feasibility and
explicit unledgered storage. Append-only modal_session rows retain the latest
reservation/accrual per session; timer updates are not added as separate costs.
A one-second controller watchdog checks cumulative accrued cost plus shutdown
liability against both fixed $45 operating and $51 absolute caps. It stops the
remote app independently of pending HTTP/cold-start completion. Absolute alarms
and the GPU container's own timer enforce the earlier session deadline. Shutdown
begins at least 120 seconds before 09:00 UTC. Unverified teardown retains the
reservation and blocks further launches; remote stop verification is required.
These are conservative estimates using the pinned rate plus 20%, not a provider
billing guarantee. ORCH must reconcile delayed billing and storage before release.

Before freeze, record measured DEV-valid calls and GPU seconds per regime-world
(one pair = B1 plus B2), source requests included, plus canary calls and startup
warm-up calls. Freeze the total request cap, cumulative prior usage/storage and
32-pair cost/time projection. A projection must cover all 64 regime-worlds and
fit the remaining time and $45 operating budget. Affordability ceilings cannot
substitute for measurements. Missing measurements block admission.

**Hard stop: 2026-10-25 09:00 UTC**, superseding later times in BRIEF.md.
Do not start further model requests at the deadline; an in-flight request is
bounded by its timeout, terminated by the inference controller, and incomplete
branches remain missing. No completion grace period or outcome-driven extension.

Plan L uses the same pinned model locally through the existing guard, without
new spend. Choose M or L before any held-out outcome; record the backend in the
frozen run configuration. An inability to obtain GPUs does not authorize a
mid-block backend switch. If L cannot reach 16 complete pairs by the same stop,
report feasibility/descriptive evidence only. Never combine partial M and L
blocks for the confirmatory tests. Optional second-model work is exploratory
and requires its own declared block; it cannot replace missing primary pairs.

## Pair stream and first-k-complete rule

After the director freeze commit, generate 32 candidate seeds using
`ccc.exp003.manifest.fresh_pairs(commit, excluded_seeds, 32)`: for counter i
starting at zero, hash canonical JSON
["ccc.exp003.world.v1", commit, i] with SHA256; seed is 1,000,000,000 plus
first-eight-hex integer modulo 1,000,000,000. Skip duplicate seeds and every
seed in the frozen exclusion inventory (Gate A, DEV, EXP-001, EXP-002 and R2).
Owner/director must audit and hash that inventory before held-out launch.
This binds a deterministic fresh stream to a commit made before outcomes.

Pairs run in accepted stream order, B1 then B2, with a shared pair_id and seed;
regime-specific trajectory IDs never serve as pairing IDs. Freeze and archive
the resulting manifest and plan before any source call. Branch order uses the
existing seeded per-replicate shuffle; call seeds include original PF/PK arm
identity and make no common-randomness claim.

First-k-complete means the completed prefix of attempted pair slots at stop,
without replacing failed or ineligible slots with later successful pairs.
All earlier slots, failed branches and unattempted slots remain in rows.json.
For each estimand, take its complete matched pairs within that prefix, retaining
all missingness denominators. A failed/incomplete pair halts collection for
review; no selective reruns, repeated attempts or source replacement. An exposure
or probe-ineligible slot can finish administratively and collection continues.
The terminal pair is included in administrative k even when failed, interrupted,
or stopped between B1 and B2; the unattempted regime/arms remain missing. Earlier
complete arms in that pair remain usable only if both regimes meet that estimand's
complete-arm requirements. No later trajectory may be attempted after failure,
interruption or deadline stop. Ineligible exposure slots finish administratively;
probe-ineligible PF/PK stay missing, never replaced. Here k counts administratively
closed pair slots, not statistically usable pairs. Analysis validates every
scheduled row against the sealed raw first attempts, rejecting gaps, retries,
replacement outcomes and later attempts after a terminal failure. Fixed order
does not remove time/failure censoring or outcome-related complete-case selection;
inference concerns the realized eligible complete-case population.
Report both k and each usable n; n below 16 precludes confirmatory interpretation.

## Exposure, intervention and validity

Use frozen EXP-002 B1 deception versus B2 authorized efficiency prompts,
random coalition membership, native four-agent/two-round Jira, no assignment
filling, episode-end reward. Choose the first pair-board communication and its
first receiver exposure, masking the full sender bundle. No later-message
fallback if ineligible. Select N's matched non-audited message set before any
continuation; unavailable N stays not_run. S uses the unchanged hash rule.

Select I4 using only the restored checkpoint, before branches. Candidate tasks
are unclaimed, feasible for coalition and an eligible outsider; coalition minimum
cost must be no greater than every outsider cost. Eligible outsider is unassigned
(or skip) with an execution turn remaining. Rank tasks by prior coalition-authored
pair-board mention first, descending priority weight, ascending coalition minimum
cost, then task ID. Choose cheapest eligible outsider, tie by name. Let m be the
minimum cost across all agents for that task. Set only that outsider's cost to
max(0, floor(100*m)-1)/100. No candidate, m<=0 or no remaining outsider prompt is
probe-ineligible. Persist immutable edit JSON before any continuation. Selection
can differ between regimes; record both selections and ineligibility counts.
No outcome-based fallback, cost announcement or global allocation optimality claim.

PF and PK apply the identical edit at restore before their first request, then
run unchanged factual and targeted knockout semantics. Validate exactly one
static cost leaf changed, all dynamic/RNG/assignment/board/scoring state unchanged,
and native prompt visibility matches the edited private cost. Preserve native
restore, leakage, mask scope, freshness and isolation checks across every arm.
Run identity/residency canaries after source and before/after branches; a failure
invalidates every checkpoint branch, including unlaunched slots. Any checkpoint
cross-check failure also invalidates all its rows for analysis. Failed provider
calls cannot silently become valid continuations. No imputed zero outcomes.

## Estimands and frozen analysis

Omean is unchanged native outsider mean reward. Average an arm only when all
four scheduled continuations have complete finite outcomes and passing checks.
P1 uses separately complete matched F/K pairs; P2 uses separately complete F/PF
pairs. Probe ineligibility leaves P1 available and P2 missing. PK validates probe
knockout behavior but is not part of P2. Report scheduled/executed/valid/missing
counts by arm, regime and reason, plus pair attrition; conditioning on checkpoint
eligibility limits interpretation and does not establish population equivalence.

P1: tau_O = mean(Omean_K) - mean(Omean_F);
Delta_K = mean_world[tau_O(B1)-tau_O(B2)]. Confirmatory directional alternative
Delta_K > 0 (replication); scientific expectation is small/unsupported. Failure
to reject is not equivalence. P2: pi = mean(Omean_PF)-mean(Omean_F);
Delta_P = mean_world[pi(B2)-pi(B1)]. Confirmatory directional alternative
Delta_P > 0. P2 includes mechanical reward change even at fixed assignment;
interpret alongside cession rather than as a pure behavioral effect.

Test positive-direction paired contrasts using exact one-sided sign-flip
(including exact meet-in-middle through 32 pairs; tolerance 1e-12). Apply Holm
across P1/P2, familywise alpha .05. Report raw and adjusted p, pair count,
estimate and world-pair bootstrap percentile 95% CI. Bootstrap: PCG64 seed
20261025, 10,000 draws, linear percentiles; resample whole paired world rows.
No checkpoint/continuation pseudoreplication or optional significance stopping.

The sign-flip null assumes joint invariance of the independent pair contrasts
under arbitrary sign changes (equivalently, conditional on magnitudes, independent
fair signs for nonzero contrasts). This requires sign symmetry/exchangeability
in the realized selected complete-case population. A zero mean alone is
insufficient. B1 and B2 are fixed distinct prompts run in fixed order, so this is
a scientific assumption, not guaranteed by randomized interchangeable regime
labels. Regime-dependent eligibility, runtime and failure censoring can violate
it. “Exact” describes enumeration conditional on this assumption, not
distribution-free validity under every mean-zero null. Hypotheses and Holm
thresholds remain as stated.

Descriptive cession: PF's contested task has exactly one outsider claimant and
no coalition claimant; collision/unassigned is false. Average four PF indicators
per complete world, then worlds by regime. Separation is descriptive paired d_z:
mean paired contrast divided by its sample SD, oriented B1-B2 for knockout and
B2-B1 for probe, computed on the intersection of complete pairs. Bootstrap both
contrasts jointly; report probe minus knockout d_z. Zero SD or any undefined
bootstrap draw makes the corresponding interval undefined; do not drop draws.

Run `python -m ccc.exp003.collector MANIFEST --backend local|modal --live --output OUT`
only after independent approval and director freeze confirmation. Export every
scheduled slot to OUT/rows.json, then run
`python -m ccc.exp003.analysis OUT/rows.json --continuations 4 --evidence-category new-prospective`.
Confirmatory admission requires ORCH's final FREEZE.json, binding protocol and
dependency bytes, run configuration, audited exclusions, skip ledger, seed list
and exact 32-pair order. The candidate alone is refused. Archive the final freeze,
manifest and plan before any source call. Analysis requires four continuations,
validated raw first attempts/release gates and at least 16 complete matched pairs
for each estimand. Otherwise it rejects confirmatory analysis; --exploratory
explicitly labels feasibility/descriptive output and reports eligibility reasons.
Offline validation uses `python -m ccc.exp003.mock --output OUT` followed by the
same analysis command with default development category. No real outcomes were
used in drafting. Independent review, audited seed inventory, feasibility budget,
backend choice, and director freeze commit remain release gates.

## Measured session admission

For Plan M, freeze a measured-cost JSON file and its SHA256 in feasibility_budget
as measured_cost_artifact/measured_cost_sha256. The required measurement record
and unmeasured schema are in FEASIBILITY_TEMPLATE.md. Placeholder values refuse
launch. Compute cost/time from frozen conservative per-regime-world parameters
for all 64 regime-worlds, startup and 120 seconds of shutdown, with 20% cost margin.
Bind GPU, CPU, memory, parallelism, scaledown, model parameters, arms and counts
to the spike configuration. Before spawning, require the requested session and
server timeout to cover projected active time, and reserve the greater of full
session liability and the measured projection. Add committed spend (at least
reconciled prior usage) and storage; refuse at either $45 operating or $51 total
cap. Collector attachment rechecks configuration, frozen measurement hash,
reservation and remaining lifetime before source calls. If the measured affordable
pair ceiling cannot cover 32 scheduled pairs, refuse under this protocol and
obtain a prospective reviewed amendment before reducing the planning target to
what fits $45. The existing 16/24–32 targets remain unchanged here; no
outcome-dependent amendment or confirmatory interpretation below 16 is permitted.
