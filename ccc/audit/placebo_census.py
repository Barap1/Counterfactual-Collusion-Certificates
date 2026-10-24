"""DEV-only placebo availability census (amendment_v1.2.md §1.5). COUNTS ONLY.

For every DEV Tier A instance (2 strata x 20 cases x DEV seeds) the scripted source run is
replayed to the checkpoint exposure and the frozen §3.1 rule is applied to the pre-checkpoint
event log. No branch, continuation, outcome, effect size or status is computed or read.
Held-out seeds are refused by ``require_dev``.

Usage: python -m ccc.audit.placebo_census [--out docs/research/sci002/placebo_census.json] [--fx1]
"""
from collections import Counter, defaultdict
from dataclasses import replace
from fractions import Fraction
import json
from pathlib import Path
import sys

from .commitments import Extractor, world_aliases
from .placebo import select_placebo

ROOT = Path(__file__).resolve().parents[2]
WINDOWS = (Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
TRIGGER = 0.5


def family(case):
    return case[:2]


def census_world(world):
    from ccc.audit.gate_a import _schedule_seed
    from ccc.fixtures.native_replay import as_replay_fixture
    from ccc.fixtures.jira import native_policy
    from ccc.replay.engine import (record_source_run, scripted_factory, candidate_exposures, event_rows)
    safe = replace(world, case=world.mechanism if world.case.startswith('A6') else 'A4b' if world.case == 'A4a' else world.case)
    fx = as_replay_fixture(safe)
    fx.spec.seed = _schedule_seed(world.roles, world.order)
    fx.spec.base_cfg['experiment']['collusion']['agent_order'] = 'random'
    fx.policy_factory = lambda: native_policy(world)
    source = record_source_run(fx.spec, scripted_factory(fx.policy_factory))
    candidates = [e for e in candidate_exposures(source)
                  if e.sender == world.roles[0] and e.receiver == world.roles[1] and e.blackboard_id == '1']
    row = {'case': world.case, 'family': family(world.case), 'stratum': world.stratum, 'seed': world.seed,
           'wording_type': world.wording_type, 'fixture_version': world.fixture_version, 'eligible': bool(candidates)}
    if not candidates:
        return row
    e = min(candidates, key=lambda x: (x.first_exposure_turn, x.posted_turn))
    co = [x.event_id for x in candidates if x.first_exposure_turn == e.first_exposure_turn and x.event_id != e.event_id]
    e = replace(e, copy_event_ids=tuple(co))
    ext = Extractor(world_aliases(world.tasks), world.roles[2:])
    rows = event_rows(source)
    boards = [str(b.blackboard_id) for b in source.world.protocol.megaboard.blackboards if e.receiver in b.agents]
    row['k'] = len(e.masked_ids)
    by_window = {}
    for w in WINDOWS:
        sel = select_placebo(rows, e.masked_ids, e.sender, e.receiver, ext, boundary=e.first_exposure_turn,
                             private_board=e.blackboard_id, receiver_boards=boards, window=w)
        by_window[str(w)] = {'status': sel['status'], 'reason': sel['reason'], 'candidates': sel['candidates'],
                             'L_star': sel['L_star'], 'L_M': sel['L_M'], 'board_rank': sel['board_rank']}
    row['windows'] = by_window
    return row


def _safe(world):
    try:
        return census_world(world)
    except Exception as exc:  # reported, never swallowed silently
        return {'case': world.case, 'family': family(world.case), 'stratum': world.stratum, 'seed': world.seed,
                'eligible': False, 'error': f'{type(exc).__name__}: {exc}'}
    finally:
        # Native source worlds contain reference cycles and full snapshot histories.
        # Reclaim each source before another cell, especially beside a live experiment.
        import gc
        gc.collect()


def summarize(rows):
    out = {'instances': len(rows), 'errors': [r for r in rows if 'error' in r]}
    groups = defaultdict(list)
    for r in rows:
        groups[('family', r['family'])].append(r)
        groups[('case', r['case'])].append(r)
        groups[('stratum', r['stratum'])].append(r)
        groups[('wording', r.get('wording_type'))].append(r)
    table = {}
    for (kind, key), rs in sorted(groups.items(), key=lambda x: (x[0][0], str(x[0][1]))):
        elig = [r for r in rs if r.get('eligible')]
        entry = {'instances': len(rs), 'eligible': len(elig)}
        for w in WINDOWS:
            ok = sum(r['windows'][str(w)]['status'] == 'accepted' for r in elig)
            entry[f'available_{w}'] = ok
            entry[f'share_{w}'] = (ok / len(elig)) if elig else None
        entry['reasons_0.25'] = dict(Counter(r['windows']['1/4']['reason'] for r in elig))
        table[f'{kind}:{key}'] = entry
    out['table'] = table
    fam = {k.split(':')[1]: v for k, v in table.items() if k.startswith('family:')}
    out['family_share_0.25'] = {f: v['share_1/4'] for f, v in fam.items()}
    out['trigger_fires'] = any(v['share_1/4'] is not None and v['share_1/4'] < TRIGGER for v in fam.values())
    out['trigger_families'] = sorted(f for f, v in fam.items() if v['share_1/4'] is not None and v['share_1/4'] < TRIGGER)
    return out


def main(argv=None):
    from contextlib import ExitStack, redirect_stdout, redirect_stderr
    from unittest.mock import patch
    import multiprocessing
    import socket
    from concurrent.futures import ProcessPoolExecutor
    from ccc import paths
    from ccc.audit.gate_a import generate_dev, require_dev
    from ccc.fixtures.jira import CASES
    from ccc.fixtures.worlds import split_manifest
    argv = list(sys.argv[1:] if argv is None else argv)
    out = Path(argv[argv.index('--out') + 1]) if '--out' in argv else ROOT / 'docs/research/sci002/placebo_census.json'
    workers = int(argv[argv.index('--workers') + 1]) if '--workers' in argv else 1
    if not 1 <= workers <= 4:
        raise ValueError("census workers must be between 1 and 4")
    manifest = split_manifest()
    bounds = manifest['development']['world_seeds']
    worlds = []
    for stratum in ('crossed', 'naturalistic'):
        for case in CASES:
            for seed in range(bounds['start'], bounds['stop_exclusive']):
                require_dev(seed, manifest)
                offset = seed - bounds['start']
                base = 'A1a' if bool((offset % 2) ^ ((offset // 2) % 2)) else 'A3a'
                worlds.append(generate_dev(case, seed, manifest, stratum=stratum,
                                           invalid_base=base if case.startswith('A6') else 'A1a',
                                           **({'fixture_version': 'fx1'} if '--fx1' in argv else {})))
    with ExitStack() as stack:
        stack.enter_context(patch.object(paths, 'colosseum_root', return_value=ROOT / 'starter/collusion_hackathon/colosseum'))
        stack.enter_context(patch.object(paths, '_local_manifest', side_effect=AssertionError('secret manifest forbidden')))
        stack.enter_context(patch.object(socket.socket, 'connect', side_effect=AssertionError('network forbidden')))
        log = stack.enter_context((out.with_suffix('.log')).open('w'))
        stack.enter_context(redirect_stdout(log))
        stack.enter_context(redirect_stderr(log))
        pool = stack.enter_context(ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('fork')))
        rows = list(pool.map(_safe, worlds))
    result = {'schema': 'ccc.placebo_census.v1', 'phase': 'development', 'counts_only': True,
              'rows': rows, 'summary': summarize(rows)}
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + '\n')
    print(json.dumps({k: result['summary'][k] for k in ('instances', 'family_share_0.25', 'trigger_fires', 'trigger_families')}, indent=1))


if __name__ == '__main__':
    main()
