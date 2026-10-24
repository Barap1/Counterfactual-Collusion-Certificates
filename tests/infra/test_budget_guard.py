"""Offline tests for ccc.infra.budget_guard (no network: all transports are fakes)."""

import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ccc.infra import budget_guard as bg

LOCAL = "http://127.0.0.1:11434/v1"
FAKE_OR_KEY = "sk-or-v1-" + "0" * 40  # fake test value, never a real key


def ok_response(model="gemma4:latest", cost=None, tool_calls=None, include_cost=False):
    usage = {"prompt_tokens": 10, "completion_tokens": 5}
    if include_cost:
        usage["cost"] = cost
    msg = {"role": "assistant", "content": "hi"}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return {"model": model, "choices": [{"message": msg, "finish_reason": "stop"}], "usage": usage}


class FakeTransport:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, url, headers, body, timeout):
        self.calls.append({"url": url, "headers": dict(headers), "body": json.loads(body)})
        code, payload = self.replies.pop(0)
        if isinstance(payload, Exception):
            raise payload
        return code, json.dumps(payload).encode()


class GuardTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name) / "ledger.jsonl"
        self.policy = bg.GuardPolicy()
        self.env = mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": FAKE_OR_KEY})
        self.env.start()
        self.sleep = mock.patch.object(bg.time, "sleep", lambda s: None)
        self.sleep.start()

    def tearDown(self):
        self.sleep.stop()
        self.env.stop()
        self.tmp.cleanup()

    def guard(self, max_calls=5, **pol):
        for k, v in pol.items():
            setattr(self.policy, k, v)
        return bg.BudgetGuard(run_id="t", task_id="TEST", max_calls=max_calls, policy=self.policy,
                              ledger_path=self.ledger)

    def records(self):
        return [json.loads(l) for l in self.ledger.read_text().splitlines() if l.strip()]


class AllowlistTests(GuardTestBase):
    def test_refuses_aliases_paid_cloud_and_wrong_hosts(self):
        g = self.guard()
        bad = [
            (bg.BACKEND_OPENROUTER, "openrouter/free", bg.OPENROUTER_BASE_URL),
            (bg.BACKEND_OPENROUTER, "openrouter/auto", bg.OPENROUTER_BASE_URL),
            (bg.BACKEND_OPENROUTER, "cohere/north-mini-code", bg.OPENROUTER_BASE_URL),
            (bg.BACKEND_OPENROUTER, "openai/gpt-4o-mini", bg.OPENROUTER_BASE_URL),
            (bg.BACKEND_OPENROUTER, "cohere/north-mini-code:free", "https://evil.example/api/v1"),
            (bg.BACKEND_OLLAMA, "gpt-oss:120b-cloud", LOCAL),
            (bg.BACKEND_OLLAMA, "gemma4:latest", "http://10.0.0.5:11434/v1"),
            (bg.BACKEND_OLLAMA, "gemma4:latest", "https://ollama.com/v1"),
            (bg.BACKEND_OLLAMA, "qwen3:8b", LOCAL),
            ("together", "x", "https://api.together.xyz/v1"),
        ]
        for backend, model, url in bad:
            with self.subTest(model=model, url=url):
                with self.assertRaises(bg.BudgetViolation):
                    g.check_request(backend, model, url)
        g.check_request(bg.BACKEND_OLLAMA, "gemma4:26b", LOCAL)  # allowed

    def test_openrouter_requires_zero_pricing_check(self):
        g = self.guard()
        m = "cohere/north-mini-code:free"
        with self.assertRaises(bg.BudgetViolation):
            g.check_request(bg.BACKEND_OPENROUTER, m, bg.OPENROUTER_BASE_URL)
        with self.assertRaises(bg.BudgetViolation):
            g.record_openrouter_pricing(m, {"prompt": "0", "completion": "0.000001"}, source="test")
        with self.assertRaises(bg.BudgetViolation):
            g.record_openrouter_pricing(m, {}, source="test")
        g.record_openrouter_pricing(m, {"prompt": "0", "completion": "0", "request": "0"}, source="test")
        g.check_request(bg.BACKEND_OPENROUTER, m, bg.OPENROUTER_BASE_URL)

    def test_policy_file_keeps_modal_blocked_and_strips_aliases(self):
        p = Path(self.tmp.name) / "policy.json"
        p.write_text(json.dumps({"openrouter": {"allowed_models": ["cohere/north-mini-code:free", "openrouter/free"],
                                                "max_in_flight": 4}, "modal": {"status": "BLOCKED"}}))
        pol = bg.GuardPolicy.from_policy_file(p)
        self.assertEqual(pol.openrouter_models, ("cohere/north-mini-code:free",))
        self.assertEqual(pol.max_in_flight, 1)
        self.assertFalse(pol.modal_enabled)
        self.assertFalse(bg.GuardPolicy.from_policy_file(Path(self.tmp.name) / "missing.json").modal_enabled)
        p.write_text(json.dumps({"modal": {"status": "APPROVED", "spend_cap_usd": 100}}))
        self.assertEqual(bg.GuardPolicy.from_policy_file(p).modal_spend_cap_usd, 45.0)


