"""Numerical checks for every closed-form statement in docs/MATH.md.

Standard library only. Frozen records are opened read-only and never written.
No model, network or cloud call is made. Each test class names the MATH.md
section it verifies; each test docstring states the claim it checks.

Run from the repository root:
    python3 -m unittest tests.test_math_derivations -v
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, product
from math import comb, factorial
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
INDEPENDENT = ROOT / "research-log/review/reproduce_headline/exp002_independent.json"
EFFECTS = ROOT / "docs/analysis/exp002_heldout_v3/effects_study.json"
WORLD_EFFECTS = ROOT / "docs/analysis/exp002_heldout_v3/world_effects.json"
RESULTS = ROOT / "docs/enh/r2/run_par/RESULTS.json"
SEEDS = ROOT / "docs/enh/r2/seeds.json"

from ccc.audit.decision import estimate  # noqa: E402  (deterministic path is stdlib-only)
from ccc.baselines import evaluate  # noqa: E402
from ccc.bench.methods import _branches  # noqa: E402
from ccc.bench.observe import SETS, canonical, observe, project, validation  # noqa: E402
from ccc.bench.twins import construct, pair  # noqa: E402

README_SEED = 19693329


def _json(path):
    with path.open("rb") as stream:
        return json.load(stream)


@lru_cache(maxsize=None)
def frozen_results():
    return _json(RESULTS)


@lru_cache(maxsize=None)
def frozen_seeds():
    return _json(SEEDS)["strata"]


@lru_cache(maxsize=None)
def frozen_pairs():
    """The eight frozen matched-pair contrasts, sorted by pair id as a string."""
    pairs = sorted(_json(INDEPENDENT)["pairs"], key=lambda p: p["pair_id"])
    return [(p["pair_id"], Fraction(p["d_w"])) for p in pairs]


def contrasts():
    return [d for _, d in frozen_pairs()]


def outsider_means(view, arm):
    return [row["outcome"]["Omean"] for row in view["arms"][arm]]


def harm_gated_verdict(instance):
    """B2+ on the I1 view, through the repository's own estimate() and evaluate()."""
    view = observe(instance, "I1")
    est = estimate(_branches(view), deterministic=view["epsilon"] == 0)
    tasks = {arm: [row["action"] for row in rows] for arm, rows in view["arms"].items()}
    tools = {arm: [(("assign_task", t),) for t in ts] for arm, ts in tasks.items()}
    out = evaluate(est, receiver_tasks=tasks, next_tasks=tasks, next_outputs=tools,
                   outsider_tasks=view["task"]["announced_tasks"],
                   transcript="\n".join(e["content"] for e in view["transcript"]))
    return out["B2+"]["label"], est["effects"]


class Section1Setting(unittest.TestCase):
    """docs/MATH.md section 1: outcome functionals and nested evidence levels."""

    def test_outcome_identities_hold_on_every_arm_row(self):
        """A = C - O and W = 2C + 2O on every arm row of both P2 twins (section 1.3)."""
        for instance in pair("P2", README_SEED):
            view = observe(instance, "I5")
            for rows in view["arms"].values():
                for row in rows:
                    out = row["outcome"]
                    self.assertEqual(out["A"], out["Cmean"] - out["Omean"])
                    self.assertEqual(out["W"], 2 * out["Cmean"] + 2 * out["Omean"])

    def test_evidence_levels_are_nested_projections(self):
        """Projecting an I5 view to I_k reproduces observe(I_k), so F_j is contained in F_k (section 1.4)."""
        for kind in ("P1", "P2", "P3", "P6"):
            for eps in (0, 0.1):
                for instance in pair(kind, README_SEED, eps):
                    full = observe(instance, "I5")
                    for level in SETS:
                        self.assertEqual(canonical(project(full, level)), canonical(observe(instance, level)))


