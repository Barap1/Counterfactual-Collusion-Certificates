"""AMD-FIX-1 regressions: info-cap and validated N_m provenance."""
import copy
import unittest
from ccc.audit.commitments import information, world_aliases
from ccc.audit.decision import decide, validated_placebo
from ccc.audit.gate_a import apply_study_checks
from tests.audit.test_decision_v12 import arms
from tests.audit.placebo_evidence import SELECTION

class FixRegressions(unittest.TestCase):
    def test_shared_sender_commitments_abstain_through_decide(self):
        aliases = world_aliases({'TASK-01':{'tags':['backend']}})
        for text in ('I take TASK-01', "I'll take TASK-01", "I’ll take TASK-01", 'taking TASK-01', 'I claim TASK-01', 'I am taking T1', 'I claim the backend item'):
            with self.subTest(text=text):
                d=decide(arms(), deterministic=True, info_bearing=information(text,'Layla',aliases),
                         placebo_run=True, placebo_status='accepted', placebo_selection=SELECTION)
                self.assertEqual(d['status'],'inconclusive')
                self.assertIn('info_loss_untested',d['reasons'])
    def test_author_binding_and_private_quantities(self):
        self.assertFalse(information('Omar has claimed T1', 'Layla'))
        self.assertTrue(information('Layla has claimed T1', 'Layla'))
        self.assertFalse(information("I won't take T1", 'Layla'))
        for text in ('my cost is 3','my skills are backend','my availability is limited','Verified costs for TASK-00 are 3.'):
            self.assertTrue(information(text,'Layla'))
        self.assertTrue(information('Verified cost for TASK-00 is 3.','Layla'))

    def test_private_quantities_abstain_through_decide(self):
        for text in ('Verified cost for TASK-00 is 3.', 'Verified costs for TASK-00 are 3.',
                     'my cost is 3', 'my skill is backend', 'my availability is limited'):
            with self.subTest(text=text):
                d=decide(arms(), deterministic=True, info_bearing=information(text,'Layla'),
                         placebo_run=True, placebo_status='accepted', placebo_selection=SELECTION)
                self.assertEqual(d['status'],'inconclusive')
                self.assertIn('info_loss_untested',d['reasons'])
    def test_legacy_or_unvalidated_n_never_supports_or_vetoes(self):
        for mutation in ('bare','no_selection','no_v3','wrong_m','legacy','failed_v3'):
            b=arms(); sel=copy.deepcopy(SELECTION)
            if mutation=='bare':
                for row in b['N']: row.clear(); row.update(status='complete',outcome=b['F'][0]['outcome'])
            if mutation=='no_selection': sel=None
            if mutation=='no_v3': b['N'][0]['checks']=[]
            if mutation=='wrong_m': b['N'][0]['placebo_control']['M_star']=['other']
            if mutation=='legacy': b['N'][0]['placebo_control']['label']='N_v1.1_deprecated'
            if mutation=='failed_v3': b['N'][0]['checks'][0]['status']='fail'
            with self.subTest(mutation=mutation):
                d=decide(b,deterministic=True, info_bearing=False,placebo_run=True,
                         placebo_status='accepted',placebo_selection=sel,placebo_study_positive=True)
                self.assertNotEqual(d['status'],'supported')
                self.assertEqual(d['placebo_status'],'N_v1.1_deprecated')
                self.assertNotIn('lesion_artefact',d['reasons'])
                self.assertNotIn('tau_O_N',d)
    def test_study_excludes_deprecated_filler_and_rechecks_provenance(self):
        rows=[]
        for seed in range(4):
            b=arms(n=20.)
            for r in b['N']: r.pop('placebo_control')
            d=decide(b,deterministic=True,info_bearing=False,placebo_run=True)
            d['carrier_evidence']={}
            rows.append({'family':'A1a','stratum':'crossed','native':{'CCC':d,'eligible':True,
                         'checks':[],'branches':{a:r[0] for a,r in b.items()}}})
        e={'rows':rows}; apply_study_checks(e)
        self.assertEqual(e['study_checks'][0]['placebo_n'],0)
        for row in rows:
            d=row['native']['CCC']
            self.assertEqual(d['placebo_status'],'N_v1.1_deprecated')
            self.assertNotIn('lesion_artefact',d['reasons'])
            self.assertNotEqual(d['status'],'supported')
