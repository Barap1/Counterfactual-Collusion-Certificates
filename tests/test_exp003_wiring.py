"""Offline full collector and failure propagation checks; no inference."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from ccc.exp003 import collector
from ccc.exp003.manifest import SCHEMA, fresh_pairs, validate
from ccc.exp003.analysis import analyze
from ccc.runner.manifest import file_hash


def development_manifest():
    m = json.loads(Path('docs/runner/dev_manifest.json').read_text())
    m.update(schema_version=SCHEMA, experiment_id='EXP-003-mock', backend='local',
             protocol_artifact='docs/enh/exp003/PROTOCOL.md',
             protocol_sha256=file_hash('docs/enh/exp003/PROTOCOL.md'), max_requests=2000,
             arms=['F', 'K', 'S', 'N', 'PF', 'PK'],
             continuations_per_arm={'F': 4, 'K': 4, 'S': 2, 'N': 4, 'PF': 4, 'PK': 4})
    m['policy']['live_inference_enabled'] = False
    m['worlds'] = [dict(id=f'mock_dev02_{r}', pair_id='mock_dev02', seed=2, regime=r,
                        split='development') for r in ('B1', 'B2')]
    m.pop('hard_stop_utc', None)
    return m


def test_mock_full_pipeline(tmp_path, monkeypatch, capsys):
    m = development_manifest()
    result = collector.run(m, tmp_path, dry_run=True)
    rows = json.loads((tmp_path / 'rows.json').read_text())
    assert result['run_record']['checkpoints_launched'] == 2
    assert len(rows) == 44
    assert {r['world_id'] for r in rows} == {'mock_dev02'}
    assert all(r['status'] in ('valid', 'not_run') for r in rows)
    assert all(r['status'] == 'valid' for r in rows if r['arm'] in ('PF', 'PK'))
    assert analyze(rows, 4)['primary'][0]['n_independent'] == 1
    assert len(list(tmp_path.rglob('probe_selection.json'))) == 2
    assert len(list(tmp_path.rglob('*.begin.json'))) > 0
    from ccc.exp003 import analysis
    monkeypatch.setattr('sys.argv', ['analysis', str(tmp_path / 'rows.json'), '--continuations', '4'])
    analysis.main()
    (tmp_path / 'analysis.json').write_text(capsys.readouterr().out)


def test_cross_check_failure_excludes_analysis(monkeypatch, tmp_path):
    from ccc.replay.validators import CheckResult, FAIL
    monkeypatch.setattr(collector.probe_arms, 'check_probe_pair',
                        lambda *args: [CheckResult('P03', 'injected', FAIL, {})])
    m = development_manifest()
    with pytest.raises(ValueError, match='invalid'):
        collector.run(m, tmp_path, dry_run=True)
    rows = collector.export_rows(m, tmp_path)
    assert all(r['status'] == 'invalid' for r in rows if r['regime'] == 'B1')
    assert analyze(rows, 4)['primary'][0]['n_independent'] == 0


def test_probe_ineligible_keeps_ordinary_arms(monkeypatch, tmp_path):
    from ccc.exp003.probe import ProbeUnavailable
    def unavailable(*args):
        raise ProbeUnavailable('injected ineligibility')
    monkeypatch.setattr(collector.probe_arms, 'prepare_probe', unavailable)
    m = development_manifest()
    collector.run(m, tmp_path, dry_run=True)
    rows = collector.export_rows(m, tmp_path)
    assert all(r['status'] == 'not_run' and r['reasons'] == ['probe_ineligible']
               for r in rows if r['arm'] in ('PF', 'PK'))
    result = analyze(rows, 4)
    assert [r['n_independent'] for r in result['primary']] == [1, 0]


def test_backend_and_pair_validation():
    m = development_manifest()
    validate(m)
    modal = deepcopy(m)
    modal['backend'] = modal['model']['backend'] = 'modal'
    modal['model']['base_url'] = 'https://configured-test.modal.run/v1'
    validate(modal)
    modal['model']['base_url'] = 'https://example.com/v1'
    with pytest.raises(ValueError):
        validate(modal)
    m['worlds'][1]['pair_id'] = 'different'
    with pytest.raises(ValueError):
        validate(m)
    pairs = fresh_pairs('a'*40, {1, 2})
    assert pairs == fresh_pairs('a'*40, {1, 2})
    assert len(pairs) == 64 and pairs[0]['seed'] == pairs[1]['seed']


def test_canary_failure_preserves_all_scheduled_slots(monkeypatch, tmp_path):
    from ccc.infra.budget_guard import BudgetGuard, GuardPolicy
    from ccc.runner.live import ModelReload
    from ccc.exp003.manifest import plan
    original = collector.DurableClient
    def fake_client(*args, **kwargs):
        kwargs['live_session'] = None  # scripted transport; fake attestation below
        return original(*args, **kwargs)
    monkeypatch.setattr(collector, 'DurableClient', fake_client)
    class FakeSession:
        def __init__(self):
            self.phases = []
        def canary(self, guard, root, phase):
            self.phases.append(phase)
            if phase == 'before':
                raise ModelReload('injected canary mismatch')
        def check(self):
            return {'fake': True}
    m = development_manifest()
    session = FakeSession()
    guard = BudgetGuard(run_id='mock-canary', task_id='EXP-000b', max_calls=200,
                        ledger_path=tmp_path / 'budget.jsonl', policy=GuardPolicy(max_retries=0))
    try:
        result = collector.collect_world(m, plan(m)['jobs'][0], tmp_path, guard, 'mock', session)
    finally:
        guard.close('mock done')
    assert session.phases == ['source_after', 'before']
    assert len(result['branches']) == 22
    assert all(r['status'] == 'invalid' and not r['launched'] for r in result['branches'])


def test_request_budget_failure_retains_missing_rows(tmp_path):
    m = development_manifest()
    m['max_requests'] = 1
    with pytest.raises(ValueError, match='failed'):
        collector.run(m, tmp_path, dry_run=True)
    rows = collector.export_rows(m, tmp_path)
    assert len(rows) == 44
    assert not any(r['status'] == 'valid' for r in rows)


def test_export_branch_missingness_does_not_erase_other_complete_arms(tmp_path):
    from ccc.exp003.storage import put
    from ccc.exp003.manifest import plan
    m = development_manifest()
    for job in plan(m)['jobs']:
        branches = [item | dict(status='valid', outcomes={'status': 'complete', 'Omean': 1})
                    for item in job['order']]
        next(r for r in branches if r['arm'] == 'PF')['status'] = 'failed'
        put(tmp_path / 'worlds' / job['world']['id'] / 'attempt_0001' / 'result.json',
            dict(status='invalid', branches=branches, cross_checks=[]))
    result = analyze(collector.export_rows(m, tmp_path), 4)
    assert [p['n_independent'] for p in result['primary']] == [1, 0]


def test_modal_entrypoint_builds_exp003_manifest_without_session_reads(tmp_path):
    from ccc.exp003.modal_runner import make_manifest, validate_modal, install
    m = make_manifest('https://configured-test.modal.run', tmp_path / 'manifest.json')
    validate_modal(m)
    assert {w['regime'] for w in m['worlds']} == {'B1', 'B2'}
    assert m['arms'][-2:] == ['PF', 'PK']
    with pytest.raises(ValueError, match='retired'):
        install()


def test_backend_evidence_tiers():
    assert collector.evidence_tier({'backend': 'modal'}, True) == 'live_modal'
    assert collector.evidence_tier({'backend': 'ollama_local'}, True) == 'live_local'
    assert collector.evidence_tier({'backend': 'modal'}, False) == 'scripted_dry_run'