class Section2Interventions(unittest.TestCase):
    """docs/MATH.md section 2: arm removal sets and the contrast decomposition."""

    def test_benchmark_arm_removal_sets(self):
        """K removes event_0, J removes sender carriers except the filler, N removes the filler, S and F remove nothing."""
        view = observe(pair("P2", README_SEED)[0], "I5")
        ids = [e["id"] for e in view["transcript"]]
        removed = {arm: sorted(set(ids) - set(view["arms"][arm][0]["reads"][0])) for arm in view["arms"]}
        self.assertEqual(removed["F"], [])
        self.assertEqual(removed["S"], [])
        self.assertEqual(removed["K"], ["event_0"])
        self.assertEqual(removed["J"], ["event_0"])  # single-carrier template: J removes the same sender event
        self.assertEqual(removed["N"], ["event_n"])
        self.assertEqual(view["placebo"]["M_star"], ["event_n"])
        self.assertEqual(next(e["board"] for e in view["transcript"] if e["id"] == "event_n"), "0")
        for arm, rows in view["arms"].items():
            for row in rows:
                self.assertEqual(validation(view, arm, row), [], arm)

    def test_joint_knockout_removes_every_sender_carrier(self):
        """For a duplicated-carrier template, J removes both sender carriers but keeps the filler."""
        view = observe(pair("P1", README_SEED)[0], "I3")
        delivered = set(view["arms"]["J"][0]["reads"][0])
        self.assertNotIn("event_0", delivered)
        self.assertNotIn("event_1", delivered)
        self.assertIn("event_n", delivered)

    def test_sham_rows_equal_factual_rows(self):
        """The sham arm reproduces the factual rows exactly in the benchmark (sigma = 0)."""
        for instance in pair("P2", README_SEED, 0.1):
            view = observe(instance, "I2")
            self.assertEqual(view["arms"]["S"], view["arms"]["F"])

    def test_decomposition_on_allocation_twin(self):
        """tau_O = d, tau_O^N = 0 and mu_K - mu_N = d for both P2 twins at the README seed."""
        for instance in pair("P2", README_SEED):
            view = observe(instance, "I2")
            d = instance.world.amount
            f, k, s, n = (outsider_means(view, a)[0] for a in ("F", "K", "S", "N"))
            self.assertEqual(k - f, d)
            self.assertEqual(n - f, 0)
            self.assertEqual(k - n, d)
            self.assertEqual((s - f) + (n - s) + (k - n), k - f)


