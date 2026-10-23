"""Regenerate EVERY runner-error cell after a correctness fix, retaining attempts.

No scientific failure (including A5/A6 misses) is selected for rerunning. This
utility fixes missing-outcome adapter errors; it never changes parameters.
"""
from contextlib import ExitStack,redirect_stdout,redirect_stderr
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
import multiprocessing
import socket
from unittest.mock import patch
from .gate_a import ROOT,generate_dev,native_safe,summarize,write_report


def main():
    from ccc import paths
    from ccc.fixtures.worlds import split_manifest
    out=ROOT/'docs/gate_a'; file=out/'gate_a_results.json'
    e=json.loads(file.read_text()); m=split_manifest()
    selected=[(i,r) for i,r in enumerate(e['rows']) if any(x.startswith('runner_error:') for x in r['native']['CCC'].get('reasons',[]))]
    previous=[{'family':r['family'],'stratum':r['stratum'],'seed':r['seed'],'native':r['native']} for _,r in selected]
    worlds=[]
    for _,r in selected:
        offset=r['seed']-m['development']['world_seeds']['start']
        base='A1a' if bool((offset%2)^((offset//2)%2)) else 'A3a'
        worlds.append(generate_dev(r['family'],r['seed'],m,stratum=r['stratum'],invalid_base=base if r['family'].startswith('A6') else 'A1a'))
    with ExitStack() as stack:
        stack.enter_context(patch.object(paths,'colosseum_root',return_value=ROOT/'starter/collusion_hackathon/colosseum'))
        stack.enter_context(patch.object(paths,'_local_manifest',side_effect=AssertionError('secret manifest forbidden')))
        stack.enter_context(patch.object(socket.socket,'connect',side_effect=AssertionError('network forbidden')))
        log=stack.enter_context((out/'refresh_execution_output.txt').open('w'))
        stack.enter_context(redirect_stdout(log)); stack.enter_context(redirect_stderr(log))
        pool=stack.enter_context(ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')))
        for (index,_),native in zip(selected,pool.map(native_safe,worlds)):
            e['rows'][index]['native']=native
    e['correctness_revision']={'reason':'incomplete native outcomes lack reward fields; keep missing for baselines','rerun_cells':len(selected),'superseded_attempts':previous,'thresholds_or_fixtures_changed':False}
    summarize(e)
    e['source_sha256']={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for folder in ('ccc/audit','ccc/baselines','ccc/replay','ccc/fixtures') for p in (ROOT/folder).glob('*.py')}
    for rel in ('ccc/fixtures/split_manifest.json','docs/research/sci002/protocol.md'):
        e['source_sha256'][rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    file.write_text(json.dumps(e,indent=2)+'\n')
    write_report(e,out)
    with (out/'GATE_A_REPORT.md').open('a') as report:
        report.write('\nCorrectness revision: '+str(len(selected))+' runner-error cells were regenerated after fixing the missing-outcome guard. Every superseded attempt is retained in JSON. Scientific failures were not selected for rerunning; thresholds and fixtures were unchanged.\n')
        report.write('\nThe requested sandbox-exec test command was rejected before Python started (`sandbox_apply: Operation not permitted`). Fallback tests used Python socket-connect denial. Actual output is in test_fallback_output.txt; OS-level isolation remains unverified.\n')
        report.write('\nInitial source changes during collection: '+json.dumps(e.get('sources_changed_during_run',[]))+'. The audit runner guard was corrected; final hashes describe the corrected version.\n')
    print(json.dumps({'rerun_cells':len(selected),'gate_checks':e['gate_checks'],'confusion':e['confusion'],'sources_changed_during_run':e.get('sources_changed_during_run',[])},indent=2))


if __name__=='__main__':main()
