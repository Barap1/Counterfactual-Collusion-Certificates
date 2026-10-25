"""Development-only tests: real native Jira, scripted clients, no network/models."""
from copy import deepcopy
from dataclasses import replace
from itertools import product
import json
import math
import socket

import numpy as np
import pytest

from ccc.exp003.analysis import analyze, exact_sign_flip
from ccc.exp003.arms import collect_branches, prepare_probe, run_branch
from ccc.exp003.probe import ProbeUnavailable, apply_probe, select_probe, validate_edit
from ccc.replay import engine
from ccc.replay.fixtures import signal_fixture
from ccc.replay.ledger import verify_branch
from ccc.replay.world import ColosseumWorld


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("EXP003 tests forbid network")
    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "getaddrinfo", deny)


@pytest.fixture(scope="module")
def checkpoint():
    fx = signal_fixture(seed=2)  # existing DEV seed; never held-out data
    factory = engine.scripted_factory(fx.policy_factory)
    source = engine.record_source_run(fx.spec, factory)
    cp = engine.make_checkpoint(source, fx.select_exposure(source))
    assert cp.valid
    return cp, factory


def restored(cp):
    world = ColosseumWorld(cp.spec, lambda n, w: engine.NoCallClient())
    world.restore(cp.snapshot)
    return world


def test_restore_probe_determinism_scope_and_native_visibility(checkpoint):
    cp, _ = checkpoint
    world = restored(cp)
    edit = prepare_probe(cp)
    assert edit == select_probe(world, cp.snapshot.snapshot_id)
    original_source = cp.source.world.static_sha256(), cp.source.world.dynamic_sha256()
    original_snapshot = cp.snapshot.dynamic
    before, dynamic = deepcopy(world.static_state()), deepcopy(world.dynamic_state())
    checks = apply_probe(world, edit)
    assert all(c.status == "pass" for c in checks)
    assert world.dynamic_state() == dynamic
    assert edit.outsider not in world.colluders
    assert all(edit.new_cost < costs[edit.task] for costs in before["costs"].values())
    assert world.env.costs[edit.outsider][edit.task] == edit.new_cost
    assert cp.snapshot.dynamic == original_snapshot
    assert original_source == (cp.source.world.static_sha256(), cp.source.world.dynamic_sha256())
    # A second edit or a different cost/assignment mutation fails closed.
    with pytest.raises(ProbeUnavailable):
        apply_probe(world, edit)
    world.env.assignment[edit.outsider] = edit.task
    assert validate_edit(before, dynamic, world, edit).status == "fail"


def test_no_suffix_outcome_selection_and_tamper_rejection(checkpoint):
    cp, _ = checkpoint
    edit = prepare_probe(cp)
    world = restored(cp)
    world.outcomes = lambda: pytest.fail("outcomes accessed in probe selection")
    world.final_summary = lambda: pytest.fail("summary accessed in probe selection")
    assert select_probe(world, cp.snapshot.snapshot_id) == edit
    with pytest.raises(ProbeUnavailable):
        apply_probe(world, replace(edit, new_cost=edit.new_cost+.01))
    # Nonpositive minima cannot be improved within native nonnegative costs.
    for costs in world.env.costs.values():
        for task in costs:
            costs[task] = 0
    with pytest.raises(ProbeUnavailable):
        select_probe(world, cp.snapshot.snapshot_id)


def test_validator_rejects_unrelated_static_edits(checkpoint):
    cp, _ = checkpoint
    world = restored(cp)
    before, dynamic = deepcopy(world.static_state()), deepcopy(world.dynamic_state())
    edit = prepare_probe(cp)
    apply_probe(world, edit)
    other = next(t for t in world.env.tasks if t != edit.task)
    world.env.costs[edit.outsider][other] += 1
    assert validate_edit(before, dynamic, world, edit).status == "fail"


