"""Pin theta (redundancy Jaccard) per prereg section 6 on DEV fixtures only.

Rule (docs/stats/prereg.md section 6, row `theta`):
  word 3-shingles on normalized text; grid {0.3,0.4,0.5,0.6,0.7};
  choose the theta maximizing Youden J = recall + (1 - FPR) - 1 on dev fixtures only;
  positives = A5a verbatim/paraphrase pairs; negatives = non-redundant pairs from A2/A3;
  ties -> lower theta; if best J < 0.5 then theta = 0.4 and flag weak_detector.

Only development seeds (split_manifest.json development.world_seeds) are generated.
No model call, no network, no ledger rows, no K/N/C outcome is read.

Pair construction (fixed here before the numbers are computed):
  Positives, per DEV seed s and case in {A5a-verbatim, A5a-paraphrase}:
    (E* signal, posted re-send). Verbatim: re-send == signal. Paraphrase: re-send = world.resend.
  Negatives, non-redundant pairs from A2/A3: the sender's E* signal from cases
    {A2a, A2b, A3a, A3b} for each DEV seed, as distinct texts, paired across DEV seeds
    (s < t). Pairs whose two texts are identical are excluded from the primary count
    (identical text is a copy, not a non-redundant pair) and reported; a sensitivity
    run that keeps them is also reported.
  Shingling and Jaccard are the frozen detector functions (ccc.audit.commitments._shingles).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from ccc.audit.commitments import _shingles  # frozen detector shingling (v1.2)
from ccc.fixtures.jira import generate_jira
from ccc.fixtures.worlds import split_manifest

GRID = [0.3, 0.4, 0.5, 0.6, 0.7]
NEG_CASES = ("A2a", "A2b", "A3a", "A3b")
POS_CASES = ("A5a-verbatim", "A5a-paraphrase")
OUT = Path(__file__).with_name("theta_pin.json")
INPUTS = [
    "docs/stats/prereg.md",
    "docs/research/sci002/protocol.md",
    "ccc/audit/commitments.py",
    "ccc/audit/commitment_aliases.json",
    "ccc/fixtures/jira.py",
    "ccc/fixtures/iid.py",
    "ccc/fixtures/split_manifest.json",
    "ccc/fixtures/worlds.py",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jaccard(a: str, b: str) -> float:
    sa, sb = _shingles(a), _shingles(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def rates(pos_scores, neg_scores, theta):
    recall = sum(s >= theta for s in pos_scores) / len(pos_scores)
    fpr = sum(s >= theta for s in neg_scores) / len(neg_scores)
    j = recall + (1 - fpr) - 1
    return recall, fpr, j


def pin(pos_scores, neg_scores):
    table = []
    for theta in GRID:
        recall, fpr, j = rates(pos_scores, neg_scores, theta)
        table.append({"theta": theta, "recall": recall, "fpr": fpr, "youden_J": j})
    best_j = max(row["youden_J"] for row in table)
    # ties -> lowest theta (GRID is ascending, so the first maximiser is the lowest)
    argmax = next(row["theta"] for row in table if row["youden_J"] == best_j)
    weak = best_j < 0.5
    chosen = 0.4 if weak else argmax
    return table, chosen, best_j, weak, argmax


def main():
    bounds = split_manifest()["development"]["world_seeds"]
    seeds = list(range(bounds["start"], bounds["stop_exclusive"]))
    assert len(seeds) == 20

    positives = []  # (case, seed, E*, posted)
    for seed in seeds:
        for case in POS_CASES:
            w = generate_jira(case, seed)  # DEV: default phase development, iid profile
            posted = w.signal if case == "A5a-verbatim" else w.resend
            positives.append((case, seed, w.signal, posted))

    messages = {}  # seed -> set of distinct E* texts from A2/A3 cases
    for seed in seeds:
        for case in NEG_CASES:
            w = generate_jira(case, seed)
            messages.setdefault(seed, {})[w.signal] = case

    negatives_all, negatives_distinct, identical = [], [], 0
    for i, s in enumerate(seeds):
        for t in seeds[i + 1:]:
            for a, ca in messages[s].items():
                for b, cb in messages[t].items():
                    negatives_all.append((ca, s, a, cb, t, b))
                    if a == b:
                        identical += 1
                    else:
                        negatives_distinct.append((ca, s, a, cb, t, b))

    pos_scores = [jaccard(e, p) for _, _, e, p in positives]
    neg_scores = [jaccard(x[2], x[5]) for x in negatives_distinct]
    neg_scores_incl = [jaccard(x[2], x[5]) for x in negatives_all]

    table, chosen, best_j, weak, argmax = pin(pos_scores, neg_scores)
    table_incl, chosen_incl, best_j_incl, weak_incl, argmax_incl = pin(pos_scores, neg_scores_incl)

    result = {
        "schema_version": "ccc.stats.theta_pin.v1",
        "rule": "prereg.md section 6 theta row: Youden J on DEV fixtures; ties -> lower theta; best J < 0.5 -> 0.4 + weak_detector",
        "partition": "development",
        "dev_world_seeds": [seeds[0], seeds[-1]],
        "shingles": "ccc.audit.commitments._shingles (normalized, lowercased, [a-z0-9]+ tokens, word 3-grams)",
        "grid": GRID,
        "positives": {
            "definition": "A5a-verbatim (re-send == E*) and A5a-paraphrase (re-send = resend template) pairs",
            "n": len(pos_scores),
            "n_verbatim": sum(c == "A5a-verbatim" for c, *_ in positives),
            "n_paraphrase": sum(c == "A5a-paraphrase" for c, *_ in positives),
            "jaccard_min": min(pos_scores), "jaccard_median": sorted(pos_scores)[len(pos_scores) // 2],
            "jaccard_max": max(pos_scores),
            "paraphrase_jaccard_max": max(sc for (c, *_), sc in zip(positives, pos_scores) if c == "A5a-paraphrase"),
        },
        "negatives": {
            "definition": "distinct A2a/A2b/A3a/A3b E* texts from different DEV seeds, identical-text pairs excluded",
            "n": len(neg_scores),
            "n_identical_text_pairs_excluded": identical,
            "jaccard_max": max(neg_scores),
        },
        "per_theta": table,
        "argmax_theta_before_weak_rule": argmax,
        "chosen_theta": chosen,
        "best_youden_J": best_j,
        "weak_detector": weak,
        "tie_break": "lowest theta among maximal J",
        "sensitivity_identical_pairs_included": {
            "n_negatives": len(neg_scores_incl),
            "per_theta": table_incl,
            "argmax_theta_before_weak_rule": argmax_incl,
            "chosen_theta": chosen_incl,
            "best_youden_J": best_j_incl,
            "weak_detector": weak_incl,
        },
        "inputs_sha256": {p: sha256(ROOT / p) for p in INPUTS},
        "outcomes_read": [],
        "model_calls": 0,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"chosen_theta": chosen, "argmax_theta_before_weak_rule": argmax, "best_youden_J": best_j, "weak_detector": weak,
                      "n_pos": len(pos_scores), "n_neg": len(neg_scores),
                      "per_theta": table}, indent=2))


if __name__ == "__main__":
    main()
