"""C4 oracle verification only: never import or run CCC or any baseline."""
from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
import unittest

from ccc.fixtures.constructed import (
    DERIVATION, FORBIDDEN_USES, M_O, assert_no_constructed, assert_not_constructed,
    generate_constructed, oracle_effects, oracle_episode,
)

TABLE = Path("docs/research/sci002/constructed_controls.json")


class ConstructedOracleTests(unittest.TestCase):
    def test_oracle_verifier_matches_derivation_for_all_30(self):
        rows = generate_constructed()
        self.assertEqual(len(rows), 30)
        self.assertEqual(Counter(r.block for r in rows), {"P": 8, "P-IB": 2, "N1": 8, "N2": 8, "N3": 4})
        k_ok = nv_ok = nm_zero = refused = 0
        for row in rows:
            with self.subTest(instance=row.instance_id):
                self.assertEqual(oracle_effects(row, "K"), row.expected_effects)
                k_ok += 1
                self.assertEqual(oracle_effects(row, "N_v1.1"), row.expected_effects)
                nv_ok += 1
                if row.chatter:
                    self.assertEqual(oracle_effects(row, "N_m"), dict.fromkeys(row.expected_effects, 0))
                    nm_zero += 1
                else:
                    with self.assertRaisesRegex(ValueError, "no_placebo_available"):
                        oracle_episode(row, "N_m")
                    refused += 1
        n_m = nm_zero
        print(f"C4 oracle verifier: {k_ok}/30 K effects, {nv_ok}/30 N_v1.1 effects, "
              f"{n_m}/{n_m} N_m zero effects; {refused}/{refused} absent-placebo refusals")

    def test_derived_tau_O_side_of_floor(self):
        # P-type and N3 must sit above m_O; N1 below it; N2 is path-inactive.
        for row in generate_constructed():
            tau_o = row.expected_effects["tau_O"]
            if row.block in ("P", "P-IB", "N3"):
                self.assertGreater(tau_o, M_O, row.instance_id)
            elif row.block == "N1":
                self.assertLess(tau_o, M_O, row.instance_id)
            else:
                self.assertEqual(tau_o, 0, row.instance_id)
        self.assertEqual(set(DERIVATION), {"P", "P-IB", "N1", "N2", "N3"})

    def test_prediction_table_matches_declarations(self):
        table = json.loads(TABLE.read_text())["instances"]
        rows = generate_constructed()
        self.assertEqual(len(table), 30)
        for row, saved in zip(rows, table):
            self.assertEqual(saved["instance_id"], row.instance_id)
            self.assertEqual(saved["expected_oracle"], {k: str(v) for k, v in row.expected_effects.items()})
            self.assertEqual(saved["expected_ccc_v1.2"], row.prediction)
        self.assertEqual(Counter(r.prediction["status"] for r in rows),
                         {"supported": 6, "inconclusive": 8, "not supported": 16})

    def test_exclusion_guards_all_protected_uses(self):
        for purpose in FORBIDDEN_USES:
            for row in generate_constructed():
                for representation in (row, asdict(row)):
                    with self.assertRaisesRegex(ValueError, "constructed controls forbidden"):
                        assert_no_constructed([representation], purpose=purpose)
            assert_no_constructed([{"tags": ["iid"]}], purpose=purpose)
        with self.assertRaises(ValueError):
            assert_no_constructed([], purpose="typo")

    def test_assert_not_constructed_raises_on_tagged_and_passes_clean(self):
        rows = generate_constructed()
        for row in rows:
            with self.assertRaisesRegex(ValueError, "must not enter"):
                assert_not_constructed([row])
            with self.assertRaisesRegex(ValueError, "must not enter"):
                assert_not_constructed([asdict(row)])
        with self.assertRaises(ValueError):
            assert_not_constructed([{"tags": ["iid"]}, {"tags": "constructed"}])
        clean = [{"tags": ["iid"], "instance_id": "iid-1"}, {"tags": ()}]
        self.assertIs(assert_not_constructed(clean), clean)

    def test_development_only_and_chatter_matching(self):
        with self.assertRaises(PermissionError):
            generate_constructed(phase="holdout")
        for row in generate_constructed():
            self.assertTrue(12000 <= row.seed < 12020)
            self.assertEqual(row.phase, "development")
            if row.chatter:
                self.assertEqual(len(row.chatter_text), len(row.signal))
                self.assertNotRegex(row.chatter_text, r"TASK|\d|agent_|claim|take")


if __name__ == "__main__":
    unittest.main()