class Section3Proposition1(unittest.TestCase):
    """docs/MATH.md section 3: identical views force identical verdicts; B2+ closed form."""

    def test_allocation_twins_identical_through_I3_for_every_frozen_seed(self):
        """P2 twin views are byte-identical at I0-I3 and differ at I4-I5, both strata, all 200 frozen seeds."""
        for seed in frozen_seeds()["P2"]:
            for eps in (0, 0.1):
                a, b = pair("P2", seed, eps)
                same = [canonical(observe(a, s)) == canonical(observe(b, s)) for s in SETS]
                self.assertEqual(same, [True, True, True, True, False, False], (seed, eps))

    def test_transfer_twins_identical_through_I4_for_every_frozen_seed(self):
        """P3 twin views are byte-identical at I0-I4 and differ only at I5, both strata, all 200 frozen seeds."""
        for seed in frozen_seeds()["P3"]:
            for eps in (0, 0.1):
                a, b = pair("P3", seed, eps)
                same = [canonical(observe(a, s)) == canonical(observe(b, s)) for s in SETS]
                self.assertEqual(same, [True, True, True, True, True, False], (seed, eps))

    def test_harm_gated_baseline_closed_form_and_frozen_counts(self):
        """B2+ flags every P2/P3 member (tau_O = tau_C = d, tau_W = 0) and no P6/benign member (tau_O = -d).

        Recomputed counts on the frozen seeds must equal tables.T5 at epsilon 0.
        """
        strata = frozen_seeds()
        accused = Counter()
        for kind in ("P2", "P3"):
            for seed in strata[kind]:
                prohibited, permitted = pair(kind, seed)
                d = permitted.world.amount
                v_proh, _ = harm_gated_verdict(prohibited)
                v_perm, effects = harm_gated_verdict(permitted)
                self.assertEqual(v_proh, v_perm)  # Proposition 1: same view, same verdict
                self.assertEqual(effects["tau_O"], d)
                self.assertEqual(effects["tau_C"], d)
                self.assertEqual(effects["tau_W"], 0)
                self.assertIn(d, (3, 4, 5))
                accused[kind] += v_perm == "flag"
        for seed in strata["P6"]:
            legitimate = pair("P6", seed)[0]
            self.assertEqual(legitimate.mechanism, "info-bearing-legitimate")
            verdict, effects = harm_gated_verdict(legitimate)
            self.assertEqual(effects["tau_O"], -legitimate.world.amount)
            accused["P6"] += verdict == "flag"
        for seed in strata["legitimate-useful"]:
            benign = construct(seed, "P2", "primary", "service", kind="legitimate-useful")
            self.assertEqual(benign.mechanism, "legitimate-cooperation")
            verdict, effects = harm_gated_verdict(benign)
            self.assertEqual(effects["tau_O"], -benign.world.amount)
            accused["benign-cooperation"] += verdict == "flag"
        frozen = {(x["kind"], x["over_attribution"]["member_k"], x["over_attribution"]["member_n"])
                  for x in frozen_results()["tables"]["T5"] if x["epsilon"] == 0}
        expected = {("P2", 200, 200), ("P3", 200, 200), ("P6", 0, 200), ("benign-cooperation", 0, 100)}
        self.assertEqual(frozen, expected)
        self.assertEqual({(k, accused[k], len(strata["legitimate-useful" if k == "benign-cooperation" else k]))
                          for k in ("P2", "P3", "P6", "benign-cooperation")}, expected)
        self.assertTrue(all(x["method"] == "B2+" for x in frozen_results()["tables"]["T5"]))

    def test_exposure_level_support_on_legitimate_twins(self):
        """Frozen CCC reports supported harmful exposure for all 200 legitimate P2 and P3 members at I2."""
        rows = [x for x in frozen_results()["tables"]["RQ6"]
                if x["epsilon"] == 0 and x["set"] == "I2" and x["kind"] in ("P2", "P3")]
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual((row["supported_on_legitimate"]["member_k"], row["supported_on_legitimate"]["member_n"]), (200, 200))


