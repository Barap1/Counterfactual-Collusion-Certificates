"""Stage-2 DEV isolation and formula regressions, offline only."""
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from ccc.analysis.stage2 import calculate, guard, theta_pin, attainability, run
from ccc.analysis.loaders import ValidationError


def data(worlds=3):
    cps=[]; rows=[]
    for w in range(worlds):
        cid=str(w)
        cps.append(dict(checkpoint_id=cid,world_id=cid,regime='B1',eligible=True))
        for arm,values in [('F',[0,2,4,6]),('S',[8,10])]:
            for rep,x in enumerate(values):
                rows.append(dict(checkpoint_id=cid,arm=arm,rep=rep,attempt_no=1,status='complete',
                    rewards=dict(a=0,b=0,x=x,y=x),roles=dict(a='coalition',b='coalition',x='outsider',y='outsider')))
    return cps,rows


class Stage2Tests(unittest.TestCase):
    def test_pooled_formula_and_rounding(self):
        cps,rows=data()
        result=calculate(cps,rows)
        self.assertAlmostEqual(result['sigma_dev'],math.sqrt(14))
        self.assertEqual(result['pooled_df'],15)
        self.assertEqual(result['m_O'],3.5)
        self.assertEqual(result['delta_W'],7)
        self.assertEqual(result['delta_S'],3.5)
        self.assertFalse(result['thin_dev'])

    def test_ignores_unreadable_kn_outcomes(self):
        cps,rows=data()
        before=calculate(cps,rows)
        rows += [dict(checkpoint_id='0',arm=a,rep=0,attempt_no=1,status='complete',rewards=None) for a in ('K','N','C')]
        self.assertEqual(before,calculate(cps,rows))

    def test_thin_and_floor(self):
        cps,rows=data(1)
        self.assertEqual(calculate(cps,rows)['m_O'],5)
        cps,rows=data()
        for row in rows: row['rewards']=dict(a=0,b=0,x=0,y=0)
        self.assertEqual(calculate(cps,rows)['m_O'],2.5)

    def test_eligible_world_count_and_incomplete(self):
        cps,rows=data()
        cps[0]['eligible']=False
        rows[6]['status']='infra_crash'
        result=calculate(cps,rows)
        self.assertTrue(result['thin_dev'])
        self.assertEqual(result['n_dev_world_pairs'],2)
        self.assertEqual(result['pooled_df'],9)

    def test_holdout_rejected_even_kn(self):
        for obj in ({'phase':'holdout'}, {'world_seed':929292}, {'seed':99,'regime':'B1'}, {'id':'H01'}):
            with self.assertRaises(ValidationError): guard(obj)
        cps,rows=data()
        rows.append(dict(arm='K',split='holdout'))
        with self.assertRaises(ValidationError): calculate(cps,rows)

    def test_theta_missing_ties_weak_and_holdout(self):
        self.assertEqual(theta_pin([])['theta_status'],'UNPINNED')
        pairs=[dict(split='dev',family='A5a',positive=True,left='one two three four',right='one two three four'),
               dict(split='dev',family='A2',positive=False,left='one two three',right='five six seven')]
        self.assertEqual(theta_pin(pairs)['theta'],.3)
        pairs[1]['right']=pairs[1]['left']
        self.assertEqual(theta_pin(pairs)['theta'],.4)
        self.assertTrue(theta_pin(pairs)['weak_detector'])
        pairs[0]['split']='holdout'
        with self.assertRaises(ValidationError): theta_pin(pairs)

    def test_zero_noise_diagnostic(self):
        result=attainability(0,5,draws=10)
        self.assertEqual(result['table'][0]['not_supported'],1)
        self.assertEqual(result['table'][1]['imprecise'],1)
        self.assertEqual(result['table'][2]['supported'],1)
        for row in result['table']:
            self.assertAlmostEqual(row['supported']+row['not_supported']+row['imprecise'],1)

    def test_reject_manifest_before_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); inp=root/'input'; inp.mkdir()
            (inp/'manifest.json').write_text(json.dumps(dict(phase='development',worlds=[dict(seed=100,regime='B1')])) )
            with self.assertRaises(ValidationError): run(inp,root/'out')
            self.assertFalse((root/'out').exists())

    def test_pilot_reader_never_opens_kn_outcomes(self):
        from ccc.analysis.loaders import Reader
        original = Reader.read
        def checked(reader, path, lines=False):
            path = Path(path)
            if path.name == 'result.json' and path.parent.name.endswith(('_K','_N','_C')):
                raise AssertionError('treatment outcomes opened')
            return original(reader,path,lines)
        with tempfile.TemporaryDirectory() as tmp, patch.object(Reader,'read',checked):
            run('docs/runner/exp001-pilot3',tmp)
            output=json.loads((Path(tmp)/'stage2.json').read_text())
            self.assertEqual(output['label'],'DEV/pilot')
            self.assertEqual(output['n_dev_checkpoints'],1)
            self.assertTrue(output['thin_dev'])
            self.assertAlmostEqual(output['sigma_dev'],3.3436508067332933)
            self.assertFalse(output['frozen'])
            self.assertIn('DRAFT',(Path(tmp)/'stage2_addendum.md').read_text())
