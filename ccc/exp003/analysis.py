"""EXP003 world-paired analysis. CLI: python -m ccc.exp003.analysis rows.json.

Input: JSON list of collector branch records, with shared matched ``world_id``
(e.g. seed, NOT the regime-specific spec hash), regime, arm, replicate, status,
outcomes. Include every scheduled branch, including failed/not_run records.
No EXP002 results are read, pooled, or rewritten.
"""
from collections import defaultdict
import json
import math
from pathlib import Path
import sys

import numpy as np
from ccc.analysis import statistics as stats
from ccc.analysis.study import paired


def exact_sign_flip(values):
    """Reuse frozen test through n=10; exact meet-in-middle extension to n=32.

    Identical zero/tie tolerance (1e-12), positive-direction mean statistic.
    Two sorted half-sum tables avoid enumerating 2**32 full assignments.
    """
    values = np.asarray(values, dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("finite paired contrasts required")
    nonzero = values[np.abs(values) > 1e-12]
    n = len(nonzero)
    if n <= 10:
        return stats.sign_flip(values.tolist())
    if n > 32:
        raise ValueError("EXP003 exact test supports at most 32 nonzero pairs")

    def sums(xs):
        out = np.array([0.])
        for x in xs:
            out = np.concatenate((out - x, out + x))
        return out

    left = sums(nonzero[:n // 2])
    right = np.sort(sums(nonzero[n // 2:]))
    threshold = float(values.sum()) - 1e-12 * len(values)
    count = np.sum(len(right) - np.searchsorted(right, threshold - left, side="left"), dtype=np.int64)
    return {"p": int(count) / 2**n, "status": "attainable", "n_nonzero": n,
            "method": "exact meet-in-middle sign-flip"}


def world_effects(records, expected_per_arm=4):
    """Complete-arm means only; no ineligible-zero or outcome imputation.

    Return missingness explicitly. A world can contribute P1 with complete F/K
    even if PF failed, and P2 with complete F/PF even if K failed.
    """
    if type(expected_per_arm) is not int or expected_per_arm < 1:
        raise ValueError("expected_per_arm must be a positive integer")
    groups, seen = defaultdict(list), set()
    for row in records:
        if row["regime"] not in ("B1", "B2"):
            raise ValueError("unknown regime")
        key = (row["world_id"], row["regime"], row["arm"], row["replicate"])
        if key in seen:
            raise ValueError("duplicate branch (resolve whole-world attempts upstream)")
        seen.add(key)
        groups[key[:2]].append(row)
    worlds = []
    for (wid, regime), rows in sorted(groups.items()):
        means, counts, missing, rates = {}, {}, {}, []
        for arm in ("F", "K", "PF", "PK"):
            scheduled = [r for r in rows if r["arm"] == arm]
            good = [r for r in scheduled if r["status"] == "valid" and r.get("outcomes")
                    and r["outcomes"].get("status") == "complete"
                    and isinstance(r["outcomes"].get("Omean"), (int, float))
                    and math.isfinite(r["outcomes"]["Omean"])
                    and all(c["status"] in ("pass", "not_applicable") for c in r.get("checks", []))]
            if len(scheduled) > expected_per_arm:
                raise ValueError("arm exceeds frozen continuation count")
            counts[arm] = len(good)
            missing[arm] = expected_per_arm - len(good)
            means[arm] = float(np.mean([r["outcomes"]["Omean"] for r in good])) if len(good) == expected_per_arm else None
            if arm == "PF" and means[arm] is not None:
                flags = [r["outcomes"].get("coalition_cedes") for r in good]
                if all(type(x) is bool for x in flags):
                    rates = flags
        f, k, pf = (means[a] for a in ("F", "K", "PF"))
        worlds.append(dict(world_id=wid, regime=regime, eligible=True, means=means,
                           counts=counts, missing=missing,
                           tau_O=k-f if k is not None and f is not None else None,
                           pi=pf-f if pf is not None and f is not None else None,
                           cedes_rate=float(np.mean(rates)) if rates else None))
    return worlds


def _dz(values):
    if len(values) < 2:
        return None
    sd = float(np.std(values, ddof=1))
    return float(np.mean(values) / sd) if sd > 1e-12 else None


def separation(knockout_pairs, probe_pairs):
    """Descriptive paired d_z; compare on common complete pairs only.

    Directions: B1-B2 for knockout, B2-B1 for probe. Bootstrap world rows
    jointly, preserving both regimes and both contrasts. Zero variance is NA.
    """
    kd = {p["world_id"]: p["d_w"] for p in knockout_pairs}
    pd = {p["world_id"]: -p["d_w"] for p in probe_pairs}
    ids = sorted(kd.keys() & pd.keys())
    k, p = np.array([kd[i] for i in ids]), np.array([pd[i] for i in ids])
    draws = []
    if len(ids) >= 2:
        rng = np.random.Generator(np.random.PCG64(stats.SEED))
        for idx in rng.integers(0, len(ids), size=(stats.B, len(ids))):
            a, b = _dz(k[idx]), _dz(p[idx])
            draws.append((a, b, b-a if a is not None and b is not None else None))
    result = {"label": "descriptive", "standardization": "paired d_z = mean(world contrast) / sample SD(world contrast)",
              "world_ids": ids, "n_independent": len(ids)}
    a, b = _dz(k), _dz(p)
    for col, name, estimate in ((0, "knockout", a), (1, "probe", b),
                               (2, "probe_minus_knockout", b-a if a is not None and b is not None else None)):
        vals = [d[col] for d in draws if d[col] is not None]
        # Do not discard degenerate resamples and call the remaining interval 95%.
        ci = list(np.percentile(vals, [2.5, 97.5], method="linear")) if vals and len(vals) == len(draws) else [None, None]
        result[name] = {"estimate": estimate, "L": ci[0], "U": ci[1],
                        "undefined_bootstrap_draws": len(draws)-len(vals)}
    return result


def analyze(records, expected_per_arm=4, evidence_category="development"):
    worlds = world_effects(records, expected_per_arm)
    kp, pp = paired(worlds, metric="tau_O", conditional=True), paired(worlds, metric="pi", conditional=True)
    primary = []
    for name, pairs, direction in (("P1_Delta_K", kp, 1), ("P2_Delta_P", pp, -1)):
        values = [direction * p["d_w"] for p in pairs]
        flip = exact_sign_flip(values)
        primary.append(dict(effect=name, **stats.summarize(values), test=flip,
                            world_ids=[p["world_id"] for p in pairs]))
    for row, adjusted in zip(primary, stats.holm([r["test"]["p"] for r in primary])):
        row["p_holm"] = adjusted
    cedes = []
    for regime in ("B1", "B2"):
        vals = [w["cedes_rate"] for w in worlds if w["regime"] == regime and w["cedes_rate"] is not None]
        cedes.append(dict(regime=regime, **stats.summarize(vals),
                          definition="world mean of PF unique-outsider wins; no coalition claimant"))
    return {"evidence_category": evidence_category, "bootstrap_seed": stats.SEED,
            "bootstrap_draws": stats.B, "expected_per_arm": expected_per_arm,
            "primary": primary, "world_effects": worlds, "coalition_cedes": cedes,
            "separation": separation(kp, pp),
            "missingness_policy": "complete arms; separate complete matched pairs per estimand; no imputation"}


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path)
    parser.add_argument("--continuations", type=int, default=4)
    parser.add_argument("--evidence-category", choices=("development", "new-prospective"), default="development")
    args = parser.parse_args()
    print(json.dumps(analyze(json.loads(args.records.read_text()), args.continuations,
                             args.evidence_category), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
