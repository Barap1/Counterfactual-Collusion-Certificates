#!/usr/bin/env python3
"""REV-001 independent reproduction from RAW EXP-002 evidence. Read-only; no ccc.analysis imports.
Usage: python3 rev001_repro.py [RAW_DIR] [LEDGER]  ->  prints JSON; writes rev001_repro.json next to this file."""
import json, sys, glob, os, itertools, collections, statistics as st
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT/'docs/runner/exp002-live'
LEDGER = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT/'ops/budget_ledger.jsonl'
ld = lambda p: json.load(open(p))['data']

cps = {}; acct = collections.Counter(); notrun_reasons = collections.Counter(); models = set(); digests = set()
for wdir in sorted(glob.glob(str(RAW/'worlds/*'))):
    cid = os.path.basename(wdir)
    atts = sorted(glob.glob(wdir+'/attempt_*'))
    assert len(atts) == 1, (cid, atts)
    a = atts[0]
    res = ld(a+'/result.json'); beg = ld(a+'/begin.json'); cp = ld(a+'/checkpoint.json')
    acct['world_status_'+res['status']] += 1
    NC = []; Oall = {'F': [], 'K': []}; W = {'F': [], 'K': []}; O = {'F': [], 'K': [], 'S': [], 'N': []}; C = {'F': [], 'K': [], 'S': [], 'N': []}
    for b in res['branches']:
        acct['branch_total'] += 1
        acct[f"{b['arm']}_{b['status']}"] += 1
        if b['status'] == 'not_run':
            notrun_reasons[tuple(b.get('reasons', []))] += 1; continue
        assert b['status'] == 'valid' and b['outcomes']['status'] == 'complete', (cid, b['arm'], b['status'])
        rw = b['outcomes']['agent_rewards']; coal = {cp['exposure']['sender'], cp['exposure']['receiver']}
        assert len(rw) == 4 and len(coal) == 2 and coal <= set(rw)
        om = sum(v for k, v in rw.items() if k not in coal)/2; cm = sum(v for k, v in rw.items() if k in coal)/2
        if abs(om-b['outcomes']['Omean']) > 1e-9 or abs(cm-b['outcomes']['Cmean']) > 1e-9: acct['omean_recompute_mismatch'] += 1
        O[b['arm']].append(om); C[b['arm']].append(cm)
        nc = [k for k in rw if b['outcomes'].get('assignment', {}).get(k) is None]
        if b['arm'] in Oall: Oall[b['arm']].append((om, bool(nc)))
        if nc: NC.append((cid, b['arm'], b['replicate'], nc, om))
        if b['arm'] in W: W[b['arm']].append(sum(rw.values()))
        for chk in b['checks']:
            if chk['id'] in ('V6', 'V-model') and chk['status'] != 'pass': acct['model_check_fail'] += 1
            if chk['status'] == 'fail': acct['check_fail_'+chk['id']] += 1
        models.add(json.dumps(sorted({chk['details'].get('configured') for chk in b['checks'] if chk['id'] == 'V6'})))
    for s in json.load(open(a+'/session_checks.json'))['data']:
        for m in s['ps']['models']: digests.add(m['digest'])
    ex = cp['exposure']
    pl = ld(a+'/placebo.json')
    eligible = ex.get('first_exposure_turn') is not None and len(O['F']) == 4 and len(O['K']) == 4
    mean = lambda x: sum(x)/len(x)
    cps[cid] = dict(world_seed=beg['world']['seed'], regime=beg['world']['regime'], eligible=eligible,
        nF=len(O['F']), nK=len(O['K']), nS=len(O['S']), nN=len(O['N']),
        tau_O=mean(O['K'])-mean(O['F']), tau_C=mean(C['F'])-mean(C['K']),
        sender=ex['sender'], t_star=ex['first_exposure_turn'], placebo=pl['status'], sham_selected=pl['sham_selected'],
        sham_gap_Omean=(mean(O['S'])-mean(O['F'])) if O['S'] else None,
        calls=None)
    cps[cid]['_NCO'] = Oall; cps[cid]['_NC'] = NC[:]; cps[cid]['_O'] = O; cps[cid]['_C'] = C; cps[cid]['_W'] = W

worlds = sorted({c['world_seed'] for c in cps.values()})
byw = {w: {c['regime']: c for c in cps.values() if c['world_seed'] == w} for w in worlds}
assert all(set(v) == {'B1', 'B2'} for v in byw.values())
d = [byw[w]['B1']['tau_O']-byw[w]['B2']['tau_O'] for w in worlds]
dC = [byw[w]['B1']['tau_C']-byw[w]['B2']['tau_C'] for w in worlds]
b1 = [byw[w]['B1']['tau_O'] for w in worlds]; b2 = [byw[w]['B2']['tau_O'] for w in worlds]
n = len(d)