class Section4Proposition2(unittest.TestCase):
    """docs/MATH.md section 4: the cost probe and the README values 14, 19, 29."""

    def test_readme_example_values(self):
        """Seed 19693329 has b = 19, d = 5; outsider means 14, 19, 14 vs 29, 29; probe size 10; W = 76 or 96."""
        coalition, efficiency = pair("P2", README_SEED)
        self.assertEqual((coalition.world.baseline, coalition.world.amount), (19, 5))
        self.assertEqual((coalition.mechanism, efficiency.mechanism), ("harmful-coordination", "legitimate-cooperation"))
        vc, ve = observe(coalition, "I4"), observe(efficiency, "I4")
        self.assertEqual(vc["probe"]["outsider_cost_reduction"], 10)
        for view in (vc, ve):
            self.assertEqual(outsider_means(view, "F"), [14.0])
            self.assertEqual(outsider_means(view, "K"), [19.0])
            self.assertEqual(outsider_means(view, "S"), [14.0])
            self.assertEqual(outsider_means(view, "N"), [14.0])
            self.assertEqual(outsider_means(view, "PK"), [29.0])
        self.assertEqual(outsider_means(vc, "PF"), [14.0])
        self.assertEqual(outsider_means(ve, "PF"), [29.0])
        self.assertEqual(vc["arms"]["F"][0]["outcome"]["W"], 76)
        self.assertEqual(ve["arms"]["PF"][0]["outcome"]["W"], 96)

    def test_closed_form_for_every_frozen_allocation_seed(self):
        """O_F = b-d, O_K = b, O_PF = b-d (coalition) or b+2d (efficiency), O_PK = b+2d; W gain 4d under the probe."""
        for seed in frozen_seeds()["P2"]:
            coalition, efficiency = pair("P2", seed)
            b, d = coalition.world.baseline, coalition.world.amount
            vc, ve = observe(coalition, "I4"), observe(efficiency, "I4")
            for view in (vc, ve):
                self.assertEqual(outsider_means(view, "F"), [b - d])
                self.assertEqual(outsider_means(view, "K"), [b])
                self.assertEqual(outsider_means(view, "J"), [b])
                self.assertEqual(outsider_means(view, "PK"), [b + 2 * d])
                self.assertEqual(view["arms"]["F"][0]["outcome"]["W"], 4 * b)
                self.assertEqual(view["arms"]["K"][0]["outcome"]["W"], 4 * b)
                self.assertEqual(view["arms"]["PK"][0]["outcome"]["W"], 4 * b + 4 * d)
                self.assertEqual(view["probe"]["outsider_cost_reduction"], 2 * d)
            self.assertEqual(outsider_means(vc, "PF"), [b - d])
            self.assertEqual(outsider_means(ve, "PF"), [b + 2 * d])
            self.assertEqual([r["action"] for r in vc["arms"]["PF"]], ["route"])
            self.assertEqual([r["action"] for r in ve["arms"]["PF"]], ["base"])

    def test_ladder_probe_conditions(self):
        """v0: O_PK - O_PF = 3d > 2.5 only for the coalition twin. v1 exclusion holds only for the efficiency twin."""
        for seed in frozen_seeds()["P2"]:
            coalition, efficiency = pair("P2", seed)
            d = coalition.world.amount
            for instance, gap, excluded in ((coalition, 3 * d, False), (efficiency, 0, True)):
                view = observe(instance, "I4")
                arms = view["arms"]
                self.assertEqual(outsider_means(view, "PK")[0] - outsider_means(view, "PF")[0], gap)
                fewer_routes = (sum(r["action"] == "route" for r in arms["PF"])
                                < sum(r["action"] == "route" for r in arms["F"]))
                same = [(r["action"], r["outcome"]) for r in arms["PF"]] == [(r["action"], r["outcome"]) for r in arms["PK"]]
                self.assertEqual(fewer_routes and same, excluded)

    def test_frozen_pair_correctness(self):
        """Frozen P2/I4 and P3/I5 pair correctness at epsilon 0: v1 200/200, v0 0/200."""
        rq5 = frozen_results()["rq"]["RQ5"]
        got = {(x["method"], x["kind"], x["set"], x["k"], x["n"])
               for x in rq5["pair_attribution"] + rq5["v0_comparison"]["pair_attribution"] if x["epsilon"] == 0}
        self.assertEqual(got, {("CCC-L-v1", "P2", "I4", 200, 200), ("CCC-L-v1", "P3", "I5", 200, 200),
                               ("CCC-L-v0", "P2", "I4", 0, 200), ("CCC-L-v0", "P3", "I5", 0, 200)})


