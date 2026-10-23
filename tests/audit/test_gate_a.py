import unittest
from unittest.mock import patch
from ccc.audit.gate_a import require_dev, generate_dev
from ccc.fixtures.worlds import split_manifest


class DevBoundary(unittest.TestCase):
    def test_all_dev_and_no_holdout_generation(self):
        m=split_manifest(); touched=[]
        with patch('ccc.fixtures.jira.generate_jira',side_effect=lambda c,s,**kw:touched.append(s)):
            for seed in range(12000,12020): generate_dev('A1a',seed,m)
            for seed in range(87000,87100):
                with self.assertRaises(PermissionError): generate_dev('A1a',seed,m)
        self.assertEqual(touched,list(range(12000,12020)))
    def test_outside_partition(self):
        for seed in (1,11999,12020,True,'12000'):
            with self.assertRaises(PermissionError): require_dev(seed,split_manifest())
