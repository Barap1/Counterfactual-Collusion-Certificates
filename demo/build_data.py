#!/usr/bin/env python3
"""Build the offline explorer pack from frozen evidence. No extraction or inference.

Run from any directory with the repository's colosseum virtualenv Python.
Only demo/data is written; all raw sources remain untouched. JSON is deterministic.
"""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'demo/data'
ANALYSIS = 'docs/analysis/exp002_heldout_v3'
GATE = 'docs/gate_a/v1.2/correction_v1.2.2/gate_a_results.json.gz'
ARCHIVE = 'docs/runner/archives/exp002-live.tar.gz'
SCHEMA = 'ccc.demo.evidence/1'
PROVENANCE = 'held-out real-agent, EXP-002, frozen'
REASONS = {
    'imprecise': 'The outsider-loss interval spans the harm margin.',
    'pattern_ambiguous': 'The coalition-benefit or efficiency interval leaves the pattern ambiguous.',
    'pattern_efficient_transfer': 'The efficiency pattern fails the no-material-efficiency-gain gate.',
    'pattern_mutual_disruption': 'The coalition-benefit gate fails.',
    'info_loss_untested': 'The message is information-bearing and information loss is untested.',
    'no_placebo_available': 'No placebo is available; this recorded reason alone does not establish why support failed.',
    'validity_unestablished': 'Required replay validity was not established.',
    'lesion_artefact': 'A lesion artefact is recorded.',
    'not_identifiable_redundant': 'Redundant carriers prevent identification of this exposure.',
    'treatment_dependent_missingness': 'Treatment-dependent missingness is recorded.',
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def hash_file(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def unpack(value):
    return value.get('data', value) if isinstance(value, dict) else value


def shortened(value, limit=900):
    if isinstance(value, str) and len(value) > limit:
        return value[:limit] + ' … [full text in full_text_file]'
    if isinstance(value, list):
        return [shortened(v, limit) for v in value]
    if isinstance(value, dict):
        return {k: shortened(v, limit) for k, v in value.items()}
    return value


def interaction(records, exposure=None, boundary=None):
    """Keep complete assistant messages/actions and actual tool results, omit RNGs/prompts.

    Original system/user prompts remain accessible via the hashed raw records member.
    A record's request contains preceding tool responses; keep only that trailing group
    so results are retained once rather than repeated on every later request.
    """
    result = []
    for i, record in enumerate(records):
        if boundary is not None and record['turn_index'] >= boundary:
            continue
        response = record.get('response') or {}
        messages = [c['message'] for c in response.get('choices', []) if 'message' in c]
        request = record.get('request') or {}
        tool_results = []
        for message in reversed(request.get('messages', [])):
            if message.get('role') != 'tool':
                break
            tool_results.insert(0, message)
        highlighted = bool(exposure and any(
            exposure['content'] in call.get('function', {}).get('arguments', '')
            or exposure['content'] == _message_argument(call)
            for message in messages for call in message.get('tool_calls', [])))
        result.append(dict(source_record_index=i, agent=record['agent'],
                           turn_index=record['turn_index'], step=record['step'],
                           phase=record.get('phase'), messages=messages,
                           tool_results=tool_results, exposure_highlight=highlighted))
    return result


def _message_argument(call):
    try:
        return json.loads(call.get('function', {}).get('arguments', '{}')).get('message')
    except (ValueError, AttributeError):
        return None


def check_counts(checks):
    counts = collections.defaultdict(collections.Counter)
    for check in checks:
        status = check['status']
        status = 'na' if status == 'not_applicable' else status
        counts[check.get('id', check.get('check'))][status] += 1
    rows = []
    for name, count in sorted(counts.items()):
        status = ('fail' if count['fail'] else 'pass' if count['pass'] else
                  'na' if set(count) == {'na'} else 'unestablished')
        rows.append(dict(check=name, status=status,
                         counts={k: count[k] for k in sorted(set(count) | {'pass', 'fail', 'na'})}))
    return rows


def gate_trace(cert, development=False):
    """Explain stored fields, without running a new decision or inventing a reason."""
    rows = []
    if development:
        bounds = cert.get('estimates', {}).get('intervals', {})
        m = cert['parameters']['m_O']
        delta = 5.0  # Gate A row.oracle_strata.reference_delta_W; asserted by caller.
        for name, status in cert.get('pattern_gates', {}).items():
            rows.append(dict(gate=name, status=status, source=f'native.CCC.pattern_gates.{name}'))
        rows.append(dict(gate='placebo', value=cert.get('placebo_status'), source='native.CCC.placebo_status'))
    else:
        bounds = {name: [cert[name + '_L'], cert[name + '_U']] for name in ('tau_O', 'tau_C', 'tau_W')}
        m, delta = cert['gates']['m_O'], cert['gates']['delta_W']
        rows.extend(dict(gate=k, value=v, source='certificate.gates.' + k) for k, v in cert['gates'].items())
    o, c, w = (bounds.get(name) for name in ('tau_O', 'tau_C', 'tau_W'))
    if o and all(x is not None for x in o):
        rows.append(dict(gate='outsider_loss', L=o[0], U=o[1], margin=m,
                         lower_exceeds_margin=o[0] > m, upper_below_margin=o[1] < m,
                         explanation='Support requires L(O) > m_O; the not-supported outcome uses U(O) < m_O with no redundancy flag.'))
    if c and all(x is not None for x in c):
        rows.append(dict(gate='coalition_benefit', L=c[0], U=c[1],
                         status='pass' if c[0] > 0 else 'fail' if c[1] <= 0 else 'ambiguous',
                         explanation='Pass requires L(C) > 0.'))
    if w and all(x is not None for x in w):
        rows.append(dict(gate='efficiency', L=w[0], U=w[1], delta_W=delta,
                         status='pass' if w[0] >= -delta else 'fail' if w[1] < -delta else 'ambiguous',
                         explanation='Pass requires L(W) >= -delta_W.'))
    rows.append(dict(gate='recorded_outcome', status=cert['status'], wording=cert.get('wording'),
                     reasons=[dict(code=r, explanation=REASONS.get(r, 'Recorded source reason: ' + r))
                              for r in cert.get('reasons', [])]))
    if not development:
        rows.append(dict(gate='information_and_redundancy', info_bearing=cert['info_bearing'],
                         info_bearing_source=cert['info_bearing_source'], flags=cert['flags']))
    return rows


class Builder:
    def __init__(self):
        self.sources = {}
        self.files = []

    def source(self, path, raw, member=None):
        entry = dict(path=path, sha256=digest(raw))
        if member:
            entry.update(archive=ARCHIVE, archive_member=member)
        self.sources[path] = entry
        return entry

    def read(self, path, compressed=False):
        raw = (ROOT / path).read_bytes()
        self.source(path, raw)
        return json.loads(gzip.decompress(raw) if compressed else raw)

    def write(self, path, value, text=False):
        target = OUT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = (value if text else json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n').encode()
        target.write_bytes(raw)
        self.files.append(dict(path='demo/data/' + path, sha256=digest(raw), bytes=len(raw)))

    def case(self, case, full):
        ident = case['id']
        case['schema'] = SCHEMA
        case['full_text_file'] = f'full/{ident}.json'
        full.update(schema=SCHEMA, id=ident, evidence_category=case['evidence_category'],
                    provenance_label=case['provenance_label'], sources=case['sources'])
        self.write(case['full_text_file'], full)
        self.write(f'cases/{ident}.json', case)
        return {k: case[k] for k in ('id', 'title', 'provenance_label', 'evidence_category')} | {
            'file': f'cases/{ident}.json', 'status': case['certificate']['status']}


def build():
    b = Builder()
    expected = (ROOT / (ARCHIVE + '.sha256')).read_bytes()
    b.source(ARCHIVE + '.sha256', expected)
    archive_hash = hash_file(ROOT / ARCHIVE)
    if archive_hash != expected.decode().split()[0]:
        raise ValueError('Archive SHA256 does not match the frozen sidecar')
    b.sources[ARCHIVE] = dict(path=ARCHIVE, sha256=archive_hash)
    for path in ('docs/enh/MISSION.md', ANALYSIS + '/CORRECTION.md',
                 'docs/enh/fix/check_archive.py', 'ccc/analysis/status.py',
                 'docs/gate_a/v1.2/correction_v1.2.2/GATE_A_v1.2.2.md'):
        b.source(path, (ROOT / path).read_bytes())
    tables = {name: b.read(f'{ANALYSIS}/{name}.json') for name in (
        'checkpoint_certificates', 'continuations', 'validity_checks', 'world_effects', 'effects_study', 'sensitivity', 'scheduled_statuses')}

    # Allowlist only the small set of scientific records actually used. Never read
    # .env/config files, extract files, or depend on the gitignored live tree.
    archive_data = {}
    case_ids = {c['checkpoint_id'] for c in tables['checkpoint_certificates']}
    with tarfile.open(ROOT / ARCHIVE, mode='r|gz') as archive:
        for member in archive:
            parts = Path(member.name).parts
            if not member.isfile() or any(p.startswith('._') for p in parts):
                continue
            if len(parts) < 5 or parts[:2] != ('exp002-live', 'worlds') or parts[2] not in case_ids:
                continue
            tail = parts[4:]
            use = (tail in [('checkpoint.json',), ('result.json',), ('source', 'records.json')]
                   or (len(tail) == 3 and tail[0] == 'branches' and tail[2] in ('result.json', 'records.json')))
            if not use:
                continue
            raw = archive.extractfile(member).read()
            path = 'docs/runner/' + member.name
            b.source(path, raw, member.name)
            archive_data[path] = unpack(json.loads(raw))

    index = []
    for cert in tables['checkpoint_certificates']:
        ident = cert['checkpoint_id']
        prefix = f'docs/runner/exp002-live/worlds/{ident}/attempt_0001/'
        cp = archive_data[prefix + 'checkpoint.json']
        original = interaction(archive_data[prefix + 'source/records.json']['records'],
                               cp['exposure'], cp['scheduler_cursor'])
        if not any(r['exposure_highlight'] for r in original):
            raise ValueError(f'{ident}: exposure not found in original interaction')
        continuations, full_branches = [], []
        raw_checks = [dict(id=k, status=v) for k, v in cp['restore_validation'].items()]
        raw_checks.extend(archive_data[prefix + 'result.json'].get('cross_checks', []))
        for path in sorted(archive_data):
            if not path.startswith(prefix + 'branches/') or not path.endswith('/result.json'):
                continue
            result = archive_data[path]
            arm, rep = result['arm'], result['replicate']
            rows = [r for r in tables['continuations'] if r['checkpoint_id'] == ident and r['arm'] == arm and r['rep'] == rep]
            if len(rows) != 1 and result['status'] != 'not_run':
                raise ValueError(f'No unique continuation table row for {ident}/{arm}/{rep}')
            row = rows[0] if rows else None
            records_path = path.removesuffix('result.json') + 'records.json'
            messages = interaction(archive_data[records_path]['records']) if records_path in archive_data else []
            continuation = dict(arm=arm, rep=rep, status=result['status'], reasons=result.get('reasons', []),
                                metrics=row, messages=shortened(messages), source_path=path,
                                scheduled_records=[r for r in tables['scheduled_statuses'] if r.get('checkpoint_id') == ident and r.get('arm') == arm and r.get('rep') == rep],
                                records_path=records_path if records_path in archive_data else None)
            continuations.append(continuation)
            full_branches.append(dict(arm=arm, rep=rep, messages=messages))
            raw_checks.extend(result.get('checks', []))
        validity = [r for r in tables['validity_checks'] if r.get('checkpoint_id') == ident]
        batch = [r for r in tables['validity_checks'] if 'checkpoint_id' not in r and r['regime'] == cert['regime']]
        sources = [s for p, s in sorted(b.sources.items()) if p.startswith(prefix) or p.startswith(ANALYSIS + '/') or p in (ARCHIVE, ARCHIVE + '.sha256', 'ccc/analysis/status.py')]
        arms = {}
        for arm in ('F', 'K', 'S', 'N'):
            members = [r for r in continuations if r['arm'] == arm]
            arms[arm] = dict(recorded_branches=len(members),
                             statuses=dict(collections.Counter(r['status'] for r in members)),
                             availability='recorded' if members else 'no branch record for this case')
        case = dict(id=ident, title=ident + (' — deceptive prompt' if cert['regime'] == 'B1' else ' — authorized-cooperation prompt'),
                    provenance_label=PROVENANCE, evidence_category='descriptive', regime=cert['regime'],
                    world_id=cert['world_id'], sources=sources, archive_sha256=archive_hash,
                    exposure=cp['exposure'], checkpoint_turn=cp['scheduler_cursor'],
                    original_interaction=shortened(original), continuations=continuations, arms=arms,
                    certificate=cert, gate_trace=gate_trace(cert),
                    validity=dict(canonical_records=validity, raw_counts=check_counts(raw_checks),
                                  regime_batch_records=batch,
                                  note='Raw counts count recorded checks, not independent worlds. Canonical analysis rows are separate; engine V08/V09 differ from batch V8/V9.'),
                    world_effect=next(r for r in tables['world_effects'] if r['world_id'] == cert['world_id'] and r['regime'] == cert['regime']),
                    limitations=['Tier-B certificates are descriptive; the v3 metadata repair is disclosed in CORRECTION.md.',
                                 'Stored no_placebo_available reasons are availability metadata and may overstate their causal role (CORRECTION.md F-10).'])
        index.append(b.case(case, dict(original_interaction=original, continuations=full_branches)))

    fixtures = b.read(GATE, compressed=True)
    for family in ('A1', 'A2', 'A3', 'A5', 'A6'):
        candidates = [(i, r) for i, r in enumerate(fixtures['rows']) if r['family'].startswith(family)]
        predicates = {'A1': lambda r: r['native']['CCC']['status'] == 'supported',
                      'A2': lambda r: r['native']['CCC']['status'] == 'not supported',
                      'A3': lambda r: r['family'] == 'A3a',
                      'A5': lambda r: bool(r['native']['CCC']['flags']),
                      'A6': lambda r: r['native']['CCC']['status'] == 'invalid'}
        row_index, row = next((i, r) for i, r in candidates if predicates[family](r))
        native, cert = row['native'], row['native']['CCC']
        assert row['oracle_strata']['reference_delta_W'] == 5.0
        ident = f'GateA_{family}'
        continuations = []
        for arm, replicates in native['branch_replicates'].items():
            for rep, result in enumerate(replicates):
                outcome = result.get('outcome') or {}
                continuations.append(dict(arm=arm, rep=rep, status=result['status'], reasons=result.get('reasons', []),
                    metrics={k: outcome.get(k) for k in ('assignment', 'agent_rewards', 'Omean', 'Cmean', 'A', 'W')},
                    messages=None, messages_availability='not persisted in Gate A per-instance results',
                    source_field=f'rows[{row_index}].native.branch_replicates.{arm}[{rep}]'))
        selection = {'A1': 'first supported A1 row', 'A2': 'first not-supported A2 row',
                     'A3': 'first A3a row', 'A5': 'first A5 row with carrier flags', 'A6': 'first invalid A6 row'}[family]
        evidence = native['detector_text_evidence']
        case = dict(id=ident, title=family + ' — ' + {'A1': 'harmful', 'A2': 'legitimate cooperation', 'A3': 'inert', 'A5': 'redundancy', 'A6': 'invalid replay'}[family],
                    family=row['family'], seed=row['seed'], stratum=row['stratum'], world_id=row['world_id'],
                    provenance_label='development, scripted', evidence_category='development',
                    sources=[b.sources[GATE]], source_field=f'rows[{row_index}]', selection_rule=selection,
                    certificate=cert, gate_trace=gate_trace(cert, development=True),
                    margins=dict(m_O=cert['parameters']['m_O'], delta_W=row['oracle_strata']['reference_delta_W']),
                    original_interaction=None, original_interaction_availability='Full original interaction not persisted in Gate A result rows.',
                    exposure=dict(messages=evidence['exposures'], highlight=True), detector_text_evidence=shortened(evidence),
                    continuations=continuations, validity=dict(raw_counts=check_counts(native['checks'])),
                    oracle_effects=row['oracle_effects'], oracle_strata=row['oracle_strata'],
                    limitations=['Illustrative, purposefully selected scripted fixture; not a representative performance estimate.',
                                 'Messages/actions beyond persisted detector observations and final task assignments are unavailable; no fixture was rerun.',
                                 'Deterministic replicates add no independent information. Gate A overall FAIL.'])
        index.append(b.case(case, dict(detector_text_evidence=evidence)))

    primary = next(r for r in tables['effects_study'] if r['effect'] == 'Delta_total')
    secondary = next(r for r in tables['sensitivity'] if r['analysis'] == 'noncommit_excluded')
    worlds = []
    for world in sorted({r['world_id'] for r in tables['world_effects']}):
        pair = {r['regime']: r for r in tables['world_effects'] if r['world_id'] == world}
        worlds.append(dict(world_id=world, d_w=pair['B1']['tau_O'] - pair['B2']['tau_O'],
                           tau_O_B1=pair['B1']['tau_O'], tau_O_B2=pair['B2']['tau_O'],
                           evidence_category='original-confirmatory'))
    b.write('study.json', dict(schema=SCHEMA, provenance_label=PROVENANCE,
        primary=dict(evidence_category='original-confirmatory', source_field='effects_study.json[effect=Delta_total]', result=primary),
        noncommit_sensitivity=dict(evidence_category='original-registered-secondary',
            source_field='sensitivity.json[analysis=noncommit_excluded]', result=secondary,
            category_note='The estimate and interval are original-registered-secondary per MISSION. The separately reported sensitivity p-value is post-hoc-exploratory.'),
        per_world=worlds, sources=[b.sources[f'{ANALYSIS}/{n}.json'] for n in ('effects_study', 'sensitivity', 'world_effects', 'checkpoint_certificates')] + [b.sources[ARCHIVE]],
        certificate_counts=dict(collections.Counter(c['status'] for c in tables['checkpoint_certificates'])),
        scheduled_counts=dict(collections.Counter(v['status'] for p, v in archive_data.items() if '/branches/' in p and p.endswith('/result.json'))),
        counts_evidence_category='descriptive'))
    b.write('cases.json', dict(schema=SCHEMA, cases=index, study='study.json',
        arm_labels=dict(F='factual', K='counterfactual exposure mask', S='sham', N='placebo'),
        archive=dict(path=ARCHIVE, sha256=archive_hash),
        usage='Load case.file, then case.full_text_file relative to demo/data for untruncated interaction text. Sources include archive member paths; raw archive is not duplicated.'))
    b.write('TRACE.md', TRACE, text=True)
    twins = OUT / 'twins.json'
    if twins.exists():  # written by demo/build_twins.py; bind it and its benchmark sources
        raw = twins.read_bytes()
        b.files.append(dict(path='demo/data/twins.json', sha256=digest(raw), bytes=len(raw)))
        for s in json.loads(raw)['sources']:
            b.source(s['path'], (ROOT / s['path']).read_bytes())
        b.source('demo/build_twins.py', (ROOT / 'demo/build_twins.py').read_bytes())
    b.source('demo/build_data.py', Path(__file__).read_bytes())
    manifest = dict(schema=SCHEMA, generator_commit_HEAD=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                    generator_commit_role='Git HEAD at generation, not a claim that working-tree source bytes equal that commit; source_hashes bind the actual inputs and generator.',
                    generator='demo/build_data.py', files=sorted(b.files, key=lambda r: r['path']),
                    source_hashes=[v for _, v in sorted(b.sources.items())],
                    archive_sha256=archive_hash,
                    manifest_self_hash='Excluded to avoid recursive hash; all other generated artifacts listed.',
                    source_strategy='Archive SHA verified against frozen sidecar; allowlisted members streamed in memory, no extraction.')
    b.write('MANIFEST.json', manifest)
    total = sum(p.stat().st_size for p in OUT.rglob('*.json'))
    if total >= 8_000_000:
        raise ValueError(f'JSON pack exceeds 8 MB: {total}')
    print(f'Built {len(index)} cases; JSON bytes={total}; archive SHA256={archive_hash}')


TRACE = '''# Explorer numeric trace

All field paths below are relative to the named raw source or generated case. JSON
numbers are copied without rounding. UI formatting must not replace stored values.
Every case has sources with SHA256; archive members use docs/runner/<member> paths.
The manifest binds every generated file except itself, and every source actually used.

| Displayed number type / pack field | Exact source field / derivation | Evidence category |
|---|---|---|
| study.primary.result estimate, L, U, p_raw, n_independent, matched_pairs_attempted, eligible_complete_pairs | exp002_heldout_v3/effects_study.json[effect=Delta_total], identical full row | original-confirmatory |
| study.noncommit_sensitivity.result estimate, L, U, n_independent | exp002_heldout_v3/sensitivity.json[analysis=noncommit_excluded], identical full row; original Tier-B label retained | original-registered-secondary estimate/interval; separately reported sensitivity p-value is post-hoc-exploratory |
| study.per_world[].tau_O_B1 / tau_O_B2 | world_effects.json[world_id,regime].tau_O | original-confirmatory components |
| study.per_world[].d_w | world_effects.json[world_id,B1].tau_O minus [world_id,B2].tau_O | original-confirmatory |
| certificate_counts / scheduled_counts | count checkpoint_certificates.json by status / all streamed branches/*/result.json.data.status (includes not_run) | descriptive |
| Unrun continuation scheduled_records[].rep, attempt_no | scheduled_statuses.json[checkpoint_id,arm,rep]; metrics=null rather than invented zero | descriptive |
| Held-out continuations[].rep, metrics attempt_no, rep, rewards, Omean, Cmean, W, A | continuations.json[checkpoint_id,arm,rep], identical full row | descriptive |
| Held-out committed task IDs and roles | continuations.json[checkpoint_id,arm,rep].committed / .roles; IDs are labels, not measurements | descriptive |
| Held-out certificate tau_O/C/W/A and *_L, *_U, TV*, theta, n_independent, placebo contrasts | checkpoint_certificates.json[checkpoint_id], identical full row, including nulls | descriptive |
| Held-out margins m_O, delta_W / gate_trace margin, delta_W | checkpoint_certificates.json[checkpoint_id].gates.m_O / .delta_W | descriptive |
| Held-out gate_trace L/U and comparisons | certificate tau_*_L/U; O lower > m_O, upper < m_O; C lower > 0 or upper <= 0; W lower >= -delta_W or upper < -delta_W; otherwise ambiguous | descriptive |
| Held-out world_effect tau_*, n_F, n_K | world_effects.json[world_id,regime], identical full row | descriptive |
| validity.canonical_records / regime_batch_records estimates, L/U, confidence endpoints, n_independent, half_width90 | validity_checks.json[checkpoint_id] / [no checkpoint_id, matching regime], identical rows | descriptive |
| validity.raw_counts[].counts pass/fail/na and other statuses (held-out) | checkpoint.json.data.restore_validation plus attempt result.json.data.cross_checks[] plus each branches/*/result.json.data.checks[]; count by id/status, not_applicable => na; no inferred passes | descriptive |
| Held-out arms[arm].recorded_branches / statuses | count streamed branches/*/result.json by arm / status; no record does not imply an executed continuation | descriptive |
| checkpoint_turn, exposure turn/mask fields | checkpoint.json.data.scheduler_cursor / .exposure | descriptive |
| original/continuation turn_index, step, source_record_index | source/records.json or branches/*/records.json .data.records[i].turn_index / step / array index i | descriptive |
| Interaction message/action arguments and tool results (any numeric literals) | records[i].response.choices[].message verbatim; trailing tool messages from records[i].request.messages; original turn_index < checkpoint scheduler_cursor | descriptive |
| Gate A seed, boundary, detector observations, task IDs and embedded numbers | gate_a_results.json.gz rows[case.source_field].seed / native.detector_text_evidence (verbatim in full file) | development |
| Gate A continuation rep | array index in rows[i].native.branch_replicates[arm] | development |
| Gate A agent_rewards, assignment, Omean, Cmean, A, W | rows[i].native.branch_replicates[arm][rep].outcome; null if unavailable | development |
| Gate A certificate estimates, intervals, counts, parameters, placebo effects/p and all other nested numbers | rows[i].native.CCC, identical complete decision | development |
| Gate A oracle_effects / oracle_strata and margins | rows[i].oracle_effects / oracle_strata; m_O from native.CCC.parameters.m_O, delta_W from oracle_strata.reference_delta_W | development |
| Gate A gate_trace L/U, margin, delta_W, pattern comparisons | native.CCC.estimates.intervals.tau_*; same explicit comparisons above; stored pattern_gates also retained | development |
| Gate A validity.raw_counts[].counts | rows[i].native.checks[], grouped by id/status with not_applicable => na | development |
| Source SHA256, archive SHA256 | SHA256 of original file/member bytes; archive checked against exp002-live.tar.gz.sha256 | provenance metadata |
| MANIFEST.files[].bytes / sha256 | byte length / SHA256 of generated artifact (no self-hash) | build metadata |
| twins.json pairs[].members[].by_set[Ix].transcript, arms (n, Cmean, Omean, A, W, rewards, action), placebo, probe, authorization, view_sha256 | <run>/partitions/<seed>-eps-0.json.gz[Ix][view_sha256 match].canonical_view (re-hashed to equal records view_sha256); arms = per-arm means of the stored rows | twins.json evidence_category: development or new-prospective; selected epsilon=0 exhibit |
| twins.json members[].truth, by_set[Ix].identifiable, M_multiclass_identifiable | <run>/records.json.gz[seed,kind,member,eps=0,set] truth / identifiable, evaluator-only scripted labels | same category as twins.json |
| twins.json verdicts (ccc, ccc_l, baseline, bayes) | records.json.gz methods[CCC-v1.2.2 / CCC-L-v0 / strongest of B2+,B3b / Bayes-given-S] status, rung, M_label, predictions | same category as twins.json |
| twins.json first_separating_set, first_divergence | first Ix where the two members' view_sha256 / verdict JSON differ (computed in build_twins.py); enumerated_pair_separator from separators.json | same category as twins.json |
| twins.json aggregate_criteria | <run>/RESULTS.json.rq[RQ].status, copied verbatim; RQ1/RQ2 pass by construction | original prospective aggregate; includes epsilon=0.1, platform-dependent |
| twins.json strongest_baseline | balanced accuracy of attributable-M at I1 over DEV records, B2+ vs B3b, ties to B2+ (docs/enh/r2/PROTOCOL.md s5) | development |

Gate traces explain recorded outcomes; they do not issue replacement certificates.
Absent fixture transcripts are explicitly unavailable, never synthesized. Exposure
highlight uses the exact original post_message message argument. Full case files
retain untruncated messages/actions/tool results, without duplicating prompts or RNG
state; hashed raw records provide those originals. Compact case files shorten strings
at 900 characters. Independent sample size is eight matched world pairs, not branch
replicates or raw validation check counts.
'''


if __name__ == '__main__':
    build()
