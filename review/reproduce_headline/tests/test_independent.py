"""Offline adversarial tests; fixture construction has no project imports."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from fractions import Fraction

MODULE = Path(__file__).resolve().parents[1] / 'independent.py'
spec = importlib.util.spec_from_file_location('independent', MODULE)
i = importlib.util.module_from_spec(spec)
spec.loader.exec_module(i)


def put(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    path.write_text(json.dumps(dict(data=data, sha256=hashlib.sha256(canonical).hexdigest())))


def fixture(root):
    worlds = [dict(id='world_' + r, seed=9, regime=r) for r in ('B1', 'B2')]
    put(root / 'manifest.json', dict(arms=['F', 'K'], worlds=worlds))
    for world in worlds:
        d = root / 'worlds' / world['id'] / 'attempt_0001'
        put(d / 'begin.json', dict(world=world))
        put(d / 'checkpoint.json', dict(exposure=dict(sender='c', receiver='a')))
        for arm in ('F', 'K'):
            # Non-committing outsider d has reward zero. Coalition rewards must
            # never contaminate Omean. B1 tau=2; B2 tau=0.
            reward = 4 if arm == 'K' and world['regime'] == 'B1' else 0
            b = dict(arm=arm, replicate=0, status='valid', outcomes=dict(
                status='complete', agent_rewards=dict(a=999, b=reward, c=-999, d=0)))
            put(d / 'branches' / ('000_' + arm) / 'result.json', b)
        put(d / 'result.json', dict(status='complete'))
    return worlds


class IndependentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.worlds = fixture(self.root)
        self.d = self.root / 'worlds/world_B1/attempt_0001'

    def test_outsider_identity_and_noncommit_zero(self):
        out = i.reproduce(self.root)
        self.assertEqual(out['Delta'], 2)
        self.assertEqual(out['sign_flip'], dict(p=0.5, numerator=1, denominator=2))
        self.assertEqual(out['attempts'][0]['arm_Omean'], dict(F=0, K=2))

    def test_noop_and_exclusion(self):
        for reason, expected in [('no_exposure', 0), ('post_decision', 0),
                                 ('pre_exposed', None), ('restore_fail', None)]:
            put(self.d / 'result.json', dict(status='ineligible', selection=dict(reason=reason)))
            self.assertEqual(i.reproduce(self.root)['worlds'][0]['tau_O'], expected)

    def test_failed_invalid_and_interrupted_branches_counted(self):
        for rep, status in [(1, 'failed'), (2, 'invalid')]:
            put(self.d / 'branches' / f'{rep:03}_F' / 'result.json',
                dict(arm='F', replicate=rep, status=status, outcomes=None))
        put(self.d / 'branches/003_F/begin.json', dict(arm='F', replicate=3))
        out = i.reproduce(self.root)
        self.assertEqual(out['worlds'][0]['counts']['F'], dict(
            attempted=4, complete=1, failed=1, invalid=1, interrupted=1, not_run=0))
        self.assertEqual(out['Delta'], 2)  # Estimator has no >=3 gate; case rule does.

    def test_final_retry_only_and_all_attempts_retained(self):
        d2 = self.d.with_name('attempt_0002')
        put(d2 / 'begin.json', dict(world=self.worlds[0]))
        put(d2 / 'result.json', dict(status='failed', outcomes=None))
        out = i.reproduce(self.root)
        self.assertIsNone(out['Delta'])
        self.assertEqual(len(out['attempts']), 3)
        self.assertEqual(out['worlds'][0]['counts']['F']['attempted'], 0)

    def test_unrun_world_is_not_zero(self):
        manifest = dict(arms=['F', 'K'], worlds=self.worlds + [dict(id='unrun', seed=10, regime='B1')])
        put(self.root / 'manifest.json', manifest)
        self.assertFalse(i.reproduce(self.root)['worlds'][-1]['attempted'])
        self.assertIsNone(next(p for p in i.reproduce(self.root)['pairs'] if p['pair_id'] == '10')['d_w'])

    def test_corrupt_hash_refused(self):
        p = self.d / 'checkpoint.json'
        obj = json.loads(p.read_text())
        obj['data']['exposure']['sender'] = 'b'
        p.write_text(json.dumps(obj))
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            i.reproduce(self.root)

    def test_summary_disagreement_refused(self):
        put(self.d / 'result.json', dict(status='complete', branches=[
            dict(arm='F', replicate=0, status='failed')]))
        with self.assertRaisesRegex(ValueError, 'disagreement'):
            i.reproduce(self.root)

    def test_incomplete_attempt_refused(self):
        (self.d / 'result.json').unlink()
        with self.assertRaisesRegex(ValueError, 'unfinished'):
            i.reproduce(self.root)

    def test_bad_reward_refused(self):
        path = self.d / 'branches/000_K/result.json'
        obj = json.loads(path.read_text())['data']
        obj['outcomes']['agent_rewards']['b'] = None
        put(path, obj)
        with self.assertRaisesRegex(ValueError, 'invalid reward'):
            i.reproduce(self.root)

    def test_sign_flip_ties_negative_zero_and_empty(self):
        self.assertEqual(i.exact_sign_flip([Fraction(0), Fraction(1), Fraction(1)])['p'], 0.25)
        self.assertEqual(i.exact_sign_flip([Fraction(-1), Fraction(-2)])['p'], 1)
        self.assertEqual(i.exact_sign_flip([Fraction(0)])['p'], 1)
        self.assertIsNone(i.exact_sign_flip([])['p'])
        # Exact decimal ties: 0.1+0.2 is 0.3, without floating tolerance.
        self.assertEqual(i.exact_sign_flip([Fraction('0.1'), Fraction('0.2'), Fraction('0.3')])['numerator'], 1)

    def test_readiness_known_vector(self):
        source = MODULE.parents[2] / 'docs/analysis/readiness/synthetic_input'
        out = i.reproduce(source)
        self.assertEqual(out['Delta'], Fraction(22, 7))
        self.assertEqual([p['d_w'] for p in out['pairs']],
                         list(map(Fraction, [0, 1, 2, 3, 4, 5, 7])) + [None])
        self.assertEqual(out['sign_flip'], dict(p=1/64, numerator=2, denominator=128))


if __name__ == '__main__':
    unittest.main()
