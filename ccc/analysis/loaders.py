"""Read only named analysis contracts or finished legacy runner metadata."""
import hashlib
import json
import math
import os
from pathlib import Path

COMPLETE = {'complete', 'complete_noncommit', 'complete_refusal'}
STATUSES = COMPLETE | {'infra_timeout','infra_rate_limit','infra_malformed_provider','infra_crash',
    'infra_wrong_route','malformed_tool_output','context_overflow','invalid_restore','session_break','cancelled'}
ROOT = Path(__file__).resolve().parents[2]


class ValidationError(ValueError):
    def __init__(self, problems):
        self.problems = problems
        super().__init__('; '.join(problems))


RUNNER_SIGNATURE = ('.collector.lock','run_manifest.json','worlds')
WATCHDOG_MARKERS = ('WATCHDOG_EXIT.json','WATCHDOG_STOP.json')
TERMINAL_MARKERS = WATCHDOG_MARKERS + ('run_end.json',)


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _marker_pid(marker):
    try:
        pid = json.loads(marker.read_bytes()).get('run_pid')
    except (OSError, ValueError, AttributeError):
        return None
    return pid if isinstance(pid, int) and not isinstance(pid, bool) else None


def active_input_problems(root, watchdog_dir=None):
    """Return (problems, warnings) for runner output.

    A lock is stale only when a watchdog marker exists, the run is not alive, and
    the lock predates the marker when no pid is recorded.
    Stale locks are reported as warnings, never refusals.
    """
    root = Path(root)
    if not any((root/name).exists() for name in RUNNER_SIGNATURE): return [], []
    marker_dirs = [root, root.with_name(root.name + '.watchdog')]
    if watchdog_dir is not None:
        marker_dirs.append(Path(watchdog_dir))
    markers = [directory/name for directory in marker_dirs for name in WATCHDOG_MARKERS
               if (directory/name).exists()]
    lock = root/'.collector.lock'
    if lock.exists():
        if not markers: return ['active experiment inputs forbidden: .collector.lock present'], []
        marker = max(markers, key=lambda m: m.stat().st_mtime)
        pid = _marker_pid(marker)
        if pid is not None:
            if _pid_alive(pid): return ['active experiment inputs forbidden: .collector.lock held by live pid %d' % pid], []
        elif lock.stat().st_mtime >= marker.stat().st_mtime:
            return ['active experiment inputs forbidden: .collector.lock newer than terminal marker'], []
        return [], ['stale_lock_ignored: %s (marker %s, run_pid %s not alive)' % (lock.name, marker.resolve(), pid)]
    if not markers and not (root/'run_end.json').exists():
        return ['active experiment inputs forbidden: no terminal run record'], []
    return [], []


