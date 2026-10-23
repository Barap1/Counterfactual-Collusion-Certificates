"""REV-GA independent fault injection. Public APIs only; each test must show a check FIRES.
Each test also asserts the clean control passes, so a vacuous always-fail check cannot satisfy it."""
import copy, json, tempfile, unittest
from pathlib import Path

from tests.replay import _support as S


def setUpModule():
    S.block_network()


def tearDownModule():
    S.restore_network()


class Faults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from ccc.replay.fixtures import run_fixture, signal_fixture
        cls.rep = run_fixture(signal_fixture())
        cls.cp = cls.rep.audit.checkpoint
        from ccc.replay.engine import scripted_factory
        cls.facs = (scripted_factory(cls.rep.fixture.policy_factory),)

    def _check(self, br, cid):
        return next(c for c in br.checks if c.id == cid)

    def test_clean_controls_valid(self):
        from ccc.replay.engine import run_branch
        for arm in ("F", "K"):
            br = run_branch(self.cp, arm, self.facs[0])
            self.assertEqual(br.status, "valid", (arm, br.reasons))

    def test_1_leaked_masked_copy_in_receiver_view(self):
        from ccc.replay.engine import run_branch
        from ccc.replay.interventions import receiver_mask_hook
        ex = self.cp.exposure
        base = receiver_mask_hook(ex)

        def leaky(agent, turn, view):  # my own leak: masked text re-appears as a SYSTEM context event
            out, d = base(agent, turn, view)
            if d["active"] and out:
                bb = sorted(out, key=int)[0]
                out[bb] = list(out[bb]) + [{"id": "rev-ga-leak", "agent": "SYSTEM", "kind": "context",
                                            "payload": {"message": "Reminder: " + ex.content}}]
            return out, d

        br = run_branch(self.cp, "K", self.facs[0], hook=leaky)
        self.assertEqual(br.status, "invalid")
        self.assertEqual(self._check(br, "V07").status, "fail")
        self.assertTrue(self._check(br, "V07").details["leaks"])

    def test_1b_leak_in_paraphrase_is_NOT_expected_to_fire(self):
        """Documents the known limit (not an assertion of success): a light paraphrase of the
        masked text re-injected into the receiver view. Records whether V07 fires."""
        from ccc.replay.engine import run_branch
        from ccc.replay.interventions import receiver_mask_hook
        ex = self.cp.exposure
        base = receiver_mask_hook(ex)

        def para(agent, turn, view):
            out, d = base(agent, turn, view)
            if d["active"] and out:
                bb = sorted(out, key=int)[0]
                words = ex.content.split()
                text = "Heads up, in other words: " + " ".join(reversed(words))
                out[bb] = list(out[bb]) + [{"id": "rev-ga-para", "agent": "SYSTEM", "kind": "context",
                                            "payload": {"message": text}}]
            return out, d

        br = run_branch(self.cp, "K", self.facs[0], hook=para)
        print("REV-GA word-reversed paraphrase leak: status=%s V07=%s" % (br.status, self._check(br, "V07").status))

    def test_2_tampered_ledger_byte(self):
        from ccc.replay.engine import run_branch
        from ccc.replay.ledger import verify_branch
        with tempfile.TemporaryDirectory() as d:
            br = run_branch(self.cp, "K", self.facs[0], ledger_dir=d)
            self.assertEqual(verify_branch(br.ledger_path)["records"], len(br.records))
            ev = Path(br.ledger_path)
            raw = bytearray(ev.read_bytes())
            i = raw.index(b"response_sha256") + 25
            raw[i] = ord("0") if raw[i] != ord("0") else ord("1")
            ev.write_bytes(bytes(raw))
            with self.assertRaises(ValueError):
                verify_branch(br.ledger_path)
        with tempfile.TemporaryDirectory() as d:  # also flip one byte of a request artifact
            br = run_branch(self.cp, "K", self.facs[0], ledger_dir=d)
            art = sorted(p for p in Path(br.ledger_path).parent.iterdir() if p.name.startswith("request") or "req" in p.name)
            self.assertTrue(art)
            b = bytearray(art[0].read_bytes()); b[len(b) // 2] ^= 1; art[0].write_bytes(bytes(b))
            with self.assertRaises(ValueError):
                verify_branch(br.ledger_path)

    def test_3_reused_nonfresh_response(self):
        from ccc.replay.clients import ReusingClient
        from ccc.replay.engine import run_branch
        recorded = self.rep.source.ledger.at_or_after(self.cp.boundary)
        br = run_branch(self.cp, "F", lambda n, w: ReusingClient([r for r in recorded if r.agent == n]))
        self.assertEqual(br.status, "invalid")
        self.assertEqual(self._check(br, "V09").status, "fail")

    def test_3b_cross_branch_response_sharing(self):
        from ccc.replay.engine import run_branch
        from ccc.replay.validators import check_fresh
        f = run_branch(self.cp, "F", self.facs[0])
        ids = {r.response_id for r in f.records}
        self.assertEqual(check_fresh(f.records, self.cp.boundary, set(), set()).status, "pass")
        self.assertEqual(check_fresh(f.records, self.cp.boundary, set(), ids).status, "fail")

    def test_4_model_id_mismatch(self):
        from ccc.replay.clients import ScriptedClient
        from ccc.replay.engine import run_branch

        class Wrong(ScriptedClient):
            def generate_response(self, input, params, ccc_context=None):  # noqa: A002
                resp, text = super().generate_response(input, params, ccc_context)
                resp["model"] = "other/model-v2"
                return resp, text
        br = run_branch(self.cp, "K", lambda n, w: Wrong(self.rep.fixture.policy_factory(), nonce="rev/" + n))
        self.assertEqual(br.status, "invalid")
        self.assertEqual(self._check(br, "V-model").status, "fail")

    def test_4b_requested_model_mismatch(self):
        from ccc.replay.validators import check_model_identity
        recs = run = None
        from ccc.replay.engine import run_branch
        recs = run_branch(self.cp, "F", self.facs[0]).records
        self.assertEqual(check_model_identity(recs, self.cp.spec.model_name).status, "pass")
        self.assertEqual(check_model_identity(recs, "expected/other").status, "fail")

    def test_5_cross_branch_state_mutation(self):
        from ccc.replay.engine import run_branch
        from ccc.replay.validators import check_isolation
        a = run_branch(self.cp, "F", self.facs[0]); b = run_branch(self.cp, "K", self.facs[0])
        snap = self.cp.snapshot
        before = snap.dynamic
        self.assertEqual(check_isolation([a.world, b.world], snap, before).status, "pass")
        # (i) alias a mutable container across branch worlds
        b.world.env.assignment = a.world.env.assignment
        r = check_isolation([a.world, b.world], snap, before)
        self.assertEqual(r.status, "fail", r.details)
        # (ii) aliased board log list
        a2 = run_branch(self.cp, "F", self.facs[0]); b2 = run_branch(self.cp, "K", self.facs[0])
        b2.world.protocol.megaboard.blackboards[0].logs = a2.world.protocol.megaboard.blackboards[0].logs
        self.assertEqual(check_isolation([a2.world, b2.world], snap, before).status, "fail")
        # (iii) checkpoint snapshot bytes changed after branching
        self.assertEqual(check_isolation([a2.world], snap, before + b" ").status, "fail")


if __name__ == "__main__":
    unittest.main()
