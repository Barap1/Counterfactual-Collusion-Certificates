"""Verify correction artifacts against measured results and preserved commitments."""
import gzip,json
from hashlib import sha256
from pathlib import Path
from collections import Counter
from tests.replay.offline_runner import guard
import sys
sys.addaudithook(guard)
ROOT=Path.cwd();OUT=ROOT/'docs/gate_a/v1.2/correction_v1.2.1';OPS=ROOT/'ops/reports/AMD-FIX-2'
def read(p):
    with gzip.open(p,'rt') as f:return json.load(f)
def digest(p):return sha256(p.read_bytes()).hexdigest()
prior=json.loads((OPS/'prior_sha256.json').read_text())
unchanged={p:digest(ROOT/p)==h for p,h in prior.items() if not p.endswith('GATE_A_v1.2.md')}
assert all(unchanged.values()),unchanged
old=(ROOT/'docs/gate_a/v1.2/GATE_A_v1.2.md').read_text().split('\n\n',1)[1]
assert sha256(old.encode()).hexdigest()==prior['docs/gate_a/v1.2/GATE_A_v1.2.md']
e=read(OUT/'gate_a_results.json.gz'); c=read(OUT/'constructed_results.json.gz')
assert len(e['rows'])==800 and len(c['rows'])==30
assert e['sources_changed_during_run']==[]
assert all(12000<=r['seed']<12020 for r in e['rows'])
assert e['holdout_worlds_generated']==e['live_calls']==e['spend_usd']==0
assert all(digest(ROOT/p)==h for p,h in e['source_sha256'].items())
assert all(r['prediction_confirmed'] and not r['voided'] for r in c['rows'])
assert not e['gate_checks']['A6_intended_validator']['passed']
assert e['gate_checks']['A6_intended_validator']['total']==360
scores=json.loads((OUT/'prediction_scorecard.json').read_text())
assert len(scores)==21
old_scores=json.loads((ROOT/'docs/gate_a/v1.2/prediction_scorecard.json').read_text())
assert {r['prediction'] for r in scores}=={r['prediction'] for r in old_scores}
provenance={'task':'AMD-FIX-2','cwd':str(ROOT),'evidence_version':'1.2.1',
 'historical_inputs_unchanged':unchanged,'historical_report_body_unchanged':True,
 'source_sha256':e['source_sha256'],
 'correction_artifact_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='provenance.json'},
 'constructed_predictions_match':30,'prediction_counts':dict(Counter(r['verdict'] for r in scores)),
 'dev_seed_range':[12000,12019],'source_changes_during_run':e['sources_changed_during_run']}
(OUT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print(json.dumps({'verified':True,'prediction_counts':provenance['prediction_counts']}))
