"""python -m ccc.bench {hashes,enumerate,run}; offline, no inference clients.

FREEZE.json schema: {schema:'ccc.bench.freeze.v0', hashes:{relative_path:sha256},
 seeds:{pairs:{P1:[200 ints],...,P6:[200 ints]}, classes:{name:[100 ints],...},
 population:[200 ints]}, prior_seed_exclusions:[ints],
 prior_seed_ledger_complete:true}. Hashes must match the EXACT manifest printed
 by `hashes`. The director must supply the complete prior seed ledger (including
 EXP-002) and post-freeze draws; this command never draws prospective seeds.
 The file itself and PROTOCOL.md are director-owned, never created here.
"""
import argparse
from collections import Counter, defaultdict
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

ROOT = Path(__file__).resolve().parents[2]
DEV_SEEDS = tuple(range(13000,13050))
PAIRS = tuple(f"P{i}" for i in range(1,7))
CLASSES = ("relayed", "paraphrased", "harmful", "useful", "harm-without-dependence",
           "inert", "invalid-state", "invalid-replay", "invalid-mask")


def hash_manifest(root=ROOT):
    paths = set((root/'ccc/bench').glob('*.py'))
    for directory in ('audit','baselines','fixtures'):
        paths.update((root/'ccc'/directory).glob('*.py'))
        paths.update((root/'ccc'/directory).glob('*.json'))
    return {p.relative_to(root).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def validate_freeze(root=ROOT):
    path = root/'docs/enh/r2/FREEZE.json'
    if not path.is_file(): raise ValueError('prospective refused: docs/enh/r2/FREEZE.json is absent')
    frozen = json.loads(path.read_text())
    if frozen.get('schema') != 'ccc.bench.freeze.v0': raise ValueError('prospective refused: unknown freeze schema')
    actual = hash_manifest(root)
    if frozen.get('hashes') != actual:
        expected = frozen.get('hashes',{})
        changed = sorted(p for p in actual.keys()|expected.keys() if actual.get(p)!=expected.get(p))
        raise ValueError('prospective refused: code hash mismatch: '+', '.join(changed))
    seeds = frozen.get('seeds',{})
    if set(seeds) != {'pairs','classes','population'} or set(seeds['pairs']) != set(PAIRS) or set(seeds['classes']) != set(CLASSES):
        raise ValueError('prospective refused: incomplete seed schedule')
    if frozen.get('prior_seed_ledger_complete') is not True or not isinstance(frozen.get('prior_seed_exclusions'),list):
        raise ValueError('prospective refused: complete prior-seed ledger required')
    excluded=set(frozen['prior_seed_exclusions']) | set(range(12000,12020)) | set(DEV_SEEDS) | set(range(87000,87100))
    lists=[(v,200) for v in seeds['pairs'].values()]+[(v,100) for v in seeds['classes'].values()]+[(seeds['population'],200)]
    for values,n in lists:
        if not isinstance(values,list) or len(values)!=n or any(type(v) is not int for v in values) or len(set(values))!=n:
            raise ValueError('prospective refused: wrong count/type or duplicate seeds')
        if set(values)&excluded: raise ValueError('prospective refused: prior seed reused')
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
    results={}
    for eps in (0,.1):
        tables=census(DEV_SEEDS[0],eps)
        write_gzip(out/f'partition-eps-{eps}.json.gz',serializable_partition(tables))
        results[str(eps)]=frontier(DEV_SEEDS[0],eps,tables)
    write_json(out/'frontier.json',results)
    write_json(out/'manifest.json',manifest)


def _schedule(block, frozen):
    if block=='dev': return {s:set(PAIRS+CLASSES) for s in DEV_SEEDS}, list(DEV_SEEDS)
    by_seed=defaultdict(set)
    for kind,values in {**frozen['seeds']['pairs'],**frozen['seeds']['classes']}.items():
        for seed in values: by_seed[seed].add(kind)
    return dict(sorted(by_seed.items())), frozen['seeds']['population']


def run(block, out, *, root=ROOT):
    # Refuse before creating output, generating a world or touching seeds.
    frozen=validate_freeze(root) if block=='prospective' else None
    schedule,pop_seeds=_schedule(block,frozen)
    hashes=hash_manifest(root)
    out.mkdir(parents=True,exist_ok=True)
    configure_cache(out/'cache')
    manifest=dict(schema=VERSION,block=block,evidence='development' if block=='dev' else 'new-prospective',
                  hashes=hashes,independent_unit='seed block; twins/variants/continuations nested',
                  seeds={str(s):sorted(k) for s,k in schedule.items()},population_seeds=pop_seeds,
                  epsilon=[0,.1],continuations={'0':1,'0.1':8},
                  prior='uniform over enumerated policies, conditional on nuisance',
                  prospective_freeze_sha256=sha256((root/'docs/enh/r2/FREEZE.json').read_bytes()).hexdigest() if frozen else None)
    write_json(out/'manifest.json',manifest)
    all_rows=[]; frontiers=[]
    for seed,kinds in schedule.items():
        for eps in (0,.1):
            tables=census(seed,eps)
            fs=frontier(seed,eps,tables)
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
                        methods=run_methods(view,design_reference(design_class))))
            all_rows.extend(rows)
            write_gzip(out/'units'/f'{seed}-eps-{eps}.json.gz',rows)
            print(f'{block}: seed {seed}, eps={eps}, {len(rows)} instance/set records complete',flush=True)
    pop=population(pop_seeds)
    k=sum(r['E'] for r in pop)
    pop_result=dict(estimand='share of forbidden worlds with oracle tau_O >= 2.5',
                    evidence=manifest['evidence'],k=k,n=len(pop),rate=k/len(pop),cp95=clopper_pearson(k,len(pop)),
                    mechanism_counts=dict(Counter(r['case'] for r in pop)),rows=pop)
    scores=summarize(all_rows)
    sym=symmetry(all_rows)
    write_gzip(out/'records.json.gz',all_rows)
    write_json(out/'scores.json',scores)
    write_json(out/'symmetry.json',sym)
    write_json(out/'separators.json',compare_separators(sym,frontiers))
    write_json(out/'frontiers.json',frontiers)
    write_json(out/'population.json',pop_result)
    if hashes != hash_manifest(root): raise ValueError('benchmark source changed during run; results not finalized')
    if block=='dev': write_dev_report(out,all_rows,pop_result,sym,frontiers)
    write_json(out/'COMPLETE.json',dict(evidence=manifest['evidence'],records=len(all_rows),independent_seeds=len(schedule),hashes=hashes))
    return all_rows


