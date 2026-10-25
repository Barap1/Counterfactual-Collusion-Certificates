"""Offline release admission. ORCH supplies FREEZE.json; this module never creates it."""
import json
import math
import re
from pathlib import Path
from .manifest import ROOT, digest, file_hash, repo_file, fresh_pairs

FREEZE = 'docs/enh/exp003/FREEZE.json'


def _hash(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value) or len(set(value)) == 1:
        raise ValueError('missing or placeholder SHA256')
    return value


def verify_freeze(m):
    path = repo_file(FREEZE)
    if not path.is_file():
        raise ValueError('ORCH FREEZE.json required; candidate is not admission')
    if file_hash(path) != _hash(m.get('freeze_sha256')):
        raise ValueError('FREEZE.json hash mismatch')
    f = json.loads(path.read_text())
    commit = m.get('director_freeze_commit', '')
    if not re.fullmatch('[0-9a-f]{40,64}', commit) or len(set(commit)) == 1 or f.get('director_freeze_commit') != commit:
        raise ValueError('actual director freeze commit required')
    if f.get('approved') is not True or f.get('pending') != [] or f.get('backend') != m.get('backend'):
        raise ValueError('freeze approval/backend/release gates missing')
    if f.get('protocol_artifact') != m['protocol_artifact'] or f.get('protocol_sha256') != m['protocol_sha256']:
        raise ValueError('protocol freeze binding mismatch')
    if file_hash(repo_file(f['protocol_artifact'])) != _hash(f['protocol_sha256']):
        raise ValueError('protocol bytes changed')
    if f.get('manifest_config_sha256') != digest({k: v for k, v in m.items() if k != 'freeze_sha256'}):
        raise ValueError('frozen run configuration mismatch')
    inventory = f.get('code_sha256', {})
    # Retain the reviewed dependency inventory and require every current EXP-003 module.
    candidate = json.loads(repo_file('docs/enh/exp003/FREEZE_candidate.json').read_text())
    reviewed = candidate['code_sha256']
    if not candidate.get('evidence_sha256', {}).keys() <= f.get('evidence_sha256', {}).keys():
        raise ValueError('incomplete evidence inventory')
    required = set(reviewed) | {str(p.relative_to(ROOT)) for p in (ROOT / 'ccc/exp003').glob('*.py')}
    if not required <= inventory.keys():
        raise ValueError('incomplete code inventory')
    for group in (inventory, f.get('evidence_sha256', {})):
        for name, expected in group.items():
            if file_hash(repo_file(name)) != _hash(expected):
                raise ValueError(f'frozen artifact changed: {name}')
    artifacts = {}
    for prefix in ('seed_exclusion', 'skip_ledger', 'seed_list'):
        name, expected = f.get(prefix + '_artifact'), _hash(f.get(prefix + '_sha256'))
        if file_hash(repo_file(name)) != expected or m.get(prefix + '_sha256') != expected:
            raise ValueError(f'{prefix} hash mismatch')
        artifacts[prefix] = json.loads(repo_file(name).read_text())
    excluded = artifacts['seed_exclusion']
    if not isinstance(excluded, list) or any(type(s) is not int for s in excluded) or len(excluded) != len(set(excluded)):
        raise ValueError('audited exclusion inventory must be unique integer seeds')
    expected = fresh_pairs(commit, excluded, 32)
    if m['worlds'] != expected or f.get('pair_order') != expected:
        raise ValueError('pair order differs from frozen 32-slot stream')
    if artifacts['seed_list'] != [w['seed'] for w in expected[::2]]:
        raise ValueError('seed list differs from stream')
    from .manifest import stream_skips
    if artifacts['skip_ledger'] != stream_skips(commit, excluded, 32):
        raise ValueError('skip ledger differs from stream')
    b = f.get('feasibility_budget', {})
    for key in ('calls_per_regime_world', 'canary_calls_per_regime_world', 'gpu_seconds_per_regime_world',
                'projected_total_usd', 'projected_total_seconds', 'reconciled_prior_usd', 'storage_usd', 'startup_calls'):
        v = b.get(key)
        if type(v) not in (int, float) or not math.isfinite(v) or v < 0:
            raise ValueError(f'measured feasibility field required: {key}')
    calls = 64 * (b['calls_per_regime_world'] + b['canary_calls_per_regime_world']) + b['startup_calls']
    if b.get('measured_dev_valid') is not True or calls <= 0 or m['max_requests'] < calls or f.get('max_requests') != m['max_requests']:
        raise ValueError('measured DEV/source+canary request budget required')
    if b['gpu_seconds_per_regime_world'] <= 0 or b['projected_total_seconds'] <= 0 or b['projected_total_usd'] <= 0 or b['projected_total_usd'] + b['reconciled_prior_usd'] + b['storage_usd'] > 45:
        raise ValueError('primary-block feasibility exceeds operating budget or is unmeasured')
    if m['backend'] == 'modal':
        from .feasibility import projection
        projection(m, f)
    return f


def verify_launch_window(m, now=None):
    import time
    from .budget import HARD_STOP_EPOCH, SHUTDOWN_SECONDS
    f = verify_freeze(m)
    now = time.time() if now is None else now
    if now + f['feasibility_budget']['projected_total_seconds'] + SHUTDOWN_SECONDS > HARD_STOP_EPOCH:
        raise ValueError('projected primary block cannot finish before absolute deadline')
    return f


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest', type=Path)
    a = p.parse_args()
    from .manifest import validate
    validate(json.loads(a.manifest.read_text()))
    print('offline freeze admission passed; no inference authorized')


if __name__ == '__main__':
    main()
