import os,sys
from pathlib import Path
from tests.replay.offline_runner import guard
os.environ['CCC_STARTER_ROOT']=str(Path.cwd()/'starter/collusion_hackathon')
sys.addaudithook(guard)
from ccc.audit.placebo_census import main
for version in (sys.argv[1:] or ('fx1','fx2')):
    main(['--out',f'docs/gate_a/v1.2/census_{version}.json']+(['--fx1'] if version=='fx1' else []))
