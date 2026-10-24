"""Exact pure-call cache for DEV ONLY; two bounded local numerical threads.

This changes no frozen function/global and no scientific result. Each unique
call is executed by the imported, unmodified decide() through its normal adapter.
The collection pass replaces only our new outer cache function, recording its
arguments rather than running any audited method or altering a frozen module.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from unittest.mock import patch
from hashlib import sha256
import json
import sys
import time

repo=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(repo))
from ccc.bench import methods
from ccc.bench.observe import SETS, observe, project
from ccc.bench.twins import suite

out=repo/'docs/enh/bench/dev_run'
methods.configure_cache(out/'cache')
calls=set()


def collect(encoded):
    calls.add(encoded)
    return {}


with patch('ccc.bench.methods._decide_cached',side_effect=collect):
    for seed in range(13000,13050):
        for eps in (0,.1):
            for instance in suite(seed,eps):
                full=observe(instance,'I5')
                for s in SETS:
                    view=project(full,s)
                    methods.ccc(view)
                    if instance.corruption: methods.ccc(view,validate=False)

start=time.monotonic()
print(f'DEV-only exact prewarm: {len(calls)} unique calls, two threads',flush=True)
completed=0
with ThreadPoolExecutor(max_workers=2) as pool:
    futures={pool.submit(methods._decide_cached,c):sha256(c.encode()).hexdigest() for c in sorted(calls)}
    for future in as_completed(futures):
        future.result()
        completed+=1
        print(f'{completed}/{len(calls)} complete; seconds={time.monotonic()-start:.1f}; key={futures[future]}',flush=True)
print('DONE',flush=True)
