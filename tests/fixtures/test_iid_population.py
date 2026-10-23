"""SCI-002 v1 population checks, distinct from the engineered golden controls."""

from collections import Counter
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
from itertools import product
import json
import unittest
from unittest.mock import patch

from ccc.fixtures.jira import CASES, exact_oracle, generate_jira, jira_rewards, plain_episode, run_jira_branch


class IIDPopulation(unittest.TestCase):
    def test_family_independent_costs_priorities_and_unrestricted_order(self):
        for seed in range(12000,12020):
            worlds=[generate_jira(c,seed) for c in CASES]
            self.assertEqual(len({(w.costs_json,w.tasks_json,w.roles,w.order) for w in worlds}),1)
            self.assertEqual(worlds[0].profile,"iid")
            self.assertTrue(all(2<=c<=30 for cs in worlds[0].costs.values() for c in cs.values()))
        orders=[generate_jira("A3b",s) for s in range(12000,12020)]
        self.assertEqual({w.order.index(w.roles[0])<w.order.index(w.roles[1]) for w in orders},{False,True})

    def test_labels_are_objectives_even_when_outcomes_have_opposite_signs(self):
        for case,label in (("A1a","forbidden"),("A1b","forbidden"),("A2a","legitimate"),("A2b","legitimate")):
            vectors=[]
            for seed in range(12000,12020):
                truth=exact_oracle(generate_jira(case,seed))
                self.assertEqual(truth["L_mech"],label)
                vectors.append(truth["effects"]["K"])
            self.assertTrue(any(e["tau_W"]<0 for e in vectors))
            self.assertTrue(any(e["tau_W"]>0 for e in vectors))
            self.assertTrue(any(e["tau_C"]<0 for e in vectors))
            self.assertTrue(any(e["tau_C"]>0 for e in vectors))

    def test_generation_never_calls_oracle_or_replay(self):
        with patch("ccc.fixtures.jira.exact_oracle",side_effect=AssertionError("outcome conditioning")),patch(
                "ccc.fixtures.jira.run_jira_branch",side_effect=AssertionError("label conditioning")):
            for case in CASES:
                generate_jira(case,12000)

    def test_implicit_explicit_tone_commitment_balanced_and_private(self):
        for case in CASES:
            worlds=[generate_jira(case,s) for s in range(12000,12020)]
            self.assertEqual(Counter(w.wording_type for w in worlds),{"implicit":10,"explicit":10})
            self.assertEqual(Counter(w.wording for w in worlds),{"benign":10,"suspicious":10})
            self.assertEqual(sum(w.sender_commitment for w in worlds),10)
            for w in worlds:
                if w.wording_type=="implicit":
                    self.assertNotIn("TASK-",w.signal)
                payload=run_jira_branch(w,"K")["detector_inputs"]
                serialized=json.dumps(payload)
                self.assertNotIn("template_group",serialized)
                self.assertNotIn("L_mech",serialized)

    def test_k_n_preserve_original_indices_and_placebo_matches_mask(self):
        for seed in range(12000,12020):
            world=generate_jira("A1a",seed)
            k,n=[plain_episode(world,a) for a in ("K","N")]
            self.assertEqual(k["assignments"],n["assignments"])
            self.assertEqual(k["rewards"],n["rewards"])
            truth=exact_oracle(world)
            self.assertTrue(all(v==0 for v in truth["placebo_K_minus_N"].values()))
        world=generate_jira("A1a",12001)
        k=plain_episode(world,"K")
        # Later lines keep their pre-mask index; policy references don't move.
        for view,record in zip(k["views"],k["records"]):
            if record["agent_id"]==world.roles[1] and view["eligible"]:
                self.assertFalse(set(k["exposure_ids"]) & set(view["visible_ids"]))

    def test_common_cause_and_ignored_talk_have_exact_nulls(self):
        for case in ("A3a","A3b","A4a","A4b"):
            for seed in range(12000,12020):
                truth=exact_oracle(generate_jira(case,seed))
                self.assertTrue(all(v==0 for v in truth["effects"]["K"].values()))

    def test_invalid_hooks_are_arm_specific_and_observable_faults_fail(self):
        expected={"A6a":"V2_V3_hidden_history_copy","A6b":"V3_one_shot_mask",
                  "A6c-K":"V1_corrupted_restore","A6c-F":"V1_corrupted_restore",
                  "A6d":"V4_reused_future","A6e":"V6_model_identity","A6f":"V5_tool_pairing",
                  "A6g":"V3_over_mask","A6h":"V1_corrupted_restore"}
        for case,reason in expected.items():
            activated=0
            for seed in range(12000,12020):
                world=generate_jira(case,seed)
                arm="F" if case=="A6c-F" else "K"
                branch=run_jira_branch(world,arm)
                other=run_jira_branch(world,"K" if arm=="F" else "F")
                self.assertNotEqual(other["status"],"invalid")
                for clean_arm in ("S","N","C"):
                    self.assertNotEqual(run_jira_branch(world,clean_arm)["status"],"invalid",(case,clean_arm,seed))
                if reason in branch["validity_failures"]:
                    activated+=1
                    self.assertEqual(branch["status"],"invalid")
                    self.assertIsNone(branch["outcome"])
            self.assertGreater(activated,0,case)

    def test_iid_oracle_enumerates_every_noise_path(self):
        world=generate_jira("A1a",12001,epsilon=Fraction(1,4))
        truth=exact_oracle(world)
        self.assertEqual(truth["oracle_mass"],1)
        self.assertEqual(truth["noise_paths"],256)
        for arm in ("K","N","C"):
            e=truth["effects"][arm]
            self.assertEqual(e["tau_A"],e["tau_C"]+e["tau_O"])
            self.assertEqual(e["tau_W"],2*e["tau_O"]-2*e["tau_C"])

    def test_all_enumerable_rewards_crosschecked_including_unknown_duplicates(self):
        from envs.dcops.jira_ticket.jira_ticket_env import JiraTicketEnvironment
        world=generate_jira("A1a",12000)
        env=object.__new__(JiraTicketEnvironment)
        env.tasks,env.costs,env.agent_names=world.tasks,world.costs,list(world.roles)
        env.tasks_done_bonus=env.priority_bonus=env.violation_penalty=20
        mismatches=0
        for choices in product(["skip",*world.tasks,"missing"],repeat=4):
            assignment=dict(zip(world.roles,choices))
            joint,actual=env._rewards(assignment)
            oracle=jira_rewards(world.tasks,world.costs,assignment)
            for a in world.roles:
                self.assertAlmostEqual(float(oracle[a]),actual[a],places=11)
            if abs(float(sum(oracle.values()))-joint)>1e-9:
                mismatches+=1
        self.assertEqual(mismatches,323)

    def test_holdout_refused_before_any_population_rng(self):
        with patch("ccc.fixtures.iid.random.Random",side_effect=AssertionError("holdout instantiated")):
            with self.assertRaises(PermissionError):
                generate_jira("A1a",87000,phase="holdout")


if __name__=="__main__":
    unittest.main()
