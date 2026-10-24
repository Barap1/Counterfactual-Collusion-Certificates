"""Repeat the historical-only census; never draw a prospective seed."""
from pathlib import Path
import json
import sys
repo=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(repo))
from ccc.bench.seeds import exclusions,list_hash
sets,sources=exclusions(repo)
recorded=json.loads((repo/'docs/enh/bench/seed_exclusions.json').read_text())
actual={k:dict(count=len(v),sha256=list_hash(v)) for k,v in sets.items()}
assert actual==recorded['excluded_sets']
assert sources==recorded['sources']
assert sets['exp002_exp001_pilot_seeds']==recorded['historical_seeds']
print(json.dumps(dict(sources=len(sources),historical_seeds=len(recorded['historical_seeds']),
                     excluded_sets=actual,prospective_seeds_drawn=0,pass_census_replay=True),indent=2))
