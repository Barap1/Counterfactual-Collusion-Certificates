#!/usr/bin/env python3
"""Build a deterministic, dependency-free DEV-only recorded evidence viewer."""
import difflib
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REAL = Path('docs/runner/exp001-live')
ANALYSIS = Path('docs/analysis/exp001_dev')
FIXTURE = Path('docs/gate_a/v1.2/correction_v1.2.2/gate_a_results.json.gz')
ARCHIVE = Path('docs/runner/archives/exp001-live.tar.gz')
SOURCES = {}


def digest(path):
    h = hashlib.sha256()
    with (ROOT / path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    path = Path(path)
    # Explicit allowlist: never traverse the repository or discover other runs.
    assert path.is_relative_to(REAL) or path.is_relative_to(ANALYSIS) or path == FIXTURE
    raw = (ROOT / path).read_bytes()
    SOURCES[str(path)] = hashlib.sha256(raw).hexdigest()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def unwrap(path):
    value = read(path)
    return value.get('data', value)


def compact_checks(checks):
    grouped = {}
    for check in checks:
        key = json.dumps(check, sort_keys=True)
        if key not in grouped:
            grouped[key] = dict(check, occurrences=0)
        grouped[key]['occurrences'] += 1
    return list(grouped.values())


def prompt_diff(before, after):
    a = json.dumps(before, ensure_ascii=False, indent=2).splitlines()
    b = json.dumps(after, ensure_ascii=False, indent=2).splitlines()
    return '\n'.join(difflib.unified_diff(a, b, fromfile='F receiver request', tofile='arm receiver request', lineterm='')) or 'UNCHANGED — identical receiver messages at the intervention boundary.'


def build():
    expected = (ROOT / (str(ARCHIVE) + '.sha256')).read_text().split()[0]
    assert digest(ARCHIVE) == expected, 'DEV archive hash mismatch'
    SOURCES[str(ARCHIVE)] = expected
    SOURCES[str(ARCHIVE) + '.sha256'] = digest(Path(str(ARCHIVE) + '.sha256'))
    certificates = read(ANALYSIS / 'checkpoint_certificates.json')
    continuations = read(ANALYSIS / 'continuations.json')
    attempts = read(ANALYSIS / 'attempts.json')
    scheduled = read(ANALYSIS / 'scheduled_statuses.json')
    study = read(ANALYSIS / 'effects_study.json')
    cases = []
    ids = sorted({r['checkpoint_id'] for r in attempts + certificates + scheduled})
    for case_id in ids:
        before_sources = set(SOURCES)
        cert = next((r for r in certificates if r['checkpoint_id'] == case_id), {})
        base = REAL / 'worlds' / case_id / 'attempt_0001'
        checkpoint = unwrap(base / 'checkpoint.json') if (ROOT / base / 'checkpoint.json').exists() else {}
        result = unwrap(base / 'result.json') if (ROOT / base / 'result.json').exists() else {}
        exposure = checkpoint.get('exposure', {})
        arms = {}
        all_checks = list(result.get('cross_checks', []))
        for key, status in checkpoint.get('restore_validation', {}).items():
            all_checks.append(dict(id=key, name='checkpoint_restore', status=status))
        for arm in ['F', 'S', 'K', 'N']:
            rows = [r for r in continuations if r['checkpoint_id'] == case_id and r['arm'] == arm]
            raw_attempts = [r for r in attempts if r['checkpoint_id'] == case_id and r['arm'] == arm]
            branch_dirs = sorted((ROOT / base / 'branches').glob('*_' + arm))
            item = dict(rows=rows, attempts=raw_attempts, audits=[], events=[])
            for branch_dir in branch_dirs:
                # Read only audit ledgers belonging to this explicit DEV checkpoint.
                ledgers = sorted((branch_dir / 'replay_ledger').glob('*'))
                for ledger in ledgers:
                    audit_path = ledger / 'prompt_audits.json'
                    if audit_path.exists():
                        audits = read(audit_path.relative_to(ROOT))
                        receiver_audits = [a for a in audits if a.get('agent') == exposure.get('receiver')]
                        item['audits'].append(dict(branch=branch_dir.name, prompts=[
                            dict(turn=a['turn_index'], messages=a['request']['messages'],
                                 delivered_events=a.get('delivered_events')) for a in receiver_audits]))
                records_path = branch_dir / 'records.json'
                if records_path.exists():
                    records = unwrap(records_path.relative_to(ROOT))
                    # Preserve the recorded tool/action rows independently of prompt diffs.
                    item['events'].append(dict(branch=branch_dir.name, turns=records.get('turns'), errors=records.get('errors'), records=[
                        {**{k:v for k,v in r.items() if k not in ['request','python_rng_state_after']},
                         'tool_results': [m for m in r.get('request', {}).get('messages', []) if m.get('role') == 'tool']}
                        for r in records.get('records', [])]))
            for branch in result.get('branches', []):
                if branch['arm'] == arm:
                    all_checks.extend(dict(c, arm=arm, replicate=branch.get('replicate')) for c in branch.get('checks', []))
            arms[arm] = item
        factual = next((a['prompts'][0]['messages'] for a in arms['F']['audits'] if a['prompts']), None)
        for arm, item in arms.items():
            target = next((a['prompts'][0]['messages'] for a in item['audits'] if a['prompts']), None)
            item['diff'] = prompt_diff(factual, target) if factual is not None and target is not None else 'Receiver request unavailable in this recorded branch.'
        cases.append(dict(id=case_id, kind='Real-agent DEV · protocol v1.1',
                          checkpoint=checkpoint, exposure=exposure, certificate=cert,
                          status=cert.get('status', result.get('status', 'unavailable')),
                          reasons=cert.get('reasons', ['No checkpoint certificate recorded.']),
                          arms=arms, checks=compact_checks(all_checks),
                          provenance=sorted(set(SOURCES) - before_sources) + [str(ANALYSIS / n) for n in ['checkpoint_certificates.json','continuations.json','attempts.json','scheduled_statuses.json']]))
    gate = read(FIXTURE)
    for row in sorted(gate['rows'], key=lambda r: (r['family'], r['world_id'], r['seed'], r['stratum'], r['wording_type'])):
        native = row['native']
        ccc = native['CCC']
        identity = ' / '.join(str(row[k]) for k in ['family','world_id','seed','stratum','wording_type'])
        arms = {}
        for arm in ['F','S','K','N']:
            reps = native.get('branch_replicates', {}).get(arm, [])
            arms[arm] = dict(rows=[dict(rep=i, **(b.get('outcome') or {}), runner_status=b.get('status'), reasons=b.get('reasons')) for i,b in enumerate(reps)],
                             means=ccc.get('estimates', {}).get('means', {}).get(arm, {}),
                             count=ccc.get('estimates', {}).get('counts', {}).get(arm),
                             recorded_branch={k:v for k,v in native.get('branches', {}).get(arm, {}).items() if k != 'checks'})
        cases.append(dict(id=identity, kind='Synthetic fixture · v1.2.2 · scripted, recorded',
                          status=ccc['status'], reasons=ccc.get('reasons', []),
                          fixture={k:v for k,v in row.items() if k not in ['native','local_fault_reference']},
                          certificate=ccc, arms=arms, checks=compact_checks(native.get('checks', []) if isinstance(native.get('checks'), list) else []),
                          exposure=native.get('detector_text_evidence', {}),
                          checkpoint=dict(snapshot_sha256=native.get('snapshot_sha256'), request_hashes=native.get('request_hashes'),
                                          placebo_selection=native.get('placebo_selection'), actual_arm_counts=native.get('actual_arm_counts'), study_checks=native.get('study_checks')),
                          provenance=[str(FIXTURE)]))
    data = dict(cases=cases, sources=SOURCES, archive=dict(path=str(ARCHIVE), sha256=expected),
                study=study, fixture_metadata={k:v for k,v in gate.items() if k not in ['rows']},
                selection='Default: lexicographically first checkpoint ID in the committed DEV analysis, regardless of outcome. All analyzed DEV checkpoint IDs and all fixture cells are included. Fixture cells sort by family, world ID, seed, stratum, then wording.')
    template = (ROOT / 'viewer/assets/template.html').read_text()
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    output = template.replace('__EVIDENCE_JSON__', payload)
    (ROOT / 'viewer/index.html').write_text(output)
    summary = dict(cases=len(cases), real_cases=len(ids), fixture_cells=len(gate['rows']), default=ids[0],
                   source_files=len(SOURCES), archive_sha256=expected, html_sha256=hashlib.sha256(output.encode()).hexdigest(),
                   html_bytes=len(output.encode()), screenshot='Skipped per task instruction; director render pending.')
    (ROOT / 'viewer/build_evidence.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    build()
