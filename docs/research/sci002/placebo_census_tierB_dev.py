"""DEV-only Tier-B placebo availability census (counts only). No continuation/outcome is read.
Run: python3 docs/research/sci002/placebo_census_tierB_dev.py  (from repo root)"""
import json, sys, glob, hashlib
from pathlib import Path
from fractions import Fraction
sys.path.insert(0, '.')
from ccc.audit.commitments import Extractor, world_aliases
from ccc.audit.placebo import select_placebo

ROOT = Path('docs/runner/exp001-live/worlds')
rows_out = []
for wd in sorted(ROOT.iterdir()):
    a = wd / 'attempt_0001'
    if 'dev' not in wd.name:
        raise SystemExit('DEV only')
    cp = json.load(open(a / 'checkpoint.json'))['data']
    ex = cp['exposure']
    cs = json.load(open(a / 'checkpoint_state.json'))['data']
    dyn, st = cs['dynamic'], cs['static']
    # first-seen snapshot cursor per event, as ccc.replay.engine.event_rows
    first = {}
    for f in sorted(glob.glob(str(a / 'source/snapshots/*.json'))):
        s = json.load(open(f))['data']
        d = json.loads(s['dynamic']) if isinstance(s['dynamic'], str) else s['dynamic']
        for b in d['megaboard']['blackboards']:
            for e in b['logs']:
                first.setdefault(e['id'], s['cursor'])
    rows = []
    for b in dyn['megaboard']['blackboards']:
        for e in b['logs']:
            rows.append({'id': e['id'], 'agent': e.get('agent'), 'kind': e.get('kind'), 'board': str(b['blackboard_id']),
                         'content': str((e.get('payload') or {}).get('content') or ''),
                         'turn_index': first[e['id']] - 1, 'seq': e.get('ts', 0)})
    outsiders = [x for x in st['agent_names'] if x not in st['colluders']]
    ext = Extractor(world_aliases({k: v for k, v in st['tasks'].items() if isinstance(v, dict)}), outsiders)
    rboards = [str(b['blackboard_id']) for b in dyn['megaboard']['blackboards'] if ex['receiver'] in b['agents']]
    E = [ex['event_id']] + list(ex.get('copy_event_ids') or [])
    boundary = ex['first_exposure_turn']
    r = {'world': wd.name, 'sender': ex['sender'], 'receiver': ex['receiver'], 'boundary': boundary, 'k': len(E)}
    for w in (Fraction(1, 10), Fraction(1, 4), Fraction(1, 2)):
        sel = select_placebo(rows, E, ex['sender'], ex['receiver'], ext, boundary=boundary,
                             private_board=ex['blackboard_id'], receiver_boards=rboards, window=w)
        r[str(w)] = {k: sel[k] for k in ('status', 'reason', 'candidates', 'L_star', 'L_M')}
    # diagnostics (counts only): sender communication events before boundary, by board, and how many fail filter (v)
    pre = [x for x in rows if x['kind'] == 'communication' and x['agent'] == ex['sender'] and x['id'] not in E and x['turn_index'] < boundary]
    r['sender_pre_comm_not_Estar'] = len(pre)
    r['of_which_content_filtered'] = sum(ext.has_content(x['content'], x['agent']) for x in pre)
    r['sender_pre_comm_by_board'] = {b: sum(1 for x in pre if x['board'] == b) for b in sorted({x['board'] for x in pre})}
    rows_out.append(r)
print(json.dumps(rows_out, indent=1))
