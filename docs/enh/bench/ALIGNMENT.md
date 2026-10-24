# BENCH-ALIGN implementation notes (development)

The binding input for the next study is `docs/enh/r2/PROTOCOL.md`, including
A1–A3. The director owns FREEZE.json. This task does not create that file, draw
prospective seeds, construct prospective worlds, or change a frozen method.

CRN was already present in BENCH-IMP: `random.Random` receives
`bench-v0:{seed}:continuation:{index}`. Member, policy, authorization and arm do
not enter it. Both noise strata and all arms/probes therefore use the same draw
for pointwise-identical policies. The new regression exercises both P3 members
for every arm, probe and continuation, then checks full method-output symmetry
at eps=.1 and injects a detectable output leak. No noise or payoff law changed.

## Historical seed enumeration

`ccc/bench/seeds.py:exclusions` walks every JSON, JSONL and CSV file under
`docs/analysis/exp002_heldout*`, `docs/analysis/exp001_dev*` and
`results/baselines/`. It streams every regular JSON/JSONL/CSV member of every
`docs/runner/archives/*.tar.gz`, including manifests, plans, branch records and
sampling requests. No archive is extracted. AppleDouble members and secret
filenames are skipped; no secret is read. No outcome is used to choose seeds.

Recursive dictionary keys containing `seed` collect integer values, lists and
nested seed mappings; numeric string seeds and embedded JSON request bodies
are decoded too. Numeric `world_id` fields are conservatively included because
analysis exports can preserve the world seed under that name. This includes
world, sampling, master, bootstrap, branch-order and placebo seeds rather than
only experiment master seeds. Conservative extra exclusions are intentional.
The per-source seed values and SHA256s are in `seed_exclusions.json`. This is
an exclusion census, not a prospective list. No seed from it is instantiated.

The ledger has 27,209 sources and 6,247 distinct historical seeds. Separate
excluded sets are Gate A 12000–12019, DEV 13000–13049, historical seeds, and all
integers 0–99999. A list hash is SHA256 of UTF-8 JSON of the sorted integers with
compact separators and no newline. The source-ledger hash uses sorted JSON
keys. Enumeration is repeated during materialisation and each seed check; any
change invalidates the frozen metadata rather than silently replacing seeds.

## Seed CLI and director freeze integration

After the director commits a reviewed `r2-freeze-1` file with status `FROZEN`,
use the following commands. **They were not run to materialise a real list in
BENCH-ALIGN.**

```sh
python -m ccc.bench seeds --protocol-sha256 HEX --out docs/enh/r2/seeds.json
python -m ccc.bench seeds --check docs/enh/r2/seeds.json
```

The unmodified protocol bytes must hash to HEX. For label s and index i the
initial payload is `HEX|s|i`, encoded as UTF-8. Its SHA256 first four bytes as a
big-endian integer, shifted right one bit, give the first 31 bits. On an excluded
value or a collision with any earlier accepted seed, j starts at 1 and the
payload becomes `HEX|s|i|j`. Every rejected value, index, salt and reason is
retained. Labels are traversed in P1–P6, jira_iid, then the class order stored in
`COUNTS` and `label_order`. Uniqueness is global across labels, not just within
a label. Self-intersection means duplicate occurrences beyond the first.

The seed file stores full strata, skip ledger, drawn-list hash, excluded-list
hashes and intersection sizes. All intersections must be zero. Materialisation
uses exclusive creation and cannot overwrite an earlier list. Tests generate
only dummy-protocol lists under `TemporaryDirectory`; no high-seed world is
constructed in tests.

Use the existing FREEZE_TEMPLATE.json with these implementation details:

- `code_hashes` contains the complete mapping printed under `hashes` by the
  hashes CLI. Nested mappings from the template are also flattened/checked.
  Every bench Python file, audit Python/JSON file, baseline Python file and
  fixture Python/JSON file is covered; extra or missing entries fail closed.
- `seeds.path` may name the seed file (default `docs/enh/r2/seeds.json`). Copy
  `seed_list_sha256`, `skips_recorded` and `excluded_sets` from the checked seed
  file into FREEZE.seeds, omitting the informational `count` in each excluded
  entry to match the template. The template's strata_counts are enforced.
- Copy `dev_derived` from the DEV strongest_baseline.json. Selection uses the
  mechanism attribution view at I1 over both equal-size DEV strata, balanced
  accuracy with member weights and no pooled CI; stratum-specific values are
  also retained. Ties go to B2+. Prospective outcomes never select the method.
- Freeze the protocol, parameters, enumeration artifact and independent review.
  The CLI checks them before creating output, and reruns hash/seed validation
  after the run. Prospective execution uses the checked file's schedule only.
  Every prospective partition is written and hashed before any method runs.

## Samples and reporting

Prospective defaults are 200 seeds for each P1–P6 and jira_iid and 100 for each
of nine remaining classes, all distinct. Every structural unit receives eps=0
and .1, with one exact branch or R=8, respectively. The three invalid variants
share a single invalid-class seed unit. Standalone classes map to existing
census recipes; no new payoff/policy equation was introduced. DEV keeps 50 seed
blocks shared across kinds, all within 13000–13049.

`python -m ccc.bench report --run DIR` writes RESULTS.json and RESULTS.md for a
prospective run and RESULTS_dev.json/RESULTS_dev.md for DEV. All RQ1–RQ6,
T1–T10, figure data, per-class M/H/E summaries, paired discordant-unit intervals
and oracle-effect cluster intervals are included. Strata remain separate.
RQ6 explicitly retains exposure-level supports on legitimate members with
unit-based CP intervals, labelled “harmful exposure, not attributable”.
RQ2/RQ5 disclose A2 circularity. Literal criterion failures, undefined
selective-accuracy/precision denominators and method failures remain visible.
The reporter never changes CCC-L to improve a measured criterion.

Original BENCH-IMP records and summary files are preserved in
`bench_imp_snapshot/`; `align_delta.json` compares matched observations and
records roster/count changes. Exact validation commands and final outcomes are
in VALIDATION.md and the short handoff in `ops/reports/BENCH-ALIGN.md`.

The enumeration command also emits `enumeration/enumeration.json` (an aggregate
file/hash index) and `enumeration/class_priors.json`. Set FREEZE.enumeration's
output_path/output_sha256 to the former and class_priors_sha256 to the latter's
file hash. `class_priors_path` is optional; its default is class_priors.json next
to output_path. Both files are checked, along with a valid past freeze timestamp.

Population alignment also supplies H using the exact J no-coordination reference
for A1a/A1b (all sender directives and induced receiver relays disabled), strict
outsider loss >2.5. Both F/J expected outsider rewards are retained. Both epsilon
strata run on the same 50 DEV / 200 prospective seeds, with separate CP intervals.
Population noise is marginalized by the frozen exact iid oracle, so there is no
extra independent continuation sample. The registered exposure threshold remains
K-F >=2.5, and all original eps=0 exposure values are unchanged.