class CapAndLedgerTests(GuardTestBase):
    def test_call_cap_counts_retries(self):
        g = self.guard(max_calls=2)
        t = FakeTransport([(503, {"error": "busy"}), (503, {"error": "busy"}), (200, ok_response())])
        c = bg.GuardedChatClient(g, backend=bg.BACKEND_OLLAMA, model="gemma4:latest", base_url=LOCAL, transport=t)
        with self.assertRaises(bg.BudgetViolation):
            c.generate_response(c.init_context("s", "u"), {})
        self.assertEqual(len(t.calls), 2)
        begins = [r for r in self.records() if r["event"] == "attempt_begin"]
        ends = [r for r in self.records() if r["event"] == "attempt_end"]
        self.assertEqual(len(begins), 2)
        self.assertEqual(len(ends), 2)

    def test_ledger_is_append_only_and_secret_free(self):
        g = self.guard()
        t = FakeTransport([(401, {"error": f"bad key {FAKE_OR_KEY}"})])
        c = bg.GuardedChatClient(g, backend=bg.BACKEND_OLLAMA, model="gemma4:latest", base_url=LOCAL, transport=t)
        with self.assertRaises(RuntimeError):
            c.generate_response(c.init_context("s", "u"), {})
        text = self.ledger.read_text()
        self.assertNotIn(FAKE_OR_KEY, text)
        self.assertNotIn("Bearer", text)
        self.assertIn("[REDACTED]", text)
        before = text
        g.close("done")
        self.assertTrue(self.ledger.read_text().startswith(before))
        with self.assertRaises(bg.BudgetViolation):
            g.ledger.append({"event": "x", "Authorization": "y"})
        with self.assertRaises(bg.BudgetViolation):
            g.ledger.append({"event": "x", "note": FAKE_OR_KEY})

    def test_local_backend_never_receives_openrouter_key_and_seed_passes(self):
        g = self.guard()
        t = FakeTransport([(200, ok_response())])
        c = bg.GuardedChatClient(g, backend=bg.BACKEND_OLLAMA, model="gemma4:latest", base_url=LOCAL, transport=t)
        _, text = c.generate_response(c.init_context("s", "u"),
                                      {"model": "gemma4:latest", "temperature": 0, "seed": 7, "max_tokens": 64})
        self.assertEqual(text, "hi")
        sent = t.calls[0]
        self.assertEqual(sent["headers"]["Authorization"], "Bearer ollama")
        self.assertEqual(sent["body"]["seed"], 7)
        self.assertEqual(sent["body"]["temperature"], 0)
        self.assertEqual(sent["body"]["max_tokens"], 64)
        self.assertNotIn("provider", sent["body"])
        with self.assertRaises(bg.BudgetViolation):
            c.generate_response(c.init_context("s", "u"), {"model": "gemma4:26b"})

    def test_daily_openrouter_cap_from_ledger(self):
        g = self.guard(openrouter_daily_cap=1)
        m = "cohere/north-mini-code:free"
        g.record_openrouter_pricing(m, {"prompt": "0", "completion": "0"}, source="test")
        t = FakeTransport([(200, ok_response(model=m, cost=0, include_cost=True))])
        c = bg.GuardedChatClient(g, backend=bg.BACKEND_OPENROUTER, model=m, base_url=bg.OPENROUTER_BASE_URL, transport=t)
        c.generate_response(c.init_context("s", "u"), {})
        body = t.calls[0]["body"]
        self.assertEqual(t.calls[0]["headers"]["Authorization"], f"Bearer {FAKE_OR_KEY}")
        self.assertFalse(body["provider"]["allow_fallbacks"])
        self.assertEqual(body["provider"]["max_price"]["completion"], 0)
        self.assertTrue(body["usage"]["include"])
        self.assertNotIn("models", body)
        with self.assertRaises(bg.BudgetHalt):
            c.generate_response(c.init_context("s", "u"), {})


