"""Read-only final source/science checks; writes only this audit's JSON receipt."""
from pathlib import Path
import collections
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def main():
    baseline = json.loads((OUT / "frozen_before.json").read_text())
    differences = [name for name, expected in baseline.items() if not (ROOT/name).is_file() or sha(ROOT/name) != expected]
    assert not differences, differences
    archives = {}
    for stem in ("exp001-live", "exp002-live"):
        p = ROOT / f"docs/runner/archives/{stem}.tar.gz"
        expected = p.with_suffix(".gz.sha256").read_text().split()[0]
        archives[stem] = {"expected": expected, "actual": sha(p)}
        assert archives[stem]["actual"] == expected
    pilot = []
    entries = [line.split(maxsplit=1) for line in (ROOT / "ops/pilot_manifest.sha256").read_text().splitlines() if line.strip()]
    candidates = [*(ROOT / "results/baselines").iterdir(), *(ROOT / "docs/release/pilot_archive").iterdir()]
    for expected, name in entries:
        matches = [base / name.strip().removeprefix("./") for base in candidates if (base/name.strip().removeprefix("./")).is_file()]
        assert matches, "pilot input missing: " + name
        assert all(sha(p) == expected for p in matches)
        pilot.append({"name":name,"matching_copies":[str(p.relative_to(ROOT)) for p in matches],"sha256":expected})
    studies = json.loads((ROOT / "docs/analysis/exp002_heldout_v3/effects_study.json").read_text())
    primary = next(x for x in studies if x["effect"] == "Delta_total")
    assert primary["estimate"] == 1.354325711018898
    assert primary["p_raw"] == 0.0703125 and primary["n_independent"] == 8
    assert [primary["L"], primary["U"]] == [-0.01954964911635066, 2.8336288730243204]
    assert primary["decision"] == "not supported" and primary["confirmatory"]
    certs = json.loads((ROOT / "docs/analysis/exp002_heldout_v3/checkpoint_certificates.json").read_text())
    statuses = dict(collections.Counter(x["status"] for x in certs))
    assert statuses == {"not_supported":11,"inconclusive":5}
    assert len(certs) == 16 and all(x["gates"]["all_valid"] for x in certs)
    raw = json.loads((OUT / "tests/headline_archive.json").read_text())
    assert abs(raw["Delta"]-primary["estimate"]) < 2e-15
    assert raw["sign_flip"] == {"denominator":256,"numerator":18,"p":0.0703125}
    draft = (ROOT / "paper/v2/draft_v2.md").read_text()
    md = (ROOT / "paper/v2/build/submission_v2.md").read_text()
    abstract = draft.split("## Abstract\n",1)[1].split("\n\n**Evidence",1)[0].strip()
    assert 150 <= len(abstract.split()) <= 250
    assert "## H. Figure plan" not in md and "rendering pending" not in md.lower()
    assert md.index("### 5.4 ") < md.index("![Figure 3.") < md.index("## 6. Discussion")
    assert all(x in md for x in ("RQ4b", "RQ5", "post hoc", "not established", "useful real-agent detection sensitivity remain unestablished"))
    original = (OUT / "paper/original/draft_v2.md").read_text()
    def heldout(s):
        return s.split("### 5.4 Original held-out study: confirmatory null",1)[1].split("## 6. Discussion",1)[0]
    assert heldout(draft) == heldout(original), "held-out source section changed"
    subprocess.run(["python3", str(ROOT / "paper/v2/make_v2.py"), "--check"], check=True, capture_output=True)
    receipt = {"classification":"EXECUTED", "frozen_files_compared":len(baseline),"frozen_differences":differences,
               "archives":archives,"pilot":pilot,"primary":primary,"certificates":statuses,
               "independent_raw_minus_frozen_delta":raw["Delta"]-primary["estimate"],
               "arithmetic_note":"Stdlib Fraction/raw reduction and frozen NumPy reduction differ at ~1e-15; no scientific output changed.",
               "abstract_words":len(abstract.split()),"heldout_section_byte_identical":True,
               "pdf_sha256":sha(ROOT/"paper/v2/build/submission_v2.pdf")}
    (OUT / "final_verification.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({k:receipt[k] for k in ("frozen_files_compared","frozen_differences","abstract_words","independent_raw_minus_frozen_delta","pdf_sha256")},indent=2))


if __name__ == "__main__":
    main()
