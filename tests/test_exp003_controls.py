"""Light offline adversarial release-control tests; no Modal imports or commands."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import socket
import pytest
from ccc.exp003 import budget
from ccc.exp003.modal_ctl import Lifetime
from ccc.exp003.analysis import analyze
from ccc.exp003.manifest import digest, file_hash, plan
from ccc.exp003.slots import validate_slots
from tests.test_exp003_wiring import development_manifest
from tests.test_exp003_probe import rows_fixture


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def deny(*a, **k):
        raise AssertionError('network forbidden')
    monkeypatch.setattr(socket.socket, 'connect', deny)
    monkeypatch.setattr(socket, 'getaddrinfo', deny)


def test_absolute_deadline_constant():
    assert budget.HARD_STOP_EPOCH == datetime(2026, 10, 25, 9, tzinfo=timezone.utc).timestamp()


def test_reservation_counts_active_cost_and_no_double_count(tmp_path):
    path = tmp_path/'budget.jsonl'
    budget.append_run(100, 'L40S', label='prior-feasibility', path=path)
    prior = budget.total_estimated(path)
    row = budget.reserve_session(600, 'L40S', path=path, now=1000, storage_usd=.2)
    assert budget.exposure(path, now=1001) == pytest.approx(prior+.2+row['reserved_usd'])
    for t in (1010, 1020, 1030):
        row, reason = budget.tick_session(row, path=path, now=t)
        assert reason is None
    assert budget.exposure(path, now=1030) == pytest.approx(prior+.2+row['reserved_usd'])
    with pytest.raises(ValueError, match='active/unverified'):
        budget.reserve_session(10, 'L40S', path=path, now=1030)
    budget.close_session(row, False, path=path, now=1040)
    with pytest.raises(ValueError, match='active/unverified'):
        budget.reserve_session(10, 'L40S', path=path, now=1040)
    budget.close_session(row, True, path=path, now=1050)
    assert budget.exposure(path, now=1050) == pytest.approx(prior+.2+50*row['rate_with_margin']/3600)


@pytest.mark.parametrize('prior', [44.99, 50.99, 51.0])
def test_prelaunch_caps(tmp_path, prior):
    path = tmp_path/'budget.jsonl'
    budget.ledger(path).append(dict(task=budget.TASK, event='modal_run', estimated_usd=prior))
    with pytest.raises(ValueError, match='operating stop'):
        budget.reserve_session(600, 'L40S', path=path, now=1000)


@pytest.mark.parametrize('prior,reason', [(45, 'operating_stop'), (51, 'total_cap')])
def test_timer_stops_without_request_completion(tmp_path, prior, reason):
    path = tmp_path/'budget.jsonl'
    row = budget.reserve_session(600, 'L40S', path=path, now=1000)
    budget.ledger(path).append(dict(task=budget.TASK, event='modal_run', estimated_usd=prior))
    stopped = []
    life = Lifetime(row, path=path, clock=lambda: 1001, shutdown=lambda app: stopped.append(app) or True)
    life.app_id = 'fake-blocked-cold-start'
    assert life.tick() == reason
    assert stopped == ['fake-blocked-cold-start']
    assert life.done.is_set()
    assert budget.session_rows(path)[row['session_id']]['state'] == 'stopping'


def test_deadline_reserves_shutdown_and_blocks_late_launch(tmp_path):
    path = tmp_path/'budget.jsonl'
    now = budget.HARD_STOP_EPOCH-200
    row = budget.reserve_session(600, 'L40S', path=path, now=now)
    assert row['deadline_epoch'] == budget.HARD_STOP_EPOCH-budget.SHUTDOWN_SECONDS
    assert budget.tick_session(row, path=path, now=row['deadline_epoch'])[1] == 'deadline'
    with pytest.raises(ValueError, match='absolute deadline'):
        budget.reserve_session(600, 'L40S', path=tmp_path/'other.jsonl', now=budget.HARD_STOP_EPOCH)


def test_confirmatory_refuses_counts_and_unbound_rows():
    with pytest.raises(ValueError, match='four continuations'):
        analyze(rows_fixture(), 3, 'new-prospective')
    with pytest.raises(ValueError, match='sealed raw'):
        analyze(rows_fixture(), 4, 'new-prospective')
    result = analyze(rows_fixture(), 3, 'new-prospective', exploratory=True)
    assert all(not p['confirmatory_eligible'] and p['interpretation'] == 'feasibility/descriptive'
               for p in result['primary'])
    assert all('fewer than 16 complete matched pairs' in p['ineligibility_reasons'] for p in result['primary'])


def scheduled(m, states):
    rows = []
    for i, job in enumerate(plan(m)['jobs']):
        w = job['world']
        state = states[i]
        rows.extend(dict(item, world_id=w['pair_id'], regime=w['regime'], slot_index=i,
                         manifest_sha256=digest(m), attempt_status=state,
                         attempt_count=0 if state == 'unattempted' else 1,
                         status='not_run', outcomes=None) for item in job['order'])
    return rows


def test_terminal_prefix_no_replacement_or_retry():
    m = development_manifest()
    m['worlds'] += [dict(w, id=w['id']+'next', pair_id='next', seed=3) for w in m['worlds'][:2]]
    rows = scheduled(m, ['complete', 'invalid', 'unattempted', 'unattempted'])
    result = validate_slots(rows, m)
    assert result['k'] == 1 and result['terminal_slot_included']
    for bad in (scheduled(m, ['invalid', 'complete', 'unattempted', 'unattempted']),
                scheduled(m, ['unattempted', 'ineligible', 'complete', 'complete'])):
        with pytest.raises(ValueError, match='replacement forbidden'):
            validate_slots(bad, m)
    bad = deepcopy(rows)
    bad[0]['attempt_count'] = 2
    with pytest.raises(ValueError):
        validate_slots(bad, m)
    rows = scheduled(m, ['ineligible', 'ineligible', 'complete', 'complete'])
    assert validate_slots(rows, m)['k'] == 2
    rows[0].update(status='valid', outcomes={'Omean': 1})
    with pytest.raises(ValueError, match='ineligible slot replaced'):
        validate_slots(rows, m)


def test_freeze_placeholder_dry_run_refusal(monkeypatch, tmp_path, capsys):
    from ccc.exp003 import freeze
    # No FREEZE.json is created: repository resolution points to a differently named test fixture.
    artifact = tmp_path/'placeholder-fixture.json'
    artifact.write_text(json.dumps({'director_freeze_commit': 'unverified'}))
    monkeypatch.setattr(freeze, 'repo_file', lambda name: artifact)
    with pytest.raises(ValueError, match='placeholder'):
        freeze.verify_freeze({'freeze_sha256': 'unverified'})
    with pytest.raises(ValueError, match='actual director freeze commit'):
        freeze.verify_freeze({'freeze_sha256': file_hash(artifact), 'director_freeze_commit': 'unverified'})
    print('PASS: offline admission refuses placeholder freeze hash and commit; no FREEZE.json created')


def freeze_fixture(monkeypatch, tmp_path):
    from ccc.exp003 import freeze, manifest
    artifact = tmp_path/'approved-fixture.json'
    code = tmp_path/'code.py'
    code.write_text('# fixture bytes\n')
    candidate = tmp_path/'candidate-fixture.json'
    candidate.write_text(json.dumps({'code_sha256': {str(code): file_hash(code)}}))
    m = development_manifest()
    m.update(phase='holdout', director_freeze_commit='ab'*20, backend='modal')
    # Synthetic DEV seed schedule; no real held-out seed stream is generated.
    m['worlds'] = [dict(id=f'synthetic_{i}_{r}', pair_id=f'synthetic_{i}', seed=i+2,
                        regime=r, split='holdout') for i in range(32) for r in ('B1', 'B2')]
    files = {}
    for name, value in [('seed_exclusion', [1]), ('skip_ledger', []),
                        ('seed_list', [w['seed'] for w in m['worlds'][::2]])]:
        p = tmp_path/(name+'.json')
        p.write_text(json.dumps(value))
        files[name] = p
        m[name+'_sha256'] = file_hash(p)
    protocol = Path(m['protocol_artifact'])
    inventory = {str(p.relative_to(freeze.ROOT)): file_hash(p) for p in (freeze.ROOT/'ccc/exp003').glob('*.py')}
    inventory[str(code)] = file_hash(code)
    f = dict(approved=True, pending=[], director_freeze_commit=m['director_freeze_commit'], backend='modal',
             protocol_artifact=m['protocol_artifact'], protocol_sha256=file_hash(protocol),
             code_sha256=inventory, evidence_sha256={}, pair_order=m['worlds'], max_requests=m['max_requests'],
             feasibility_budget=dict(calls_per_regime_world=20, canary_calls_per_regime_world=3,
                 gpu_seconds_per_regime_world=60, projected_total_usd=5, projected_total_seconds=4000,
                 reconciled_prior_usd=1, storage_usd=.1, startup_calls=2, measured_dev_valid=True))
    from ccc.exp003.feasibility import workload_sha256
    measured = tmp_path/'measured-cost-fixture.json'
    measured.write_text(json.dumps(dict(status='measured', measured_dev_valid=True,
        workload_sha256=workload_sha256(m), safety_margin=1.2,
        launch_config=dict(gpu='L40S', cpu=4, mem_gib=16, parallel=1, scaledown=180),
        seconds_per_regime_world=60, cost_per_regime_world_usd=.05,
        startup_seconds=100, startup_cost_usd=.1,
        calls_per_regime_world=20, canary_calls_per_regime_world=3, startup_calls=2)))
    f['feasibility_budget'].update(measured_cost_artifact=str(measured), measured_cost_sha256=file_hash(measured))
    for name, p in files.items():
        f[name+'_artifact'] = str(p)
        f[name+'_sha256'] = file_hash(p)
    original = freeze.repo_file
    monkeypatch.setattr(freeze, 'repo_file', lambda n: artifact if n == freeze.FREEZE else
                        candidate if n == 'docs/enh/exp003/FREEZE_candidate.json' else
                        Path(n) if str(n).startswith(str(tmp_path)) else original(n))
    from ccc.exp003 import feasibility
    monkeypatch.setattr(feasibility, 'repo_file', freeze.repo_file)
    monkeypatch.setattr(freeze, 'fresh_pairs', lambda *a: deepcopy(f['pair_order']))
    monkeypatch.setattr(manifest, 'stream_skips', lambda *a: [])
    def save():
        f['manifest_config_sha256'] = digest({k: v for k, v in m.items() if k != 'freeze_sha256'})
        artifact.write_text(json.dumps(f))
        m['freeze_sha256'] = file_hash(artifact)
    save()
    return freeze, m, f, save, files


def test_freeze_bindings_tamper_and_placeholder_fields(monkeypatch, tmp_path):
    freeze, m, f, save, files = freeze_fixture(monkeypatch, tmp_path)
    assert freeze.verify_freeze(m)['approved']
    for field in ('seed_list_sha256', 'skip_ledger_sha256', 'seed_exclusion_sha256'):
        bad = dict(m, **{field: 'unverified'})
        with pytest.raises(ValueError):
            freeze.verify_freeze(bad)
    bad = deepcopy(m)
    bad['worlds'][:4] = bad['worlds'][2:4]+bad['worlds'][:2]
    with pytest.raises(ValueError, match='configuration mismatch|pair order'):
        freeze.verify_freeze(bad)
    files['seed_list'].write_text('[]')
    with pytest.raises(ValueError, match='seed_list'):
        freeze.verify_freeze(m)
    files['seed_list'].write_text(json.dumps([w['seed'] for w in m['worlds'][::2]]))
    f['code_sha256'][next(iter(f['code_sha256']))] = '1234'*16
    save()
    with pytest.raises(ValueError, match='artifact changed'):
        freeze.verify_freeze(m)


def test_subfloor_rejected_after_release_gate(monkeypatch, tmp_path):
    from ccc.exp003 import storage, collector, manifest, slots
    rows = rows_fixture()
    # Four continuations, but six complete pairs: independently test the sample floor.
    rows += [dict(r, replicate=3) for r in rows if r['replicate'] == 0]
    monkeypatch.setattr(storage, 'verify', lambda root: None)
    monkeypatch.setattr(storage, 'get', lambda path: {'phase': 'holdout'})
    monkeypatch.setattr(manifest, 'validate', lambda m: m)
    monkeypatch.setattr(collector, 'export_rows', lambda *a: rows)
    monkeypatch.setattr(slots, 'validate_slots', lambda *a: {'validated': True, 'k': 6})
    with pytest.raises(ValueError, match='at least 16'):
        analyze(rows, 4, 'new-prospective', evidence_root=tmp_path)
    result = analyze(rows, 4, 'new-prospective', evidence_root=tmp_path, exploratory=True)
    assert [p['n_independent'] for p in result['primary']] == [6, 6]
    assert all(not p['confirmatory_eligible'] for p in result['primary'])


def test_teardown_unknown_schema_fails_closed(monkeypatch):
    from types import SimpleNamespace
    from ccc.exp003 import modal_ctl
    for payload, expected in [([{'unknown': 'running'}], False),
                              ([{'App ID': 'ap-test', 'State': 'running'}], False),
                              ([{'App ID': 'ap-test', 'State': 'stopped'}], True), ([], True)]:
        monkeypatch.setattr(modal_ctl.subprocess, 'run', lambda *a, **k:
                            SimpleNamespace(returncode=0, stdout=json.dumps(payload)))
        assert modal_ctl.verify_stopped('ap-test') is expected


def test_feasibility_projection_blocks_late_launch(monkeypatch, tmp_path):
    freeze, m, f, save, files = freeze_fixture(monkeypatch, tmp_path)
    assert freeze.verify_launch_window(m, now=budget.HARD_STOP_EPOCH-5000)
    with pytest.raises(ValueError, match='cannot finish'):
        freeze.verify_launch_window(m, now=budget.HARD_STOP_EPOCH-1000)


def test_prospective_export_requires_seal_and_rejects_retry(tmp_path):
    from ccc.exp003 import collector
    from ccc.exp003.storage import put, seal
    m = development_manifest()
    m['phase'] = 'holdout'
    w = m['worlds'][0]
    attempt = tmp_path/'worlds'/w['id']/'attempt_0001'
    put(attempt/'begin.json', {'retry_of': None})
    put(attempt/'result.json', {'status': 'complete'})
    with pytest.raises(ValueError, match='must be sealed'):
        collector.export_rows(m, tmp_path)
    seal(attempt)
    assert collector.export_rows(m, tmp_path)
    other = tmp_path/'retry'
    attempt = other/'worlds'/w['id']/'attempt_0001'
    put(attempt/'begin.json', {'retry_of': 'hidden-earlier-failure'})
    put(attempt/'result.json', {'status': 'complete'})
    seal(attempt)
    with pytest.raises(ValueError, match='retried failure'):
        collector.export_rows(m, other)


def test_sixteen_pair_floor_passes_only_after_release(monkeypatch, tmp_path):
    from ccc.exp003 import storage, collector, manifest, slots
    rows = rows_fixture(16)
    rows += [dict(r, replicate=3) for r in rows if r['replicate'] == 0]
    monkeypatch.setattr(storage, 'verify', lambda root: None)
    monkeypatch.setattr(storage, 'get', lambda path: {'phase': 'holdout'})
    monkeypatch.setattr(manifest, 'validate', lambda m: m)
    monkeypatch.setattr(collector, 'export_rows', lambda *a: rows)
    monkeypatch.setattr(slots, 'validate_slots', lambda *a: {'validated': True, 'k': 16})
    result = analyze(rows, 4, 'new-prospective', evidence_root=tmp_path)
    assert all(p['confirmatory_eligible'] and p['n_independent'] == 16 for p in result['primary'])


def test_measured_placeholder_dry_run_refuses_before_spawn(monkeypatch, tmp_path):
    from types import SimpleNamespace
    from ccc.exp003 import modal_ctl, manifest
    freeze, m, f, save, _ = freeze_fixture(monkeypatch, tmp_path)
    measured = Path(f['feasibility_budget']['measured_cost_artifact'])
    measured.write_text(json.dumps({'status': 'placeholder', 'cost_per_regime_world_usd': None}))
    f['feasibility_budget']['measured_cost_sha256'] = file_hash(measured)
    save()
    monkeypatch.setattr(manifest, 'load', lambda _: m)
    monkeypatch.setattr(modal_ctl.subprocess, 'Popen', lambda *a, **k: pytest.fail('must refuse before spawn'))
    args = SimpleNamespace(development=False, manifest='synthetic', gpu='L40S', parallel=1,
                           scaledown=180, max_minutes=90, storage_usd=.1)
    with pytest.raises(ValueError, match='placeholder'):
        modal_ctl.start(args)


def test_short_or_changed_config_launch_refused(monkeypatch, tmp_path):
    from types import SimpleNamespace
    from ccc.exp003 import modal_ctl, manifest
    freeze, m, f, save, _ = freeze_fixture(monkeypatch, tmp_path)
    monkeypatch.setattr(manifest, 'load', lambda _: m)
    monkeypatch.setattr(modal_ctl, 'SESSION_FILE', tmp_path/'absent-session')
    monkeypatch.setattr(modal_ctl.time, 'time', lambda: budget.HARD_STOP_EPOCH-10000)
    monkeypatch.setenv('EXP003_CPU', '4')
    monkeypatch.setenv('EXP003_MEM_MIB', '16384')
    monkeypatch.setattr(budget, 'reserve_session', lambda *a, **k: pytest.fail('must refuse before reservation'))
    args = SimpleNamespace(development=False, manifest='synthetic', gpu='L40S', parallel=1,
                           scaledown=180, max_minutes=1, storage_usd=.1)
    with pytest.raises(ValueError, match='requested lifetime'):
        modal_ctl.start(args)
    args.max_minutes = 90
    args.gpu = 'H100'
    with pytest.raises(ValueError, match='configuration differs'):
        modal_ctl.start(args)


def test_measured_projection_reservation_and_attach(monkeypatch, tmp_path):
    from ccc.exp003.feasibility import projection, validate_session
    freeze, m, f, save, _ = freeze_fixture(monkeypatch, tmp_path)
    p = projection(m, f)
    path = tmp_path/'budget.jsonl'
    binding = dict(launch_config=p['config'], manifest_sha256=digest(m), measured_cost_sha256=p['measured_cost_sha256'])
    row = budget.reserve_session(5000, 'L40S', path=path, now=1000, minimum_seconds=p['seconds'],
                                 minimum_usd=p['cost'], reconciled_prior_usd=1, storage_usd=.1, binding=binding)
    assert row['reserved_usd'] >= 5
    assert budget.exposure(path, now=1000) >= 6.1
    assert validate_session(m, f, row, now=1001) == p
    with pytest.raises(ValueError, match='active reserved lifetime'):
        validate_session(m, f, row, now=3000)
    with pytest.raises(ValueError, match='configuration'):
        validate_session(m, f, dict(row, launch_config={}), now=1001)
    with pytest.raises(ValueError, match='operating stop'):
        budget.reserve_session(5000, 'L40S', path=tmp_path/'over.jsonl', now=1000,
                               minimum_usd=5, reconciled_prior_usd=40, storage_usd=.1)
    with pytest.raises(ValueError, match='reserved lifetime'):
        budget.reserve_session(5000, 'L40S', path=tmp_path/'late.jsonl', now=budget.HARD_STOP_EPOCH-1000,
                               minimum_seconds=p['seconds'], minimum_usd=p['cost'])


def test_measured_hash_and_underprojection_refused(monkeypatch, tmp_path):
    from ccc.exp003.feasibility import projection
    freeze, m, f, save, _ = freeze_fixture(monkeypatch, tmp_path)
    f['feasibility_budget']['projected_total_usd'] = .01
    with pytest.raises(ValueError, match='understates'):
        projection(m, f)
    f['feasibility_budget']['measured_cost_sha256'] = 'ab'*32
    with pytest.raises(ValueError, match='hash mismatch'):
        projection(m, f)


def test_launch_passes_measured_reservation_binding(monkeypatch, tmp_path):
    from types import SimpleNamespace
    from ccc.exp003 import modal_ctl, manifest
    freeze, m, f, save, _ = freeze_fixture(monkeypatch, tmp_path)
    monkeypatch.setattr(manifest, 'load', lambda _: m)
    monkeypatch.setattr(modal_ctl, 'SESSION_FILE', tmp_path/'absent-session')
    monkeypatch.setattr(modal_ctl.time, 'time', lambda: budget.HARD_STOP_EPOCH-10000)
    monkeypatch.setenv('EXP003_CPU', '4')
    monkeypatch.setenv('EXP003_MEM_MIB', '16384')
    def reserve(seconds, gpu, **kw):
        assert seconds == 5400 and gpu == 'L40S'
        assert kw['minimum_seconds'] == 4000 and kw['minimum_usd'] == 5
        assert kw['reconciled_prior_usd'] == 1 and kw['storage_usd'] == .1
        assert kw['binding']['manifest_sha256'] == digest(m)
        assert kw['binding']['measured_cost_sha256'] == f['feasibility_budget']['measured_cost_sha256']
        raise ValueError('dry-run reservation reached; no daemon')
    monkeypatch.setattr(budget, 'reserve_session', reserve)
    args = SimpleNamespace(development=False, manifest='synthetic', gpu='L40S', parallel=1,
                           scaledown=180, max_minutes=90, storage_usd=.1)
    with pytest.raises(ValueError, match='dry-run reservation reached'):
        modal_ctl.start(args)
