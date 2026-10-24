import unittest
from ccc.fixtures.jira import generate_jira, plain_episode


class ActivationPrecondition(unittest.TestCase):
    def test_a6b_generation_records_exercisability_without_seed_search(self):
        inactive=0
        for seed in range(12000,12020):
            base='A1a' if bool(((seed-12000)%2)^(((seed-12000)//2)%2)) else 'A3a'
            w=generate_jira('A6b',seed,invalid_base=base)
            p=w.fault_precondition
            self.assertEqual(w.seed,seed)
            episode=plain_episode(w,'F')
            turns=[v['turn'] for v in episode['views'] if v['agent']==w.roles[1] and v['eligible']]
            self.assertEqual(p['receiver_exposure_turns'],turns)
            self.assertEqual(p['exercisable'],len(turns)>=2)
            if len(turns)<2:
                inactive+=1
                self.assertEqual(p['status'],'not exercisable')
        self.assertEqual(inactive,5)

    def test_strict_fault_generation_refuses_inactive_cells_without_search(self):
        active = inactive = 0
        for seed in range(12000, 12020):
            base = 'A1a' if bool(((seed-12000)%2)^(((seed-12000)//2)%2)) else 'A3a'
            metadata = generate_jira('A6b', seed, invalid_base=base)
            if metadata.fault_precondition['exercisable']:
                strict = generate_jira('A6b', seed, invalid_base=base, require_fault_exercisable=True)
                self.assertEqual(strict.seed, seed)
                active += 1
            else:
                with self.assertRaisesRegex(AssertionError, "A6b not exercisable"):
                    generate_jira('A6b', seed, invalid_base=base, require_fault_exercisable=True)
                inactive += 1
        self.assertEqual((active, inactive), (15, 5))
