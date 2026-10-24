"""Deterministic synthetic metadata generator; never reads experiment artifacts."""
import json
import hashlib
from pathlib import Path
from ccc.analysis.loaders import sham_selected


def put(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    canonical=json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    path.write_text(json.dumps({'data':value,'sha256':hashlib.sha256(canonical).hexdigest()},sort_keys=True)+'\n')


def generate(root):
    root=Path(root); root.mkdir(parents=True,exist_ok=True)
    worlds=[dict(id=f'SYN{i:02}_{r}',seed=100+i,regime=r,split='synthetic_readiness') for i in range(1,9) for r in ('B1','B2')]
    manifest=dict(schema_version='ccc.runner.manifest.v1',experiment_id='SYNTHETIC-STAT-002c',
        phase='synthetic_readiness',frozen=True,protocol_sha256='synthetic-only',
        continuations_per_arm={'F':4,'K':4,'S':1,'N':4},arms=['F','K','S','N'],
        model=dict(requested_id='scripted-offline',backend='synthetic',parameters={}),
        policy=dict(new_out_of_pocket_usd=0,live_inference_enabled=False),worlds=worlds)
    put(root/'manifest.json',manifest)
    # Terminal sidecar is raw JSON, as written by the real watchdog.
    (root/'WATCHDOG_EXIT.json').write_text(json.dumps({'run_pid':None,'synthetic':True})+'\n')
    for w in worlds:
        d=root/'worlds'/w['id']/'attempt_0001'
        put(d/'begin.json',dict(world=w,load_session='synthetic-session'))
        if w['seed']==108:
            put(d/'result.json',dict(status='failed',outcomes=None,error='frozen request cap exhausted' if w['regime']=='B2' else 'synthetic source infrastructure failure'))
            continue
        if w['seed']==107 and w['regime']=='B2':
            put(d/'selection.json',dict(reason='no_exposure'))
            put(d/'result.json',dict(status='ineligible',selection=dict(reason='no_exposure'),outcomes=None))
            continue
        put(d/'checkpoint.json',dict(exposure=dict(sender='a',receiver='b'),restore_validation={'V1':'pass'}))
        put(d/'placebo.json',dict(status='no_placebo_available',M_star=[],sham_selected=sham_selected(w['id']),
            arm_counts={'F':4,'K':4,'S':int(sham_selected(w['id'])),'N':0}))
        branches=[]
        for arm,n in [('F',4),('K',4),('S',int(sham_selected(w['id']))),('N',4)]:
            for rep in range(n):
                b=dict(arm=arm,replicate=rep)
                if arm=='N': b.update(status='not_run',outcomes=None,reasons=['no_placebo_available'])
                else:
                    effect=(w['seed']-100) if w['regime']=='B1' else 1
                    o=effect if arm=='K' else 0
                    c=10-effect if arm=='K' else 10
                    b.update(status='valid',checks=[dict(id=f'V{i}',status='pass') for i in range(1,8)],
                        outcomes=dict(status='complete',agent_rewards=dict(a=c,b=c,x=o,y=o),
                            assignment=dict(a='t1',b='t2',x='t3',y='t4')))
                branches.append(b)
                put(d/'branches'/f'{rep:03}_{arm}'/'result.json',b)
        put(d/'result.json',dict(status='complete',branches=branches,load_session='synthetic-session',cross_checks=[]))
        (d/'budget.jsonl').write_text(json.dumps(dict(event='attempt_end',model_resolved='scripted-offline',api_cost_usd=0))+'\n')
    return manifest


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--out',required=True)
    generate(p.parse_args().out)
