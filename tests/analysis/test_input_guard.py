"""Input guard: refuse active or incomplete runner output; accept finished runs with failed attempts."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from ccc.analysis.loaders import load, ValidationError
from ccc.analysis.pipeline import run


def legacy_run(root, terminal=True):
    """Finished (or active) legacy DEV runner output with one world whose only attempt failed."""
    manifest = {'schema_version':'ccc.runner.manifest.v1','experiment_id':'guard','phase':'development',
        'protocol_sha256':'dev','arms':['F','K','S','N'],'continuations_per_arm':{'F':1,'K':1,'S':1,'N':1},
        'model':{'requested_id':'offline','parameters':{}},'policy':{'new_out_of_pocket_usd':0},
        'worlds':[{'id':'dev05_B2','seed':5}]}
    (root/'worlds'/'dev05_B2'/'attempt_0001').mkdir(parents=True)
    (root/'manifest.json').write_text(json.dumps(manifest))
    (root/'run_manifest.json').write_text(json.dumps({'data':{}}))
    attempt = root/'worlds'/'dev05_B2'/'attempt_0001'
    (attempt/'begin.json').write_text(json.dumps({'world':{'id':'dev05_B2','regime':'B2','seed':5,'split':'development'},'load_session':'s'}))
    (attempt/'result.json').write_text(json.dumps({'status':'failed','error':'BudgetViolation: per-run call cap 223 reached','load_session':'s'}))
    if terminal:
        (root/'WATCHDOG_EXIT.json').write_text(json.dumps({'exited_utc':'2026-10-24T02:08:05Z','run_pid':1}))
    return root


class InputGuardTests(unittest.TestCase):
    def test_active_run_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = legacy_run(Path(d)/'in', terminal=False)
            (root/'.collector.lock').write_text('')
            with self.assertRaises(ValidationError) as ctx:
                load(root)
            self.assertIn('active experiment inputs forbidden', ctx.exception.problems[0])

    def test_incomplete_run_without_terminal_record_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = legacy_run(Path(d)/'in', terminal=False)
            with self.assertRaises(ValidationError) as ctx:
                load(root)
            self.assertIn('no terminal run record', ctx.exception.problems[0])

    def test_finished_run_with_failed_attempt_is_accepted_and_counted(self):
        with tempfile.TemporaryDirectory() as d:
            root = legacy_run(Path(d)/'in', terminal=True)
            manifest, cps, rows, events, scheduled, hashes, warnings, addendum = load(root)
            failed = [s for s in scheduled if s['status'] == 'failed']
            self.assertEqual(len(failed), 1)
            self.assertEqual(failed[0]['checkpoint_id'], 'dev05_B2')
            out = Path(d)/'out'
            self.assertEqual(run(root, out), 0)
            aggregate = json.loads((out/'aggregate.json').read_text())
            self.assertEqual(aggregate['scheduled_statuses'], {'failed': 1})

    def _locked_run(self, root, pid):
        legacy_run(root, terminal=True)
        marker = root/'WATCHDOG_EXIT.json'
        marker.write_text(json.dumps({'exited_utc':'2026-10-24T02:08:05Z','run_pid':pid}))
        lock = root/'.collector.lock'
        lock.write_text('')
        os.utime(lock, (1_000_000_000, 1_000_000_000))
        os.utime(marker, (2_000_000_000, 2_000_000_000))
        return root

    def test_stale_lock_with_dead_pid_is_accepted_with_warning(self):
        child = subprocess.Popen(['true'])
        child.wait()
        with tempfile.TemporaryDirectory() as d:
            root = self._locked_run(Path(d)/'in', child.pid)
            manifest, cps, rows, events, scheduled, hashes, warnings, addendum = load(root)
            self.assertTrue(any(w.startswith('stale_lock_ignored') for w in warnings))
            self.assertEqual([s['status'] for s in scheduled if s['status'] == 'failed'], ['failed'])

    def test_lock_with_marker_and_live_pid_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._locked_run(Path(d)/'in', os.getpid())
            with self.assertRaises(ValidationError) as ctx:
                load(root)
            self.assertIn('held by live pid', ctx.exception.problems[0])

    def test_lock_newer_than_marker_without_pid_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = self._locked_run(Path(d)/'in', None)
            os.utime(root/'.collector.lock', (3_000_000_000, 3_000_000_000))
            with self.assertRaises(ValidationError):
                load(root)

    def test_holdout_refusal_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            manifest = {'schema_version':'ccc.run.v1','experiment_id':'h','phase':'holdout','protocol_sha256':'x',
                'stat001_hash':'x','frozen':False,'arms':['F'],'continuations_by_arm':{'F':1},'n_subset_seed':1,
                'branch_order_seed':1,'sampling_seed':1,'model':{'requested_id':'o','resolved_id':'o','parameters':{}},
                'policy':{'new_out_of_pocket_usd':0}}
            (root/'manifest.json').write_text(json.dumps(manifest))
            (root/'checkpoints.json').write_text('[]')
            (root/'worlds.json').write_text('[]')
            (root/'branch_ledger.jsonl').write_text('')
            with self.assertRaises(ValidationError) as ctx:
                load(root)
            self.assertIn('holdout must be frozen', ctx.exception.problems)


if __name__ == '__main__':
    unittest.main()
