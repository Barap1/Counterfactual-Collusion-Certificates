"""Offline, DEV-only descriptive diagnosis of archived and corrected Gate A cells."""
import csv
import gzip
from hashlib import sha256
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
old_path = ROOT / 'docs/gate_a/gate_a_results.json.gz'
old = json.load(gzip.open(old_path, 'rt'))
new_path = OUT / 'gate_a_results.json.gz'
new = json.load(gzip.open(new_path, 'rt'))
from ccc.audit.gate_a import require_dev
from ccc.fixtures.worlds import split_manifest
for data in (old, new):
    assert data['phase'] == 'development' and data['holdout_worlds_generated'] == 0
    for row in data['rows']:
        require_dev(row['seed'], split_manifest())

def vflags(row):
    return sorted({f for c in row['native']['checks'] if c['id'] == 'V07'
                   for f in c.get('details', {}).get('flags', [])})

summary = {'input_sha256': {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                            for p in (old_path, new_path)}, 'A1': {}, 'A5': {}, 'A6_inactive': []}
with gzip.open(OUT / 'A1_cells.csv.gz', 'wt', newline='') as stream:
    writer = csv.writer(stream)
    writer.writerow(['family','stratum','seed','wording','tau_O','CI_lower','CI_upper',
                     'oracle_tau_O','F_Omean','K_Omean','status','reasons'])
    for r in old['rows']:
        if r['family'] not in ('A1a', 'A1b'): continue
        d = r['native']['CCC']; e = d['estimates']; tau = e['effects']['tau_O']
        assert e['intervals']['tau_O'] == [tau, tau]
        assert abs(tau - r['oracle_effects']['tau_O']) < 1e-8
        assert tau == e['means']['K']['Omean'] - e['means']['F']['Omean']
        writer.writerow([r['family'],r['stratum'],r['seed'],r['wording_type'],tau,
                         *e['intervals']['tau_O'],r['oracle_effects']['tau_O'],
                         e['means']['F']['Omean'],e['means']['K']['Omean'],d['status'],';'.join(d['reasons'])])
for family in ('A1a','A1b'):
    rows = [r for r in old['rows'] if r['family'] == family]
    vals = [r['oracle_effects']['tau_O'] for r in rows]
    high = [r for r in rows if r['oracle_effects']['tau_O'] > 2.5]
    summary['A1'][family] = {'n':len(rows), 'min':min(vals),'max':max(vals),
        'mean':sum(vals)/len(vals),'negative':sum(v<0 for v in vals),'zero':vals.count(0),
        'positive_below_floor':sum(0<v<2.5 for v in vals),'equal_floor':vals.count(2.5),
        'above_floor':len(high), 'point_CI_equals_oracle':len(rows),
        'statuses':dict(Counter(r['native']['CCC']['status'] for r in rows)),
        'above_floor_reasons':dict(Counter(reason for r in high for reason in r['native']['CCC']['reasons'])),
        'distribution':[{'tau_O':v,'count':n} for v,n in sorted(Counter(vals).items())]}
for family in ('A5a-verbatim','A5a-paraphrase','A5b'):
    before = [r for r in old['rows'] if r['family'] == family]
    after = [r for r in new['rows'] if r['family'] == family]
    summary['A5'][family] = {'n':len(before),
        'V07_flagged_cells':sum(bool(vflags(r)) for r in before),
        'V07_flags':dict(Counter(f for r in before for f in vflags(r))),
        'old_decision_flagged_cells':sum(bool(r['native']['CCC']['flags']) for r in before),
        'old_statuses':dict(Counter(r['native']['CCC']['status'] for r in before)),
        'new_statuses':dict(Counter(r['native']['CCC']['status'] for r in after)),
        'residual_not_supported':[{'seed':r['seed'],'stratum':r['stratum'],'wording':r['wording_type'],
                                   'V07_flags':vflags(r),
                                   'surviving_private_communications':[t for o in r['native']['detector_text_evidence']['observations'] for t in o['surfaces'].get('1',[]) if not t.startswith('[')]} for r in after if r['native']['CCC']['status']=='not supported']}
for r in old['rows']:
    if r['family']=='A6b' and not r['native']['fault_exercised']:
        n=r['native']
        summary['A6_inactive'].append({'seed':r['seed'],'stratum':r['stratum'],
            'receiver_observations':len(n['detector_text_evidence']['observations']),
            'branch_statuses':{a:b['status'] for a,b in n['branches'].items()},
            'failed_checks':[c for c in n['checks'] if c['status']=='fail'],
            'local_fault_reference':r['local_fault_reference']})
pairs = list(zip(old['rows'], new['rows']))
assert all((a['family'],a['stratum'],a['seed']) == (b['family'],b['stratum'],b['seed']) for a,b in pairs)
summary['rerun_comparison'] = {
    'cells': len(pairs),
    'changed_decisions': sum(a['native']['CCC']['status'] != b['native']['CCC']['status'] for a,b in pairs),
    'branch_outcome_mismatches': sum(a['native'].get('branches') != b['native'].get('branches') for a,b in pairs),
    'baseline_label_mismatches': sum(a['native']['baselines'] != b['native']['baselines'] for a,b in pairs),
    'oracle_effect_mismatches': sum(a['oracle_effects'] != b['oracle_effects'] for a,b in pairs)}
summary['new_gate_checks'] = new['gate_checks']
summary['new_confusion'] = new['confusion']
summary['source_drift'] = new['sources_changed_during_run']
(OUT / 'diagnosis_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
