"""Read terminal v1.2 runner metadata without opening traces or calling providers."""
import hashlib
import re
from .loaders import ROOT, ValidationError, COMPLETE


def adapt(reader, manifest):
    synthetic = manifest.get('phase') == 'synthetic_readiness'
    if synthetic:
        if manifest.get('policy', {}).get('live_inference_enabled') is not False:
            raise ValidationError(['synthetic readiness requires live inference disabled'])
        if any(w.get('split') != 'synthetic_readiness' for w in manifest['worlds']):
            raise ValidationError(['synthetic split mismatch'])
    else:
        # This validator only reads the frozen protocol/approval; it performs no I/O to providers.
        from ccc.runner.manifest import validate
        validate(dict(manifest))
        for name in (manifest['protocol_artifact'],manifest['stat001']['artifact']):
            reader.hashes['repo:'+name] = hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    addendum_path = ROOT/'docs/stats/stage2/STAGE2_ADDENDUM.md'
    raw = addendum_path.read_bytes()
    reader.hashes['repo:docs/stats/stage2/STAGE2_ADDENDUM.md'] = hashlib.sha256(raw).hexdigest()
    text = raw.decode()
    addendum = {}
    for name in ('m_O', 'delta_W', 'delta_S'):
        match = re.search(r'\| `'+name+r'` \| \*\*([0-9.]+)\*\*', text)
        if not match: raise ValidationError(['missing pinned '+name])
        addendum[name] = float(match[1])
    if '| **0.4** (weak detector)' not in text:
        raise ValidationError(['unrecognized frozen theta'])
    addendum.update(theta=.4, weak_detector=True)
    m = dict(manifest, phase='holdout', runner_adapter=True,
             synthetic=synthetic, continuations_by_arm=manifest['continuations_per_arm'])
    m['model'] = dict(m['model'], resolved_id=m['model']['requested_id'])
    cps, rows, events, scheduled = [], [], [], []
    for world in manifest['worlds']:
        cid = world['id']
        directories = sorted((reader.root/'worlds'/cid).glob('attempt_*'))
        cp = None
        for attempt_no, directory in enumerate(directories, 1):
            begin = reader.read(directory/'begin.json')
            if begin['world'] != world: raise ValidationError(['world metadata mismatch: '+cid])
            result = reader.read(directory/'result.json') if (directory/'result.json').exists() else {'status':'interrupted'}
            scheduled.append(dict(checkpoint_id=cid, attempt_no=attempt_no, status=result['status'],
                                  kind='world_attempt', error=result.get('error'), reason=result.get('reason')))
            checkpoint = reader.read(directory/'checkpoint.json') if (directory/'checkpoint.json').exists() else {}
            exposure = checkpoint.get('exposure', {})
            selection = reader.read(directory/'selection.json') if (directory/'selection.json').exists() else result.get('selection', {})
            reason = (result.get('reason') or selection.get('reason')) if result['status']=='ineligible' else 'restore_fail'
            if result['status'] != 'ineligible':
                error = result.get('error','').lower()
                reason = 'request_cap' if 'request cap' in error or 'call cap' in error else 'world_attempt_'+result['status']
            elif reason not in ('no_exposure','post_decision','pre_exposed','restore_fail'):
                reason = 'restore_fail'
            cp = dict(checkpoint_id=cid, world_id=str(world['seed']), regime=world['regime'],
                      eligible=bool(exposure), ineligible_reason=None if exposure else reason,
                      world_attempt_status=result['status'], eligibility_observed=bool(exposure) or result['status']=='ineligible',
                      sender=exposure.get('sender'), receiver=exposure.get('receiver'),
                      info_bearing=True, info_bearing_source='unavailable; conservative true', flags={},
                      v_checks=dict(checkpoint.get('restore_validation', {})),
                      n_subset=False, mstar_available=False, placebo_kind='N_m')
            if (directory/'placebo.json').exists():
                placebo = reader.read(directory/'placebo.json')
                cp.update(n_subset=placebo['status']=='accepted', mstar_available=placebo['status']=='accepted')
            branches = {(b['arm'], b['replicate']): b for b in result.get('branches', [])}
            for location in sorted((directory/'branches').glob('*')):
                if (location/'result.json').exists():
                    b = reader.read(location/'result.json'); branches[(b['arm'],b['replicate'])] = b
                elif (location/'begin.json').exists():
                    b = reader.read(location/'begin.json'); branches.setdefault((b['arm'],b['replicate']),dict(b,status='cancelled'))
            checks = list(result.get('cross_checks', []))
            if (directory/'cross_checks.json').exists(): checks += reader.read(directory/'cross_checks.json')
            for b in branches.values():
                checks += b.get('checks', [])
                if b['status']=='not_run':
                    scheduled.append(dict(checkpoint_id=cid,attempt_no=attempt_no,arm=b['arm'],rep=b['replicate'],
                                          status='not_run',kind='unscheduled_arm',reasons=b.get('reasons',[])))
                    continue
                outcome = b.get('outcomes') or {}
                status = outcome.get('status') if b['status']=='valid' else 'session_break' if 'model_reload' in b.get('reasons',[]) else 'infra_crash' if b['status']=='failed' else 'invalid_restore' if b['status']=='invalid' else 'cancelled'
                if status not in COMPLETE | {'session_break','infra_crash','invalid_restore','cancelled'}: status='infra_crash'
                rewards = outcome.get('agent_rewards', {})
                assignments = outcome.get('assignment') or {}
                noncommit = [a for a in rewards if assignments.get(a) in (None,'skip')]
                if status=='complete' and noncommit: status='complete_noncommit'
                rows.append(dict(attempt_id=f'{cid}/{attempt_no}/{b["arm"]}/{b["replicate"]}',
                    checkpoint_id=cid,arm=b['arm'],rep=b['replicate'],attempt_no=attempt_no,status=status,
                    runner_status=b['status'],load_session_id=result.get('load_session',begin.get('load_session')),
                    rewards=rewards,roles={a:'coalition' if a in (cp['sender'],cp['receiver']) else 'outsider' for a in rewards},
                    committed=assignments,noncommit_agents=noncommit,model_resolved=m['model']['resolved_id'],
                    v3_pass=not any(c['id']=='V3' and c['status']=='fail' for c in b.get('checks',[])),cost_usd=None))
            for check in checks:
                if cp['v_checks'].get(check['id']) != 'fail': cp['v_checks'][check['id']] = check['status']
                cp['flags'].update({f:True for f in check.get('details',{}).get('flags',[])})
            if (directory/'budget.jsonl').exists(): events.extend(reader.read(directory/'budget.jsonl',lines=True))
        if cp is not None: cps.append(cp)
        else: scheduled.append(dict(checkpoint_id=cid,status='unrun',kind='scheduled_world'))
    resolved = {e.get('model_resolved') for e in events if e.get('model_resolved') is not None}
    if resolved and resolved != {m['model']['resolved_id']}: raise ValidationError(['invalid_batch: mixed model in events'])
    if rows and not resolved: raise ValidationError(['runner requires recorded model identity in event ledger'])
    reader.warnings.append('Runner metadata lacks frozen info_bearing output; conservatively true; support blocked when unestablished')
    return m,cps,rows,events,scheduled,addendum
