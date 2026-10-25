"""Independent frozen-bootstrap arithmetic from the stdlib raw pair output."""
from pathlib import Path
import json
import numpy as np

p = Path(__file__).resolve().parent
raw = json.loads((p / "tests/exp002_independent.json").read_text())
v = np.asarray([x["d_w"] for x in sorted(raw["pairs"], key=lambda x:x["pair_id"])], float)
rng = np.random.Generator(np.random.PCG64(20261025))
draws = v[rng.integers(0, len(v), size=(10000, len(v)))].mean(axis=1)
ci = np.quantile(draws, [.025, .975])
expected = [-.01954964911635066, 2.8336288730243204]
assert np.allclose(ci, expected, rtol=0, atol=2e-14)
print(json.dumps({"classification":"EXECUTED", "source":"independent raw EXP002 contrasts; string-sorted pair IDs",
                  "algorithm":"PCG64(20261025),10000 cluster draws,quantile(.025,.975)",
                  "ci":ci.tolist(),"frozen_ci":expected,"differences":(ci-np.asarray(expected)).tolist(),
                  "n_independent":len(v)}, indent=2))
