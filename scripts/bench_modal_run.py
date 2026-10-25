"""Execution-only Modal CPU runner. Import and --dry-run require no Modal SDK.

Use Python (not `modal run`): python -m scripts.bench_modal_run --gate 40
Only ORCH may execute cloud work. Frozen benchmark sources are never changed.
"""
import argparse
import gzip
import json
from pathlib import Path
import sys
import tempfile

from ccc.bench import __main__ as frozen
from scripts import bench_parallel_run as execution

ROOT = frozen.ROOT
SERIAL = ROOT / 'docs/enh/r2/run'
DEFAULT_OUT = ROOT / 'docs/enh/r2/run_par'


def identity():
    import numpy
    return dict(hashes=frozen.hash_manifest(),
                freeze=frozen.sha256((ROOT/'docs/enh/r2/FREEZE.json').read_bytes()).hexdigest(),
                drivers={name:frozen.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest()
                         for name in ('bench_modal_run.py', 'bench_parallel_run.py')},
                python=list(sys.version_info[:2]), numpy=numpy.__version__)


def execute_task(task):
    """The exact mapped callable, also exercised in-process with DEV seeds."""
    frozen.validate_freeze()
    if identity() != task['identity']:
        raise ValueError('container source/runtime identity differs from driver')
    seed=task['seed']; phase=task['phase']
    with tempfile.TemporaryDirectory(prefix='ccc-modal-') as temporary:
        out=Path(temporary)
        frozen.configure_cache(out/'cache')  # private, never shared between inputs
        if phase=='enumerate':
            execution.partition_seed(seed,out)
            frontiers=[]; failures=[]
            names=[n for n in execution.seed_files(seed) if n.startswith('partitions/')]
        elif phase=='methods':
            frontiers,failures=execution.per_seed(seed,set(task['kinds']),task['block'],out)
            names=execution.seed_files(seed)
        else:
            raise ValueError('unknown execution phase')
        files={name:(out/name).read_bytes() for name in names}
    frozen.validate_freeze()
    import zlib
    return dict(seed=seed,phase=phase,identity=task['identity'],files=files,
                runtime=dict(python=sys.version,zlib=zlib.ZLIB_RUNTIME_VERSION),
                frontiers=frontiers,failures=failures)


def mount_files():
    """Explicit file allowlist; no checkout-wide mount, credentials or run outputs."""
    files={ROOT/name for name in frozen.hash_manifest()}
    files.update((ROOT/'ccc').glob('*.py'))
    files.update(ROOT/'scripts'/name for name in ('bench_modal_run.py','bench_parallel_run.py'))
    files.update(ROOT/'docs/enh/r2'/name for name in ('FREEZE.json','seeds.json','PROTOCOL.md'))
    spec=json.loads((ROOT/'docs/enh/r2/FREEZE.json').read_text())
    files.update(ROOT/spec['enumeration'][key] for key in ('output_path','class_priors_path'))
    # validate_freeze -> seeds.check scans these exact historical sources.
    _,sources=frozen.seed_tools.exclusions(ROOT)
    files.update(ROOT/source['path'].split('!',1)[0] for source in sources)
    # Empty/no-seed archives still participate in the source census.
    files.update((ROOT/'docs/runner/archives').glob('*.tar.gz'))
    for path in files:
        if path.is_symlink() or path.name.startswith('.env') or path.name=='compute.env' or path.name.endswith('.local.json'):
            raise ValueError('unsafe mount path')
    return sorted(files)


