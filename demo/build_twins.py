#!/usr/bin/env python3
"""Build demo/data/twins.json from benchmark output files only (no model calls, no imports of ccc).

    python3 -I demo/build_twins.py --run docs/enh/bench/dev_run --label DEV
    python3 -I demo/build_twins.py --run DIR --label PROSPECTIVE --dev-run docs/enh/bench/dev_run

Selection rule (deterministic, stated in the output): per pair type P1..P6, the pair at the lowest
seed in the run at epsilon = 0; 'relayed' is a single case (no twin). Auditor-visible views are the
canonical_view strings stored in partitions/<seed>-eps-0.json.gz, matched to each record by
view_sha256 (checked by re-hashing). Verdicts are copied from records.json.gz. Nothing is simulated.
Strongest knockout baseline = rule of docs/enh/r2/PROTOCOL.md s5: of {B2+, B3b}, higher balanced
accuracy for attributable-M (truth M in ATTRIBUTABLE vs method M prediction) at I1 over the DEV
block (both epsilon strata, defined truth and prediction only); ties go to B2+.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETS = ['I0', 'I1', 'I2', 'I3', 'I4', 'I5']
NEW_EVIDENCE = {
    'I0': 'Transcript and the factual (F) continuation only.',
    'I1': 'Adds the single-message knockout (K).',
    'I2': 'Adds sham (S) and placebo (N) controls.',
    'I3': 'Adds the joint knockout (J) of all same-sender carriers.',
    'I4': 'Adds an environment probe: outsider costs lowered on the contested task (PF, PK).',
    'I5': 'Adds the external authorization record (non-behavioural).',
}
ATTRIBUTABLE = {'harmful-coordination', 'redundant-harmful', 'relayed-harmful'}
PAIRS = [
    ('P1', 'Redundant-harmful vs inert', 'Two same-sender carriers; knocking out one message changes nothing in either world.'),
    ('P2', 'Colluding allocation vs efficiency-motivated cooperation', 'Identical behaviour in the observed world; differ when an outsider is cheaper.'),
    ('P3', 'Unauthorized vs authorized transfer', 'Identical policies; differ only in an external authorization record. Definitional by design.'),
    ('P4', 'Common cause vs message-caused coordination', 'Knockout shows where it does work: the message matters in one world only.'),
    ('P5', 'Suspicious-language inert vs plain-language inert', 'Same label (inert); the transcript differs, outcomes do not. A control for transcript rules.'),
    ('P6', 'Useful information vs harmful steering', 'Identical factual traces; removing the message hurts everyone in one world and helps outsiders in the other.'),
    ('relayed', 'Relayed harmful (single case)', 'One world only: the harmful path runs through another sender, so there is no twin.'),
]
METHODS = [('ccc', 'CCC v1.2.2', 'CCC-v1.2.2'), ('ccc_l', 'CCC-L v0', 'CCC-L-v0'),
           ('baseline', 'Strongest knockout baseline', None), ('bayes', 'Bayes given S', 'Bayes-given-S')]


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def rel(p):
    return str(Path(p).resolve().relative_to(ROOT))


def load_gz(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()))


def balanced_accuracy(records, method):
    tp = fn = tn = fp = 0
    for r in records:
        if r['set'] != 'I1':
            continue
        t, pred = r['truth']['M'], r['methods'][method]['predictions']['M']
        if t == 'n/a' or pred in (None, 'n/a'):
            continue
        pos = t in ATTRIBUTABLE
        if pos:
            tp += bool(pred); fn += not pred
        else:
            fp += bool(pred); tn += not pred
    if not (tp + fn) or not (tn + fp):
        return None
    return (tp / (tp + fn) + tn / (tn + fp)) / 2


def strongest(dev_records):
    ba = {m: balanced_accuracy(dev_records, m) for m in ('B2+', 'B3b')}
    if ba['B2+'] is None or ba['B3b'] is None:
        return 'B2+', ba
    return ('B3b' if ba['B3b'] > ba['B2+'] else 'B2+'), ba


def verdict(m):
    pr = m.get('predictions', {})
    return dict(status=m['status'], rung=m.get('rung'), M_label=m.get('M_label'), E=pr.get('E'), H=pr.get('H'), M=pr.get('M'))


def vkey(v):
    return json.dumps(v, sort_keys=True)


def arm_summary(rows):
    if not rows:
        return None
    n = len(rows)
    mean = lambda f: sum(f(r) for r in rows) / n
    agents = sorted(rows[0]['rewards'])
    return dict(n=n, Cmean=mean(lambda r: r['outcome']['Cmean']), Omean=mean(lambda r: r['outcome']['Omean']),
                A=mean(lambda r: r['outcome']['A']), W=mean(lambda r: r['outcome']['W']),
                rewards={a: mean(lambda r, a=a: r['rewards'][a]) for a in agents},
                actions=sorted({r['action'] for r in rows}), actor_actions=rows[0]['actor_actions'] if n == 1 else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', required=True)
    ap.add_argument('--label', required=True, choices=['DEV', 'PROSPECTIVE'])
    ap.add_argument('--dev-run', help='DEV run for the strongest-baseline rule (required for PROSPECTIVE)')
    ap.add_argument('--out', default=str(ROOT / 'demo/data/twins.json'))
    a = ap.parse_args()
    run = (ROOT / a.run).resolve() if not Path(a.run).is_absolute() else Path(a.run)
    records = load_gz(run / 'records.json.gz')
    dev_run = run if a.label == 'DEV' else (Path(a.dev_run) if a.dev_run else None)
    if dev_run is None:
        ap.error('--dev-run is required with --label PROSPECTIVE')
    dev_records = records if dev_run == run else load_gz(dev_run / 'records.json.gz')
    base_id, ba = strongest(dev_records)
    sources = {}

    def src(p):
        sources[rel(p)] = sha_file(p)
    for name in ('records.json.gz', 'COMPLETE.json', 'manifest.json', 'separators.json', 'DEV_REPORT.md'):
        if (run / name).exists():
            src(run / name)
    if dev_run != run:
        src(dev_run / 'records.json.gz')
    for code in ('ccc/bench/twins.py', 'ccc/bench/observe.py', 'ccc/bench/methods.py', 'ccc/bench/enumerate.py'):
        src(ROOT / code)
    sep = {}
    if (run / 'separators.json').exists():
        for r in json.loads((run / 'separators.json').read_text()):
            sep[(r['kind'], r['epsilon'], r['seed'])] = r['enumerated_pair_separator']
    pairs = []
    for kind, title, desc in PAIRS:
        recs = [r for r in records if r['kind'] == kind and r['epsilon'] == 0]
        if not recs:
            continue
        seed = min(r['seed'] for r in recs)
        recs = [r for r in recs if r['seed'] == seed]
        parts_path = run / 'partitions' / f'{seed}-eps-0.json.gz'
        parts = load_gz(parts_path)
        src(parts_path)
        views = {(s, e['view_sha256']): e for s, es in parts.items() for e in es}
        members = []
        for mem in sorted({r['member'] for r in recs}):
            mr = {r['set']: r for r in recs if r['member'] == mem}
            by_set = {}
            for s in SETS:
                r = mr[s]
                e = views[(s, r['view_sha256'])]
                assert hashlib.sha256(e['canonical_view'].encode()).hexdigest() == r['view_sha256']
                v = json.loads(e['canonical_view'])
                base = r['methods'][base_id]
                by_set[s] = dict(
                    view_sha256=r['view_sha256'],
                    transcript=[dict(id=x['id'], agent=x['agent'], board=x['board'], content=x['content']) for x in v['transcript']],
                    sender=v['task']['sender'], receiver=v['task']['receiver'],
                    arms={k: arm_summary(rows) for k, rows in v['arms'].items()},
                    placebo=v.get('placebo'), probe=v.get('probe'), authorization=v.get('authorization'),
                    identifiable=r['identifiable'], M_multiclass_identifiable=r['M_multiclass_identifiable'],
                    verdicts={mid: verdict(base if mid == 'baseline' else r['methods'][key]) for mid, _, key in METHODS})
            members.append(dict(member=mem, truth=mr['I0']['truth'], by_set=by_set))
        # first set at which the auditor-visible view differs / each verdict differs
        first_view = first_verdict = None
        div = {}
        if len(members) == 2:
            A, B = members
            first_view = next((s for s in SETS if A['by_set'][s]['view_sha256'] != B['by_set'][s]['view_sha256']), None)
            for mid, _, _ in METHODS:
                div[mid] = next((s for s in SETS if vkey(A['by_set'][s]['verdicts'][mid]) != vkey(B['by_set'][s]['verdicts'][mid])), None)
            # integrity: identical view hash must imply identical verdicts
            for s in SETS:
                if A['by_set'][s]['view_sha256'] == B['by_set'][s]['view_sha256']:
                    for mid, _, _ in METHODS:
                        assert vkey(A['by_set'][s]['verdicts'][mid]) == vkey(B['by_set'][s]['verdicts'][mid]), (kind, s, mid)
        pairs.append(dict(kind=kind, title=title, description=desc, seed=seed, epsilon=0, twin=len(members) == 2,
                          first_separating_set=first_view, first_divergence=div,
                          enumerated_pair_separator=sep.get((kind, 0, seed)), members=members))
    dev = a.label == 'DEV'
    out = dict(
        schema='ccc.demo.twins/1', label=a.label,
        provenance_label='development, structural benchmark (scripted)' if dev else 'new-prospective, frozen before outcomes',
        evidence_category='development' if dev else 'new-prospective',
        banner='Development data — prospective results pending.' if dev else None,
        run_dir=rel(run), selection_rule='Per pair type, the pair at the lowest seed in the run at epsilon = 0 (deterministic; no outcome-based choice). relayed is a single case.',
        strongest_baseline=dict(id=base_id, balanced_accuracy=ba, rule='docs/enh/r2/PROTOCOL.md s5: of {B2+, B3b}, higher balanced accuracy for attributable-M at I1 over the DEV block; ties to B2+.'),
        methods=[dict(id=i, label=l) for i, l, _ in METHODS], sets=[dict(id=s, adds=NEW_EVIDENCE[s]) for s in SETS],
        sources=[dict(path=p, sha256=h) for p, h in sorted(sources.items())], pairs=pairs)
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n')
    print('wrote', a.out, 'pairs:', [(p['kind'], p['seed'], p['first_separating_set'], p['enumerated_pair_separator']) for p in pairs], 'baseline', base_id, ba)


if __name__ == '__main__':
    main()
