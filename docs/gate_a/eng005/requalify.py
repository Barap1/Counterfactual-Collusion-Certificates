"""Reapply every DEV decision after the study-only one-sided-bound correction.

Full native collection is preserved, not selected or resampled. No branch code
or collection parameters changed in this qualification revision.
"""
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from tests.replay.offline_runner import guard
ROOT=Path(__file__).resolve().parents[3]
os.environ['CCC_STARTER_ROOT']=str(ROOT/'starter/collusion_hackathon')
sys.addaudithook(guard)
from ccc.audit.gate_a import apply_study_checks, summarize, write_fixed_report
out=ROOT/'docs/gate_a/eng005'
p=out/'gate_a_results.json.gz'
archive=out/'qualification_prior.json.gz'
original=archive.read_bytes() if archive.exists() else p.read_bytes()
if not archive.exists():
    archive.write_bytes(original)
e=json.loads(gzip.decompress(original))
def branch_hash(e):
    return sha256(json.dumps([dict(family=r['family'],stratum=r['stratum'],seed=r['seed'],
        branches=r['native'].get('branches'),baselines=r['native']['baselines'],
        checks=r['native']['checks']) for r in e['rows']],sort_keys=True).encode()).hexdigest()
before=branch_hash(e)
collection_sources=e.get('qualification_revision',{}).get('collection_source_sha256',e['source_sha256'])
e['qualification_revision']={'reason':'analysis_spec study V10 uses one-sided 95% t lower bound',
    'requalified_cells':len(e['rows']),'prior_qualification_sha256':sha256(original).hexdigest(),
    'collection_source_sha256':collection_sources, 'branch_baseline_check_sha256_before':before,
    'thresholds_or_fixtures_changed':False}
apply_study_checks(e)
summarize(e)
assert branch_hash(e)==before
e['qualification_revision']['branch_baseline_check_sha256_after']=branch_hash(e)
e['source_sha256']={rel:sha256((ROOT/rel).read_bytes()).hexdigest() for rel in e['source_sha256']}
e['qualification_revision']['changed_sources_since_collection']=[rel for rel,h in
    e['qualification_revision']['collection_source_sha256'].items() if e['source_sha256'][rel]!=h]
with gzip.open(p,'wb') as stream:
    stream.write((json.dumps(e,indent=2)+'\n').encode())
write_fixed_report(e,out)
with (out/'GATE_A_v1.1-fixed.md').open('a') as stream:
    stream.write('\nQualification provenance: the full 800-cell native collection was followed by a full '
                 '800-cell decision requalification to use the analysis contract’s one-sided 95% V10 lower bound. '
                 'A prior qualification is retained as `qualification_prior.json.gz`. '
                 'All branch, validator and baseline records are byte-equivalent under the canonical hash '
                 'recorded before/after in `qualification_revision`; only audit study math changed. '
                 'Current qualification source hashes and native-collection source hashes are both retained.\n')
print(json.dumps({'gate_checks':e['gate_checks'],'confusion':e['confusion'],
                  'supported':sum(r['native']['CCC']['status']=='supported' for r in e['rows']),
                  'qualification_revision':e['qualification_revision']},indent=2))