def selection_status(view):
    return view['placebo']['status']


def write_dev_report(out,rows,pop,sym,frontiers):
    legit=[r for r in rows if r['truth']['M'] in ('legitimate-cooperation','info-bearing-legitimate') and r['methods']['CCC-v1.2.2']['status']=='supported']
    violations=sum(x['rate']['unit_k'] for x in sym['violations'] if isinstance(x['rate'],dict))
    examples='\n'.join(f"- {r['seed']}/{r['kind']}/{r['member']}, eps={r['epsilon']}, {r['set']}" for r in legit[:12]) or '- none'
    separators={k:v['minimal_pair_separator'] for k,v in frontiers[0]['pairs'].items()}
    text=f'''# DEV evidence — BENCH-IMP

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

Fresh iid Jira RQ3, deterministic oracle, iid fair A1a/A1b mixture: {pop['k']}/{pop['n']}
= {pop['rate']:.3f}, CP95 {pop['cp95']}; one world per seed.

Scope: all P1–P6, relay, paraphrase, harmful, useful, harm without dependence,
inert and three actual trace corruptions. Public read/state/tool checks are
structural checks, not native Jira replay certificates. Population is the
frozen iid code with a locally bound seed-range dependency, no frozen mutation.
Stochastic oracle is exact; observed equivalence is conditional on the fixed
8-continuation random schedule. Priors are uniform over finite policy recipes.
Benign E-positive cases remain E-positive. CCC's M/H axes are inapplicable.
Member rates are descriptive; CP intervals label unit-any or unit-all events.
Risk costs .25/.5 receive no invalid binomial intervals.

Benchmark corrections and final validation commands/results are recorded in
VALIDATION.md. No method was tuned or changed. No prospective block was run.
'''
    (out/'DEV_REPORT.md').write_text(text)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('hashes')
    enum=commands.add_parser('enumerate'); enum.add_argument('--out',type=Path,required=True)
    execute=commands.add_parser('run'); execute.add_argument('--block',choices=('dev','prospective'),required=True)
    execute.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='hashes':
            print(json.dumps(dict(schema='ccc.bench.freeze.v0',hashes=hash_manifest()),indent=2,sort_keys=True))
        elif args.command=='enumerate': enumerate_dev(args.out)
        else: run(args.block,args.out)
    except (ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        parser.exit(2,str(exc)+'\n')


if __name__=='__main__': main()
