"""BENCH-ALIGN2 final lineage, amendment, frozen-source and demo integration checks."""
from hashlib import sha256
import gzip
import json
from pathlib import Path
import re
import sys
repo=Path(__file__).resolve().parents[3];sys.path.insert(0,str(repo))
from ccc.bench.__main__ import hash_manifest
base=repo/'docs/enh/bench';run=base/'dev_run'
def read(path): return json.loads(path.read_text())
manifest=read(run/'manifest.json');complete=read(run/'COMPLETE.json');results=read(run/'RESULTS_dev.json')
assert manifest['hashes']==complete['hashes']==hash_manifest()==read(base/'hash_manifest.json')['hashes']
assert read(base/'enumeration/manifest.json')['hashes']==hash_manifest()
assert all(sha256((run/p).read_bytes()).hexdigest()==h for p,h in results['inputs'].items())
assert {int(x) for x in manifest['seeds']}==set(range(13000,13050))
assert set(manifest['population_seeds'])==set(range(13000,13050))
assert complete['records']==13800
assert not (repo/'docs/enh/r2/FREEZE.json').exists()
assert not (repo/'docs/enh/r2/seeds.json').exists()
assert read(base/'align2_numeric_delta.json')['original_12_method_outputs_and_all_observations_identical']
with gzip.open(base/'bench_align_snapshot/RESULTS_dev.json.gz','rt') as f: prior=json.load(f)
assert results['tables']['T5']==prior['tables']['T5']
assert results['rq']['RQ4']==prior['rq']['RQ4']
assert [{k:v for k,v in cell.items() if k!='method'} for cell in results['tables']['T8_v0']]==prior['tables']['T8']
assert results['tables']['T4']==prior['tables']['T4']
assert results['tables']['RQ6']==prior['tables']['RQ6']
assert results['twin_exhibit']['seed']==13000
assert (run/'RESULTS.json').read_bytes()==(run/'RESULTS_dev.json').read_bytes()
assert set(results['twin_exhibit']['members'])=={'A','B'}
stale=[]
for entry in read(repo/'demo/data/MANIFEST.json')['source_hashes']:
    if 'archive_member' in entry: continue
    path=repo/entry['path']
    assert path.name not in ('.env','compute.env') and not path.name.endswith('.local.json')
    if sha256(path.read_bytes()).hexdigest()!=entry['sha256']: stale.append(entry['path'])
assert not stale, stale
logs={}
for name in ('targeted_tests','offline_suite'):
    content=(base/f'align2_{name}.log').read_text()
    assert re.search(r'^OK(?: \(skipped=\d+\))?$',content,re.M), content[-3000:]
    total=int(re.search(r'Ran (\d+) tests',content)[1])
    skipped=re.search(r'skipped=(\d+)',content)
    skipped=int(skipped[1]) if skipped else 0
    logs[name]=dict(total=total,passed=total-skipped,skipped=skipped,failed=0)
result=dict(evidence='development',source_hashes_match=True,report_input_hashes_match=True,
    original_RQ4_verbatim_and_T5_unchanged=True,v0_T8_unchanged=True,
    population_and_RQ6_unchanged=True,prospective_seed_list_or_freeze_created=False,
    records=13800,methods=13,seeds='13000-13049',stale_demo_sources=stale,validation=logs,
    rq={k:v['status'] for k,v in results['rq'].items()})
(base/'align2_final_checks.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2,sort_keys=True))