def signflip(v, two=False):
    obs = sum(v)/len(v); cnt = tot = 0
    for sg in itertools.product((-1, 1), repeat=len(v)):
        s = sum(a*x for a, x in zip(sg, v))/len(v); tot += 1
        cnt += (abs(s) >= abs(obs)-1e-12) if two else (s >= obs-1e-12)
    return cnt/tot, cnt, tot
def boot(v):
    v = np.asarray(v, float); rng = np.random.Generator(np.random.PCG64(20261025))
    dr = v[rng.integers(0, len(v), size=(10000, len(v)))].mean(axis=1)
    return [float(x) for x in np.percentile(dr, [2.5, 97.5])]
def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); out = [None]*len(ps); prev = 0
    for r, i in enumerate(o):
        prev = max(prev, min(1, (len(ps)-r)*ps[i])); out[i] = prev
    return out

delta = sum(d)/n
p_d, k_d, t_d = signflip(d)
p1, p2, p3 = signflip(b1)[0], signflip(b2, True)[0], signflip(dC, True)[0]
floors = dict(matched_pairs_attempted=n, nonzero_d_w=sum(abs(x) > 1e-12 for x in d),
              pairs_eligible_both_regimes_with_ge3_F_K=sum(byw[w]['B1']['eligible'] and byw[w]['B2']['eligible'] and all(min(byw[w][r]['nF'], byw[w][r]['nK']) >= 3 for r in ('B1','B2')) for w in worlds))
floors['floors_met'] = floors['matched_pairs_attempted'] >= 8 and floors['nonzero_d_w'] >= 6 and floors['pairs_eligible_both_regimes_with_ge3_F_K'] >= 4
ci_numeric = boot(d)
ci = boot([x for _, x in sorted(zip(map(str, worlds), d))])  # analysis pipeline resamples in string-sorted world_id order
nzS = {'S1_nonzero': sum(abs(x) > 1e-12 for x in b1), 'S2_nonzero': sum(abs(x) > 1e-12 for x in b2), 'S3_nonzero': sum(abs(x) > 1e-12 for x in dC)}
hol = holm([p1, p2, p3])

# ---- sensitivity: exclude behavioural non-commit continuations (prereg 7 sensitivity ii)
def tau_ex(c):
    f = [o for o, n_ in c['_NCO']['F'] if not n_]; k = [o for o, n_ in c['_NCO']['K'] if not n_]
    return sum(k)/len(k)-sum(f)/len(f)
dnc = [tau_ex(byw[w]['B1'])-tau_ex(byw[w]['B2']) for w in worlds]
noncommit = dict(delta_excl_noncommit=sum(dnc)/n, signflip_p=signflip(dnc)[0],
    boot95=boot([x for _, x in sorted(zip(map(str, worlds), dnc))]),
    noncommit_branches=sorted({(a, b, c_, tuple(d_), round(e, 3)) for c in cps.values() for (a, b, c_, d_, e) in c['_NC']}))
# ---- case-level: exact shift-permutation bounds (prereg 4.3 / protocol 8), grid 0.01 on [-60,60]
def shift_bounds(F, K, sign=1):
    """tau = sign*(mean K - mean F). returns (L, U): L=inf{m: p_ge(m)>.05}, U=sup{m: p_le(m)>.05}."""
    nF, nK = len(F), len(K); idx = range(nF+nK); combos = list(itertools.combinations(idx, nK))
    def pvals(m):
        # H0(m): K = F + m (in tau units; for sign=-1 tau=mean F - mean K so K = F - m)
        Kadj = [k - sign*m for k in K]; pool = list(F)+Kadj
        obs = sum(Kadj)/nK - sum(F)/nF; ge = le = 0
        for cb in combos:
            ks = set(cb); t = sum(pool[i] for i in ks)/nK - sum(pool[i] for i in idx if i not in ks)/nF
            ge += t >= obs-1e-9; le += t <= obs+1e-9
        return ge/len(combos), le/len(combos)
    grid = [i/100 for i in range(-6000, 6001)]
    if sign == 1:
        ok_lo = [m for m in grid if pvals(m)[0] > .05]; ok_hi = [m for m in grid if pvals(m)[1] > .05]
        return min(ok_lo), max(ok_hi)
    # sign=-1: tau = -(mean K - mean F) ; bounds are the negated bounds of the K-F contrast
    lo, hi = shift_bounds(F, K, 1); return -hi, -lo
