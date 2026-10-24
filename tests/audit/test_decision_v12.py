"""AMD-IMP-3: decide() under v1.2 (no_placebo_available, exact lesion test, contrast, record text)."""
from tests.audit.placebo_evidence import bind, SELECTION
import unittest

from ccc.audit.decision import decide, exact_bounds, SUPPORTED_RECORD_TEXT


def out(o, c=10., ):
    return {"Omean": o, "Cmean": c, "A": c - o, "W": 2 * c + 2 * o}


def arms(f=10., k=20., n=10., c_k=5., spread=0.):
    def rows(base, cm):
        return [{"status": "complete", "outcome": out(base + spread * i, cm)} for i in range(4)]
    b = {"F": rows(f, 15.), "S": rows(f, 15.), "K": rows(k, c_k)}
    if n is not None:
        b["N"] = rows(n, 15.)
    return bind(b)


class V12(unittest.TestCase):
    def test_exact_bounds_reference_vectors(self):
        self.assertEqual(exact_bounds([0, 1, 2, 3], [10, 11, 12, 13]), (8.0, 12.0))
        self.assertEqual(exact_bounds([4, 7, 9, 12], [6, 10, 13, 15]), (-2.5, 8.5))
        self.assertEqual(exact_bounds([5] * 4, [12.5] * 4), (7.5, 7.5))
        self.assertEqual(exact_bounds([3, 5, 8, 6], [4, 6, 7, 5]), (-2.5, 2.5))

    def test_supported_prints_required_text_and_mandatory_contrast(self):
        d = decide(arms(), deterministic=True, info_bearing=False, placebo_run=True, placebo_selection=SELECTION, placebo_status="accepted")
        self.assertEqual(d["status"], "supported")
        self.assertEqual(d["record_text"], SUPPORTED_RECORD_TEXT)
        c = d["tau_O_minus_tau_O_N"]
        self.assertEqual((c["estimate"], c["interval"], c["gating"]), (10., [10., 10.], False))

    def test_exact_lesion_test_uses_c3_p_ge_m_O(self):
        d = decide(arms(n=20.), deterministic=True, info_bearing=False, placebo_run=True, placebo_selection=SELECTION, placebo_status="accepted")
        self.assertIn("lesion_artefact", d["reasons"])
        self.assertLessEqual(d["placebo_exact_p"], .05)
        self.assertNotEqual(d["status"], "supported")
        # Point rule withdrawn: tau_O^N = 2.0 < m_O is not flagged, 5.0 > m_O is (4v4 deterministic).
        self.assertNotIn("lesion_artefact", decide(arms(n=12.), deterministic=True, info_bearing=False,
                                                    placebo_run=True, placebo_selection=SELECTION, placebo_status="accepted")["reasons"])

    def test_no_placebo_available_blocks_supported_and_is_listed_last(self):
        d = decide(arms(n=None), deterministic=True, info_bearing=False, placebo_run=False,
                   placebo_status="no_placebo_available")
        self.assertEqual((d["status"], d["reasons"]), ("inconclusive", ["no_placebo_available"]))

    def test_no_placebo_available_co_lists_and_does_not_hide_others(self):
        d = decide(arms(n=None), deterministic=True, info_bearing=True, placebo_run=False,
                   placebo_status="no_placebo_available")
        self.assertEqual(d["reasons"], ["info_loss_untested", "no_placebo_available"])

    def test_not_supported_does_not_require_placebo(self):
        d = decide(arms(k=10.5, n=None), deterministic=True, info_bearing=False, placebo_run=False,
                   placebo_status="no_placebo_available")
        self.assertEqual(d["status"], "not supported")
        self.assertIn("semantic carriers", d["limit_text"])

    def test_unselected_sham_is_not_treatment_missingness(self):
        b = arms()
        del b["S"]
        d = decide(b, deterministic=True, info_bearing=False, placebo_run=True,
                   placebo_selection=SELECTION, placebo_status="accepted", sham_selected=False, sham_batch="uncertain")
        self.assertEqual(d["status"], "supported")
        self.assertTrue(d["sham_uncertain"])
        self.assertNotIn("treatment_dependent_missingness", d["reasons"])
        selected = decide(b, deterministic=True, info_bearing=False, placebo_run=True,
                          placebo_selection=SELECTION, placebo_status="accepted", sham_selected=True)
        self.assertIn("treatment_dependent_missingness", selected["reasons"])

    def test_carrier_flag_preserves_protocol_status_precedence(self):
        # Section 9 caps a would-be "not supported"; it is not a validity failure.
        d = decide(arms(), deterministic=True, info_bearing=False, placebo_run=True,
                   placebo_selection=SELECTION, placebo_status="accepted", flags=["resend_detected"])
        self.assertEqual(d["status"], "supported")
        small = decide(arms(k=10.5), deterministic=True, info_bearing=False, placebo_run=True,
                       placebo_selection=SELECTION, placebo_status="accepted", flags=["resend_detected"])
        self.assertEqual(small["status"], "inconclusive")
        self.assertIn("not_identifiable_redundant", small["reasons"])

    def test_partial_placebo_failure_cannot_support(self):
        b = arms()
        b["N"][0] = {"status": "failed", "outcome": None}
        d = decide(b, deterministic=True, info_bearing=False, placebo_run=True,
                   placebo_selection=SELECTION, placebo_status="accepted")
        self.assertEqual(d["status"], "inconclusive")
        self.assertIn("placebo_missing", d["reasons"])

    def test_case_decisions_use_frozen_exact_intervals(self):
        b = arms(spread=1.)
        d = decide(b, info_bearing=False, placebo_run=True, placebo_selection=SELECTION, placebo_status="accepted")
        self.assertEqual(d["estimates"]["intervals"]["tau_O"], [8., 12.])
        self.assertEqual(d["estimates"]["interval_method"], "exact shift-permutation (C2)")

    def test_extractor_clarifications_without_editing_independent_contract(self):
        from ccc.audit.commitments import extract, world_aliases
        self.assertEqual(extract("Layla will be taking T1", author="Omar"), {("layla", "t1")})
        self.assertEqual(extract("- Layla: T1"), {("layla", "t1")})
        aliases = world_aliases({"TASK-01": {"tags": ["backend"]}})
        self.assertEqual(extract("I claim the backend item", author="Layla", aliases=aliases),
                         {("layla", "task-01")})

    def test_legacy_without_status_still_blocks_supported(self):
        d = decide(arms(n=None), deterministic=True, info_bearing=False, placebo_run=False)
        self.assertEqual(d["status"], "inconclusive")
        self.assertIn("placebo_not_run", d["reasons"])


if __name__ == "__main__":
    unittest.main()
