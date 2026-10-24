"""DEV-only release driver. No CLI input override, credentials, or inference."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.replay.offline_runner import guard

def release_guard(event, args):
    guard(event, args)
    if event in ('open', 'os.listdir', 'os.scandir') and args and isinstance(args[0], (str, bytes, os.PathLike)):
        p = Path(os.fsdecode(args[0])).absolute()
        if p.is_relative_to(ROOT):
            rel = p.relative_to(ROOT).as_posix()
            if rel.startswith(('docs/runner/exp002', 'runs/exp002')) or rel == 'ops/budget_ledger.jsonl':
                raise PermissionError('held-out access forbidden')
sys.addaudithook(release_guard)
from ccc.analysis.pipeline import run
from ccc.analysis.stage2 import run as pin
from ccc.audit.gate_a import main, resolve_parameters

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main_driver():
    out = Path(sys.argv[1]).resolve()
    source = ROOT/'docs/release/exp001_dev_input'
    expected = json.loads((ROOT/'docs/release/input_hashes.json').read_text())
    for name, sha in expected.items():
        assert digest(source/name) == sha, 'DEV input hash mismatch: '+name
    run(source, out/'analysis')
    pin(source, out/'stage2')
    theta = runpy.run_path(str(ROOT/'docs/stats/stage2/theta_pin.py'))
    theta['main'].__globals__['OUT'] = out/'theta_pin.json'
    theta['main']()
    gate = out/'gate_a'
    if not (gate/'gate_a_results.json').exists():
        main(gate, params=resolve_parameters(theta=.4, bootstrap_draws=10000))
    evidence = json.loads((gate/'gate_a_results.json').read_text())
    evidence['evidence_version']='1.2.2'
    evidence['correction_task']='v1.2.2 theta pin + DEV bootstrap'
    (gate/'gate_a_results.json').write_text(json.dumps(evidence, indent=2)+'\n')
    # gzip container metadata is deliberately excluded: compare decompressed bytes.
    import gzip
    reference = ROOT/'docs/gate_a/v1.2/correction_v1.2.2/gate_a_results.json.gz'
    assert (gate/'gate_a_results.json').read_bytes() == gzip.decompress(reference.read_bytes()), 'Gate A differs'
    checks = {'gate_a_decompressed':digest(gate/'gate_a_results.json')}
    run(source, out/'analysis_repeat')
    differences=[]
    metadata_differences=[]
    def compatible(old,new,path=''):
        if isinstance(old,dict):
            assert isinstance(new,dict), path
            for key in ('code_hashes','rule_hashes','rules','warnings'):
                if key in old or key in new:
                    if old.get(key) != new.get(key):
                        metadata_differences.append(path+'/'+key)
            for key,value in old.items():
                child_path=path+'/'+key
                if key in ('code_hashes','rule_hashes','rules','warnings'):
                    continue
                assert key in new, 'archived field removed: '+path+'/'+key
                compatible(value,new[key],child_path)
        elif isinstance(old,list):
            assert len(old)==len(new), 'archived row count differs: '+path
            for i,(a,b) in enumerate(zip(old,new)): compatible(a,b,path+'/'+str(i))
        else:
            assert old==new, 'archived scientific value differs: '+path
    for folder, ref in [('analysis','docs/analysis/exp001_dev_v2'), ('stage2','docs/stats/stage2/exp001')]:
        for p in sorted((out/folder).rglob('*')):
            if not p.is_file(): continue
            relative = p.relative_to(out/folder)
            baseline = ROOT/ref/relative
            if folder=='analysis':
                assert p.read_bytes()==(out/'analysis_repeat'/relative).read_bytes(), 'current analysis nondeterminism: '+str(relative)
                if p.read_bytes()!=baseline.read_bytes():
                    differences.append(str(relative))
                    if p.suffix not in ('.json','.csv'):
                        assert p.read_bytes()==baseline.read_bytes(), 'archived output differs: '+str(relative)
                    if p.suffix=='.json':
                        a=json.loads(p.read_text()); b=json.loads(baseline.read_text())
                        if relative.name=='aggregate.json':
                            for key in ('code_hashes','limitations','synthetic'):
                                a.pop(key,None); b.pop(key,None)
                        compatible(b,a,str(relative))
            else:
                if p.suffix == '.json':
                    compatible(json.loads(baseline.read_text()), json.loads(p.read_text()), str(relative))
                elif relative.name == 'stage2_addendum.md':
                    old_text=baseline.read_text(); new_text=p.read_text()
                    marker='```json\n'; closing='\n```'
                    old_start=old_text.rfind(marker); new_start=new_text.rfind(marker)
                    assert old_start >= 0 and new_start >= 0, 'Stage-2 addendum JSON block missing'
                    assert old_text[:old_start] == new_text[:new_start], 'Stage-2 addendum text differs'
                    old_end=old_text.find(closing,old_start); new_end=new_text.find(closing,new_start)
                    assert old_end >= 0 and new_end >= 0, 'Stage-2 addendum JSON block unterminated'
                    assert old_text[old_end:] == new_text[new_end:], 'Stage-2 addendum suffix differs'
                    compatible(json.loads(old_text[old_start+len(marker):old_end]),
                               json.loads(new_text[new_start+len(marker):new_end]),
                               str(relative))
                else:
                    assert p.read_bytes()==baseline.read_bytes(), 'output differs: '+str(relative)
            checks[folder+'/'+str(relative)] = digest(p)
    theta_reference = json.loads((ROOT/'docs/stats/stage2/theta_pin.json').read_text())
    theta_output = json.loads((out/'theta_pin.json').read_text())
    compatible(theta_reference, theta_output, 'theta_pin.json')
    if metadata_differences:
        print('Report-only metadata differences: '+', '.join(metadata_differences))
    (out/'analysis_compatibility.json').write_text(json.dumps(dict(
        archived_byte_differences=differences,
        report_only_metadata_differences=metadata_differences,
        method='Current analysis repeated with exact byte/hash agreement. Archived scientific fields retained and equal; additive fields allowed. code_hashes, rule_hashes, and warnings differences are reported but excluded from value comparison.'),indent=2)+'\n')
    checks['theta_pin.json']=digest(out/'theta_pin.json')
    (out/'verified_hashes.json').write_text(json.dumps(checks,indent=2)+'\n')
    print('Verified DEV inputs, analysis, Stage-2 draft, theta pin and Gate A; Gate A remains FAIL.')

if __name__ == '__main__': main_driver()
