"""DEV-only execution equality; no SDK import, network or prospective generation."""
import ast
import inspect
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from ccc.bench import __main__ as frozen
from scripts import bench_modal_run as driver
from scripts import bench_parallel_run as execution


def task(seed, phase, kinds):
    assert seed in (13000,13001)
    return dict(seed=seed,phase=phase,kinds=sorted(kinds),block='dev',identity=driver.identity())


def test_dev_serial_vs_mapped_callable(tmp_path):
    serial=tmp_path/'serial'; mapped=tmp_path/'mapped'
    configure=frozen.configure_cache
    def warm(path):
        execution.warm_cache(path)
        configure(path)
    with patch.object(frozen,'DEV_SEEDS',(13000,13001)), patch.object(frozen,'configure_cache',warm):
        frozen.run('dev',serial)
        schedule,pop=frozen._schedule('dev',None)
        manifest=driver.manifest('dev',schedule,pop,None)
        frozen.write_json(mapped/'manifest.json',manifest)
        # Reverse completion order exercises canonical schedule reassembly.
        for seed,kinds in reversed(list(schedule.items())):
            item=task(seed,'methods',kinds)
            driver.save_result(mapped,item,driver.execute_task(item))
            assert driver.checkpoint(mapped,item)
        driver.finalize('dev',mapped,schedule,pop,manifest)
    def artifacts(out):
        return {p.relative_to(out):p.read_bytes() for p in out.rglob('*')
                if p.is_file() and not {'cache','execution'}.intersection(p.relative_to(out).parts)}
    assert artifacts(serial)==artifacts(mapped)
    item=task(13000,'methods',schedule[13000])
    class NoWork:
        def map(self,items,**kwargs):
            assert items==[]
            return iter(())
    driver.run_phase(mapped,[item],NoWork())
    unit=mapped/execution.seed_files(13000)[0]
    unit.write_bytes(unit.read_bytes()+b'corruption')
    with pytest.raises(ValueError,match='checksum mismatch'):
        driver.checkpoint(mapped,item)


def test_frozen_tail_ast():
    def tail(fn):
        nodes=ast.parse(inspect.getsource(fn)).body[0].body
        start=next(i for i,n in enumerate(nodes) if isinstance(n,ast.Assign)
                   and ast.unparse(n.targets[0])=='population_strata')
        module=ast.Module(body=nodes[start:],type_ignores=[])
        for n in ast.walk(module):
            if isinstance(n,ast.ImportFrom) and n.module=='report':
                n.module='ccc.bench.report'; n.level=0
        return ast.dump(module)
    assert tail(driver.finalize)==tail(frozen.run)


def test_gate_bytes_and_missing(tmp_path):
    left=tmp_path/'left'; right=tmp_path/'right'
    for name in execution.seed_files(13000):
        for directory in (left,right):
            p=directory/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b'opaque')
    result=driver.compare_gate(left,[13000],right)
    assert result['status']=='PASS' and result['compared']==4
    (right/execution.seed_files(13000)[0]).unlink()
    assert driver.compare_gate(left,[13000],right)['status']=='FAIL'
    assert json.loads((left/'GATE.json').read_text())['status']=='FAIL'


def test_task_identity_refuses_before_compute():
    item=task(13000,'methods',{'P1'}); item['identity']={}
    with patch.object(execution,'per_seed',side_effect=AssertionError('computed')):
        with pytest.raises(ValueError,match='identity differs'):
            driver.execute_task(item)


def test_dry_run_without_modal(capsys):
    with patch.object(driver,'modal_application',side_effect=AssertionError('Modal')):
        driver.main(['--dry-run','--gate','40'])
    assert '40 seed blocks, 80 unit files' in capsys.readouterr().out
