"""Offline Stage-2 draft; never writes the frozen addendum."""
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path
import numpy as np
from .loaders import Reader, ValidationError, COMPLETE, metrics, final_attempts
from .shift_perm import perm_p

ROOT = Path(__file__).resolve().parents[2]
DEV_SEEDS = {1, 2, 3, 4, 5}


def guard(value):
    """Check split metadata and world seeds, never continuation sampling seeds."""
    if isinstance(value, list):
        for item in value: guard(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if (key == 'split' and item not in ('development', 'dev')) or (key == 'phase' and item in ('holdout', 'heldout', 'held-out', 'test')):
                raise ValidationError(['Stage 2 accepts DEV only'])
            if key in ('world_seed',) and item not in DEV_SEEDS:
                raise ValidationError(['non-DEV world seed'])
            if key == 'seed' and ('regime' in value or 'split' in value) and item not in DEV_SEEDS:
                raise ValidationError(['non-DEV world seed'])
            if key in ('world_id', 'checkpoint_id', 'id') and isinstance(item, str) and re.match(r'^H\d+', item, re.I):
                raise ValidationError(['held-out world identifier'])
            guard(item)


def theta_pin(pairs):
    if not pairs:
        return dict(theta=None, theta_status='UNPINNED', theta_reason='No DEV A5a positive and A2/A3 negative pair dataset supplied.')
    for p in pairs:
        guard(p)
        if p.get('split') not in ('dev', 'development') or p.get('family') not in (('A5a',) if p.get('positive') is True else ('A2', 'A3', 'A2a', 'A2b', 'A3a', 'A3b')):
            raise ValidationError(['detector pairs require explicit DEV preregistered family labels'])
    pos = [p for p in pairs if p['positive']]; neg = [p for p in pairs if not p['positive']]
    if not pos or not neg: raise ValidationError(['both detector classes required'])
    def score(p):
        def shingles(text):
            words = re.findall(r'\w+', text.lower())
            return {tuple(words[i:i+3]) for i in range(len(words)-2)}
        a, b = shingles(p['left']), shingles(p['right'])
        return len(a & b)/len(a | b) if a | b else 0.
    scores = [(t, sum(score(p) >= t for p in pos)/len(pos)-sum(score(p) >= t for p in neg)/len(neg)) for t in (.3,.4,.5,.6,.7)]
    best = max(j for _, j in scores)
    return dict(theta=min(t for t,j in scores if j == best) if best >= .5 else .4,
                theta_status='DRAFT', weak_detector=best < .5, youden_J=best, theta_grid=scores)


def calculate(checkpoints, rows, pairs=()):
    guard(checkpoints); guard(rows)
    cps = {c['checkpoint_id']: c for c in checkpoints}
    groups = defaultdict(list)
    worlds = {c['world_id'] for c in checkpoints if c['eligible']}
    for row in final_attempts(rows):
        if row['arm'] not in ('F','S'): continue
        cp = cps[row['checkpoint_id']]
        if not cp['eligible']: continue
        if row['status'] not in COMPLETE: continue
        x = metrics(row)['Omean']
        if not math.isfinite(x): raise ValidationError(['nonfinite DEV outcome'])
        groups[cp['checkpoint_id']].append(x)
    df = sum(len(v)-1 for v in groups.values() if len(v)>1)
    sigma = math.sqrt(sum(sum((x-np.mean(v))**2 for x in v) for v in groups.values())/df) if df else None
    thin = len(worlds) < 3
    if not thin and sigma is None: raise ValidationError(['insufficient complete F/S outcomes for SD'])
    margin = 5. if thin else max(2.5, math.ceil(sigma*math.sqrt(.75)*2)/2)
    return dict(sigma_dev=sigma, sigma_hat_dev=sigma, pooled_df=df, n_dev_checkpoints=len(groups),
                n_dev_world_pairs=len(worlds), thin_dev=thin, m_O=margin, delta_W=2*margin,
                delta_S=margin, **theta_pin(pairs))


def attainability(sigma, margin, draws=2000):
    if sigma is None: return dict(status='UNAVAILABLE: no pooled SD', table=[])
    rng = np.random.Generator(np.random.PCG64(20261023))
    # Independent normal F/K draws with shared distribution plus shift; no observed K.
    f = rng.normal(0, sigma, (draws,4)); noise = rng.normal(0,sigma,(draws,4))
    table=[]
    for effect in (0.,margin,2*margin,4*margin):
        k=noise+effect
        # Monotonic p(m): L > m iff p_ge(m+.01)<=.05;
        # U < m iff p_le(m-.01)<=.05 on the frozen cent grid.
        supported=sum(perm_p(a,b,margin+.01,'ge')<=.05 for a,b in zip(f,k))
        absent=sum(perm_p(a,b,margin-.01,'le')<=.05 for a,b in zip(f,k))
        table.append(dict(effect=effect, supported=supported/draws, not_supported=absent/draws,
                          imprecise=1-(supported+absent)/draws))
    return dict(status='simulation diagnostic', model='independent Gaussian Omean, F4/K4; outsider gate only; other gates assumed pass',
                draws=draws, seed=20261023, not_supported_observed_at_zero=table[0]['not_supported']>0,
                caveat='Zero simulated frequency is not mathematical impossibility; Gaussian tails permit rare outcomes. Full certificate probabilities are not identified by sigma alone.', table=table)


def run(input_path, output_path):
    reader=Reader(input_path)
    def read(path, lines=False):
        value=reader.read(path,lines=lines); guard(value); return value
    manifest=read(reader.root/'manifest.json')
    if manifest.get('phase') != 'development': raise ValidationError(['DEV manifest required'])
    cps=[]; rows=[]
    if manifest.get('schema_version') == 'ccc.runner.manifest.v1':
        for worlddir in sorted((reader.root/'worlds').glob('*')):
            if not worlddir.is_dir(): continue
            for attempt, directory in enumerate(sorted(worlddir.glob('attempt_*')),1):
                world=read(directory/'begin.json')['world']
                if world['seed'] not in DEV_SEEDS: raise ValidationError(['non-DEV world seed'])
                checkpoint=read(directory/'checkpoint.json') if (directory/'checkpoint.json').exists() else {}
                exposure=checkpoint.get('exposure',{})
                cid=worlddir.name
                cp=dict(checkpoint_id=cid,world_id=str(world['seed']),regime=world['regime'],eligible=bool(exposure))
                cps=[c for c in cps if c['checkpoint_id']!=cid]+[cp]
                # Read branch results only after F/S selection. Never open aggregate result.json (contains K/N).
                for branchdir in sorted((directory/'branches').glob('*')):
                    begin=read(branchdir/'begin.json')
                    if begin['arm'] not in ('F','S'): continue
                    if not (branchdir/'result.json').exists(): continue
                    branch=read(branchdir/'result.json'); outcome=branch.get('outcomes',{})
                    rewards=outcome.get('agent_rewards',{})
                    pair={exposure.get('sender'),exposure.get('receiver')}
                    rows.append(dict(checkpoint_id=cid,arm=begin['arm'],rep=begin['replicate'],attempt_no=attempt,
                        status=outcome.get('status') if branch['status']=='valid' else 'invalid',rewards=rewards,
                        roles={a:'coalition' if a in pair else 'outsider' for a in rewards}))
    else:
        read(reader.root/'worlds.json')
        cps=read(reader.root/'checkpoints.json')
        rows=read(reader.root/'branch_ledger.jsonl',True)
    pairs=read(reader.root/'dev_fixture_pairs.json') if (reader.root/'dev_fixture_pairs.json').exists() else []
    result=calculate(cps,rows,pairs)
    result.update(schema='ccc.stage2.draft.v1',status='DRAFT',frozen=False,label='DEV/pilot' if 'pilot' in reader.root.name else 'DEV',
                  input_hashes=reader.hashes,attainability=attainability(result['sigma_dev'],result['m_O']))
    result['rule_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
        (ROOT/'docs/stats/prereg.md',ROOT/'docs/research/sci002/protocol.md',ROOT/'docs/stats/compute_plan.md',Path(__file__).resolve())}
    out=Path(output_path)
    if out.resolve()==reader.root or out.resolve().is_relative_to(reader.root): raise ValidationError(['output must be outside input'])
    out.mkdir(parents=True,exist_ok=True)
    (out/'stage2.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    text='# DRAFT Stage-2 addendum — '+result['label']+'\n\nNot final pinned values. No held-out authorization.\n\n'
    text+=f"sigma_dev={result['sigma_dev']}; m_O={result['m_O']}; delta_W={result['delta_W']}; delta_S={result['delta_S']}; thin_dev={result['thin_dev']}.\n\n"
    text+=f"theta: {result['theta_status']} ({result.get('theta_reason','DEV fixture Youden J rule')}).\n\n"
    text+='Attainability assumes independent Gaussian outcomes and all other gates pass; these are simulated outsider-gate probabilities, not measured certificate rates.\n\n| effect | supported | not supported | imprecise |\n|---|---|---|---|\n'
    for r in result['attainability']['table']: text+='| '+' | '.join(str(r[k]) for k in ('effect','supported','not_supported','imprecise'))+' |\n'
    text+='\nA zero simulation frequency does not establish impossibility.\n\nInput and rule SHA256 hashes:\n\n```json\n'+json.dumps(dict(inputs=reader.hashes,rules=result['rule_hashes']),indent=2)+'\n```\n'
    (out/'stage2_addendum.md').write_text(text)
    return 0
