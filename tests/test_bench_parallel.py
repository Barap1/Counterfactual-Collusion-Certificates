"""Execution-only checks; every computed fixture is in DEV 13000--13049."""
import ast
import inspect
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ccc.bench import __main__ as frozen
from scripts import bench_parallel_run as parallel


class ParallelTests(unittest.TestCase):
    def test_per_seed_orchestration_and_tail_ast(self):
        original=ast.parse(inspect.getsource(frozen.run)).body[0]
        loop=next(n for n in original.body if isinstance(n,ast.For)
                  and ast.unparse(n.target)=='(seed, kinds)')
        expected=loop.body[0]
        actual=ast.parse(inspect.getsource(parallel.per_seed)).body[0].body[2]
        # The parent reloads rows in schedule/epsilon order instead of extending
        # shared memory inside the worker. Every other per-seed statement matches.
        expected.body=[n for n in expected.body
                       if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
                               and ast.unparse(n.value.func)=='all_rows.extend')]
        self.assertEqual(ast.dump(expected),ast.dump(actual))
        candidate=ast.parse(inspect.getsource(parallel.run_parallel)).body[0]
        def tail(nodes):
            start=next(i for i,n in enumerate(nodes)
                       if isinstance(n,ast.Assign)
                       and ast.unparse(n.targets[0])=='population_strata')
            return ast.dump(ast.Module(body=nodes[start:],type_ignores=[]))
        # The external driver must use an absolute import for the same report.
        for node in ast.walk(original):
            if isinstance(node,ast.ImportFrom) and node.module=='report':
                node.module='ccc.bench.report'; node.level=0
        self.assertEqual(tail(original.body),tail(candidate.body))

    def test_dev_output_bytes(self):
        # Two seeds exercise multiple workers, all pair/class strata, both eps,
        # population, aggregation, COMPLETE and the frozen report.
        with tempfile.TemporaryDirectory(prefix='benchpar-dev-') as tmp:
            serial=Path(tmp)/'serial'; concurrent=Path(tmp)/'parallel'
            parallel.warm_cache(serial/'cache')
            with patch.object(frozen,'DEV_SEEDS',(13000,13001)):
                frozen.run('dev',serial)
            parallel.run_parallel('dev',concurrent,workers=2,limit=2)
            def artifacts(directory):
                return {p.relative_to(directory):p.read_bytes()
                        for p in directory.rglob('*') if p.is_file()
                        and not {'cache','execution'}.intersection(p.relative_to(directory).parts)}
            self.assertEqual(artifacts(serial).keys(),artifacts(concurrent).keys())
            for name,data in artifacts(serial).items():
                self.assertEqual(data,artifacts(concurrent)[name],str(name))
            before={p.name:p.stat().st_mtime_ns for p in (concurrent/'units').iterdir()}
            with patch.object(parallel,'checkpoint_seed',side_effect=AssertionError('recomputed')):
                parallel.run_parallel('dev',concurrent,workers=2,limit=2,resume=True)
            self.assertEqual(before,{p.name:p.stat().st_mtime_ns for p in (concurrent/'units').iterdir()})
            unit=next((concurrent/'units').iterdir())
            unit.write_bytes(unit.read_bytes()+b'corrupt')
            with self.assertRaisesRegex(ValueError,'checksum mismatch'):
                parallel.run_parallel('dev',concurrent,workers=2,limit=2,resume=True)

    def test_nonempty_output_refused(self):
        with tempfile.TemporaryDirectory(prefix='benchpar-refuse-') as tmp:
            out=Path(tmp); (out/'existing').write_text('preserve')
            with self.assertRaisesRegex(ValueError,'not empty'):
                parallel.run_parallel('dev',out,limit=1)
            self.assertEqual((out/'existing').read_text(),'preserve')


if __name__=='__main__':
    unittest.main()
