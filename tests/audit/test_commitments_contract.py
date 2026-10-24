"""Commitment-extractor contract suite, CCC protocol v1.2 (AMD-001 r3).

Written from the specification only: docs/research/sci002/amendment_v1.2.md
(Change 2, sections 2.2 and 2.3) and docs/research/sci002/protocol.md section 9.
The implementation was not consulted beyond its public signatures and docstrings.

Conventions and assumptions (not fixed by the spec, stated here):
- Task ids are written T1, T2, T3 (spec placeholders T, U). Agent names are
  capitalised ("Layla"); comparisons are case-insensitive via `pairs()`.
- `extract(text, author=...)` returns a set of (agent, task) tuples.
- `matches(left, right, theta, left_author, right_author)`: `left` is the
  exposure E* text, `right` is the candidate line.
- Wording of PC4, PC5, NC2, NC7 is chosen by the author to exhibit the
  descriptor given in the spec (explicit paraphrase, private resend, generic
  verb, outsider quote). The expected outcome follows from the spec rule.
- Jaccard tests use only identical texts (J = 1) and disjoint texts (J = 0),
  so they hold for any theta in (0, 1]; the numeric theta is not in the spec.
"""
import unittest

from ccc.audit.commitments import extract, matches

THETA = 0.8
SENDER = "Layla"


def pairs(tuples):
    return {(agent.lower(), task.lower()) for agent, task in tuples}


def carrier(exposure, candidate, *, sender=SENDER, candidate_author=SENDER):
    return matches(exposure, candidate, theta=THETA,
                   left_author=sender, right_author=candidate_author)


class PositiveControls(unittest.TestCase):
    """Must match (7 positives: PC1-PC7)."""

    def test_PC1_verbatim_copy_by_sender_on_board0(self):
        # E* = "I claim T1" by s; the same sentence reappears verbatim from s.
        self.assertTrue(carrier("I claim T1", "I claim T1"))

    @unittest.skip("SPEC-AMBIGUOUS: the row syntax of a CURRENT ASSIGNMENTS "
                   "entry is not specified; only that a row gives (agent, task).")
    def test_PC2_current_assignments_row(self):
        pass

    def test_PC3_third_person_relay_compared_on_agent_and_task(self):
        # Relay author Omar is not the agent; the tuple is (Layla, T1).
        self.assertEqual(pairs(extract("Layla has committed to T1", author="Omar")),
                         {("layla", "t1")})
        self.assertTrue(carrier("I claim T1", "Layla has committed to T1",
                                candidate_author="Omar"))

    def test_PC4_explicit_paraphrase_from_other_wording(self):
        self.assertTrue(carrier("I claim T1", "I am taking T1"))

    def test_PC5_private_resend_by_sender(self):
        # Surface is private (P); the extractor is surface-agnostic.
        self.assertTrue(carrier("I claim T1",
                                "I'm on T1, as I said before."))

    def test_PC6_strict_superset_same_agent_line_matches(self):
        # Old NC5, now positive: E* tuple set {(s,T1)} is contained in {(s,T1),(s,T2)}.
        self.assertTrue(carrier("I'm on T1", "I'm on T1 and T2"))

    def test_PC7_instead_of_then_clause_matches_for_taken_task(self):
        # Negation scoped to U only; the clause "I'll take T1" is extracted normally.
        self.assertEqual(pairs(extract("instead of T2, I'll take T1", author=SENDER)),
                         {("layla", "t1")})
        self.assertTrue(carrier("I'll take T1", "instead of T2, I'll take T1"))


class NegativeControls(unittest.TestCase):
    """Must NOT match (7 negatives: NC1-NC7, with NC5' as the 'instead of' case)."""

    def test_NC1_other_agent_planning_to_take_same_task(self):
        self.assertFalse(carrier("I claim T1", "planning to take T1",
                                 candidate_author="Omar"))
        self.assertEqual(pairs(extract("planning to take T1", author="Omar")),
                         {("omar", "t1")})

    def test_NC2_generic_verb_lines_give_no_tuple(self):
        text = "Route T1 to whoever is free; pick up T1 or take T1 if needed."
        self.assertEqual(extract(text, author=SENDER), set())
        self.assertFalse(carrier("I claim T1", text))

    def test_NC3_negated_commitment(self):
        self.assertEqual(extract("I won't take T1", author=SENDER), set())
        self.assertFalse(carrier("I claim T1", "I won't take T1"))

    def test_NC4_same_agent_different_task(self):
        self.assertFalse(carrier("I claim T1", "I claim T2"))

    def test_NC5_prime_instead_of_negates_only_following_task(self):
        # E* = (s, T1). The clause after the comma gives (s, T2) only.
        self.assertEqual(pairs(extract("instead of T1, I'll take T2", author=SENDER)),
                         {("layla", "t2")})
        self.assertFalse(carrier("I claim T1", "instead of T1, I'll take T2"))

    def test_NC6_task_in_blocked_or_infeasible_clause(self):
        text = "T1 is infeasible for me"
        self.assertEqual(extract(text, author=SENDER), set())
        self.assertFalse(carrier("I claim T1", text))

    def test_NC7_outsider_quote_of_unrelated_task(self):
        candidate = 'Priya wrote: "I am on T3 next week"'
        self.assertFalse(carrier("I claim T1", candidate, candidate_author="Priya"))


class SpecRulesBeyondControls(unittest.TestCase):
    """Rules stated in section 2.2 / section 9 that the controls do not isolate."""

    def test_clause_split_stops_anchor_crossing_sentence_boundary(self):
        # Anchor and task are in different clauses: no tuple.
        self.assertEqual(extract("I'm on it. T1 is next.", author=SENDER), set())

    def test_negation_does_not_cross_clause_boundary(self):
        # "won't" is in an earlier clause; "I claim T1" keeps its tuple.
        self.assertEqual(pairs(extract("I won't say more. I claim T1.", author=SENDER)),
                         {("layla", "t1")})

    def test_containment_requires_every_sender_pair(self):
        # E* has two tuples (s,T1),(s,T2); a candidate with only T1 does not contain E*.
        self.assertFalse(carrier("I claim T1. I claim T2.", "I claim T1"))

    def test_third_person_form_gives_named_agent(self):
        self.assertEqual(pairs(extract("Layla will be taking T1", author="Omar")),
                         {("layla", "t1")})

    def test_implicit_exposure_empty_tuples_uses_jaccard_only(self):
        # No task id and no alias: tuple matching is unavailable. Identical text
        # reaches Jaccard = 1 and matches.
        text = "I'm strong on the backend ticket and nearly free this sprint"
        self.assertEqual(extract(text, author=SENDER), set())
        self.assertTrue(carrier(text, text))

    def test_implicit_exposure_empty_tuples_ignores_candidate_tuples(self):
        # Candidate has a tuple, but E* has none, so tuple matching is off and
        # disjoint wording gives Jaccard 0.
        self.assertFalse(carrier("Quiet week, nothing new to report.", "I claim T1"))

    @unittest.skip("SPEC-AMBIGUOUS: the alias-list format (mapping and "
                   "DEV-pinned contents) is not specified in the amendment.")
    def test_registered_alias_gives_tuple(self):
        pass

    @unittest.skip("SPEC-AMBIGUOUS: the surface form of 'attribution' is not "
                   "specified; the spec says only that it maps to 'claim'.")
    def test_attribution_maps_to_claim(self):
        pass


if __name__ == "__main__":
    unittest.main()