def test_pf_pk_offline_collector_ledgers_and_frozen_f(checkpoint, tmp_path):
    cp, factory = checkpoint
    f = engine.run_branch(cp, "F", factory)
    output = collect_branches(cp, [{"arm": a, "replicate": 0} for a in ("F", "K", "PF", "PK")],
                              lambda item: factory, ledger_dir=tmp_path)
    assert all(c.status in ("pass", "na") for c in output["cross_checks"])
    branches = {r.arm: r for r in output["branches"]}
    for arm, branch in branches.items():
        assert branch.status == "valid", (arm, branch.reasons, [c.to_json() for c in branch.checks])
        assert verify_branch(branch.ledger_path)["records"] == len(branch.records)
        assert all(r.branch_id == arm for r in branch.records)
    assert branches["F"].outcomes == f.outcomes
    assert branches["F"].world.static_sha256() == cp.snapshot.static_sha256
    for arm in ("PF", "PK"):
        br = branches[arm]
        assert {c.id for c in br.checks} >= {"P01", "P02", "V3", "V6"}
        assert isinstance(br.outcomes["coalition_cedes"], bool)
        assert br.outcomes["Omean"] == np.mean([v for a, v in br.outcomes["agent_rewards"].items()
                                               if a not in br.world.colluders])
        summary = json.loads((__import__("pathlib").Path(br.ledger_path).parent / "branch.json").read_text())
        assert summary["arm"] == arm
        assert summary["execution"]["probe"] == output["edit"]
    actual_rows = [dict(world_id="dev02", regime="B1", arm=r.arm, replicate=0,
                       status=r.status, outcomes=r.outcomes, checks=[c.to_json() for c in r.checks])
                   for r in branches.values()]
    assert analyze(actual_rows, 1)["world_effects"][0]["counts"] == {a: 1 for a in branches}
    with pytest.raises(ProbeUnavailable):
        run_branch(cp, "PF", factory, edit=replace(prepare_probe(cp), checkpoint_id="wrong"))


def test_native_unprompted_cooperation_fixture(tmp_path):
    from ccc.fixtures.jira import generate_jira
    from ccc.fixtures.native_replay import as_replay_fixture
    # Existing DEV golden fixture, native B2-style coalition_prompt='never'.
    fx = as_replay_fixture(generate_jira("A1a", 12000, profile="golden"))
    factory = engine.scripted_factory(fx.policy_factory)
    source = engine.record_source_run(fx.spec, factory)
    cp = engine.make_checkpoint(source, fx.select_exposure(source))
    output = collect_branches(cp, [{"arm": a, "replicate": 0} for a in ("PF", "PK")],
                              lambda item: factory, ledger_dir=tmp_path)
    assert output["status"] == "complete"
    assert all(c.status in ("pass", "not_applicable") for c in output["cross_checks"])
    assert all("Collusion blackboard_id:" not in r.request["messages"][1]["content"]
               for b in output["branches"] for r in b.records)


def test_exact_sign_flip_matches_frozen_and_bruteforce():
    from ccc.analysis.statistics import sign_flip
    for xs in ([1, 2, -3, 4, 0, 5], [0, 0], [1, -1]):
        assert exact_sign_flip(xs) == sign_flip(xs)
    xs = [1, -2, 3, -4, 5, -6, 7, 8, 9, -10, 11, 0]
    obs = sum(xs)/len(xs)
    nz = [x for x in xs if x]
    expected = sum(sum(s*x for s, x in zip(signs, nz))/len(xs) >= obs-1e-12
                   for signs in product((-1, 1), repeat=len(nz)))/2**len(nz)
    assert exact_sign_flip(xs)["p"] == expected
    assert exact_sign_flip([1.]*32)["p"] == 2**-32
    assert exact_sign_flip([-1.]*32)["p"] == 1
    with pytest.raises(ValueError):
        exact_sign_flip([math.nan])


def rows_fixture(n=6):
    rows = []
    for w in range(n):
        for regime in ("B1", "B2"):
            for arm in ("F", "K", "PF", "PK"):
                value = 10 + (w+1 if arm == "K" and regime == "B1" else
                              2*(w+1) if arm == "PF" and regime == "B2" else 0)
                for rep in range(3):
                    rows.append(dict(world_id=str(w), regime=regime, arm=arm, replicate=rep,
                                     status="valid", outcomes=dict(status="complete", Omean=value,
                                     coalition_cedes=regime == "B2")))
    return rows


def test_analysis_directions_reused_ci_holm_and_missingness():
    from ccc.analysis.statistics import summarize, holm
    rows = rows_fixture()
    result = analyze(rows, 3)
    p1, p2 = result["primary"]
    assert p1["estimate"] == 3.5 and p2["estimate"] == 7
    assert (p1["L"], p1["U"]) == (summarize(range(1, 7))["L"], summarize(range(1, 7))["U"])
    assert [p1["p_holm"], p2["p_holm"]] == holm([1/64, 1/64])
    assert result["coalition_cedes"][0]["estimate"] == 0
    assert result["coalition_cedes"][1]["estimate"] == 1
    assert result == analyze(rows, 3)
    assert result["separation"]["probe"]["estimate"] == pytest.approx(result["separation"]["knockout"]["estimate"])
    rows[0]["status"] = "failed"
    partial = analyze(rows, 3)
    assert partial["primary"][0]["n_independent"] == 5
    assert partial["primary"][1]["n_independent"] == 5
    assert partial["world_effects"][0]["missing"]["F"] == 1
    with pytest.raises(ValueError):
        analyze(rows + [rows[0]], 3)
