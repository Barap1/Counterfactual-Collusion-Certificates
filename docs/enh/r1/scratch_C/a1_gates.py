"""Throwaway: binding gates on A1 (truth=forbidden) cells, v1.2.2. Read-only. Run: python3 -I a1_gates.py"""
import gzip, json, collections as C
d = json.load(gzip.open('docs/gate_a/v1.2/correction_v1.2.2/gate_a_results.json.gz'))
A1 = [x for x in d['rows'] if x['family'] in ('A1a', 'A1b')]
def bucket(x):
    t = x['oracle_effects']['tau_O']; n = x['native']['CCC']
    if t == 0: return 'oracle tau_O = 0 (path inactive)'
    if t < 2.5: return '0 < oracle tau_O < m_O'
    if n['status'] == 'supported': return 'active, supported'
    return 'active, blocked: ' + ','.join(n['reasons'])
c = C.Counter(bucket(x) for x in A1)
for k, v in c.items(): print(v, k)
act = [x for x in A1 if x['oracle_effects']['tau_O'] >= 2.5]
print('active:', len(act), 'info_bearing True among active:', sum(bool(x['native']['CCC']['info_bearing']) for x in act))
print('world groups (seeds) active:', sorted({x['seed'] for x in act}))
for fam in ('A5a-verbatim', 'A5a-paraphrase', 'A5b', 'A2a'):
    R = [x for x in d['rows'] if x['family'] == fam]
    print(fam, len(R), 'active', sum(x['oracle_strata']['path_active'] for x in R),
          C.Counter(x['native']['CCC']['status'] for x in R))
