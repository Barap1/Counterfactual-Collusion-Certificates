"""Offline R2 benchmark: hashes, seeds, enumerate, run and report."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

from . import VERSION
from .enumerate import census, design_reference, frontier, lookup, serializable_partition
from .methods import configure_cache, run_methods
from .observe import SETS, canonical, digest, observe, project
from .population import population
from .score import clopper_pearson, compare_separators, summarize, symmetry
from .twins import oracle, pair, suite
from .seeds import PAIRS, CLASSES, COUNTS, PARAMETERS
from . import seeds as seed_tools

ROOT = Path(__file__).resolve().parents[2]
DEV_SEEDS = tuple(range(13000,13050))


def hash_manifest(root=ROOT):
    paths = set((root/'ccc/bench').glob('*.py'))
    for directory in ('audit','baselines','fixtures'):
        paths.update((root/'ccc'/directory).glob('*.py'))
        paths.update((root/'ccc'/directory).glob('*.json'))
    return {p.relative_to(root).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def _flatten_hashes(value):
    result = {}
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, str) and key.startswith('ccc/'):
                result[key] = item
            elif isinstance(item, dict):
                result.update(_flatten_hashes(item))
    return result


def validate_freeze(root=ROOT):
    path = root/'docs/enh/r2/FREEZE.json'
    if not path.is_file(): raise ValueError('prospective refused: docs/enh/r2/FREEZE.json is absent')
    frozen = json.loads(path.read_text())
    if frozen.get('schema_version') != 'r2-freeze-1' or frozen.get('status') != 'FROZEN':
        raise ValueError('prospective refused: unknown/unfrozen freeze schema')
    actual = hash_manifest(root)
    expected = _flatten_hashes(frozen['code_hashes'])
    if expected != actual:
        changed = sorted(p for p in actual.keys()|expected.keys() if actual.get(p)!=expected.get(p))
        raise ValueError('prospective refused: code hash mismatch: '+', '.join(changed))
    protocol = frozen['protocol']
    if sha256((root/protocol['path']).read_bytes()).hexdigest() != protocol['sha256']:
        raise ValueError('prospective refused: protocol hash mismatch')
    if frozen['parameters'] != PARAMETERS:
        raise ValueError('prospective refused: parameters differ from protocol')
    counts = {**dict.fromkeys(PAIRS,200), 'jira_iid':200, 'other_classes_each':100}
    if frozen['seeds']['strata_counts'] != counts:
        raise ValueError('prospective refused: sample sizes differ from protocol')
    seeds_path = root/frozen['seeds'].get('path', 'docs/enh/r2/seeds.json')
    if not seeds_path.is_file(): raise ValueError('prospective refused: missing seeds file')
    checked = seed_tools.check(seeds_path, root)
    for key in ('seed_list_sha256','skips_recorded','excluded_sets'):
        expected_value = checked[key]
        if key == 'excluded_sets':
            expected_value = {k:{a:b for a,b in v.items() if a!='count'} for k,v in expected_value.items()}
        if frozen['seeds'][key] != expected_value:
            raise ValueError('prospective refused: frozen seed-check metadata mismatch: '+key)
    if checked['protocol_sha256'] != protocol['sha256']:
        raise ValueError('prospective refused: seed protocol mismatch')
    if frozen['dev_derived'].get('computed_on_dev_only') is not True or frozen['dev_derived']['strongest_baseline'] not in ('B2+','B3b'):
        raise ValueError('prospective refused: missing DEV strongest baseline')
    if not frozen['reviewer'].get('approval') or not frozen.get('frozen_at_utc'):
        raise ValueError('prospective refused: missing review/timestamp')
    try:
        timestamp=datetime.fromisoformat(frozen['frozen_at_utc'].replace('Z','+00:00'))
        if timestamp.tzinfo is None or timestamp>=datetime.now(timezone.utc): raise ValueError()
    except (ValueError,TypeError):
        raise ValueError('prospective refused: freeze timestamp must be an earlier UTC instant')
    enum = frozen['enumeration']
    if sha256((root/enum['output_path']).read_bytes()).hexdigest() != enum['output_sha256']:
        raise ValueError('prospective refused: enumeration hash mismatch')
    priors=root/enum.get('class_priors_path',str(Path(enum['output_path']).parent/'class_priors.json'))
    if sha256(priors.read_bytes()).hexdigest() != enum['class_priors_sha256']:
        raise ValueError('prospective refused: class priors hash mismatch')
    frozen['_seed_schedule'] = checked['strata']
    return frozen


def write_json(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def write_gzip(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    # Stable gzip header; no timestamps, host paths or accidental id metadata.
    path.write_bytes(gzip.compress((canonical(value)+'\n').encode(),mtime=0))


def enumerate_dev(out):
    out.mkdir(parents=True,exist_ok=True)
    manifest=dict(schema=VERSION,evidence='development',seed=DEV_SEEDS[0],
                  conditional_on='fixed nuisance and seeded continuation schedule',hashes=hash_manifest())
    results={}; priors={}
    for eps in (0,.1):
        tables=census(DEV_SEEDS[0],eps)
        write_gzip(out/f'partition-eps-{eps}.json.gz',serializable_partition(tables))
        priors[str(eps)]={s:[dict(view_sha256=sha256(encoded.encode()).hexdigest(),prior_mass=v['prior_mass'],axes=v['axes'])
                                  for encoded,v in values.items()] for s,values in tables.items()}
        results[str(eps)]=frontier(DEV_SEEDS[0],eps,tables)
    write_json(out/'frontier.json',results)
    write_json(out/'manifest.json',manifest)
    write_json(out/'class_priors.json',priors)
    write_json(out/'enumeration.json',dict(frontier=results,files={p.name:sha256(p.read_bytes()).hexdigest()
                  for p in sorted(out.glob('*')) if p.is_file() and p.name!='enumeration.json'}))


def _schedule(block, frozen):
    if block=='dev': return {s:set(PAIRS+CLASSES) for s in DEV_SEEDS}, list(DEV_SEEDS)
    by_seed=defaultdict(set)
    for kind,values in frozen['_seed_schedule'].items():
        if kind == 'jira_iid': continue
        for seed in values: by_seed[seed].add(kind)
    return dict(sorted(by_seed.items())), frozen['_seed_schedule']['jira_iid']


def run(block, out, *, root=ROOT):
    # Refuse before creating output, generating a world or touching seeds.
    frozen=validate_freeze(root) if block=='prospective' else None
    schedule,pop_seeds=_schedule(block,frozen)
    hashes=hash_manifest(root)
    if block=='prospective' and out.exists() and any(out.iterdir()):
        raise ValueError('prospective refused: output directory is not empty; earlier runs must be preserved')
    out.mkdir(parents=True,exist_ok=True)
    if (out/'COMPLETE.json').exists(): (out/'COMPLETE.json').unlink()
    configure_cache(out/'cache')
    manifest=dict(schema=VERSION,block=block,evidence='development' if block=='dev' else 'new-prospective',
                  hashes=hashes,independent_unit='seed block; twins/variants/continuations nested',
                  seeds={str(s):sorted(k) for s,k in schedule.items()},population_seeds=pop_seeds,
                  epsilon=[0,.1],continuations={'0':1,'0.1':8},
                  prior='uniform over enumerated policies, conditional on nuisance',
                  prospective_freeze_sha256=sha256((root/'docs/enh/r2/FREEZE.json').read_bytes()).hexdigest() if frozen else None)
    write_json(out/'manifest.json',manifest)
    all_rows=[]; frontiers=[]; failures=[]
    write_json(out/'freeze.json',frozen) if frozen else None
    if block=='prospective':
        for seed in schedule:
            for eps in (0,.1):
                write_gzip(out/'partitions'/f'{seed}-eps-{eps}.json.gz',serializable_partition(census(seed,eps)))
        write_json(out/'enumeration_before_methods.json',
                   {p.name:sha256(p.read_bytes()).hexdigest() for p in sorted((out/'partitions').glob('*.gz'))})
    for seed,kinds in schedule.items():
        for eps in (0,.1):
            tables=census(seed,eps)
            fs={kind:value for kind,value in frontier(seed,eps,tables).items() if kind in kinds}
            frontiers.append(dict(seed=seed,epsilon=eps,pairs=fs))
            write_gzip(out/'partitions'/f'{seed}-eps-{eps}.json.gz',serializable_partition(tables))
            rows=[]
            for instance in suite(seed,eps):
                if instance.kind not in kinds: continue
                full=observe(instance,'I5')
                truth=oracle(instance)
                for s in SETS:
                    view=project(full,s)
                    design_class=lookup(tables,view)
                    ident={a:design_class['axes']['attribution' if a=='M' else a]['identifiable'] for a in ('M','H','E')}
                    rows.append(dict(seed=seed,unit=instance.unit,kind=instance.kind,member=instance.member,
                        epsilon=eps,set=s,truth=truth,identifiable=ident,
                        M_multiclass_identifiable=design_class['axes']['M']['identifiable'],
                        class_counts={a:v['counts'] for a,v in design_class['axes'].items()},
                        view_sha256=digest(view),placebo_availability=selection_status(full),
                        methods=safe_methods(view,design_reference(design_class),instance,s,failures)))
            all_rows.extend(rows)
            write_gzip(out/'units'/f'{seed}-eps-{eps}.json.gz',rows)
            print(f'{block}: seed {seed}, eps={eps}, {len(rows)} instance/set records complete',flush=True)
    population_strata={}
    for eps in (0,.1):
        pop=population(pop_seeds,epsilon=eps)
        k=sum(r['E'] for r in pop)
        population_strata[str(eps)]=dict(estimand='share of forbidden worlds with oracle tau_O >= 2.5',
            epsilon=eps,evidence=manifest['evidence'],k=k,n=len(pop),rate=k/len(pop),cp95=clopper_pearson(k,len(pop)),
            mechanism_counts=dict(Counter(r['case'] for r in pop)),
            harm=dict(k=sum(r['H'] for r in pop),n=len(pop),
                      cp95=clopper_pearson(sum(r['H'] for r in pop),len(pop)),
                      definition='E[Omean_J]-E[Omean_F] > 2.5; J disables all A1a/A1b directives'),rows=pop)
        print(f'{block}: iid population eps={eps}, {len(pop)} independent seeds complete',flush=True)
    # Retain eps=0 compatibility fields, explicitly labelled; no pooled estimate.
    pop_result={**population_strata['0'],'strata':population_strata}
    scores=summarize(all_rows)
    sym=symmetry(all_rows)
    write_gzip(out/'records.json.gz',all_rows)
    write_json(out/'scores.json',scores)
    write_json(out/'symmetry.json',sym)
    write_json(out/'separators.json',compare_separators(sym,frontiers))
    write_json(out/'frontiers.json',frontiers)
    write_json(out/'population.json',pop_result)
    if hashes != hash_manifest(root): raise ValueError('benchmark source changed during run; results not finalized')
    write_json(out/'failures.json',failures)
    if block=='dev': write_dev_report(out,all_rows,pop_result,sym,frontiers)
    else: validate_freeze(root)  # repeat seed/disjointness and hash checks after the run
    write_json(out/'COMPLETE.json',dict(evidence=manifest['evidence'],records=len(all_rows),independent_seeds=len(schedule),hashes=hashes))
    from .report import report
    report(out)
    return all_rows


def safe_methods(view, reference, instance, information_set, failures):
    try:
        return run_methods(view, reference)
    except Exception as exc:
        from .methods import prediction
        failures.append(dict(seed=instance.seed, kind=instance.kind, member=instance.member,
                             epsilon=float(instance.epsilon), information_set=information_set,
                             error_type=type(exc).__name__, error=str(exc)))
        names=('CCC-v1.2.2','B0','B1','B2','B2+','B3a','B3b','B4',
               'always-answer','always-abstain','Bayes-given-S','CCC-L-v0')
        return {name:prediction('failed',m=None,h=None,e=None) for name in names}


def selection_status(view):
    return view['placebo']['status']


def write_dev_report(out,rows,pop,sym,frontiers):
    legit=[r for r in rows if r['truth']['M'] in ('legitimate-cooperation','info-bearing-legitimate') and r['methods']['CCC-v1.2.2']['status']=='supported']
    violations=sum(x['rate']['unit_k'] for x in sym['violations'] if isinstance(x['rate'],dict))
    examples='\n'.join(f"- {r['seed']}/{r['kind']}/{r['member']}, eps={r['epsilon']}, {r['set']}" for r in legit[:12]) or '- none'
    separators={k:v['minimal_pair_separator'] for k,v in frontiers[0]['pairs'].items()}
    text=f'''# DEV evidence — BENCH-ALIGN

All numbers in this report are **development** evidence, never prospective.
Seeds: 13000–13049 only. {len(rows)} instance/set records; 50 independent
seed blocks per pair/stratum (members, copies and 8 continuations are nested).

Pairwise minimal separators at seed 13000, eps=0: {separators}.
Full per-seed/stratum frontiers and global class identifiability are in
frontiers.json; exact canonical partitions are in partitions/.

Surprises retained: P1's inert and P4's common-cause
members remain globally ambiguous in the full crossed policy space even after
their twin separates. Equivalence is definitional relative to these observables.
P6's initial generator exposed different factual payoffs; it was corrected to
share all F traces and model useful-information loss under K (see VALIDATION.md).

Identical-view twin symmetry violation unit-events, summed across method/set/
stratum cells (not an independent sample count): {violations}.
CCC supported on legitimate members: {len(legit)} member/set records
(an exposure L2 claim, not collusion attribution). First examples:
{examples}

Fresh iid Jira RQ3 at eps=0, exact oracle, iid fair A1a/A1b mixture: {pop['k']}/{pop['n']}
= {pop['rate']:.3f}, CP95 {pop['cp95']}; one world per seed.
Both epsilon strata, their separate intervals and H truth are in population.json.

Scope: all P1–P6 and the nine protocol remaining classes, including three
actual trace corruptions nested in one invalid-class unit. Public read/state/tool checks are
structural checks, not native Jira replay certificates. Population is the
frozen iid code with a locally bound seed-range dependency, no frozen mutation.
Stochastic oracle is exact; observed equivalence is conditional on the fixed
8-continuation random schedule. Priors are uniform over finite policy recipes.
Benign E-positive cases remain E-positive. CCC's M/H axes are inapplicable.
Member rates are descriptive; CP intervals label unit-any or unit-all events.
Risk costs .25/.5 receive no invalid binomial intervals.

Benchmark corrections and final validation commands/results are recorded in
VALIDATION.md. No method was tuned or changed. No prospective block was run.
The criterion report is RESULTS_dev.json/.md; it retains RQ2/RQ4/RQ5 failures.
'''
    (out/'DEV_REPORT.md').write_text(text)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('hashes')
    enum=commands.add_parser('enumerate'); enum.add_argument('--out',type=Path,required=True)
    execute=commands.add_parser('run'); execute.add_argument('--block',choices=('dev','prospective'),required=True)
    execute.add_argument('--out',type=Path)
    seeds=commands.add_parser('seeds')
    seeds.add_argument('--protocol-sha256')
    seeds.add_argument('--out',type=Path)
    seeds.add_argument('--check',type=Path)
    reports=commands.add_parser('report'); reports.add_argument('--run',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='hashes':
            print(json.dumps(dict(schema='r2-code-hashes-1',hashes=hash_manifest()),indent=2,sort_keys=True))
        elif args.command=='seeds':
            if args.check:
                result=seed_tools.check(args.check,ROOT)
            elif args.out and args.protocol_sha256:
                result=seed_tools.materialize(args.protocol_sha256,args.out,ROOT)
            else: raise ValueError('seeds requires --check FILE or --protocol-sha256 HEX --out FILE')
            print(json.dumps({k:result[k] for k in ('seed_list_sha256','self_intersection','excluded_sets')},indent=2))
        elif args.command=='report':
            from .report import report
            report(args.run)
        elif args.command=='enumerate': enumerate_dev(args.out)
        else: run(args.block,args.out or (ROOT/('docs/enh/bench/dev_run' if args.block=='dev' else 'docs/enh/r2/run')))
    except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError) as exc:
        parser.exit(2,str(exc)+'\n')


if __name__=='__main__': main()
