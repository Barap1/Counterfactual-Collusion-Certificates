"""Duck-typed tests of the replay engineer's PolicyCall/Policy interface."""

import json
from types import SimpleNamespace
import unittest

from ccc.fixtures import Family, generate, run_branch
from ccc.fixtures.replay_adapter import make_policy, policy_messages


class ReplayPolicyAdapter(unittest.TestCase):
    def test_policy_callable_matches_structural_receiver_for_all_valid_families(self):
        for family in Family:
            if family == Family.INVALID:
                continue
            for seed in range(12000, 12020):
                world = generate(family, seed)
                policy = make_policy(world)
                for arm in ("F", "S", "K"):
                    call = SimpleNamespace(agent=world.receiver, messages=policy_messages(world, arm), tool_names=[])
                    result = policy(call)
                    self.assertEqual(json.loads(result["content"])["action"], run_branch(world, arm)["outcome"]["action"])
                    self.assertEqual(result["tool_calls"], [])

    def test_policy_emits_tool_call_shape_expected_by_scripted_client(self):
        world = generate(Family.HARMFUL, 12000)
        result = make_policy(world)(SimpleNamespace(
            agent=world.receiver, messages=policy_messages(world), tool_names=["commit_dispatch"],
        ))
        self.assertEqual(result, {"content": "", "tool_calls": [{"name": "commit_dispatch", "arguments": {"action": "route"}}]})

    def test_sender_and_other_agents_are_scripted(self):
        world = generate(Family.HARMFUL, 12000)
        policy = make_policy(world)
        sender = policy(SimpleNamespace(agent=world.sender, messages=policy_messages(world, agent_id=world.sender), tool_names=[]))
        other = policy(SimpleNamespace(agent=world.agents[2], messages=policy_messages(world, agent_id=world.agents[2]), tool_names=[]))
        self.assertEqual(json.loads(sender["content"]), {"text": world.message})
        self.assertEqual(json.loads(other["content"]), {"action": "wait"})

    def test_joint_knockout_and_mismatched_world(self):
        world = generate(Family.REDUNDANT, 12000)
        call = SimpleNamespace(agent=world.receiver, messages=policy_messages(world, "K", joint_mask=True), tool_names=[])
        self.assertEqual(json.loads(make_policy(world)(call)["content"])["action"], "base")
        call.messages = policy_messages(generate(Family.HARMFUL, 12001))
        with self.assertRaises(ValueError):
            make_policy(world)(call)

    def test_masked_agent_never_receives_another_agents_intact_copy(self):
        world = generate(Family.HARMFUL, 12000)
        request = policy_messages(world, "K")
        self.assertNotIn(world.message, request[0]["content"])
        payload = json.loads(request[0]["content"])
        self.assertEqual({o["agent_id"] for o in payload["observations"]}, {world.receiver})


if __name__ == "__main__":
    unittest.main()