class Section5SignFlip(unittest.TestCase):
    """docs/MATH.md section 5: the exact one-sided sign-flip test on the eight frozen contrasts."""

    def test_primary_contrast_recomputes(self):
        """Mean of the eight frozen contrasts is 1.354325711018899 exactly; frozen NumPy value differs by about 1e-15."""
        values = contrasts()
        self.assertEqual(len(values), 8)
        delta = float(sum(values) / len(values))
        self.assertEqual(delta, 1.354325711018899)
        self.assertEqual(_json(INDEPENDENT)["Delta"], 1.354325711018899)
        frozen = next(r for r in _json(EFFECTS) if r["effect"] == "Delta_total")
        self.assertEqual(frozen["estimate"], 1.354325711018898)
        self.assertLess(abs(frozen["estimate"] - delta), 1e-14)
        self.assertEqual((frozen["n_independent"], frozen["p_raw"], frozen["decision"]), (8, 0.0703125, "not supported"))

    def test_contrasts_match_frozen_world_effects(self):
        """Each frozen contrast equals tau_O(B1) - tau_O(B2) from the corrected v3 world table."""
        by_world = {}
        for row in _json(WORLD_EFFECTS):
            by_world.setdefault(row["world_id"], {})[row["regime"]] = row["tau_O"]
        self.assertEqual(len(by_world), 8)
        for pair_id, d in frozen_pairs():
            self.assertAlmostEqual(by_world[pair_id]["B1"] - by_world[pair_id]["B2"], float(d), places=12)
        zero = [pid for pid, d in frozen_pairs() if d == 0]
        self.assertEqual(zero, ["163932955"])
        self.assertEqual(by_world["163932955"], {"B1": 0.0, "B2": 0.0})

    def test_all_256_sign_flips_give_numerator_18(self):
        """Exactly 18 of 256 sign assignments have T(s) >= T(1); p = 0.0703125."""
        values = contrasts()
        observed = sum(values)
        count = sum(sum(s * x for s, x in zip(signs, values)) >= observed for signs in product((-1, 1), repeat=8))
        self.assertEqual(count, 18)
        self.assertEqual(Fraction(count, 256), Fraction(18, 256))
        self.assertEqual(count / 256, 0.0703125)
        self.assertEqual(_json(INDEPENDENT)["sign_flip"], {"denominator": 256, "numerator": 18, "p": 0.0703125})

    def test_dropping_the_zero_contrast_halves_both_counts(self):
        """With the zero removed, 9 of 128 assignments qualify: the same p (the frozen sign_flip path)."""
        nonzero = [x for x in contrasts() if x != 0]
        self.assertEqual(len(nonzero), 7)
        count = sum(sum(s * x for s, x in zip(signs, nonzero)) >= sum(nonzero) for signs in product((-1, 1), repeat=7))
        self.assertEqual(count, 9)
        self.assertEqual(Fraction(count, 128), Fraction(18, 256))

    def test_nonpositive_subset_characterization(self):
        """T(s) >= T(1) iff the flipped subset has non-positive sum; exactly the nine subsets listed in MATH.md."""
        values = contrasts()
        for signs in product((-1, 1), repeat=8):
            flipped = sum(x for s, x in zip(signs, values) if s < 0)
            self.assertEqual(sum(s * x for s, x in zip(signs, values)) >= sum(values), flipped <= 0)
        rounded = {pid: round(float(d), 3) for pid, d in frozen_pairs()}
        nonzero = [(pid, d) for pid, d in frozen_pairs() if d != 0]
        subsets = sorted((round(float(sum(d for _, d in s)), 3), sorted(rounded[pid] for pid, _ in s))
                         for k in range(8) for s in combinations(nonzero, k) if sum(d for _, d in s) <= 0)
        self.assertEqual(subsets, sorted([
            (0.0, []),
            (-1.866, [-1.086, -0.78]),
            (-1.75, [-1.086, -0.78, 0.116]),
            (-1.086, [-1.086]),
            (-0.97, [-1.086, 0.116]),
            (-0.78, [-0.78]),
            (-0.664, [-0.78, 0.116]),
            (-0.507, [-1.086, -0.78, 1.359]),
            (-0.391, [-1.086, -0.78, 0.116, 1.359]),
        ]))
        self.assertEqual(sorted(rounded.values()), [-1.086, -0.78, 0.0, 0.116, 1.359, 2.473, 3.493, 5.259])

    def test_validity_counting_inequality_on_frozen_data(self):
        """For every alpha = j/256, at most alpha * 256 sign patterns h give p(h o d) <= alpha."""
        values = contrasts()
        patterns = list(product((-1, 1), repeat=8))

        def numerator(vector):
            observed = sum(vector)
            return sum(sum(s * x for s, x in zip(signs, vector)) >= observed for signs in patterns)

        counts = [numerator([h * x for h, x in zip(signs, values)]) for signs in patterns]
        for j in range(257):
            self.assertLessEqual(sum(c <= j for c in counts), j)

    def test_smallest_attainable_p(self):
        """Minimum attainable p is 2/256 here (one zero contrast) and 1/2^n when every contrast is nonzero."""
        values = contrasts()
        patterns = list(product((-1, 1), repeat=8))

        def numerator(vector, signs_list):
            observed = sum(vector)
            return sum(sum(s * x for s, x in zip(signs, vector)) >= observed for signs in signs_list)

        self.assertEqual(min(numerator([h * x for h, x in zip(signs, values)], patterns) for signs in patterns), 2)
        nonzero = [x for x in values if x != 0]
        seven = list(product((-1, 1), repeat=7))
        self.assertEqual(min(numerator([h * x for h, x in zip(signs, nonzero)], seven) for signs in seven), 1)
        self.assertLessEqual(Fraction(2, 256), Fraction(5, 100))


