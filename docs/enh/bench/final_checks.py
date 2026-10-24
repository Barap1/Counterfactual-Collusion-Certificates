"""Final source/report lineage, sample-stratum and integration evidence checks."""
from pathlib import Path
from hashlib import sha256
import json
import re
import sys
repo=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(repo))
from ccc.bench.__main__ import hash_manifest

base=repo/'docs/enh/bench';out=base/'dev_run'
def read(path): return json.loads(path.read_text())
manifest=read(out/'manifest.json'); complete=read(out/'COMPLETE.json');result=read(out/'RESULTS_dev.json')
assert complete['hashes']==manifest['hashes']==hash_manifest()
assert read(base/'hash_manifest.json')['hashes']==hash_manifest()
assert read(base/'enumeration/manifest.json')['hashes']==hash_manifest()
assert all(sha256((out/p).read_bytes()).hexdigest()==h for p,h in result['inputs'].items())
assert not (repo/'docs/enh/r2/FREEZE.json').exists()
assert not (repo/'docs/enh/r2/seeds.json').exists()
assert not (base/'should-not-exist').exists()
assert complete['records']==13800
pop=result['tables']['T4']['strata']
assert set(pop)=={'0','0.1'}
for e,value in pop.items():
    assert value['n']==50
    assert {r['seed'] for r in value['rows']}==set(range(13000,13050))
    assert all(r['epsilon']==float(e) and type(r['H']) is bool for r in value['rows'])
assert read(base/'align_delta.json')['population_exposure_identical']
changes=[]
for row in read(repo/'demo/data/MANIFEST.json')['source_hashes']:
    if 'archive_member' in row: continue
    p=repo/row['path']
    if p.name in ('.env','compute.env') or p.name.endswith('.local.json'):
        raise AssertionError('unexpected secret path')
    actual=sha256(p.read_bytes()).hexdigest()
    if actual!=row['sha256']: changes.append(dict(path=row['path'],expected=row['sha256'],actual=actual))
(base/'align_integration_mismatches.json').write_text(json.dumps(changes,indent=2,sort_keys=True)+'\n')
bench_log=(base/'align_targeted_tests_final.log').read_text()
suite_log=(base/'align_offline_suite_final.log').read_text()
bench_n=int(re.search(r'Ran (\d+) tests',bench_log)[1])
assert re.search(r'^OK$',bench_log,re.M)
total=int(re.search(r'Ran (\d+) tests',suite_log)[1])
failed=int(re.search(r'failures=(\d+)',suite_log)[1]) if 'failures=' in suite_log else 0
errors=int(re.search(r'errors=(\d+)',suite_log)[1]) if 'errors=' in suite_log else 0
skipped=int(re.search(r'skipped=(\d+)',suite_log)[1]) if 'skipped=' in suite_log else 0
checks=dict(final_source_hashes_match=True,report_inputs_match=True,prospective_freeze_created=False,
            prospective_seeds_materialised=False,records=complete['records'],bench_tests=bench_n,
            offline_suite=dict(total=total,passed=total-failed-errors-skipped,failed=failed,errors=errors,skipped=skipped),
            population={e:dict(k=v['k'],n=v['n'],rate=v['rate'],cp95=v['cp95'],H=v['harm']) for e,v in pop.items()},
            RQ={k:v['status'] for k,v in result['rq'].items()},demo_stale_sources=len(changes))
(base/'align_final_checks.json').write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
print(json.dumps(checks,indent=2))
