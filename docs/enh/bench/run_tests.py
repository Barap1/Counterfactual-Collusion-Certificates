"""Release discovery with its sole persistent artifact redirected to owned space."""
import runpy
import sys
from pathlib import Path

repo=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(repo))
original=Path.write_text
source=repo/'docs/analysis/readiness/coverage_simulation.json'


def write_text(self,*args,**kwargs):
    if self.resolve()==source:
        self=repo/'docs/enh/bench/coverage_simulation.json'
    return original(self,*args,**kwargs)


Path.write_text=write_text
sys.argv=['tests.replay.offline_runner','-s','tests','-t','.']
runpy.run_module('tests.replay.offline_runner',run_name='__main__')
