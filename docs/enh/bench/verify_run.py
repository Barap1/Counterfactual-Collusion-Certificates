"""Post-run DEV artifact checks and complete seed-13000 replay, using pure cache."""
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

repo=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(repo))
from ccc.bench.__main__ import DEV_SEEDS, hash_manifest
from ccc.bench.enumerate import census, design_reference, lookup
from ccc.bench.methods import configure_cache, run_methods
from ccc.bench.observe import SETS, canonical, digest, observe, project
from ccc.bench.twins import ATTRIBUTABLE, oracle, suite

out=repo/'docs/enh/bench/dev_run'
manifest=json.loads((out/'manifest.json').read_text())
complete=json.loads((out/'COMPLETE.json').read_text())
assert manifest['hashes']==hash_manifest()==complete['hashes']
assert {int(s) for s in manifest['seeds']}==set(DEV_SEEDS)
assert manifest['population_seeds']==list(DEV_SEEDS)
rows=json.loads(gzip.decompress((out/'records.json.gz').read_bytes()))
assert len(rows)==13800==complete['records']
assert {r['seed'] for r in rows}==set(DEV_SEEDS)
assert len({r['unit'] for r in rows})==50
assert all(len(r['methods'])==13 for r in rows)
assert all(r['placebo_availability']=='accepted' for r in rows)
assert all(r['truth']['H']==r['truth']['E']=='n/a' for r in rows if r['kind'].startswith('invalid-'))
assert all(r['methods']['CCC-v1.2.2']['status']=='invalid' for r in rows if r['kind'].startswith('invalid-') and r['set']!='I0')
assert all(r['methods']['CCC-v1.2.2']['predictions']['M']=='n/a' for r in rows)
assert all(r['identifiable']['M'] and r['truth']['M'] in ATTRIBUTABLE for r in rows
           if r['methods']['CCC-L-v0']['predictions']['M'] is True)
sym=json.loads((out/'symmetry.json').read_text())
violations=sum(v['rate']['unit_k'] for v in sym['violations'] if isinstance(v['rate'],dict))
assert violations==0
separators=json.loads((out/'separators.json').read_text())
assert not any(r['earlier_than_observable_separator'] for r in separators)

configure_cache(out/'cache')
for eps in (0,.1):
    tables=census(13000,eps)
    expected=json.loads(gzip.decompress((out/'units'/f'13000-eps-{eps}.json.gz').read_bytes()))
    replay=[]
    for instance in suite(13000,eps):
        full=observe(instance,'I5')
        for s in SETS:
            view=project(full,s); entry=lookup(tables,view)
            replay.append(dict(seed=13000,unit=instance.unit,kind=instance.kind,member=instance.member,
                epsilon=eps,set=s,truth=oracle(instance),
                identifiable={a:entry['axes']['attribution' if a=='M' else a]['identifiable'] for a in ('M','H','E')},
                M_multiclass_identifiable=entry['axes']['M']['identifiable'],
                class_counts={a:v['counts'] for a,v in entry['axes'].items()},view_sha256=digest(view),
                placebo_availability=full['placebo']['status'],
                methods=run_methods(view,design_reference(entry))))
    assert canonical(replay)==canonical(expected),f'full-seed replay mismatch, eps={eps}'

before=json.loads((repo/'docs/enh/bench/frozen_sources_before.json').read_text())
assert all(hash_manifest()[p]==h for p,h in before.items())
pop=json.loads((out/'population.json').read_text())
assert len(pop['rows'])==50 and {r['seed'] for r in pop['rows']}==set(DEV_SEEDS)
assert pop['k']==sum(r['E'] for r in pop['rows'])
legit=Counter((r['kind'],r['epsilon'],r['set']) for r in rows
              if r['truth']['M'] in ('legitimate-cooperation','info-bearing-legitimate')
              and r['methods']['CCC-v1.2.2']['status']=='supported')
frontiers=json.loads((out/'frontiers.json').read_text())
frontier_counts=Counter((kind,entry['minimal_pair_separator']) for f in frontiers for kind,entry in f['pairs'].items())
result=dict(evidence='development',records=len(rows),independent_seed_blocks=50,
    methods=13,symmetry_violation_unit_events=violations,
    full_seed_replay=dict(seed=13000,epsilon=[0,.1],records=276,canonical_bytes_identical=True),
    frozen_files_unchanged=len(before),population=dict(k=pop['k'],n=pop['n'],rate=pop['rate'],cp95=pop['cp95']),
    CCC_support_legitimate=[dict(kind=k,epsilon=e,information_set=s,member_records=n) for (k,e,s),n in sorted(legit.items())],
    pairwise_separator_counts=[dict(kind=k,separator=s,seed_stratum_count=n) for (k,s),n in sorted(frontier_counts.items())],
    artifact_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.json*'))})
(out/'verification.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('CCC_support_legitimate','artifact_sha256')},indent=2))
print('PASS: DEV artifact invariants, frozen sources and complete seed replay')
