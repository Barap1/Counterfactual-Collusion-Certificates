# RA-PROBE handoff

**Task:** EXP-003 additive PF/PK incentive probe and paired analysis.

**Status:** Implemented; development/offline validation passed. No commits.

**Artifacts:** `ccc/exp003/probe.py`, `arms.py`, `analysis.py`;
`tests/test_exp003_probe.py`; `docs/enh/exp003/probe_design.md` (under 600 words).
Existing-file edits: **none**. RA-MODAL files untouched.

**Validation:** Seven EXP-003 pytest tests passed, including real native Jira
DEV fixtures, B2-style unprompted cooperation, state corruption, private-prompt
identity, PF/PK freshness/mask checks, immutable ledgers, missingness, Holm,
bootstrap determinism and exact sign-flip through 32 pairs. Earlier combined
run: 72 passed (six EXP-003 plus 66 existing replay tests).

Exact successful command (repository root):
```sh
CCC_STARTER_ROOT="$PWD/starter/collusion_hackathon" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -c 'import sys, site; site.addsitedir("starter/collusion_hackathon/colosseum/.venv/lib/python3.14/site-packages"); from tests.replay.offline_runner import guard; sys.addaudithook(guard); import pytest; raise SystemExit(pytest.main(["-q", "tests/test_exp003_probe.py", "-p", "no:cacheprovider"]))'
```
For the combined run, the pytest argument list additionally contained
`"tests/replay"`. The installed native venv lacks pytest; system Python supplies
pytest and loads native dependencies using `site.addsitedir`. Guards deny
network/DNS and secret-file reads.

**Limitations:** EXP-002 has no contested-task selector; the documented
checkpoint-only extension needs protocol approval/freeze. Native costs remain
private. No real-agent efficacy claim. P2 includes mechanical reward changes.
The original collector's hardcoded arm/manifest validation cannot schedule
PF/PK: integrate the new wrapper/seam in EXP-003, retaining canaries/budgets,
probe-ineligible cases, cross-check failures and shared world pairing IDs.

**Budget:** $0; no network/model/Modal calls. Coding agent: Codex (exact model
ID not exposed). Added
PF+PK costs 2r branches/checkpoint, each T..3T calls; r=4 adds eight branches.

**Next:** RA-LEAD freezes selection/missingness/standardization details, persists
`prepare_probe(cp).to_json()` before continuations, and wires its controller to
`arms.run_branch` or `collect_branches`. Analyze normalized scheduled rows via
`python -m ccc.exp003.analysis rows.json --continuations 4`.
