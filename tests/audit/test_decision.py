import copy
import unittest
from ccc.audit import decide, estimate, Parameters
from ccc.audit.text import information, carriers
from ccc.baselines import evaluate, js, tv


def branches(o=10,c=5,w=10):
    f={'Omean':10.,'Cmean':20.,'A':10.,'W':60.}
    k={'Omean':10.+o,'Cmean':20.-c,'A':10.-c-o,'W':60.+2*o-2*c}
    return {a:[{'status':'complete','outcome':v}] for a,v in [('F',f),('S',f.copy()),('K',k),('N',f.copy())]}


class Decisions(unittest.TestCase):
    def run_rule(self,b=None,**kw):
        return decide(b or branches(),deterministic=True,info_bearing=False,placebo_run=True,**kw)
    def test_signs_identities(self):
        e=estimate(branches(),deterministic=True)['effects']
        self.assertEqual(e,dict(tau_O=10.,tau_C=5.,tau_A=15.,tau_W=10.))
    def test_supported(self): self.assertEqual(self.run_rule()['status'],'supported')
    def test_exact_margin_abstains(self): self.assertEqual(self.run_rule(branches(2.5))['status'],'inconclusive')
    def test_small(self): self.assertEqual(self.run_rule(branches(0,0))['status'],'not supported')
    def test_info_cap(self):
        r=decide(branches(),deterministic=True,info_bearing=True,placebo_run=True)
        self.assertIn('info_loss_untested',r['reasons'])
    def test_efficient(self): self.assertIn('pattern_efficient_transfer',self.run_rule(branches(10,20))['reasons'])
    def test_mutual(self): self.assertIn('pattern_mutual_disruption',self.run_rule(branches(10,-2))['reasons'])
    def test_zero_benefit_fails(self): self.assertIn('pattern_mutual_disruption',self.run_rule(branches(10,0))['reasons'])
    def test_redundancy(self): self.assertIn('not_identifiable_redundant',self.run_rule(branches(0,0),flags=['resend_detected'])['reasons'])
    def test_invalid_precedes_ineligible(self): self.assertEqual(self.run_rule(validity=['V3'],ineligible='no_exposure')['status'],'invalid')
    def test_ineligible(self): self.assertEqual(self.run_rule(ineligible='post_decision')['reasons'],['ineligible:post_decision'])
    def test_placebo_literal_f_vs_n(self):
        b=branches(); b['N']=copy.deepcopy(b['K'])
        self.assertIn('lesion_artefact',self.run_rule(b)['reasons'])
    def test_sham_invalid(self): self.assertEqual(self.run_rule(sham_batch='invalid')['status'],'invalid')
    def test_sham_uncertain_nonblocking(self): self.assertEqual(self.run_rule(sham_batch='uncertain')['status'],'supported')
    def test_missing_no_zero(self):
        b=branches(); b['K']=[{'status':'failed','outcome':None}]
        r=self.run_rule(b); self.assertEqual(r['estimates']['effects'],{})
        self.assertIn('treatment_dependent_missingness',r['reasons'])
    def test_unvalidated_info(self): self.assertEqual(decide(branches(),deterministic=True,placebo_run=True)['status'],'inconclusive')
    def test_stochastic_singleton(self): self.assertEqual(estimate(branches())['intervals']['tau_O'],[None,None])
    def test_no_mutation(self):
        b=branches(); before=copy.deepcopy(b); self.run_rule(b); self.assertEqual(b,before)
    def test_bad_identity(self):
        b=branches(); b['K'][0]['outcome']['W']=0
        with self.assertRaises(ValueError): estimate(b)
    def test_floor(self):
        with self.assertRaises(ValueError): Parameters(m_O=1)
    def test_extract_literal(self):
        self.assertTrue(information('I am on TASK-03.'))
        self.assertFalse(information('I am on the backend item.'))
    def test_carrier_is_not_invalidity(self):
        r=carriers(['select TASK-01'],[{'turn':5,'surfaces':{'1':['select TASK-01']}}],2)
        self.assertIn('resend_detected',r)
    def test_divergences(self):
        self.assertEqual(js({'a':1},{'b':1}),1)
        self.assertEqual(tv({'a':1},{'b':1}),1)
    def test_baselines_ignore_info(self):
        e=estimate(branches(),deterministic=True)
        b=evaluate(e,receiver_tasks={'F':['a'],'K':['b']},next_tasks={'F':['a'],'K':['a']},next_outputs={'F':[('post_message',None)],'K':[('noop',None)]})
        self.assertEqual(b['B2']['label'],'flag'); self.assertEqual(b['B3a']['label'],'no flag'); self.assertEqual(b['B3b']['label'],'flag')

class StateCarriers(unittest.TestCase):
    def test_agent_tuple_required(self):
        from ccc.audit.text import matches
        self.assertFalse(matches('agent_0: I am on TASK-01','agent_1: I am on TASK-01',1.0))
    def test_explicit_state(self):
        r=carriers(['agent_0: I am on TASK-01'],[{'turn':2,'surfaces':{'state':['- agent_0: TASK-01']}}],2)
        self.assertIn('state_redundant',r)
    def test_later_state(self):
        r=carriers(['agent_0: I am on TASK-01'],[{'turn':3,'surfaces':{'state':['- agent_0: TASK-01']}}],2)
        self.assertIn('post_fork_carrier',r)

class InvalidEffect(unittest.TestCase):
    def test_invalid_has_no_interpretable_effect(self):
        result=decide(branches(),validity=['V1'],deterministic=True)
        self.assertEqual(result['status'],'invalid')
        self.assertEqual(result['estimates']['effects'],{})
