#!/usr/bin/env python3
"""Independent, read-only reconstruction of the preregistered F/K headline.

Only Python's standard library is used. No project modules are imported.
"""
import argparse
from contextlib import contextmanager
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys


def read(path, hashes):
    raw = path.read_bytes()
    hashes[str(path)] = hashlib.sha256(raw).hexdigest()
    obj = json.loads(raw)
    data = obj['data']
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'),
                           ensure_ascii=False).encode('utf-8')
    if obj['sha256'] != hashlib.sha256(canonical).hexdigest():
        raise ValueError(f'evidence hash mismatch: {path}')
    return data


def optional(path, hashes):
    return read(path, hashes) if path.exists() else {}


def safe_id(value):
    if not isinstance(value, str) or value in ('', '.', '..') or '/' in value or '\\' in value:
        raise ValueError(f'unsafe identifier: {value!r}')
    return value


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'invalid reward: {value!r}')
    return Fraction(str(value))


def average(values):
    return sum(values, Fraction()) / len(values) if values else None


def exact_sign_flip(values):
    """Enumerate all signs, including zeros; ties are counted against H1."""
    if not values:
        return dict(p=None, numerator=0, denominator=0)
    if len(values) > 20:
        raise ValueError('exact sign-flip limited to 20 pairs (protocol has at most 10)')
    observed = sum(values, Fraction())
    count = sum(sum((s * x for s, x in zip(signs, values)), Fraction()) >= observed
                for signs in itertools.product((-1, 1), repeat=len(values)))
    return dict(p=count / (2 ** len(values)), numerator=count, denominator=2 ** len(values))


def counts():
    return dict(attempted=0, complete=0, failed=0, invalid=0, interrupted=0, not_run=0)


def classify(branch):
    status = branch.get('status')
    outcome = branch.get('outcomes') or {}
    if status == 'not_run':
        return 'not_run'
    if status == 'invalid' or outcome.get('status') in ('invalid', 'context_overflow'):
        return 'invalid'
    if status == 'failed' or outcome.get('status') == 'failed':
        return 'failed'
    if status in ('valid', 'complete') and outcome.get('status') == 'complete':
        return 'complete'
    if status is None or status in ('interrupted', 'running'):
        return 'interrupted'
    raise ValueError(f'unrecognized branch status: {status!r}/{outcome.get("status")!r}')


def omean(branch, checkpoint):
    # Exposure endpoints are the two designated coalition members, not selected
    # by reward or behaviour. All other agents are outsiders.
    exposure = checkpoint['exposure']
    coalition = {exposure['sender'], exposure['receiver']}
    rewards = branch['outcomes']['agent_rewards']
    if len(coalition) != 2 or len(rewards) != 4 or not coalition <= rewards.keys():
        raise ValueError('expected four agents and two distinct coalition endpoints')
    outsiders = sorted(rewards.keys() - coalition)
    return average([number(rewards[a]) for a in outsiders])


def attempt_record(path, hashes, arms):
    begin = read(path / 'begin.json', hashes)
    result = optional(path / 'result.json', hashes)
    checkpoint = optional(path / 'checkpoint.json', hashes)
    selection = optional(path / 'selection.json', hashes)
    branches = []
    tallies = {a: counts() for a in arms}
    embedded = {(b['arm'], b['replicate']): b for b in result.get('branches', [])}
    seen = set()
    branch_root = path / 'branches'
    if branch_root.exists():
        for directory in sorted(branch_root.iterdir()):
            if not directory.is_dir():
                continue
            bbegin = optional(directory / 'begin.json', hashes)
            branch = optional(directory / 'result.json', hashes)
            if not branch and not bbegin:
                raise ValueError(f'branch has neither begin nor result: {directory}')
            arm = branch.get('arm', bbegin.get('arm'))
            rep = branch.get('replicate', bbegin.get('replicate'))
            if arm not in tallies or not isinstance(rep, int) or isinstance(rep, bool) or rep < 0:
                raise ValueError(f'bad branch identity: {directory}')
            key = (arm, rep)
            if key in seen:
                raise ValueError(f'duplicate branch: {key}')
            seen.add(key)
            if key in embedded and branch != embedded[key]:
                raise ValueError(f'branch/summary disagreement: {directory}')
            category = classify(branch)
            tallies[arm][category] += 1
            tallies[arm]['attempted'] += category != 'not_run'
            value = omean(branch, checkpoint) if category == 'complete' else None
            branches.append(dict(arm=arm, replicate=rep, status=category,
                                 Omean=value))
    if embedded.keys() - seen:
        raise ValueError(f'summary branches missing standalone evidence: {path}')
    reason = (result.get('selection') or selection).get('reason')
    values = {a: [b['Omean'] for b in branches if b['arm'] == a and b['status'] == 'complete']
              for a in ('F', 'K')}
    means = {a: average(v) for a, v in values.items()}
    tau = None
    definition = 'undefined'
    status = result.get('status', 'interrupted')
    if status == 'ineligible' and reason in ('no_exposure', 'post_decision'):
        tau, definition = Fraction(), 'no_op_zero'
    elif status == 'complete' and checkpoint and all(means[a] is not None for a in ('F', 'K')):
        tau = means['K'] - means['F']
        definition = 'complete_continuations'
    return dict(attempt=path.name, world=begin.get('world'), world_status=status,
                ineligible_reason=reason, definition=definition, counts=tallies,
                branches=branches, arm_Omean=means, tau_O=tau)


