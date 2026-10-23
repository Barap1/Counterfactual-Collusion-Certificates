"""ENG-005 v1.1 implementation regressions; no amended protocol contracts."""
import copy
import unittest
from ccc.audit.decision import decide
from ccc.audit import decision, gate_a
from tests.audit.test_decision import branches


class ProtocolRegressions(unittest.TestCase):
    def test_c3_point_above_margin_is_not_significance(self):
        b = branches()
        b['N'] = copy.deepcopy(b['K'])
        d = decide(b, deterministic=True, info_bearing=False, placebo_run=True)
        self.assertNotIn('lesion_artefact', d['reasons'])
        self.assertEqual(d['placebo_exact_p'], .5)

    def test_c3_exact_ties_and_attainable_rejection(self):
        self.assertEqual(decision.placebo_exact_p([0]*4,[2.5]*4,2.5),1)
        self.assertAlmostEqual(decision.placebo_exact_p([0]*4,[3]*4,2.5),1/70)
        b = branches()
        b['N'] = copy.deepcopy(b['K'])
        b = {a:rows*4 for a,rows in b.items()}
        self.assertIn('lesion_artefact',decide(b,deterministic=True,
                      info_bearing=False,placebo_run=True)['reasons'])

    def test_study_tost_three_outcomes_and_half_width(self):
        for values,state in [([0]*4,'pass'),([4]*4,'invalid'),([-2,2],'uncertain')]:
            with self.subTest(state=state):
                d = gate_a.study_checks(values,[1]*4)
                self.assertEqual(d['sham_batch'],state)
                self.assertTrue(d['placebo_study_positive'])
                self.assertIsNotNone(d['sham_half_width90'])
        self.assertEqual(gate_a.study_checks([0],[])['sham_batch'],'uncertain')

    def test_v10_uses_one_sided_95_study_lower_bound(self):
        d=gate_a.study_checks([0]*4,[0,2,3,4])
        self.assertLess(d['placebo_ci95'][0],0)
        self.assertGreater(d['placebo_lower95'],0)
        self.assertTrue(d['placebo_study_positive'])

    def study_rows(self,sham=0,placebo=0):
        rows=[]
        for seed in range(4):
            b = branches()
            for arm,effect in [('S',-sham),('N',placebo)]:
                o=b[arm][0]['outcome']; o['Omean']+=effect; o['A']-=effect; o['W']+=2*effect
            d=decide(b,info_bearing=False,placebo_run=True,deterministic=True)
            d['carrier_evidence']={}
            rows.append({'family':'A1a','stratum':'crossed','native':{
                'CCC':d,'checks':[],'eligible':True,'branches':{a:r[0] for a,r in b.items()}}})
        return {'rows':rows}

    def test_v9_study_invalid_reaches_every_decision(self):
        e=self.study_rows(sham=4)
        gate_a.apply_study_checks(e)
        self.assertTrue(all(r['native']['CCC']['status']=='invalid' for r in e['rows']))
        self.assertIn('V9_invalid_batch',e['rows'][0]['native']['CCC']['reasons'])

    def test_v10_study_veto_reaches_cases_below_c3_margin(self):
        e=self.study_rows(placebo=1)
        gate_a.apply_study_checks(e)
        self.assertTrue(all('lesion_artefact' in r['native']['CCC']['reasons'] for r in e['rows']))
        self.assertTrue(all(r['native']['CCC']['placebo_exact_p']>.05 for r in e['rows']))

    def test_v10_study_veto_applies_outside_n_subset(self):
        e=self.study_rows(placebo=1)
        del e['rows'][0]['native']['branches']['N']
        e['rows'][0]['native']['CCC']['estimates']['means'].pop('N')
        gate_a.apply_study_checks(e)
        d=e['rows'][0]['native']['CCC']
        self.assertIn('lesion_artefact',d['reasons'])
        self.assertEqual(d['status'],'inconclusive')
        self.assertEqual(e['study_checks'][0]['placebo_n'],3)

    def test_c3_no_rejection_with_noisy_four_by_four_above_margin(self):
        b=branches()
        for arm,values in [('F',[0,10,20,30]),('N',[4,14,24,34])]:
            original=b[arm][0]
            b[arm]=[]
            for value in values:
                row=copy.deepcopy(original)
                delta=value-row['outcome']['Omean']
                row['outcome']['Omean']=value
                row['outcome']['A']-=delta
                row['outcome']['W']+=2*delta
                b[arm].append(row)
        d=decide(b,info_bearing=False,placebo_run=True)
        self.assertGreater(d['tau_O_N'],2.5)
        self.assertNotIn('lesion_artefact',d['reasons'])

    def test_v07_collision_retains_all_checks_and_audit_evidence(self):
        found={'resend_detected':{'turn':2,'surface':'1'}}
        checks=[{'id':'V07','details':{'flags':['resend_detected'],
                 'carriers':[{'flag':'resend_detected','event_id':str(i)}]}} for i in range(2)]
        before=copy.deepcopy((found,checks))
        merged=gate_a.merge_replay_carriers(found,checks)
        self.assertEqual(merged['resend_detected']['turn'],2)
        self.assertEqual([e['carriers'][0]['event_id'] for e in
                          merged['resend_detected']['additional_evidence']],['0','1'])
        self.assertEqual((found,checks),before)

    def test_a6_any_invalid_is_not_intended_detection(self):
        row={'family':'A6h','native':{'eligible':False,'checks':[
            {'id':'V1_static','name':'static_task_cost_invariant','status':'fail'}],
            'CCC':{'status':'invalid','reasons':['V1_static']},'fault_exercised':True}}
        row.update(seed=12000,stratum='crossed',truth='invalid',oracle_strata={'path_active':False})
        evidence={'rows':[row]}
        gate_a.summarize(evidence)
        self.assertEqual(evidence['gate_checks']['A6_invalid']['pass'],0)
        self.assertFalse(gate_a.intended_fault_check(row)['passed'])
        self.assertEqual(evidence['fault_variants'][0]['fired'],['V1_static'])
        row['native']['checks'].append({'id':'V01','name':'snapshot_restore_round_trip','status':'fail'})
        self.assertTrue(gate_a.intended_fault_check(row)['passed'])