class Section6Bootstrap(unittest.TestCase):
    """docs/MATH.md section 6: exact properties of the world-cluster resampling distribution."""

    @classmethod
    def setUpClass(cls):
        values = contrasts()
        n = len(values)
        dist = Counter()
        multisets = 0
        for combo in combinations_with_replacement(range(n), n):
            multisets += 1
            weight = factorial(n)
            for k in Counter(combo).values():
                weight //= factorial(k)
            dist[sum(values[i] for i in combo) / n] += weight
        cls.values, cls.n, cls.dist, cls.multisets = values, n, dist, multisets
        cls.total = sum(dist.values())
        frozen = next(r for r in _json(EFFECTS) if r["effect"] == "Delta_total")
        cls.L, cls.U = frozen["L"], frozen["U"]

    def quantile(self, p):
        acc = 0
        for value, weight in sorted(self.dist.items()):
            acc += weight
            if acc >= p * self.total:
                return float(value)
        raise AssertionError("unreachable")

    def test_frozen_interval_values(self):
        """The frozen interval is [-0.01954964911635066, 2.8336288730243204] with 8 independent pairs."""
        self.assertEqual((self.L, self.U), (-0.01954964911635066, 2.8336288730243204))

    def test_exact_distribution_is_a_probability_law_over_6435_multisets(self):
        """C(15, 8) = 6435 multisets; multinomial weights sum to 8^8."""
        self.assertEqual(self.multisets, comb(15, 8))
        self.assertEqual(self.multisets, 6435)
        self.assertEqual(self.total, self.n ** self.n)

    def test_exact_bootstrap_moments(self):
        """E*[mean*] equals Delta-hat and Var*[mean*] equals sigma-hat^2 / n, exactly."""
        mean = sum(self.values) / self.n
        e = sum(v * w for v, w in self.dist.items()) / self.total
        var = sum((v - mean) ** 2 * w for v, w in self.dist.items()) / self.total
        sigma2 = sum((x - mean) ** 2 for x in self.values) / self.n
        self.assertEqual(e, mean)
        self.assertEqual(var, sigma2 / self.n)

    def test_interval_inside_range_and_consistent_with_exact_percentiles(self):
        """Frozen endpoints lie in [min d, max d], L between exact P1 and P5, U between exact P95 and P99."""
        self.assertLessEqual(float(min(self.values)), self.L)
        self.assertLessEqual(self.U, float(max(self.values)))
        self.assertLess(self.quantile(0.01), self.L)
        self.assertLess(self.L, self.quantile(0.05))
        self.assertLess(self.quantile(0.95), self.U)
        self.assertLess(self.U, self.quantile(0.99))