case = {}
for cid, c in cps.items():
    O_, C_, W_ = c['_O'], c['_C'], c['_W']
    bO = shift_bounds(O_['F'], O_['K']); bC = shift_bounds(C_['F'], C_['K'], -1); bW = shift_bounds(W_['F'], W_['K'])
    m, dW = 2.5, 5.0
    cg = 'pass' if bC[0] > 0 else 'fail' if bC[1] <= 0 else 'ambiguous'
    wg = 'pass' if bW[0] >= -dW else 'fail' if bW[1] < -dW else 'ambiguous'
    ns = bO[1] < m
    st_ = 'not_supported' if ns else ('inconclusive:imprecise' if bO[0] <= m <= bO[1] else 'inconclusive:other')
    case[cid] = dict(tau_O_L=bO[0], tau_O_U=bO[1], tau_C_L=bC[0], tau_W_L=bW[0], C_gate=cg, W_gate=wg,
                     supported_possible_ignoring_info_and_placebo=bool(bO[0] > m and cg == 'pass' and wg == 'pass'), status_from_bounds=st_)
out_case = case

# ledger
rows = [json.loads(l) for l in open(LEDGER)]
e2 = [r for r in rows if str(r.get('run_id', '')).startswith('EXP-002/')]
led = dict(rows=len(e2), run_opens=sum(r['event'] == 'run_open' for r in e2), run_closes=sum(r['event'] == 'run_close' for r in e2),
    attempt_begin=sum(r['event'] == 'attempt_begin' for r in e2),
    attempt_end=sum(1 for r in e2 if 'api_cost_usd' in r),
    api_cost_usd=sum(r.get('api_cost_usd') or 0 for r in e2), out_of_pocket_usd=sum(r.get('new_out_of_pocket_usd') or 0 for r in e2),
    backends=sorted({r.get('backend') for r in e2 if r.get('backend')}), hosts=sorted({r.get('base_url_host') for r in e2 if r.get('base_url_host')}),
    models_requested=sorted({r.get('model_requested') for r in e2 if r.get('model_requested')}), models_resolved=sorted({str(r.get('model_resolved')) for r in e2 if 'model_resolved' in r}),
    end_status=dict(collections.Counter(r.get('status') for r in e2 if 'api_cost_usd' in r)),
    http_status=dict(collections.Counter(r.get('http_status') for r in e2 if 'api_cost_usd' in r)),
    errors=sum(1 for r in e2 if r.get('error')), max_calls=sorted({r['max_calls'] for r in e2 if r['event'] == 'run_open'}))

out = dict(
  Delta_total=delta, d_w=dict(zip(map(str, worlds), d)), signflip_one_sided_p=p_d, signflip_count=f'{k_d}/{t_d}',
  bootstrap95=ci, bootstrap95_numeric_world_order=ci_numeric, tau_O_B1_mean=sum(b1)/n, tau_O_B2_mean=sum(b2)/n,
  tau_O_B1=dict(zip(map(str, worlds), b1)), tau_O_B2=dict(zip(map(str, worlds), b2)),
  floors=floors, S=dict(p_raw=[p1, p2, p3], p_holm=hol, **nzS), prereg_decision=dict(boot_lower_gt_0=ci[0] > 0, signflip_p_le_05=p_d <= .05),
  accounting=dict(acct), not_run_reasons={'|'.join(k): v for k, v in notrun_reasons.items()},
  model_ids=sorted(models), ollama_digests=sorted(digests), ledger_exp002=led,
  noncommit_sensitivity=noncommit, case_level=out_case,
  placebo_available=[k for k, c in cps.items() if c['placebo'] != 'no_placebo_available'],
  sham_selected=[k for k, c in cps.items() if c['sham_selected']],
  per_checkpoint={k: {kk: vv for kk, vv in c.items() if kk != '_O'} for k, c in cps.items()},
  regime_structure={r: dict(senders=collections.Counter(c['sender'] for c in cps.values() if c['regime'] == r),
        t_star_mean=st.mean(c['t_star'] for c in cps.values() if c['regime'] == r),
        t_star_vals=sorted(c['t_star'] for c in cps.values() if c['regime'] == r)) for r in ('B1', 'B2')},
)
out['regime_structure'] = json.loads(json.dumps(out['regime_structure']))
js = json.dumps(out, indent=1, default=str)
Path(__file__).with_name('rev001_repro.json').write_text(js)
print(js)
