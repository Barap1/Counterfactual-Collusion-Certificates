import json,gzip
from pathlib import Path
from collections import Counter
R=Path('/Users/aarav/Documents/Projects/ApartSprint');P=R/'docs/enh/r2/run_par';O=Path('/private/tmp/ccc-W1-R3');m=json.loads((P/'manifest.json').read_text());s=json.loads((R/'docs/enh/r2/seeds.json').read_text());rows=json.loads(gzip.decompress((P/'records.json.gz').read_bytes()))
expected={str(seed):[kind] for kind,seeds in s['strata'].items() if kind!='jira_iid' for seed in seeds};pop=json.loads((P/'population.json').read_text());d=dict(manifest_schedule_equal=m['seeds']==expected,population_seeds_equal=m['population_seeds']==s['strata']['jira_iid'],row_schedule_violations=[(r['seed'],r['kind']) for r in rows if r['kind'] not in expected.get(str(r['seed']),[])],counts=[],attempt_lengths={})
for kind in sorted(s['strata']):
 if kind=='jira_iid':continue
 for e in (0,.1):
  group=[r for r in rows if r['kind']==kind and r['epsilon']==e];seeds={r['seed'] for r in group};d['counts'].append(dict(kind=kind,epsilon=e,n=len(seeds),expected_seed_set_equal=seeds==set(s['strata'][kind])))
d['population_raw_seed_sets_equal']={e:{r['seed'] for r in v['rows']}==set(s['strata']['jira_iid']) for e,v in pop['strata'].items()}
for phase in ('enumerate','methods'):
 d['attempt_lengths'][phase]=dict(Counter(len(json.loads(f.read_text())) for f in (P/'execution/modal/attempts'/phase).glob('*.json')))
(O/'schedule.json').write_text(json.dumps(d,indent=2)+'\n');print({k:v for k,v in d.items() if k!='counts'});assert all(x['expected_seed_set_equal'] for x in d['counts'])