class Reader:
    def __init__(self, root, watchdog_dir=None):
        self.root = Path(root).resolve()
        problems, self.warnings = active_input_problems(self.root, watchdog_dir=watchdog_dir)
        if problems: raise ValidationError(problems)
        self.hashes = {}

    def read(self, path, lines=False):
        path = Path(path).resolve()
        if not path.is_relative_to(self.root):
            raise ValidationError(['artifact path escapes input root'])
        if path.name in ('.env','compute.env','instances.jsonl') or path.name.endswith('.local.json'):
            raise ValidationError(['forbidden analysis input: '+path.name])
        data = path.read_bytes()
        self.hashes[str(path.relative_to(self.root))] = hashlib.sha256(data).hexdigest()
        if lines:
            return [json.loads(line) for line in data.splitlines() if line.strip()]
        value = json.loads(data)
        if isinstance(value,dict) and set(value) == {'data','sha256'}:
            encoded = json.dumps(value['data'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
            if hashlib.sha256(encoded).hexdigest() != value['sha256']:
                raise ValidationError(['envelope hash mismatch: '+str(path)])
            return value['data']
        return value


def sham_selected(checkpoint_id):
    return int(hashlib.sha256(('ccc.sham.v1|'+checkpoint_id).encode()).hexdigest(),16)%2 == 0


def metrics(row):
    if row['status'] not in COMPLETE:
        return dict(Omean=None, Cmean=None, W=None, A=None, missing=True)
    rewards, roles = row['rewards'], row['roles']
    o = [rewards[a] for a in rewards if roles[a] == 'outsider']
    c = [rewards[a] for a in rewards if roles[a] == 'coalition']
    if len(o) != 2 or len(c) != 2:
        raise ValueError('exactly two outsiders and two coalition agents required')
    O, C, W = sum(o)/2, sum(c)/2, sum(rewards.values())
    assert abs(W-2*C-2*O) < 1e-9
    return dict(Omean=O,Cmean=C,W=W,A=C-O,missing=False)


def final_attempts(rows):
    selected = {}
    for r in rows:
        key = (r['checkpoint_id'],r['arm'],r['rep'])
        if key not in selected or r['attempt_no'] > selected[key]['attempt_no']:
            selected[key] = r
    return [selected[k] for k in sorted(selected)]


def _legacy(reader, manifest):
    if manifest.get('phase') != 'development':
        raise ValidationError(['legacy adapter is DEV only'])
    checkpoints, rows, events, scheduled = [], [], [], []
    manifest = dict(manifest, label='DEV/pilot', legacy=True)
    counts = manifest['continuations_per_arm']
    manifest['continuations_by_arm'] = counts if isinstance(counts,dict) else {arm:counts for arm in manifest['arms']}
    for world_dir in sorted((reader.root/'worlds').glob('*')):
        if not world_dir.is_dir(): continue
        attempts = sorted(world_dir.glob('attempt_*'))
        cp = None
        for attempt_no, directory in enumerate(attempts, 1):
            begin = reader.read(directory/'begin.json')
            world = begin['world']
            result = reader.read(directory/'result.json') if (directory/'result.json').exists() else {'status':'cancelled','branches':[]}
            checkpoint = reader.read(directory/'checkpoint.json') if (directory/'checkpoint.json').exists() else {}
            exposure = checkpoint.get('exposure',{})
            cid = world_dir.name
            cp = {'checkpoint_id':cid,'world_id':str(world['seed']),'regime':world['regime'],
                  'eligible':bool(exposure),'ineligible_reason':result.get('ineligible_reason','restore_fail') if not exposure else None,
                  'receiver':exposure.get('receiver'),'sender':exposure.get('sender'),
                  'info_bearing':True,'flags':{},'v_checks':{},'n_subset':False,
                  'placebo_kind':'N_v1.1_deprecated','legacy':True}
            branches=list(result.get('branches',[]))
            known={(b['arm'],b['replicate']) for b in branches}
            for branch_dir in sorted((directory/'branches').glob('*')):
                if not (branch_dir/'begin.json').exists(): continue
                branch_begin=reader.read(branch_dir/'begin.json')
                if (branch_begin['arm'],branch_begin['replicate']) in known: continue
                if (branch_dir/'result.json').exists(): branches.append(reader.read(branch_dir/'result.json'))
                else: branches.append(dict(branch_begin,status='cancelled',outcomes={}))
            for branch in branches:
                outcome = branch.get('outcomes',{})
                rewards = outcome.get('agent_rewards',{})
                pair = {exposure.get('sender'),exposure.get('receiver')}
                status = outcome.get('status','infra_crash') if branch['status']=='valid' else branch['status'] if branch['status'] in STATUSES else 'invalid_restore'
                if status not in STATUSES: status = 'infra_crash'
                checks = branch.get('checks',[])
                for check in checks:
                    if check['status']=='fail': cp['v_checks'][check['id']]='fail'
                    cp['flags'].update({f:True for f in check.get('details',{}).get('flags',[])})
                rows.append({'attempt_id':f'{cid}/{attempt_no}/{branch["arm"]}/{branch["replicate"]}',
                    'checkpoint_id':cid,'arm':branch['arm'],'rep':branch['replicate'],'attempt_no':attempt_no,
                    'status':status,'runner_status':branch['status'],'load_session_id':result.get('load_session',begin.get('load_session')),
                    'rewards':rewards,'roles':{a:'coalition' if a in pair else 'outsider' for a in rewards},
                    'committed':outcome.get('assignment',{}),'noncommit_agents':[a for a in rewards if a not in outcome.get('assignment',{})],
                    'model_resolved':manifest['model']['requested_id'],'cost_usd':None,'context_overflow':False,
                    'v3_pass':all(x['status']!='fail' for x in checks if x['id']=='V3')})
            # Retain interrupted world attempts even if no branch result survived.
            if not result.get('branches'):
                scheduled.append({'checkpoint_id':cid,'attempt_no':attempt_no,'status':result['status'],'kind':'world_attempt'})
            budget = directory/'budget.jsonl'
            if budget.exists(): events.extend(reader.read(budget, lines=True))
        if cp: checkpoints.append(cp)
    resolved={e.get('model_resolved') for e in events if e.get('event')=='attempt_end' and e.get('model_resolved') is not None}
    if len(resolved)>1 or (resolved and resolved!={manifest['model']['requested_id']}): raise ValidationError(['invalid_batch: mixed model in event ledger'])
    if rows and not resolved: raise ValidationError(['legacy DEV requires recorded model identity in event ledger'])
    manifest['model'] = dict(manifest['model'],resolved_id=next(iter(resolved)) if resolved else None,resolved_id_source='event ledger')
    seen = {c['checkpoint_id'] for c in checkpoints}
    for w in manifest.get('worlds',[]):
        if w['id'] not in seen: scheduled.append({'checkpoint_id':w['id'],'status':'unrun','kind':'scheduled_world'})
    return manifest, checkpoints, rows, events, scheduled


def validate(manifest, checkpoints, rows, strict=True):
    problems, warnings = [], []
    def require(obj, fields, where):
        for field in fields:
            if field not in obj: problems.append(where+': missing '+field)
    require(manifest,['experiment_id','phase','protocol_sha256','model','continuations_by_arm','policy'],'manifest')
    if manifest.get('phase') not in ('development','holdout'): problems.append('invalid phase')
    if not isinstance(manifest.get('continuations_by_arm'),dict): problems.append('continuations_by_arm must be a map')
    elif any(not isinstance(n,int) or isinstance(n,bool) or n<0 for n in manifest['continuations_by_arm'].values()): problems.append('invalid arm count')
    if strict:
        require(manifest,['stat001_hash','frozen','arms','n_subset_seed','branch_order_seed','sampling_seed'],'manifest')
        require(manifest.get('model',{}),['requested_id','resolved_id','parameters'],'model')
    if manifest.get('policy',{}).get('new_out_of_pocket_usd') != 0: problems.append('budget policy must be zero')
    if manifest.get('phase') == 'holdout' and not manifest.get('runner_adapter'):
        if manifest.get('frozen') is not True: problems.append('holdout must be frozen')
        for key, path in [('stat001_hash',ROOT/'docs/stats/stage2_addendum.json'),('protocol_sha256',ROOT/'docs/research/sci002/protocol.md')]:
            if not path.exists() or manifest.get(key) != hashlib.sha256(path.read_bytes()).hexdigest():
                problems.append('holdout hash mismatch: '+key)
    units=[(c.get('world_id'),c.get('regime')) for c in checkpoints]
    if len(units)!=len(set(units)): problems.append('multiple checkpoints per world/regime are not registered')
    ids = [c['checkpoint_id'] for c in checkpoints]
    if len(ids) != len(set(ids)): problems.append('duplicate checkpoint')
    seen, attempt_ids = set(), set()
    for r in rows:
        require(r,['attempt_id','checkpoint_id','arm','rep','attempt_no','status','load_session_id','rewards','roles','committed','noncommit_agents','model_resolved'], 'attempt')
        if strict:
            require(r,['n_calls','tokens_prompt','tokens_completion','latency_ms_total','latency_ms_p95','context_overflow','v3_pass','leak','resend','cost_usd'],'attempt')
        if not isinstance(r.get('rep'),int) or r.get('rep',-1)<0 or not isinstance(r.get('attempt_no'),int) or not 1<=r.get('attempt_no',0)<=2: problems.append('invalid replicate/attempt index')
        key = (r.get('checkpoint_id'),r.get('arm'),r.get('rep'),r.get('attempt_no'))
        if key in seen or r.get('attempt_id') in attempt_ids: problems.append('duplicate attempt')
        seen.add(key); attempt_ids.add(r.get('attempt_id'))
        if r.get('checkpoint_id') not in ids: problems.append('unknown checkpoint')
        if any(earlier.get('status') in COMPLETE and earlier.get('checkpoint_id')==r.get('checkpoint_id') and earlier.get('arm')==r.get('arm') and earlier.get('rep')==r.get('rep') and earlier.get('attempt_no',0)<r.get('attempt_no',0) for earlier in rows): problems.append('behavioural outcomes must not be retried')
        if r.get('status') not in STATUSES: problems.append('unknown status: '+str(r.get('status')))
        if r.get('arm') not in ('F','K','S','N','C'): problems.append('unknown arm')
        if r.get('model_resolved') != manifest.get('model',{}).get('resolved_id'): problems.append('invalid_batch: mixed model')
        if r.get('phase',manifest.get('phase')) != manifest.get('phase'): problems.append('mixed phases')
        if r.get('status') in COMPLETE:
            values = r.get('rewards',{})
            if len(values)!=4 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in values.values()):
                problems.append('complete rewards must be four finite numbers')
            else:
                try: metrics(r)
                except (ValueError,KeyError): problems.append('invalid roles/rewards')
            for a in r.get('noncommit_agents',[]):
                if values.get(a) != 0: problems.append('noncommit reward must be zero')
            if r.get('status')=='complete_refusal' and not r.get('noncommit_agents'): problems.append('refusal subtype requires skip/zero agents')
            if r.get('status')=='complete_noncommit' and not r.get('noncommit_agents'): problems.append('noncommit subtype requires noncommit agents')
    for cp in checkpoints:
        if strict:
            require(cp,['world_id','regime','eligible','ineligible_reason','sender','receiver','t_star','estar_event_ids','n_subset','info_bearing','flags','v_checks'],'checkpoint')
            if set(cp.get('v_checks',{})) != {f'V{i}' for i in range(1,8)}: problems.append('V1..V7 required')
            if any(v not in ('pass','fail','na') for v in cp.get('v_checks',{}).values()): problems.append('invalid V check value')
        if not isinstance(cp.get('eligible'),bool) or not isinstance(cp.get('info_bearing'),bool): problems.append('eligibility/info_bearing must be boolean')
        if bool(cp.get('eligible')) == bool(cp.get('ineligible_reason')): problems.append('inconsistent eligibility reason')
        allowed_reasons = {None,'no_exposure','post_decision','pre_exposed','restore_fail'}
        if manifest.get('runner_adapter'): allowed_reasons |= {'request_cap','world_attempt_failed','world_attempt_interrupted','world_attempt_stopped_hard_stop','world_attempt_cancelled'}
        if cp.get('ineligible_reason') not in allowed_reasons: problems.append('invalid ineligible reason')
        rs = [r for r in rows if r.get('checkpoint_id')==cp['checkpoint_id']]
        if len({r.get('load_session_id') for r in rs}) > 1: warnings.append(cp['checkpoint_id']+': session_break')
        if not cp.get('eligible'): continue
        for arm,n in (manifest.get('continuations_by_arm',{}) if isinstance(manifest.get('continuations_by_arm'),dict) else {}).items():
            if not isinstance(n,int) or isinstance(n,bool) or n<0: continue
            if arm=='N' and not (cp.get('n_subset') or cp.get('legacy')): n=0
            if arm=='S' and manifest.get('phase')=='holdout': n=int(sham_selected(cp['checkpoint_id']))
            actual = {r['rep'] for r in rs if r['arm']==arm}
            if actual-set(range(n)): problems.append(cp['checkpoint_id']+': excess replicates '+arm)
            if set(range(n))-actual: warnings.append(cp['checkpoint_id']+': missing scheduled '+arm)
        if manifest.get('phase')=='holdout':
            if not isinstance(cp.get('mstar_available'),bool): problems.append('holdout requires mstar_available boolean')
            if cp.get('placebo_kind')!='N_m': problems.append('holdout requires N_m placebo kind')
            if manifest['continuations_by_arm'] != {'F':4,'K':4,'S':1,'N':4}: problems.append('v1.2 heldout requires F4 K4 S1 N4 map')
            if cp.get('mstar_available') and not cp.get('n_subset'): problems.append('N_m required on every available checkpoint')
    if problems: raise ValidationError(sorted(set(problems)))
    return sorted(set(warnings))


def load(root, watchdog_dir=None):
    reader = Reader(root, watchdog_dir=watchdog_dir)
    manifest = reader.read(reader.root/'manifest.json')
    manifest.pop('runner_adapter', None)  # Only the checked adapter may set this internal marker.
    runner_addendum = None
    if manifest.get('schema_version') == 'ccc.runner.manifest.v1':
        if manifest.get('phase') in ('holdout','synthetic_readiness'):
            from .runner_input import adapt
            manifest,cps,rows,events,scheduled,runner_addendum = adapt(reader,manifest)
        else:
            manifest, cps, rows, events, scheduled = _legacy(reader,manifest)
    else:
        cps = reader.read(reader.root/'checkpoints.json')
        worlds=reader.read(reader.root/'worlds.json')
        world_problems=[]
        for world in worlds:
            for key in ('world_id','regime','world_seed','agents','pair','outsiders','order'):
                if key not in world: world_problems.append('world missing '+key)
        for world in worlds:
            agents=set(world.get('agents',[])); pair=set(world.get('pair',[])); outsiders=set(world.get('outsiders',[]))
            if len(agents)!=4 or len(pair)!=2 or len(outsiders)!=2 or pair & outsiders or pair|outsiders!=agents or set(world.get('order',[]))!=agents: world_problems.append('invalid world agent partition/order')
            if world.get('split',manifest['phase'])!=manifest['phase']: world_problems.append('world phase mismatch')
        known={(w.get('world_id'),w.get('regime')) for w in worlds}
        if any((c['world_id'],c['regime']) not in known for c in cps): world_problems.append('checkpoint has no matching world record')
        if world_problems: raise ValidationError(world_problems)
        rows = reader.read(reader.root/'branch_ledger.jsonl',lines=True)
        worldmap={(w['world_id'],w['regime']):w for w in worlds}
        cpmap={c['checkpoint_id']:c for c in cps}
        for row in rows:
            cp=cpmap.get(row.get('checkpoint_id'))
            if cp is None: continue
            world=worldmap[(cp['world_id'],cp['regime'])]
            expected={a:'coalition' if a in world['pair'] else 'outsider' for a in world['agents']}
            if row.get('roles')!=expected: raise ValidationError(['branch roles disagree with world partition'])
        events = reader.read(reader.root/'events.jsonl',lines=True) if (reader.root/'events.jsonl').exists() else []
        scheduled = []
    warnings = list(reader.warnings) + validate(manifest,cps,rows,strict=not (manifest.get('legacy') or manifest.get('runner_adapter')))
    if any(e.get('model_resolved') not in (None,manifest['model']['resolved_id']) for e in events): raise ValidationError(['invalid_batch: mixed model in events'])
    addendum = runner_addendum or (reader.read(reader.root/'stage2_addendum.json') if (reader.root/'stage2_addendum.json').exists() else None)
    if manifest['phase']=='holdout' and not manifest.get('runner_adapter'):
        if addendum is None: raise ValidationError(['input must include stage2_addendum.json'])
        if reader.hashes['stage2_addendum.json'] != manifest['stat001_hash']: raise ValidationError(['input addendum hash mismatch'])
    return manifest,cps,rows,events,scheduled,reader.hashes,warnings,addendum
