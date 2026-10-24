"""Compare preserved BENCH-IMP evidence with the final aligned DEV run."""
from collections import Counter
import gzip
import json
from pathlib import Path
import sys

repo=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(repo))
from ccc.bench.observe import canonical
from ccc.bench.report import strongest_baseline

base=repo/'docs/enh/bench'
old_dir=base/'bench_imp_snapshot'; new_dir=base/'dev_run'
def read_rows(path):
    with gzip.open(path/'records.json.gz','rt') as stream: return json.load(stream)
old=read_rows(old_dir); new=read_rows(new_dir)
renames={'relayed':'relayed-harmful','useful':'legitimate-useful'}
faults={'invalid-state':'state_mismatch','invalid-replay':'non_replayable','invalid-mask':'leaked_mask'}
def normalized(row):
    row=dict(row)
    if row['kind'] in faults:
        row['member']=faults[row['kind']];row['kind']='invalid-corrupted-trace'
    row['kind']=renames.get(row['kind'],row['kind'])
    return row

def key(row): return tuple(row[k] for k in ('seed','kind','member','epsilon','set'))
old_map={key(normalized(r)):normalized(r) for r in old}
new_map={key(r):r for r in new}
common=old_map.keys() & new_map.keys()
changed=[list(k) for k in sorted(common) if canonical(old_map[k])!=canonical(new_map[k])]
old_scores=json.loads((old_dir/'scores.json').read_text()); new_scores=json.loads((new_dir/'scores.json').read_text())
def score_key(r): return tuple(r[k] for k in ('method','axis','information_set','epsilon'))
old_scores={score_key(r):r for r in old_scores};new_scores={score_key(r):r for r in new_scores}
score_changes=[dict(key=list(k),before=old_scores[k],after=new_scores[k]) for k in sorted(old_scores.keys() & new_scores.keys()) if old_scores[k]!=new_scores[k]]
def count_legit(rows):
    return sum(r['truth']['M'] in ('legitimate-cooperation','info-bearing-legitimate') and r['methods']['CCC-v1.2.2']['status']=='supported' for r in rows)
report=json.loads((new_dir/'RESULTS_dev.json').read_text())
result=dict(evidence='development',before_records=len(old),after_records=len(new),matched_records=len(common),
    changed_matched_records=changed,removed_records=len(old_map.keys()-new_map.keys()),added_records=len(new_map.keys()-old_map.keys()),
    before_class_counts=dict(Counter(r['kind'] for r in old)),after_class_counts=dict(Counter(r['kind'] for r in new)),
    population_identical=(old_dir/'population.json').read_bytes()==(new_dir/'population.json').read_bytes(),
    population_exposure_identical=[(r['seed'],r['case'],r['E'],r['tau_O'],r['tau_C'],r['tau_W']) for r in json.loads((old_dir/'population.json').read_text())['rows']]==[(r['seed'],r['case'],r['E'],r['tau_O'],r['tau_C'],r['tau_W']) for r in json.loads((new_dir/'population.json').read_text())['rows']],
    frontiers_identical=(old_dir/'frontiers.json').read_bytes()==(new_dir/'frontiers.json').read_bytes(),
    CCC_supported_legitimate=dict(before=count_legit(old),after=count_legit(new)),
    strongest_baseline=dict(before=strongest_baseline(old),after=strongest_baseline(new)),
    aggregate_score_cells_changed=len(score_changes),aggregate_score_changes=score_changes,
    RQ_verdicts={k:v['status'] for k,v in report['rq'].items()},
    RQ4_class_rates=[{k:v for k,v in r.items() if k!='CCC_L2_supported'} for r in report['tables']['T5']],
    changes=[
      'A1: existing CRN law verified and regression tested; no continuation or oracle changes.',
      'Seed/freeze CLI: R2 hash-derived global disjoint streams and historical exclusion census; no prospective list/world drawn, no effect on DEV outcomes.',
      'Roster: replace standalone harmful/paraphrased with explicit common-cause, redundant, suspicious-no-harm and info-bearing controls; relayed/useful renamed, three invalid variants share one class unit. Counts 12600 to 13800.',
      'RQ1 cells now retain pair type and zero-eligible cells, with CRN metadata; zero violations unchanged.',
      'Criterion report: all RQ1–RQ6, T1–T10, figure data, per-class scores, cluster intervals and discordant-unit comparisons added; no method adjusted to turn failures into passes.',
      'DEV strongest baseline selected at I1 with balanced accuracy and explicit tie rule; selection is frozen for prospective use.',
      'Prospective guard validates R2 freeze, exact code/protocol/enumeration/prior hashes, parameters, timestamp, review, seed-file schedule and exclusions; no in-place prospective rerun.',
      'Both population epsilon strata evaluated by exact iid expectation, with separate RQ3 criteria and intervals; eps=0 exposure results unchanged.',
      'Population H supplied from the frozen J no-coordination oracle for A1a/A1b, strict outsider loss >2.5; prior H n/a removed. RQ3 exposure rows unchanged.',
      'Method exceptions retained as failed outputs for all methods and included in crash counts; final DEV had none.',
      'All prospective partitions hashed before method calls; report checks seed/hash metadata again after run. DEV sampling stays 50 blocks shared across classes, eps=0/.1 and R=8.'
    ])
(base/'align_delta.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('aggregate_score_changes','changes','RQ4_class_rates')},indent=2))