class HaltTests(GuardTestBase):
    M = "cohere/north-mini-code:free"

    def _client(self, g, replies):
        g.record_openrouter_pricing(self.M, {"prompt": "0", "completion": "0"}, source="test")
        return bg.GuardedChatClient(g, backend=bg.BACKEND_OPENROUTER, model=self.M,
                                    base_url=bg.OPENROUTER_BASE_URL, transport=FakeTransport(replies))

    def test_positive_cost_halts_persistently(self):
        g = self.guard()
        c = self._client(g, [(200, ok_response(model=self.M, cost=0.0001, include_cost=True))])
        with self.assertRaises(bg.BudgetHalt):
            c.generate_response(c.init_context("s", "u"), {})
        with self.assertRaises(bg.BudgetHalt):
            self.guard()  # a new run refuses to open while HALT is uncleared
        bg.Ledger(self.ledger).append({"event": "halt_cleared", "by": "owner-test"})
        self.guard()

    def test_missing_cost_halts_openrouter_only(self):
        g = self.guard()
        c = self._client(g, [(200, ok_response(model=self.M))])
        with self.assertRaises(bg.BudgetHalt):
            c.generate_response(c.init_context("s", "u"), {})
        g2 = self.guard()  # not a global halt: a new run can open
        with self.assertRaises(bg.BudgetHalt):
            g2.check_request(bg.BACKEND_OPENROUTER, self.M, bg.OPENROUTER_BASE_URL)
        g2.check_request(bg.BACKEND_OLLAMA, "gemma4:latest", LOCAL)  # local still allowed

    def test_key_status_tightens_daily_cap(self):
        g = self.guard()
        with self.assertRaises(bg.BudgetViolation):
            g.apply_openrouter_key_status({"is_free_tier": False})
        with self.assertRaises(bg.BudgetViolation):
            g.apply_openrouter_key_status({"is_free_tier": True, "usage": 0})
        allowed = g.apply_openrouter_key_status({"is_free_tier": True, "usage": 0, "usage_daily": 0,
                                                 "free_model_daily_requests": {"used": 48, "limit": 50, "remaining": 2}},
                                                reserve=2)
        self.assertEqual(allowed, 0)
        g.record_openrouter_pricing(self.M, {"prompt": "0", "completion": "0"}, source="test")
        with self.assertRaises(bg.BudgetHalt):
            g.check_request(bg.BACKEND_OPENROUTER, self.M, bg.OPENROUTER_BASE_URL)
        with self.assertRaises(bg.BudgetHalt):
            g.apply_openrouter_key_status({"is_free_tier": True, "usage": 0.002,
                                           "free_model_daily_requests": {"remaining": 10}})
        with self.assertRaises(bg.BudgetHalt):
            self.guard()  # nonzero account usage is a global halt

    def test_resolved_model_mismatch_halts(self):
        g = self.guard()
        c = self._client(g, [(200, ok_response(model="openai/gpt-4o", cost=0, include_cost=True))])
        with self.assertRaises(bg.BudgetHalt):
            c.generate_response(c.init_context("s", "u"), {})

    def test_openrouter_429_halts_without_retry(self):
        g = self.guard()
        c = self._client(g, [(429, {"error": "rate"}), (200, ok_response(model=self.M, cost=0, include_cost=True))])
        with self.assertRaises(bg.BudgetHalt):
            c.generate_response(c.init_context("s", "u"), {})
        self.assertEqual(len(c.transport.calls), 1)


