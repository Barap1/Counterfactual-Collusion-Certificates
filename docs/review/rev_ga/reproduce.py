"""REV-GA independent recomputation from raw cell-level evidence (no report numbers used)."""
import gzip, json, collections, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'docs/gate_a/diag/gate_a_results.json.gz'
R = json.load(gzip.open(P))['rows']
mO = 2.5
a1 = [r for r in R if r['family'] in ('A1a', 'A1b')]
# 1. A1 oracle effects (independent oracle) vs floor; native point estimates
below = [r for r in a1 if r['oracle_effects']['tau_O'] < mO]
nonpos = [r for r in a1 if r['oracle_effects']['tau_O'] <= 0]
print('A1 n=%d oracle tau_O<m_O: %d ; <=0: %d ; >m_O: %d' % (len(a1), len(below), len(nonpos), sum(r['oracle_effects']['tau_O'] > mO for r in a1)))
nat = [r['native']['CCC']['estimates']['effects']['tau_O'] for r in a1]
print('native-vs-oracle max |diff| over A1: %.3g' % max(abs(n - r['oracle_effects']['tau_O']) for n, r in zip(nat, a1)))
hi = [r for r in a1 if r['oracle_effects']['tau_O'] > mO]
print('above-floor cells: %d ; with N==K (|tau_O_N-tau_O|<1e-9): %d ; lesion reason: %d ; status=%s' % (
    len(hi), sum(abs(r['native']['CCC']['tau_O_N'] - r['native']['CCC']['estimates']['effects']['tau_O']) < 1e-9 for r in hi),
    sum('lesion_artefact' in r['native']['CCC']['reasons'] for r in hi),
    dict(collections.Counter(r['native']['CCC']['status'] for r in hi))))
# 2. A6: activated faults
a6 = [r for r in R if r['family'].startswith('A6')]
act = [r for r in a6 if r['native']['fault_exercised']]
print('A6 requested=%d activated=%d activated&invalid=%d ; inactive by family=%s' % (
    len(a6), len(act), sum(r['native']['CCC']['status'] == 'invalid' for r in act),
    dict(collections.Counter(r['family'] for r in a6 if not r['native']['fault_exercised']))))
# 3. A5 not-exonerated
a5 = [r for r in R if r['family'].startswith('A5')]
print('A5 not-supported (bad): %s / %d' % (dict(collections.Counter(r['family'] for r in a5 if r['native']['CCC']['status'] == 'not supported')), len(a5)))
# 4. Is N ever distinct from K anywhere? (lesion veto discriminative power)
d = [(r['family']) for r in R if 'tau_O_N' in r['native']['CCC'] and r['native']['CCC']['estimates'].get('effects')
     and abs(r['native']['CCC']['tau_O_N'] - r['native']['CCC']['estimates']['effects']['tau_O']) > 1e-9]
print('cells where tau_O_N != tau_O:', len(d))
print('CCC supported anywhere:', sum(r['native']['CCC']['status'] == 'supported' for r in R))