def modal_application(containers):
    import modal  # lazy: DEV tests and --dry-run never import Modal
    import numpy
    image=(modal.Image.debian_slim(python_version='.'.join(map(str,sys.version_info[:2])))
           .pip_install('numpy=='+numpy.__version__)
           .env({'PYTHONPATH':'/repo','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}))
    for path in mount_files():
        image=image.add_local_file(path,'/repo/'+path.relative_to(ROOT).as_posix())
    app=modal.App('ccc-frozen-r2-cpu')
    worker=app.function(image=image,cpu=1,memory=4096,timeout=86400,
                        max_containers=containers,retries=0)(execute_task)
    return app,worker


def atomic_bytes(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_bytes(data)
    temporary.replace(path)


def receipt_path(out,phase,seed):
    return out/'execution'/'modal'/phase/f'{seed}.json'


def expected_files(phase,seed):
    return [name for name in execution.seed_files(seed)
            if phase=='methods' or name.startswith('partitions/')]


def checkpoint(out,task):
    path=receipt_path(out,task['phase'],task['seed'])
    if not path.exists():
        return None
    receipt=json.loads(path.read_text())
    if receipt['task'] != task or set(receipt['sha256']) != set(expected_files(task['phase'],task['seed'])):
        raise ValueError('resume task/receipt differs')
    for name,checksum in receipt['sha256'].items():
        if frozen.sha256((out/name).read_bytes()).hexdigest()!=checksum:
            raise ValueError('resume checksum mismatch: '+name)
    return receipt


def save_result(out,task,result):
    if any(result[k]!=task[k] for k in ('seed','phase','identity')):
        raise ValueError('returned task identity differs')
    if set(result['files']) != set(expected_files(task['phase'],task['seed'])):
        raise ValueError('returned file layout differs')
    for name,data in result['files'].items():
        json.loads(gzip.decompress(data))
        path=out/name
        if path.exists() and path.read_bytes()!=data:
            raise ValueError('refusing to overwrite differing output: '+name)
        if not path.exists(): atomic_bytes(path,data)
    receipt=dict(task=task,sha256={n:frozen.sha256(d).hexdigest() for n,d in result['files'].items()},
                 frontiers=result['frontiers'],failures=result['failures'],runtime=result['runtime'])
    execution.atomic_json(receipt_path(out,task['phase'],task['seed']),receipt)


def run_phase(out,tasks,worker):
    pending=[]
    for task in tasks:
        if checkpoint(out,task) is not None: continue
        # No automatic retry: ORCH may resume infrastructure failures only.
        path=out/'execution'/'modal'/'attempts'/task['phase']/f"{task['seed']}.json"
        attempts=json.loads(path.read_text()) if path.exists() else []
        if len(attempts)>=3: raise ValueError('infrastructure retry limit reached')
        from datetime import datetime,timezone
        attempts.append(dict(started_utc=datetime.now(timezone.utc).isoformat(),task=task))
        execution.atomic_json(path,attempts)
        pending.append(task)
    by_seed={t['seed']:t for t in pending}
    for result in worker.map(pending,order_outputs=False):
        save_result(out,by_seed[result['seed']],result)


def compare_gate(out,seeds,serial=SERIAL):
    result=execution.compare_units(out,serial,seeds)
    result.update(status='PASS' if not result['mismatches'] else 'FAIL',seeds=seeds,
                  identity=identity(),serial=str(serial.resolve()),out=str(out.resolve()),
                  reference_unit_count=len(list((serial/'units').glob('*.json.gz'))))
    execution.atomic_json(out/'GATE.json',result)
    print('GATE '+result['status'],flush=True)
    return result


V2_RECEIPT=ROOT/'docs/enh/r2/run_par/GATE_v2.json'
DIRECTOR_EXCEPTION='D-046'


def require_gate(out,seeds):
    saved=json.loads((out/'GATE.json').read_text())
    if (saved.get('status')=='PASS' and saved.get('identity')==identity()
            and saved.get('seeds')==seeds and saved.get('compared')==4*len(seeds)):
        checked=execution.compare_units(out,SERIAL,seeds)
        if checked['mismatches']: raise ValueError('gate bytes changed')
        return
    # D-046 exception: cross-platform identity is required for eps-0 only; eps-0.1 must be
    # self-deterministic on the container platform (GATE_v2 self-check). See PARALLEL_EXECUTION.md.
    v2=json.loads(V2_RECEIPT.read_text())
    if (v2.get('status')!='PASS' or v2.get('exception')!=DIRECTOR_EXCEPTION
            or v2.get('identity')!=identity() or not set(v2.get('seeds',[])).issubset(seeds)):
        raise ValueError('full run requires current PASS gate (or GATE_v2 under D-046)')
    # eps-0 cross-platform identity for the 40 gate seeds: 40/40 in the archived gate-1 run
    # (ops/reports/codex_runs/gate1_failed/run_par_prev/GATE.json). Re-verified after the full run
    # against SERIAL (eps-0 units only; eps-0.1 excluded by D-046).


def run_selected(out,selected,containers):
    app,worker=modal_application(containers)
    with app.run():
        for phase in ('enumerate','methods'):
            tasks=[dict(seed=seed,kinds=sorted(kinds),block='prospective',phase=phase,identity=identity())
                   for seed,kinds in selected.items()]
            run_phase(out,tasks,worker)
            if phase=='enumerate':
                frozen.write_json(out/'enumeration_before_methods.json',
                    {p.name:frozen.sha256(p.read_bytes()).hexdigest()
                     for p in sorted((out/'partitions').glob('*.gz'))})


def self_check(schedule,spec,containers):
    # Two independent Modal app runs (separate containers) on the same first 5 seeds.
    seeds=list(schedule)[:5]
    selected={seed:schedule[seed] for seed in seeds}
    base=ROOT/'docs/enh/r2/run_par/gate_v2'
    for label in ('A','B'):
        run_selected(base/label,selected,containers)
    self_cmp=execution.compare_units(base/'A',base/'B',seeds)
    cross=execution.compare_units(base/'A',SERIAL,seeds)
    eps0_cross=[m for m in cross['mismatches'] if 'eps-0.1' not in m]
    ok=(not self_cmp['mismatches']) and (not eps0_cross)
    receipt=dict(status='PASS' if ok else 'FAIL',exception=DIRECTOR_EXCEPTION,seeds=seeds,
                 identity=identity(),self_check=dict(compared=self_cmp['compared'],
                 mismatches=self_cmp['mismatches']),cross_platform_eps0=dict(compared=cross['compared'],
                 mismatches=eps0_cross),cross_platform_eps01_mismatches=[m for m in cross['mismatches'] if 'eps-0.1' in m],
                 platform='modal linux, CPython '+'.'.join(map(str,sys.version_info[:3])))
    execution.atomic_json(V2_RECEIPT,receipt)
    print('GATE_v2 '+receipt['status'],flush=True)
    return receipt


def manifest(block,schedule,pop_seeds,frozen_spec):
    return dict(schema=frozen.VERSION,block=block,evidence='development' if block=='dev' else 'new-prospective',
        hashes=frozen.hash_manifest(),independent_unit='seed block; twins/variants/continuations nested',
        seeds={str(s):sorted(k) for s,k in schedule.items()},population_seeds=pop_seeds,
        epsilon=[0,.1],continuations={'0':1,'0.1':8},
        prior='uniform over enumerated policies, conditional on nuisance',
        prospective_freeze_sha256=frozen.sha256((ROOT/'docs/enh/r2/FREEZE.json').read_bytes()).hexdigest() if frozen_spec else None)


def finalize(block,out,schedule,pop_seeds,manifest):
    # Same frozen tail, with rows restored in schedule order, never map order.
    from scripts.bench_parallel_run import (
        population, Counter, clopper_pearson, summarize, symmetry, write_gzip,
        write_json, compare_separators, hash_manifest, write_dev_report, validate_freeze)
    root=ROOT; hashes=manifest['hashes']
    all_rows=[]; frontiers=[]; failures=[]
    for seed,kinds in schedule.items():
        receipt=checkpoint(out,dict(seed=seed,kinds=sorted(kinds),block=block,
                                  phase='methods',identity=identity()))
        if receipt is None: raise ValueError('missing seed checkpoint')
        frontiers.extend(receipt['frontiers']); failures.extend(receipt['failures'])
        for eps in (0,.1):
            with gzip.open(out/'units'/f'{seed}-eps-{eps}.json.gz','rt') as stream:
                all_rows.extend(json.load(stream))
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


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=DEFAULT_OUT)
    parser.add_argument('--gate',type=int,choices=(40,))
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--self-check',action='store_true')
    parser.add_argument('--containers',type=int,default=3)
    args=parser.parse_args(argv)
    if args.containers<1: parser.error('containers must be positive')
    spec=frozen.validate_freeze()
    schedule,pop_seeds=frozen._schedule('prospective',spec)
    selected=dict(list(schedule.items())[:40]) if args.gate else schedule
    if args.dry_run:
        print(f"plan: {len(selected)} seed blocks, {2*len(selected)} unit files, "
              f"{2*len(selected)} partition files; {len(pop_seeds)} population seeds; "
              f"gate={bool(args.gate)}; no Modal")
        return
    out=args.out.resolve()
    if out==SERIAL.resolve() or out.is_relative_to(SERIAL.resolve()) or SERIAL.resolve().is_relative_to(out):
        parser.error('serial directory is read-only')
    current=manifest('prospective',schedule,pop_seeds,spec)
    if (out/'manifest.json').exists():
        if json.loads((out/'manifest.json').read_text())!=current:
            raise ValueError('resume manifest differs')
    elif out.exists() and any(out.iterdir()):
        raise ValueError('nonempty output without manifest')
    frozen.write_json(out/'manifest.json',current)
    frozen.write_json(out/'freeze.json',spec)
    if args.self_check:
        receipt=self_check(schedule,spec,args.containers)
        if receipt['status']!='PASS': raise SystemExit(1)
        return
    gate_seeds=list(schedule)[:40]
    if args.gate:
        missing=[name for seed in gate_seeds for name in execution.seed_files(seed)
                 if not (SERIAL/name).is_file()]
        if missing:
            compare_gate(out,gate_seeds)
            raise SystemExit(1)
    else:
        require_gate(out,gate_seeds)
    try:
        run_selected(out,selected,args.containers)
        frozen.validate_freeze()
    except Exception:
        if args.gate:
            # Infrastructure failure cannot be reported as a successful gate.
            result=execution.compare_units(out,SERIAL,gate_seeds)
            result.update(status='FAIL',seeds=gate_seeds,identity=identity(),
                          infrastructure_error=True)
            execution.atomic_json(out/'GATE.json',result)
            print('GATE FAIL (infrastructure)',flush=True)
        raise
    if args.gate:
        if compare_gate(out,gate_seeds)['status']!='PASS': raise SystemExit(1)
    else:
        finalize('prospective',out,schedule,pop_seeds,current)


if __name__=='__main__': main()
