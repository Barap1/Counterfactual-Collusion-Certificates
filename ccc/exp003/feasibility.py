"""Pure offline measured-cost projection; no measurements are supplied by code."""
import json
import math
from .manifest import digest, file_hash, repo_file
from . import budget


def workload_sha256(m):
    return digest({'model': {k: v for k, v in m['model'].items() if k != 'base_url'},
                   'continuations_per_arm': m['continuations_per_arm'], 'arms': m['arms']})


def projection(m, f):
    b = f['feasibility_budget']
    if not isinstance(b.get('measured_cost_artifact'), str):
        raise ValueError('measured-cost file required; placeholder refuses launch')
    path = repo_file(b['measured_cost_artifact'])
    if file_hash(path) != b.get('measured_cost_sha256'):
        raise ValueError('measured-cost file hash mismatch')
    v = json.loads(path.read_text())
    if v.get('status') != 'measured' or v.get('measured_dev_valid') is not True:
        raise ValueError('measured-cost placeholder/unvalidated spike refuses launch')
    config = v.get('launch_config', {})
    if set(config) != {'gpu', 'cpu', 'mem_gib', 'parallel', 'scaledown'}:
        raise ValueError('complete measured launch configuration required')
    if v.get('workload_sha256') != workload_sha256(m):
        raise ValueError('measured workload configuration mismatch')
    if config['gpu'] not in budget.GPU_USD_PER_H:
        raise ValueError('measured GPU type required')
    for k in ('cpu', 'mem_gib', 'parallel', 'scaledown'):
        if type(config[k]) not in (float, int) or not math.isfinite(config[k]) or config[k] <= 0:
            raise ValueError('invalid measured launch configuration')
    if type(config['parallel']) is not int or type(config['scaledown']) is not int:
        raise ValueError('integer parallel/scaledown configuration required')
    for k in ('seconds_per_regime_world', 'cost_per_regime_world_usd', 'startup_seconds',
              'startup_cost_usd', 'calls_per_regime_world', 'canary_calls_per_regime_world', 'startup_calls'):
        x = v.get(k)
        if type(x) not in (float, int) or not math.isfinite(x) or x < 0:
            raise ValueError('finite measured-cost parameter required: ' + k)
    if v['seconds_per_regime_world'] <= 0 or v['cost_per_regime_world_usd'] <= 0 or v.get('safety_margin') != budget.MARGIN:
        raise ValueError('positive measured per-world cost/time with 20% margin required')
    rate = budget.container_rate(config['gpu'], config['cpu'], config['mem_gib']) * budget.MARGIN / 3600
    if (v['cost_per_regime_world_usd'] < v['seconds_per_regime_world'] * rate or
            v['startup_cost_usd'] < v['startup_seconds'] * rate):
        raise ValueError('measured costs understate pinned resource rate plus margin')
    for bk, vk in [('calls_per_regime_world', 'calls_per_regime_world'),
                   ('canary_calls_per_regime_world', 'canary_calls_per_regime_world'),
                   ('startup_calls', 'startup_calls'), ('gpu_seconds_per_regime_world', 'seconds_per_regime_world')]:
        if b[bk] != v[vk]:
            raise ValueError('freeze differs from measured-cost parameter: ' + bk)
    # Always project all 32 scheduled pairs; no outcome-dependent shortening.
    seconds = v['startup_seconds'] + 64 * v['seconds_per_regime_world']
    cost = v['startup_cost_usd'] + 64 * v['cost_per_regime_world_usd'] + budget.SHUTDOWN_SECONDS * rate
    if b['projected_total_seconds'] < seconds or b['projected_total_usd'] < cost:
        raise ValueError('frozen projection understates measured full-block cost/time')
    cost = b['projected_total_usd']
    total = cost + b['reconciled_prior_usd'] + b['storage_usd']
    if total >= budget.OPERATING_STOP or total >= budget.TOTAL_CAP:
        raise ValueError('measured full-block projection reaches operating stop or total cap')
    return dict(seconds=b['projected_total_seconds'], cost=cost, config=config,
                measured_cost_sha256=b['measured_cost_sha256'])


def validate_session(m, f, row, *, now):
    p = projection(m, f)
    if row.get('launch_config') != p['config'] or row.get('manifest_sha256') != digest(m) or row.get('measured_cost_sha256') != p['measured_cost_sha256']:
        raise ValueError('active session is not bound to measured frozen configuration')
    if row['deadline_epoch'] - now < p['seconds']:
        raise ValueError('active reserved lifetime cannot cover projected block including startup')
    if row['reserved_usd'] < p['cost']:
        raise ValueError('active reservation cannot cover measured projected block')
    return p