@contextmanager
def collection_guard(root):
    """Hold a shared lock while reading; a live collector uses an exclusive one."""
    import fcntl
    lock = root / '.collector.lock'
    stream = lock.open('rb') if lock.exists() else None
    try:
        if stream:
            try:
                fcntl.flock(stream, fcntl.LOCK_SH | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ValueError('collection is active; refusing input') from exc
        yield
    finally:
        if stream:
            stream.close()


def reproduce(root):
    root = Path(root).resolve()
    hashes = {}
    with collection_guard(root):
        manifest = read(root / 'manifest.json', hashes)
        arms = manifest['arms']
        if not {'F', 'K'} <= set(arms) or len(arms) != len(set(arms)):
            raise ValueError('manifest must have distinct arms including F and K')
        worlds, attempts, paired = [], [], {}
        for world in manifest['worlds']:
            wid = safe_id(world['id'])
            regime = world['regime']
            if regime not in ('B1', 'B2'):
                raise ValueError(f'unsupported primary regime: {regime}')
            # Frozen matrix pairs B1/B2 by generator seed, not by string slicing.
            pair = str(world['seed'])
            if regime in paired.setdefault(pair, {}):
                raise ValueError(f'duplicate seed/regime: {pair}/{regime}')
            directory = root / 'worlds' / wid
            paths = sorted(directory.glob('attempt_[0-9][0-9][0-9][0-9]')) if directory.exists() else []
            records = [attempt_record(p, hashes, arms) for p in paths]
            for record in records:
                if record['world'] != world:
                    raise ValueError(f'world identity mismatch: {wid}/{record["attempt"]}')
                attempts.append(dict(world_id=wid, **record))
            final = records[-1] if records else None
            if final and final['world_status'] in ('interrupted', 'running'):
                raise ValueError(f'unfinished final world attempt: {wid}')
            row = dict(world_id=wid, pair_id=pair, regime=regime,
                       attempted=bool(records), final_attempt=final['attempt'] if final else None,
                       world_status=final['world_status'] if final else 'unrun',
                       tau_O=final['tau_O'] if final else None,
                       definition=final['definition'] if final else 'undefined',
                       counts=final['counts'] if final else {a: counts() for a in arms})
            worlds.append(row)
            paired[pair][regime] = row
        pairs = []
        for pair, regimes in sorted(paired.items()):
            b1, b2 = regimes.get('B1'), regimes.get('B2')
            defined = b1 is not None and b2 is not None and b1['tau_O'] is not None and b2['tau_O'] is not None
            pairs.append(dict(pair_id=pair, d_w=b1['tau_O'] - b2['tau_O'] if defined else None))
        ds = [p['d_w'] for p in pairs if p['d_w'] is not None]
        return dict(schema='rev001a.independent.v1', input=str(root),
                    label='exploratory; numeric reproduction only',
                    Delta=average(ds), n_defined_pairs=len(ds),
                    n_nonzero_pairs=sum(d != 0 for d in ds), sign_flip=exact_sign_flip(ds),
                    within_regime_tau_O={r: average([w['tau_O'] for w in worlds
                                            if w['regime'] == r and w['tau_O'] is not None])
                                         for r in ('B1', 'B2')},
                    worlds=worlds, pairs=pairs, attempts=attempts, input_sha256=hashes)


def json_default(value):
    if isinstance(value, Fraction):
        return float(value)
    raise TypeError(type(value).__name__)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = reproduce(args.input)
        print(json.dumps(result, indent=2, sort_keys=True, default=json_default, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'independent reproduction refused: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