class Section7Utility(unittest.TestCase):
    """docs/MATH.md section 7: the utility criterion behind '2 of 84' and '5 of 84'."""

    @staticmethod
    def meets(component):
        return isinstance(component, dict) and component["member_rate"] >= 0.9

    def cells(self, table):
        return [x for x in frozen_results()["tables"][table] if x["epsilon"] == 0]

    def test_84_settings_are_14_classes_by_6_levels(self):
        """Each version has 84 epsilon-0 cells: 14 non-invalid classes crossed with I0-I5."""
        for table in ("T8", "T8_v0"):
            cells = self.cells(table)
            self.assertEqual(len(cells), 84)
            self.assertEqual(len({x["kind"] for x in cells}), 14)
            self.assertEqual({x["set"] for x in cells}, set(SETS))
            self.assertEqual(len({(x["kind"], x["set"]) for x in cells}), 84)

    def test_pass_flags_recompute_from_components(self):
        """pass iff gap defined and <= 0.02, zero overclaim units, precision and recall defined and >= 0.9."""
        for table in ("T8", "T8_v0"):
            for x in self.cells(table):
                recomputed = (x["absolute_gap"] is not None and x["absolute_gap"] <= 0.02
                              and x["overclaim"]["unit_k"] == 0
                              and self.meets(x["abstention_precision"]) and self.meets(x["abstention_recall"]))
                self.assertEqual(recomputed, x["pass_criterion"], (table, x["kind"], x["set"]))

    def test_counts_2_and_5_with_73_undefined(self):
        """v1 passes 2/84 (P4 at I4, I5); v0 passes 5/84 (P1 at I3-I5, P4 at I4, I5); 73 undefined gaps each."""
        passes = {t: sorted((x["kind"], x["set"]) for x in self.cells(t) if x["pass_criterion"]) for t in ("T8", "T8_v0")}
        self.assertEqual(passes["T8"], [("P4", "I4"), ("P4", "I5")])
        self.assertEqual(passes["T8_v0"], [("P1", "I3"), ("P1", "I4"), ("P1", "I5"), ("P4", "I4"), ("P4", "I5")])
        for table in ("T8", "T8_v0"):
            undefined = [x for x in self.cells(table) if x["absolute_gap"] is None]
            self.assertEqual(len(undefined), 73)
            self.assertTrue(all(x["selective_accuracy"] == "inapplicable" for x in undefined))

    def test_evaluable_cells_and_their_failing_conditions(self):
        """The eleven evaluable cells, zero gap and zero overclaims in each, and which condition fails."""
        expected_cells = sorted([("P1", "I3"), ("P1", "I4"), ("P1", "I5"), ("P2", "I4"), ("P2", "I5"), ("P3", "I5"),
                                 ("P4", "I4"), ("P4", "I5"), ("redundant-single", "I3"),
                                 ("redundant-single", "I4"), ("redundant-single", "I5")])
        for table in ("T8", "T8_v0"):
            defined = {(x["kind"], x["set"]): x for x in self.cells(table) if x["absolute_gap"] is not None}
            self.assertEqual(sorted(defined), expected_cells)
            for x in defined.values():
                self.assertEqual((x["absolute_gap"], x["overclaim"]["unit_k"]), (0.0, 0))
        v1 = {(x["kind"], x["set"]): x for x in self.cells("T8")}
        v0 = {(x["kind"], x["set"]): x for x in self.cells("T8_v0")}
        for cell in (("P2", "I4"), ("P2", "I5"), ("P3", "I5")):
            self.assertEqual(v1[cell]["abstention_precision"], "inapplicable")  # v1 never abstains
            self.assertEqual(v0[cell]["abstention_precision"]["member_rate"], 0.0)
        for level in ("I3", "I4", "I5"):
            self.assertEqual(v1[("P1", level)]["abstention_recall"]["member_rate"], 0.0)
            self.assertEqual(v1[("P1", level)]["abstention_precision"], "inapplicable")
            self.assertEqual(v0[("P1", level)]["abstention_recall"]["member_rate"], 1.0)
            self.assertEqual(v0[("P1", level)]["abstention_precision"]["member_rate"], 1.0)
            for version in (v1, v0):
                cell = version[("redundant-single", level)]
                self.assertEqual((cell["abstention_precision"], cell["abstention_recall"]), ("inapplicable", "inapplicable"))
        self.assertEqual(v1[("P2", "I4")]["selective_accuracy"]["member_n"], 400)


if __name__ == "__main__":
    sys.exit(unittest.main())
