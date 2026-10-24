"""D-034/F-1: study labels and the unchanged preregistered decision rule."""
import unittest
from unittest.mock import patch
from ccc.analysis.study import study_effects


def worlds(n=8):
    return [dict(world_id=str(i), regime=r, eligible=True, n_F=4, n_K=4,
                 tau_O=float(i+1) if r == 'B1' else 0.,
                 tau_C=float(i+1), tau_W=0., tau_A=0.)
            for i in range(n) for r in ('B1', 'B2')]


class LabelCorrectionTests(unittest.TestCase):
    def test_confirmatory_family_and_descriptive_conditional(self):
        rows, _ = study_effects(worlds(), 'holdout', 2.5)
        family = [r for r in rows if r['effect'] in ('Delta_total', 'S1', 'S2', 'S3')]
        self.assertEqual(len(family), 4)
        for row in family:
            self.assertTrue(row['confirmatory'])
            self.assertEqual(row['inference_tier'], 'A-confirmatory')
            self.assertEqual(row['tier'], 'A-confirmatory')
        self.assertFalse(rows[1]['confirmatory'])
        self.assertEqual(rows[0]['decision'], 'supported')

    def test_floors_and_phase(self):
        for data, phase in ((worlds(7), 'holdout'), (worlds(), 'development')):
            rows, _ = study_effects(data, phase, 2.5)
            for row in rows:
                self.assertFalse(row['confirmatory'])
            self.assertEqual(rows[0]['inference_tier'], 'feasibility')
            self.assertEqual(rows[0]['decision'], 'exploratory')

    def test_dev_exploratory_and_holdout_not_supported(self):
        data = worlds()
        for row in data:
            row['tau_O'] *= -1
        for phase, expected in (('development', 'exploratory'), ('holdout', 'not supported')):
            with self.subTest(phase=phase):
                rows, _ = study_effects(data, phase, 2.5)
                self.assertEqual(rows[0]['decision'], expected)
                self.assertEqual(rows[0]['confirmatory'], phase == 'holdout')
                self.assertEqual(rows[0]['inference_tier'],
                                 'A-confirmatory' if phase == 'holdout' else 'feasibility')

    def test_both_criteria_and_boundaries(self):
        for lower, p, expected in ((0., .01, 'not supported'),
                                   (-.01, .01, 'not supported'),
                                   (.01, .050001, 'not supported'),
                                   (.01, None, 'not supported'),
                                   (None, .01, 'not supported'),
                                   (.01, .05, 'supported')):
            with self.subTest(lower=lower, p=p):
                with patch('ccc.analysis.study.summarize', return_value={
                    'estimate': 1., 'L': lower, 'U': 2., 'n_independent': 8
                }), patch('ccc.analysis.study.sign_flip', return_value={
                    'p': p, 'status': 'attainable'
                }):
                    rows, _ = study_effects(worlds(), 'holdout', 2.5)
                self.assertEqual(rows[0]['decision'], expected)
