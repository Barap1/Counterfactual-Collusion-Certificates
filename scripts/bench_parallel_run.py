"""Execution-only parallel orchestration of the frozen R2 benchmark.

No scientific functions are implemented here. Worker caches are private because
the frozen cache publishes JSON with non-atomic write_text(). Results are loaded
in frozen schedule order, independent of worker completion order.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import gzip
import json
import multiprocessing
import os
import shutil
from pathlib import Path
import time

from ccc.bench.__main__ import (
    ROOT, VERSION, Counter, sha256, validate_freeze, _schedule, hash_manifest,
    configure_cache, write_json, write_gzip, census, serializable_partition,
    frontier, suite, observe, oracle, SETS, project, lookup, digest,
    selection_status, safe_methods, design_reference, population,
    clopper_pearson, summarize, symmetry, compare_separators, write_dev_report,
)


def warm_cache(target):
    # Read-only DEV memoization: frozen keys bind numerical runtime, scientific
    # source hashes and canonical inputs. Each worker subsequently writes alone.
    target=Path(target)
    target.mkdir(parents=True,exist_ok=True)
    for source in (ROOT/'docs/enh/bench/dev_run/cache').glob('*.json'):
        destination=target/source.name
        if not destination.exists():
            shutil.copyfile(source,destination)


def initialize_worker(out):
    target=Path(out)/'cache'/f'worker-{os.getpid()}'
    warm_cache(target)
    configure_cache(target)


def partition_seed(seed, out):
    for eps in (0,.1):
        write_gzip(out/'partitions'/f'{seed}-eps-{eps}.json.gz',
                   serializable_partition(census(seed,eps)))


def per_seed(seed, kinds, block, out):
    frontiers=[]; failures=[]
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
        write_gzip(out/'units'/f'{seed}-eps-{eps}.json.gz',rows)
        print(f'{block}: seed {seed}, eps={eps}, {len(rows)} instance/set records complete',flush=True)
    return frontiers, failures


def execution_identity():
    import sys
    import numpy
    return dict(driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                python=sys.version,numpy=numpy.__version__)


def seed_files(seed):
    return [f'{directory}/{seed}-eps-{eps}.json.gz'
            for directory in ('units','partitions') for eps in (0,.1)]


def atomic_json(path, value):
    temporary=path.with_suffix('.tmp')
    write_json(temporary,value)
    temporary.replace(path)


def load_checkpoint(out, seed):
    path=out/'execution'/'seeds'/f'{seed}.json'
    if not path.exists(): return None
    saved=json.loads(path.read_text())
    expected=seed_files(seed)
    if saved.get('seed') != seed or sorted(saved['sha256']) != sorted(expected):
        raise ValueError(f'resume refused: invalid checkpoint for {seed}')
    for name in expected:
        file=out/name
        if not file.is_file() or sha256(file.read_bytes()).hexdigest()!=saved['sha256'][name]:
            raise ValueError(f'resume refused: checksum mismatch: {name}')
    return saved['frontiers'],saved['failures']


def checkpoint_seed(seed, kinds, block, out):
    # A receipt is published only after both epsilon outputs and metadata exist.
    # Uncommitted files from an interrupted infrastructure attempt are rerun.
    attempt_path=out/'execution'/'attempts'/f'{seed}.json'
    attempts=json.loads(attempt_path.read_text()) if attempt_path.exists() else []
    if len(attempts)>=3:
        raise ValueError(f'infrastructure retry limit reached for seed {seed}')
    attempts.append(dict(started_unix=time.time(),pid=os.getpid()))
    atomic_json(attempt_path,attempts)
    fs,failures=per_seed(seed,kinds,block,out)
    atomic_json(out/'execution'/'seeds'/f'{seed}.json',
                dict(seed=seed,frontiers=fs,failures=failures,
                     sha256={name:sha256((out/name).read_bytes()).hexdigest()
                             for name in seed_files(seed)}))
    return fs,failures


def run_parallel(block, out, *, root=ROOT, workers=13, limit=None, units_only=False, resume=False):
    # Always validate first, including DEV and verification invocations.
    frozen_checked=validate_freeze(root)
    frozen=frozen_checked if block=='prospective' else None
    schedule,pop_seeds=_schedule(block,frozen)
    if limit is not None:
        if limit < 1: raise ValueError('limit must be positive')
        schedule=dict(list(schedule.items())[:limit])
        if block=='dev': pop_seeds=list(schedule)
    hashes=hash_manifest(root)
    if not resume and out.exists() and any(out.iterdir()):
        raise ValueError('parallel refused: output directory is not empty')
    if out.resolve().is_relative_to((ROOT/'docs/enh/r2/run').resolve()):
        raise ValueError('parallel refused: serial output is read-only')
    out.mkdir(parents=True,exist_ok=True)
    manifest=dict(schema=VERSION,block=block,evidence='development' if block=='dev' else 'new-prospective',
                  hashes=hashes,independent_unit='seed block; twins/variants/continuations nested',
                  seeds={str(s):sorted(k) for s,k in schedule.items()},population_seeds=pop_seeds,
                  epsilon=[0,.1],continuations={'0':1,'0.1':8},
                  prior='uniform over enumerated policies, conditional on nuisance',
                  prospective_freeze_sha256=sha256((root/'docs/enh/r2/FREEZE.json').read_bytes()).hexdigest() if frozen else None)
    if resume:
        if not (out/'manifest.json').is_file() or json.loads((out/'manifest.json').read_text()) != manifest:
            raise ValueError('resume refused: manifest differs')
        identity=json.loads((out/'execution'/'identity.json').read_text())
        if identity != execution_identity():
            raise ValueError('resume refused: driver/runtime differs')
    else:
        write_json(out/'execution'/'identity.json',execution_identity())
    write_json(out/'manifest.json',manifest)
    all_rows=[]; frontiers=[]; failures=[]
    write_json(out/'freeze.json',frozen) if frozen else None
    results={}
    if resume:
        for seed in schedule:
            saved=load_checkpoint(out,seed)
            if saved is not None:
                results[seed]=saved
    print(f'parallel: {len(results)} checksum-validated seeds skipped; {len(schedule)-len(results)} pending',flush=True)
    start=time.monotonic()
    context=multiprocessing.get_context('spawn')
    with ProcessPoolExecutor(max_workers=workers, mp_context=context,
                             initializer=initialize_worker, initargs=(out,)) as pool:
        # Preserve the frozen enumeration-before-any-methods barrier.
        if block=='prospective':
            enumeration=out/'enumeration_before_methods.json'
            if resume and enumeration.exists():
                expected=json.loads(enumeration.read_text())
                actual={p.name:sha256(p.read_bytes()).hexdigest()
                        for p in sorted((out/'partitions').glob('*.gz'))}
                if expected!=actual:
                    raise ValueError('resume refused: enumeration checksum mismatch')
            else:
                tasks=[pool.submit(partition_seed,seed,out) for seed in schedule]
                for task in as_completed(tasks): task.result()
                atomic_json(enumeration,
                           {p.name:sha256(p.read_bytes()).hexdigest()
                            for p in sorted((out/'partitions').glob('*.gz'))})
        tasks={pool.submit(checkpoint_seed,seed,kinds,block,out):seed
               for seed,kinds in schedule.items() if seed not in results}
        for completed,task in enumerate(as_completed(tasks),1):
            results[tasks[task]]=task.result()
            elapsed=time.monotonic()-start
            print(f'parallel: {completed}/{len(schedule)} seeds; '
                  f'{completed/elapsed:.6f} seeds/s; '
                  f'ETA {(len(schedule)-completed)*elapsed/completed:.1f}s',flush=True)
    for seed in schedule:
        fs,failed=results[seed]
        frontiers.extend(fs); failures.extend(failed)
        if not units_only:
            for eps in (0,.1):
                with gzip.open(out/'units'/f'{seed}-eps-{eps}.json.gz','rt') as stream:
                    all_rows.extend(json.load(stream))
    if units_only:
        if hashes != hash_manifest(root): raise ValueError('source changed during check')
        validate_freeze(root)
        return
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
    from ccc.bench.report import report
    report(out)
    return all_rows



def compare_units(out, serial, seeds):
    """Read opaque bytes only; missing serial files also fail the gate."""
    compared=0; mismatches=[]
    for seed in seeds:
        for eps in (0,.1):
            for directory in ('units','partitions'):
                relative=Path(directory)/f'{seed}-eps-{eps}.json.gz'
                left=out/relative; right=serial/relative
                if not left.is_file() or not right.is_file():
                    mismatches.append(str(relative)+': missing')
                elif left.read_bytes()!=right.read_bytes():
                    mismatches.append(str(relative)+': bytes differ')
                compared+=1
    return dict(compared=compared,mismatches=mismatches)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--block',choices=('dev','prospective'),default='prospective')
    parser.add_argument('--out',type=Path,default=ROOT/'docs/enh/r2/run_par')
    parser.add_argument('--workers',type=int,default=13)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--check-against',type=Path)
    parser.add_argument('--proof',type=Path,
                        help='Successful 40-seed byte-comparison receipt required for full prospective run')
    args=parser.parse_args()
    frozen=validate_freeze()
    schedule,_=_schedule(args.block,frozen if args.block=='prospective' else None)
    if args.workers<1: parser.error('workers must be positive')
    if args.block=='prospective' and args.limit is None:
        if not args.proof: parser.error('full prospective run requires --proof')
        receipt=json.loads(args.proof.read_text())
        expected=list(schedule)[:40]
        if (receipt.get('seeds')!=expected or receipt.get('compared')!=160
                or receipt.get('mismatches')!=[]
                or receipt.get('hashes')!=hash_manifest()
                or receipt.get('driver_sha256')!=sha256(Path(__file__).read_bytes()).hexdigest()):
            parser.error('invalid determinism proof')
        # Recheck bytes at launch; receipts alone cannot bypass the gate.
        check=compare_units(Path(receipt['scratch']),Path(receipt['serial']),expected)
        if check['compared']!=160 or check['mismatches']:
            parser.error('determinism proof no longer matches')
    if args.check_against:
        if args.block!='prospective' or args.limit!=40:
            parser.error('byte-check requires prospective --limit 40')
        # Require all reference files BEFORE performing new computation.
        for seed in list(schedule)[:40]:
            for eps in (0,.1):
                for directory in ('units','partitions'):
                    path=args.check_against/directory/f'{seed}-eps-{eps}.json.gz'
                    if not path.is_file(): parser.error(f'missing serial reference: {path}')
    run_parallel(args.block,args.out,workers=args.workers,limit=args.limit,
                 units_only=bool(args.check_against),resume=args.resume)
    if args.check_against:
        result=compare_units(args.out,args.check_against,list(schedule)[:40])
        result.update(seeds=list(schedule)[:40],hashes=hash_manifest(),
                      scratch=str(args.out.resolve()),serial=str(args.check_against.resolve()),
                      driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        write_json(args.out/'BYTE_COMPARISON.json',result)
        print(json.dumps(result,sort_keys=True),flush=True)
        if result['mismatches']: raise SystemExit('STOP: byte comparison failed')


if __name__=='__main__':
    main()
