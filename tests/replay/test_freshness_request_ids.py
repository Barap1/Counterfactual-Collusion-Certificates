"""V09 freshness keyed on client-generated request ids (Ollama's provider ids repeat; they prove nothing)."""

import unittest

from ccc.replay.recorder import RequestRecord
from ccc.replay.validators import check_fresh

BOUNDARY = 3


def rec(seq, client_rid, response_id, *, unique, cache_mode="fresh", turn=5):
    return RequestRecord(
        seq=seq, branch_id="F", replicate_id="0", turn_index=turn, agent="a", phase="p", planning_round=None,
        step=1, request={"messages": [], "params": {}}, request_sha256="0" * 64,
        response={"id": response_id}, response_id=response_id, cache_mode=cache_mode, finish_reason="stop",
        latency_ms=1.0, client_request_id=client_rid, unique_response_ids=unique)


class FreshnessRequestIdTests(unittest.TestCase):

    def test_a_ollama_repeating_provider_ids_with_distinct_request_ids_pass(self):
        # Ollama-style: "chatcmpl-NN" repeats within the branch and across source and other branches.
        branch = [rec(i, f"req-{i}", f"chatcmpl-{i % 2}", unique=False) for i in range(4)]
        res = check_fresh(branch, BOUNDARY, {"chatcmpl-0", "chatcmpl-1"}, {"chatcmpl-0"},
                          source_request_ids={"src-1"}, other_request_ids={"other-1"})
        self.assertEqual(res.status, "pass", res.details)

    def test_b_reused_client_request_id_across_branches_fails(self):
        branch = [rec(0, "req-shared", "x-0", unique=False), rec(1, "req-1", "x-1", unique=False)]
        res = check_fresh(branch, BOUNDARY, set(), set(), other_request_ids={"req-shared"})
        self.assertEqual(res.status, "fail")
        self.assertTrue(any("shared with another branch" in p for p in res.details["problems"]))

    def test_b2_client_request_id_reused_from_source_fails(self):
        branch = [rec(0, "src-req", "x-0", unique=False)]
        res = check_fresh(branch, BOUNDARY, set(), set(), source_request_ids={"src-req"})
        self.assertEqual(res.status, "fail")
        self.assertTrue(any("reused from the source run" in p for p in res.details["problems"]))

    def test_c_missing_client_request_id_fails(self):
        branch = [rec(0, "req-0", "a", unique=True), rec(1, None, "b", unique=True)]
        res = check_fresh(branch, BOUNDARY, set(), set())
        self.assertEqual(res.status, "fail")
        self.assertTrue(any("without client request id" in p for p in res.details["problems"]))

    def test_d_scripted_backend_reused_provider_id_fails(self):
        branch = [rec(0, "req-0", "scripted:n:1", unique=True), rec(1, "req-1", "scripted:n:1", unique=True)]
        res = check_fresh(branch, BOUNDARY, set(), set())
        self.assertEqual(res.status, "fail")
        self.assertTrue(any("duplicate response ids" in p for p in res.details["problems"]))

    def test_d2_scripted_provider_id_shared_with_other_branch_fails(self):
        branch = [rec(0, "req-0", "scripted:n:7", unique=True)]
        res = check_fresh(branch, BOUNDARY, set(), {"scripted:n:7"})
        self.assertEqual(res.status, "fail")

    def test_non_fresh_cache_mode_fails(self):
        branch = [rec(0, "req-0", "a", unique=True, cache_mode="prefix_replay")]
        res = check_fresh(branch, BOUNDARY, set(), set())
        self.assertEqual(res.status, "fail")

    def test_fake_clients_declare_unique_ids_and_mint_a_request_id_per_call(self):
        from ccc.replay.clients import ScriptedClient, new_request_id
        self.assertTrue(ScriptedClient.unique_response_ids)
        self.assertEqual(len(new_request_id()), 32)
        client = ScriptedClient(lambda call: {"content": "ok"}, nonce="t")
        params = {"model": "m", "tools": []}
        client.generate_response([{"role": "system", "content": "s"}, {"role": "user", "content": "u"}], params,
                                 ccc_context={"turn_index": 0, "agent": "a", "step": 1})
        first = client.last_request_id
        client.generate_response([{"role": "system", "content": "s"}, {"role": "user", "content": "u"}], params,
                                 ccc_context={"turn_index": 0, "agent": "a", "step": 2})
        self.assertIsNotNone(first)
        self.assertNotEqual(first, client.last_request_id)


if __name__ == "__main__":
    unittest.main()
