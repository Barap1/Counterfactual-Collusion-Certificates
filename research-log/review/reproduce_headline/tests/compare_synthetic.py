"""Compare JSON artifacts only; never imports or calls the reference implementation."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ours = json.loads((ROOT / 'synthetic_independent.json').read_text())
reference = ROOT / 'synthetic_blackbox'


def load(name):
    return json.loads((reference / name).read_text())


checks = []
disagreements = []


def check(name, actual, expected):
    checks.append(name)
    if actual != expected:
        disagreements.append(dict(check=name, independent=actual, blackbox=expected))


# This comparator is intentionally restricted to the labelled readiness fixture.
assert Path(ours['input']).name == 'synthetic_input'
assert all(w['world_id'].startswith('SYN') for w in ours['worlds'])
study = next(r for r in load('effects_study.json') if r['effect'] == 'Delta_total')
check('Delta', ours['Delta'], study['estimate'])
check('sign_flip.p', ours['sign_flip']['p'], study['p_raw'])
check('n_defined_pairs', ours['n_defined_pairs'], study['n_independent'])
for row in load('world_effects.json'):
    world = next(w for w in ours['worlds'] if w['pair_id'] == row['world_id'] and w['regime'] == row['regime'])
    check(f"tau_O:{world['world_id']}", world['tau_O'], row['tau_O'])
for row in load('figure_data/fig_delta_by_world.json'):
    pair = next(p for p in ours['pairs'] if p['pair_id'] == row['world_id'])
    check(f"d_w:{pair['pair_id']}", pair['d_w'], row['d_w'])
for row in load('continuations.json'):
    if row['arm'] not in ('F', 'K'):
        continue
    attempt = next(a for a in ours['attempts'] if a['world_id'] == row['checkpoint_id'])
    branch = next(b for b in attempt['branches'] if b['arm'] == row['arm'] and b['replicate'] == row['rep'])
    check(f"Omean:{row['attempt_id']}", branch['Omean'], row['Omean'])
# Reference continuation attempts omit unscheduled N; its schedule table retains them.
ref_attempts = load('attempts.json')
ref_schedule = load('scheduled_statuses.json')
for world in ours['worlds']:
    for arm, count in world['counts'].items():
        rows = [r for r in ref_attempts if r['checkpoint_id'] == world['world_id'] and r['arm'] == arm]
        prefix = f"counts:{world['world_id']}:{arm}:"
        check(prefix + 'attempted', count['attempted'], len(rows))
        for status in ('complete', 'failed', 'invalid', 'interrupted'):
            check(prefix + status, count[status], sum(r['status'] == status for r in rows))
        skipped = sum(r.get('kind') == 'unscheduled_arm' and r.get('checkpoint_id') == world['world_id']
                      and r.get('arm') == arm and r.get('status') == 'not_run' for r in ref_schedule)
        check(prefix + 'not_run', count['not_run'], skipped)
result = dict(synthetic_only=True, checks=len(checks), disagreements=disagreements,
              Delta=ours['Delta'], sign_flip=ours['sign_flip'],
              d_w=[p['d_w'] for p in ours['pairs']],
              reference=str(reference.relative_to(ROOT)))
(ROOT / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
raise SystemExit(bool(disagreements))
