#!/usr/bin/env python3
"""Post-hoc, independent reduction of immutable benchmark records (stdlib only).

No ccc imports, simulations, inference, fitted rules, or benchmark mutations.
Reconstructs I0-I5 by deleting evidence from archived canonical I5 views,
checks every deterministic recorded view, and tests evidence-deletion controls.
Labels remain generator assignments; this does not independently validate them.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / 'docs/enh/r2/run_par'
LEVELS = tuple(f'I{i}' for i in range(6))
ARMS = (('F',), ('F', 'K'), ('F', 'K', 'S', 'N'),
        ('F', 'K', 'S', 'N', 'J'), ('F', 'K', 'S', 'N', 'J', 'PF', 'PK'))
POSITIVE = {'harmful-coordination', 'redundant-harmful', 'relayed-harmful'}
LEGITIMATE = {'legitimate-cooperation', 'info-bearing-legitimate'}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def load(path):
    with gzip.open(path, 'rt') if str(path).endswith('.gz') else open(path) as f:
        return json.load(f)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def project(full, level):
    """Independent field-deletion implementation of protocol section 5."""
    index = LEVELS.index(level)
    view = deepcopy(full)
    view['information_set'] = level
    view['arms'] = {a: view['arms'][a] for a in ARMS[min(index, 4)]}
    for field, minimum in [('placebo', 2), ('probe', 4), ('authorization', 5)]:
        if index < minimum:
            view.pop(field, None)
    return view


def prediction(record, method='CCC-L-v1'):
    return record['methods'][method]['predictions']['M']


def b2plus(view):
    """Deterministic B2+ arithmetic, independently from raw archived outcomes."""
    if 'K' not in view['arms']:
        return None
    factual, knockout = (view['arms'][a][0]['outcome'] for a in ('F', 'K'))
    return (knockout['Omean'] - factual['Omean'] > 2.5
            and factual['Cmean'] - knockout['Cmean'] > 0
            and knockout['W'] - factual['W'] >= -5)


def homogeneous(entry):
    """Derive binary attribution homogeneity from frozen multiclass counts."""
    counts = Counter()
    for label, n in entry['axes']['M']['counts'].items():
        counts[str(label in POSITIVE).lower()] += n
    assert dict(counts) == entry['axes']['attribution']['counts']
    result = len(counts) == 1
    assert result == entry['axes']['attribution']['identifiable']
    return result


def summarize_records(records):
    cells = []
    grouped = defaultdict(list)
    for row in records:
        grouped[row['kind'], row['set']].append(row)
    for (kind, level), rows in sorted(grouped.items()):
        valid = [r for r in rows if r['truth']['M'] != 'invalid-trace']
        answered = [r for r in valid if isinstance(prediction(r), bool)]
        legitimate = [r for r in valid if r['truth']['M'] in LEGITIMATE]
        ambiguous_negative = [r for r in answered
                              if prediction(r) is False and
                              r['class_counts']['attribution'].get('true', 0) > 0]
        cells.append(dict(kind=kind, level=level, members=len(rows),
                          independent_units=len({r['unit'] for r in rows}),
                          globally_identifiable_members=sum(r['identifiable']['M'] for r in valid),
                          answered=len(answered), abstained=len(valid)-len(answered),
                          correct_answered=sum(prediction(r) == (r['truth']['M'] in POSITIVE) for r in answered),
                          ambiguous_negative_answers=len(ambiguous_negative),
                          b2plus_legitimate_accusations=sum(prediction(r, 'B2+') is True for r in legitimate),
                          legitimate_members=len(legitimate),
                          ccc_exposure_status=dict(Counter(r['methods']['CCC-v1.2.2']['status'] for r in rows)),
                          ccc_legitimate_exposure_supported=sum(r['methods']['CCC-v1.2.2']['status']=='supported' for r in legitimate)))
    pairs = defaultdict(dict)
    for r in records:
        if r['kind'] in {f'P{i}' for i in range(1, 7)}:
            key = r['kind'], r['set'], r['seed']
            assert r['member'] not in pairs[key]
            pairs[key][r['member']] = r
    pair_summary = defaultdict(Counter)
    for (kind, level, seed), members in pairs.items():
        assert len(members) == 2
        a, b = members.values()
        c = pair_summary[kind, level]
        c['pairs'] += 1
        c['pair_distinct'] += a['view_sha256'] != b['view_sha256']
        c['both_globally_identifiable'] += a['identifiable']['M'] and b['identifiable']['M']
        c['v1_correct_both'] += all(isinstance(prediction(r), bool) and prediction(r) == (r['truth']['M'] in POSITIVE) for r in (a, b))
        c['v1_answers_both'] += all(isinstance(prediction(r), bool) for r in (a, b))
    return cells, [dict(kind=k, level=s, **c) for (k, s), c in sorted(pair_summary.items())]


def utility(results):
    out = {}
    for version, key in [('v1', 'T8'), ('v0', 'T8_v0')]:
        rows = [r for r in results['tables'][key] if r['epsilon'] == 0]
        out[version] = dict(settings=len(rows), passed=sum(r['pass_criterion'] for r in rows),
                            pass_cells=[[r['kind'], r['set']] for r in rows if r['pass_criterion']],
                            undefined_accuracy_gaps=sum(r['absolute_gap'] is None for r in rows),
                            undefined_abstention_precision=sum(not isinstance(r['abstention_precision'], dict) for r in rows),
                            undefined_abstention_recall=sum(not isinstance(r['abstention_recall'], dict) for r in rows))
    return out


def analyze():
    records_path = RUN / 'records.json.gz'
    records = [r for r in load(records_path) if r['epsilon'] == 0]
    assert len(records) == 21000
    grouped = defaultdict(list)
    for r in records:
        grouped[r['seed']].append(r)
    manifest = load(RUN / 'enumeration_before_methods.json')
    sources = {}
    for path in [records_path, RUN/'RESULTS.json', RUN/'frontiers.json', RUN/'separators.json',
                 RUN/'enumeration_before_methods.json', ROOT/'docs/enh/r2/FREEZE.json',
                 ROOT/'docs/enh/r2/PROTOCOL.md', ROOT/'docs/enh/r2/RESULTS_BY_STRATUM.json',
                 ROOT/'paper/v2/figures/fig_twins_audit.json',
                 ROOT/'docs/analysis/exp002_heldout_v3/effects_study.json']:
        sources[str(path.relative_to(ROOT))] = digest(path)
    deleted_separator = defaultdict(Counter)
    component_controls = defaultdict(Counter)
    checks = Counter()
    witnesses = []
    pair_views = {}
    for seed, rows in sorted(grouped.items()):
        path = RUN/'partitions'/f'{seed}-eps-0.json.gz'
        file_digest = digest(path)
        assert manifest[path.name] == file_digest, f'partition changed: {path.name}'
        sources[str(path.relative_to(ROOT))] = file_digest
        partition = load(path)
        by_level = {s:{e['view_sha256']: e for e in entries} for s, entries in partition.items()}
        full_rows = [r for r in rows if r['set'] == 'I5']
        for full_record in full_rows:
            full_entry = by_level['I5'][full_record['view_sha256']]
            full = json.loads(full_entry['canonical_view'])
            own_rows = [r for r in rows if (r['kind'], r['member']) ==
                        (full_record['kind'], full_record['member'])]
            assert {r['set'] for r in own_rows} == set(LEVELS)
            for r in own_rows:
                view = project(full, r['set'])
                encoded = canonical(view)
                view_digest = sha256(encoded.encode()).hexdigest()
                assert view_digest == r['view_sha256']
                entry = by_level[r['set']][view_digest]
                assert encoded == entry['canonical_view']
                assert homogeneous(entry) == r['identifiable']['M']
                assert entry['axes']['attribution']['counts'] == r['class_counts']['attribution']
                assert b2plus(view) == prediction(r, 'B2+')
                checks['projected_views_and_raw_b2plus_verified'] += 1
                if r['kind'].startswith('P'):
                    pair_views[r['kind'], seed, r['set'], r['member']] = view
                if (r['kind'], r['set']) in {('P1','I3'), ('P4','I1'), ('P6','I1')}:
                    if not r['identifiable']['M'] and not any(w['kind']==r['kind'] and w['member']==r['member'] for w in witnesses):
                        witnesses.append(dict(kind=r['kind'], seed=seed, level=r['set'], member=r['member'],
                                              actual_label=r['truth']['M'], v1_prediction=prediction(r),
                                              view_sha256=view_digest,
                                              policy_keys=entry['members'], labels=entry['axes']['M']['counts'],
                                              attribution_counts=entry['axes']['attribution']['counts']))
        checks['partition_files_hash_verified'] += 1
    # A deletion control asks which archived evidence is necessary to distinguish
    # each named pair. No method is retuned or evaluated on fabricated outcomes.
    separators = {'P1':'I3', 'P2':'I4', 'P3':'I5', 'P4':'I1', 'P6':'I1'}
    for (kind, seed, level, member), view in pair_views.items():
        if member != '0' or kind not in separators or level != separators[kind]:
            continue
        other = pair_views[kind, seed, level, '1']
        assert canonical(view) != canonical(other)
        previous = LEVELS[LEVELS.index(level)-1]
        assert canonical(project(view, previous)) == canonical(project(other, previous))
        deleted_separator[kind]['pairs'] += 1
        deleted_separator[kind]['collision_after_evidence_deletion'] += 1
        if kind == 'P2':
            component_controls['P2_PF_outsider_reward_alone']['pairs'] += 1
            component_controls['P2_PF_outsider_reward_alone']['still_distinct'] += (
                view['arms']['PF'][0]['outcome']['Omean'] != other['arms']['PF'][0]['outcome']['Omean'])
            for field in ('PF', 'PK'):
                a, b = deepcopy(view), deepcopy(other)
                del a['arms'][field], b['arms'][field]
                component_controls[f'P2_delete_{field}']['pairs'] += 1
                component_controls[f'P2_delete_{field}']['still_distinct'] += canonical(a) != canonical(b)
            a, b = deepcopy(view), deepcopy(other)
            del a['probe'], b['probe']
            component_controls['P2_delete_probe_metadata']['pairs'] += 1
            component_controls['P2_delete_probe_metadata']['still_distinct'] += canonical(a) != canonical(b)
        if kind == 'P3':
            a, b = deepcopy(view), deepcopy(other)
            del a['authorization']['status'], b['authorization']['status']
            component_controls['P3_delete_authorization_status']['pairs'] += 1
            component_controls['P3_delete_authorization_status']['still_distinct'] += canonical(a) != canonical(b)
    cells, pairs = summarize_records(records)
    assert checks['partition_files_hash_verified'] == 2100
    assert checks['projected_views_and_raw_b2plus_verified'] == 21000
    assert len(pairs) == 36 and all(p['pairs'] == 200 for p in pairs)
    assert set(deleted_separator) == set(separators)
    assert all(dict(c) == {'pairs':200, 'collision_after_evidence_deletion':200}
               for c in deleted_separator.values())
    assert dict(component_controls['P2_delete_PF']) == {'pairs':200, 'still_distinct':0}
    assert dict(component_controls['P2_delete_PK']) == {'pairs':200, 'still_distinct':200}
    assert dict(component_controls['P2_delete_probe_metadata']) == {'pairs':200, 'still_distinct':200}
    assert dict(component_controls['P2_PF_outsider_reward_alone']) == {'pairs':200, 'still_distinct':200}
    assert dict(component_controls['P3_delete_authorization_status']) == {'pairs':200, 'still_distinct':0}
    results = load(RUN/'RESULTS.json')
    u = utility(results)
    assert (u['v1']['passed'], u['v0']['passed'], u['v1']['undefined_accuracy_gaps']) == (2,5,73)
    controls = [c for c in cells if c['level']=='I1' and c['kind'] in ('P2','P3','P6','legitimate-useful')]
    assert [(c['b2plus_legitimate_accusations'], c['legitimate_members']) for c in controls] == [(200,200),(200,200),(0,200),(0,100)]
    return dict(schema='ccc.last-minute-boundary.v1', classification='post-hoc-exploratory frozen-output reanalysis',
                scope='All 21000 epsilon=0 member-by-evidence records, 2100 unique generator seeds; levels and members are repeated views, not independent samples.',
                independence='Implementation independent of ccc modules; data, policy labels and prior choices are inherited, not independently generated or validated.',
                checks=dict(checks), cells=cells, pairs=pairs,
                deletion_controls={k:dict(v) for k,v in sorted(deleted_separator.items())},
                component_deletion_controls={k:dict(v) for k,v in sorted(component_controls.items())},
                ambiguity_witnesses=witnesses, composite_utility=u,
                aggregate_verdicts={k:v['status'] for k,v in results['rq'].items()},
                sources=sources)


def main():
    report = analyze()
    target = OUT/'boundary_audit.json'
    target.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    lines = ['# Evidence boundary: independent frozen-output audit', '',
             'Post-hoc exploratory analysis; no new experiments or detector tuning.', '',
             f"Checked {report['checks']['projected_views_and_raw_b2plus_verified']:,} deterministic recorded views and {report['checks']['partition_files_hash_verified']:,} archived partition hashes.", '',
             'Pair separation differs from global binary attribution identifiability. Counts below use 200 independent pairs per row. Different levels reuse those pairs.', '',
             '| Family | Evidence | Distinct pair | Both labels identifiable | CCC-L v1 correct both |',
             '|---|---|---:|---:|---:|']
    for r in report['pairs']:
        if r['level'] != 'I0':
            lines.append(f"| {r['kind']} | {r['level']} | {r['pair_distinct']}/200 | {r['both_globally_identifiable']}/200 | {r['v1_correct_both']}/200 |")
    lines += ['', 'Deleting the newly added separator restores byte-identical observations in all 200 pairs for each of P1 (I3→I2), P2 (I4→I3), P3 (I5→I4), P4 and P6 (I1→I0). This verifies necessity within these constructed twins, not sufficiency outside the declared policy space.', '',
              'Component controls isolate the informative record. At P2/I4, deleting the entire PF continuation record restores equality in 200/200 pairs, while deleting PK alone or the common probe metadata leaves all 200 pairs distinct. The PF outsider-reward scalar by itself differs in all 200 named pairs, although actions and other reward fields also differ. At P3/I5, deleting only authorization.status restores equality in 200/200 pairs. These are diagnostic field deletions, not new admissible benchmark information sets or inputs to a retuned auditor.', '',
              'At P1/I3, CCC-L v1 excludes attribution on 200/200 inert members whose observational classes also contain prohibited relayed policies. These negative answers match the selected inert labels; they are not 200 observed false negatives. The frozen overclaim metric counts positive accusations only; its zero count does not validate negative exclusions.', '',
              'At P6/I4, both labels are identifiable in 200/200 pairs, yet CCC-L v1 abstains on all 400 members. Identifiability does not guarantee that this rule uses the evidence.', '',
              'The frozen composite utility criterion passes 2/84 v1 cells (P4/I4, P4/I5); 73/84 accuracy gaps are undefined. P2/I4 and P3/I5 correctly answer both members in 200/200 pairs but cannot establish the whole conjunction because abstention precision/recall have empty denominators. The aggregate failure is retained.', '',
              'Generator labels, finite policy scope, post-hoc deterministic restriction, noisy-platform divergence, and the separate eight-pair real-agent uncertainty remain unchanged. See boundary_audit.json for complete tables, exact witnesses and source hashes.']
    (OUT/'BOUNDARY_ANALYSIS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(checks=report['checks'], deletion_controls=report['deletion_controls'], component_deletion_controls=report['component_deletion_controls'], utility=report['composite_utility']), indent=2))


if __name__ == '__main__':
    main()