class ModalTests(GuardTestBase):
    URL = "https://ws--app.modal.run/v1"

    def test_modal_blocked_by_default(self):
        g = self.guard(modal_models=("Qwen/Qwen3-8B",))
        with self.assertRaises(bg.BudgetViolation):
            g.check_request(bg.BACKEND_MODAL, "Qwen/Qwen3-8B", self.URL)
        with self.assertRaises(bg.BudgetViolation):
            g.reserve_modal(1.0)

    def test_modal_requires_verified_fresh_billing_and_cap(self):
        g = self.guard(modal_enabled=True, modal_models=("Qwen/Qwen3-8B",))
        with self.assertRaises(bg.BudgetViolation):
            g.check_request(bg.BACKEND_MODAL, "Qwen/Qwen3-8B", self.URL)  # no billing snapshot
        g.record_modal_billing(10.0, source="test", verified=False)
        with self.assertRaises(bg.BudgetViolation):
            g.check_request(bg.BACKEND_MODAL, "Qwen/Qwen3-8B", self.URL)  # unverified
        g.record_modal_billing(10.0, source="test", verified=True)
        g.check_request(bg.BACKEND_MODAL, "Qwen/Qwen3-8B", self.URL)
        with self.assertRaises(bg.BudgetViolation):
            g.check_request(bg.BACKEND_MODAL, "Qwen/Qwen3-8B", "http://ws--app.modal.run/v1")
        g.reserve_modal(30.0)
        with self.assertRaises(bg.BudgetViolation):
            g.reserve_modal(6.0)  # 10 + 30 + 6 > 45
        with self.assertRaises(bg.BudgetHalt):
            g.record_modal_billing(45.0, source="test", verified=True)
        with self.assertRaises(bg.BudgetHalt):
            g.check_request(bg.BACKEND_MODAL, "Qwen/Qwen3-8B", self.URL)

    def test_modal_never_uses_openrouter_key(self):
        with self.assertRaises(bg.BudgetViolation):
            bg.api_key_for(bg.BACKEND_MODAL, "OPENROUTER_API_KEY")
        self.assertEqual(bg.api_key_for(bg.BACKEND_OLLAMA), "ollama")


class ToolLoopTests(GuardTestBase):
    def test_process_tool_calls_matches_terrarium_semantics(self):
        g = self.guard()
        c = bg.GuardedChatClient(g, backend=bg.BACKEND_OLLAMA, model="gemma4:latest", base_url=LOCAL,
                                 transport=FakeTransport([]))
        resp = ok_response(tool_calls=[
            {"id": "c1", "type": "function", "function": {"name": "post_message", "arguments": '{"message": "x", "blackboard_id": 0}'}},
            {"id": "c2", "type": "function", "function": {"name": "post_message", "arguments": "{not json"}},
        ])
        seen = []

        async def cb(name, args):
            seen.append((name, args))
            return {"ok": True}

        n, ctx, steps = asyncio.run(c.process_tool_calls(resp, [], cb))
        self.assertEqual(n, 2)
        self.assertEqual(seen[0], ("post_message", {"message": "x", "blackboard_id": 0}))
        self.assertEqual(seen[1], ("post_message", {}))
        self.assertEqual([m["role"] for m in ctx], ["assistant", "tool", "tool"])


if __name__ == "__main__":
    unittest.main()
