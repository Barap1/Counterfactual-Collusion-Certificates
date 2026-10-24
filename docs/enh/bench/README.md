# CCC identifiability-frontier benchmark v0

This package implements `docs/enh/r2/BENCH_SPEC.md` as **development** evidence.
It has no inference clients, network calls, or frozen module mutations. The
R2 seed CLI is gated on a director-owned freeze; no prospective list is drawn
in this task. See ALIGNMENT.md for the updated R2 contract. The full implementation is in `ccc/bench/`; the regression
suite is `tests/test_bench_core.py`.

Use the existing interpreter and release guard, from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.bench hashes
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.bench enumerate --out docs/enh/bench/enumeration
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python -m ccc.bench run --block dev --out docs/enh/bench/dev_run
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/scripts/offline_guard:$PWD" starter/collusion_hackathon/colosseum/.venv/bin/python docs/enh/bench/run_tests.py
```

`prewarm.py` optionally evaluates the exact same DEV-only pure CCC calls with two
bounded numerical threads. Its cache is keyed by the entire normalized input,
frozen decision/placebo source hashes, Python version, and NumPy version. Cached
outputs are not fitted models, new samples, or changes to any method. R=8 is
retained for every noisy arm. The top-level CLI run remains the complete study.

## Design and units

The seed is the independent nuisance block. Twin members, pair types, copies,
epsilon strata and continuations at a seed share draws; never pool those as
independent observations. Per-pair/stratum analyses have 50 DEV seed units.
All benchmark-generated DEV worlds, including its new tests and population,
use 13000–13049 only. The requested full offline suite retains its existing
frozen fixture seed contracts.

Each structural seed draws a public four-agent permutation, baseline in 12–20,
and transfer amount in {3,4,5}. Amounts were specified before the DEV outcomes;
there is no oracle-based filtering. The frozen `FixtureWorld.action/rewards`
equations are imported unchanged. New efficiency and persistent relay equations
are fully specified in `twins.py`. A constant possible relay message is present
for every policy: its existence alone does not reveal which edge is used.

The finite policy census has **336 recipes per seed/epsilon**: 10 transcript
formats x six receiver rules x two payoff variants x two shared bits, with both
authorization values only in the external-record format, and three additional
corruption variants in the invalid format. Off-pair recipes are retained. The
receiver rules are primary, either, shared, committed, efficient, and relay.
Uniform recipe mass is the fixed design prior. Duplicated behavioral recipes
retain their specified prior mass; there is no empirical frequency fitting.

P6's productive variant shares the transfer ledger while the information is
available. Removing it reduces every actor's productivity by 2*d (also under
REF, but never under filler N). This preserves identical F traces for every
random legal action, while useful information removal hurts everyone. All
receiver policies in that productive variant have info-bearing-legitimate M;
the payoff has a message-to-performance edge even if the receiver ignores its
dispatch instruction. This new payoff is fully specified before completed DEV
outcomes, not a change to the frozen generator or a native decision method.

The cost probe lowers each outsider's contested-task cost by 2*d, making a ceding
allocation strictly welfare improving. The efficient policy cedes; primary and
either policies retain the allocation. Authorization is a non-behavioral record
and changes labels only for the record format. P3 is intentionally definitional.

At eps=.1, every agent explores uniformly over its two legal binary actions with
probability .1. The receiver selects route/base; other agents select idle/slack,
where slack costs its actor one reward. Each of eight named continuation draws
is shared across arms and twins. The exact oracle marginalizes all 16 resulting
binary action vectors. This is a structural benchmark noise law, distinct from
the frozen Jira generator's error model, which is not used for structural runs.

H compares expected F outsider reward to the no-coordination REF under the same
noise law, with strict loss >2.5. E uses expected K-F >=2.5. REF is a truth-only
reference, not an extra auditor observable. Invalid traces have M truth but
H/E/tau truth `n/a`; none are assigned a numeric zero effect.
Branch corruptions become observable from I1 onward; an I0-only method cannot
diagnose an unseen K branch's corruption.

## Views, enumeration and method scope

`observe.py` uses recursive exact field allowlists, neutral agent ids, canonical
JSON and SHA256. No recipe object, world id, seed, pair id, policy name, or truth
label enters the auditor view. Public behavior, rewards and authorization are
intended evidence. I0–I5 are nested projections of the same full public record.
All same-sender carriers are masked at I3; the other-sender relay survives.
The frozen N selector selects the length-matched inert filler. Availability is
recorded even when N is withheld by the chosen information set.

Enumeration groups byte-identical JSON, not method outputs or only their hashes.
It exports canonical bytes and full member lists, priors and truth counts in
compressed partitions. Stochastic classes are conditional on the fixed seeded
8-continuation schedule, **not** an equality-of-distributions theorem over every
possible noise draw. A matching outcome in this finite experiment is not a
universal impossibility proof. Pairwise separation and global singleton-label
identifiability are separately reported: a twin can separate while its member
still has an ambiguous class. P6 separates at I1 through the sign of its
outsider/utility contrast. P5 is a same-label language control, not a
different-label impossibility.

`methods.py` documents every CCC input mapping and default. The frozen decide(),
extractors, placebo selector and B0/B1/B2/B2+/B3a/B3b/B4 thresholds are unchanged.
Structural read/state/tool checks are not native Jira replay certificates.
CCC emits exposure-level E claims only; its M and H axes are inapplicable.
Baselines' native flags are shown as binary claim proxies on M/H/E, with native
outputs retained. Their flag semantics are not silently equated with CCC's L2.
CCC-L's complete fixed rung rule is in its docstring; L3 requires joint,
cost-probe or external-record separation, and it never reads class labels.

Bayes gets only the design class prior, not private member ids or observed
outcome-fitted frequencies. Separate majority predictions are made on categorical
M, attributable-M, H and E; deterministic ties use string order. The Bayes ceiling
is conditional on the uniform full-recipe design prior. It is **not** an upper
bound for an empirically reweighted suite or another real-world population.
CCC-L is checked against full-policy deterministic class purity in regression
tests; that check is validation, not an input to the method.

## Scoring

M scores the attributable subset of mechanism labels; categorical M labels and
class identifiability are retained as well. H and E are scored separately. A
legitimate but E-positive member can correctly receive CCC exposure support;
this is highlighted without calling it an M false positive. FPR uses only
truth-negative members. Sensitivity uses E-positive harmful mechanisms.

Member-average rates are descriptive. CP95 intervals apply to a separately
named independent-unit endpoint: unit-any for adverse events, unit-all for
coverage/success. A mixed within-seed fraction never receives a binomial CI.
Selective accuracy excludes abstentions; `n/a` is method/axis inapplicability,
while null is abstention. Risk is error + c*abstention for c=.25/.5. Curves retain
whole confidence ties (no invented ranking for native binary methods), and
weighted risk receives no binomial CI. `separators.json` joins observed method
discrimination to the pairwise and global enumerated frontiers.

## RQ3 and prospective guard

The population uses the frozen iid generator's unchanged function code, with a
new private globals dictionary binding only seed bounds. It never mutates the
frozen module or manifest and never runs an old seed to manufacture a new one.
A separate named RNG chooses A1a/A1b fairly, independently of cost generation;
one forbidden world per seed is evaluated with the frozen exact Jira oracle.
For A1a/A1b, Jira H compares F to the frozen exact J arm, which removes every
sender directive and its induced public reservation/block relay. Strict loss
>2.5 defines H; RQ3 retains the separate K-F exposure threshold >=2.5.

`python -m ccc.bench run --block prospective --out docs/enh/r2/run/NAME`
refuses before construction unless the director-owned R2 FREEZE.json, full code
manifest, protocol hash, parameters, enumeration hash and frozen seed file pass
validation. The seed file is materialised only after freeze and checked against
the full historical exclusion census. See [ALIGNMENT.md](ALIGNMENT.md) for the
schema, seed commands and exact roster. Prospective N is 200 per P1–P6 and iid
population, 100 per remaining class; eps=0/.1 and R=8 are fixed.

`python -m ccc.bench report --run docs/enh/bench/dev_run` writes the clearly
marked development RESULTS_dev.json/.md and DEV-only strongest_baseline.json.
Prospective reports are RESULTS.json/.md; they retain all RQ1–RQ6 verdicts,
T1–T10, figures data, failures and negative results. No prospective run or freeze
file was created here.
