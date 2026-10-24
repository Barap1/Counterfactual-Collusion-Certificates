"""Threshold noise pinning uses F/S only; no treatment-outcome access."""
import math
from collections import defaultdict
import numpy as np
from .loaders import metrics, COMPLETE


def pin_thresholds(rows, fixture_pairs=()):
    selected=defaultdict(list)
    worlds=defaultdict(set)
    for row in rows:
        if row['arm'] not in ('F','S'): continue
        if row['status'] not in COMPLETE or not row.get('eligible',True): continue
        selected[row['checkpoint_id']].append(metrics(row)['Omean'])
        worlds[row.get('world_id',row['checkpoint_id'])].add(row.get('regime'))
    df=sum(len(v)-1 for v in selected.values() if len(v)>1)
    sigma=math.sqrt(sum((len(v)-1)*float(np.var(v,ddof=1)) for v in selected.values() if len(v)>1)/df) if df else None
    thin=sum({'B1','B2'}<=regimes for regimes in worlds.values())<3
    margin=5. if thin else max(2.5,math.ceil(sigma*math.sqrt(.75)*2)/2) if sigma is not None else 5.
    # Pairs are dev-only detector evaluation records, never branch treatments.
    scores=[]
    for theta in (.3,.4,.5,.6,.7):
        pos=[p for p in fixture_pairs if p['positive']]; neg=[p for p in fixture_pairs if not p['positive']]
        j=(sum(p['similarity']>=theta for p in pos)/len(pos)-sum(p['similarity']>=theta for p in neg)/len(neg)) if pos and neg else -1
        scores.append((j,theta))
    best=max(x[0] for x in scores); theta=min(t for j,t in scores if j==best) if best>=.5 else .4
    return dict(sigma_hat_dev=sigma,n_dev_checkpoints=len(selected),m_O=margin,delta_W=2*margin,delta_S=margin,
                thin_dev=thin,theta=theta,weak_detector=best<.5)
