"""Additive engine/collector adapter. Pass run_branch in place of engine.run_branch.

No global patches: the client-factory seam installs a restore decorator on each
new world instance. Engine F/K retain their exact frozen validation semantics.
"""
from copy import deepcopy

from ccc.replay import engine
from ccc.replay.ledger import persist_branch
from ccc.replay.world import ColosseumWorld, RestoreError
from .probe import ProbeUnavailable, apply_probe, select_probe, validate_call_costs

ARMS = (*engine.ARMS, "PF", "PK")


def prepare_probe(checkpoint):
    """Select once and persist to the collector's selection artifact before arms."""
    if not checkpoint.valid:
        raise ProbeUnavailable("invalid checkpoint")
    world = ColosseumWorld(checkpoint.spec, lambda n, w: engine.NoCallClient())
    world.restore(checkpoint.snapshot)
    return select_probe(world, checkpoint.snapshot.snapshot_id)


def run_branch(checkpoint, arm, client_factory, *, edit=None, **kwargs):
    """Drop-in branch call; PF->F, PK->K; other arms delegate unchanged.

    Caller must use EXP003 ARMS for scheduling (the frozen collector's hardcoded
    membership gate does not accept PF/PK). No monkeypatching that collector.
    """
    if arm not in ("PF", "PK"):
        return engine.run_branch(checkpoint, arm, client_factory, **kwargs)
    edit = edit or prepare_probe(checkpoint)
    if edit.checkpoint_id != checkpoint.snapshot.snapshot_id:
        raise ProbeUnavailable("edit belongs to another checkpoint")
    probe_checks = []
    evidence = {}

    def factory(agent, world):
        if not getattr(world, "_exp003_restore_installed", False):
            original_restore = world.restore
            world.branch_id = arm

            def restore(snapshot):
                original_restore(snapshot)  # all native static/dynamic checks first
                evidence["pre_static_sha256"] = world.static_sha256()
                evidence["pre_dynamic_sha256"] = world.dynamic_sha256()
                try:
                    probe_checks.extend(apply_probe(world, edit))
                except ProbeUnavailable as exc:
                    raise RestoreError(f"probe validation: {exc}") from exc
                evidence["post_static_sha256"] = world.static_sha256()
                evidence["post_dynamic_sha256"] = world.dynamic_sha256()
                evidence["edited_static"] = deepcopy(world.static_state())

            world.restore = restore
            world._exp003_restore_installed = True
        return client_factory(agent, world)

    # Engine's provisional F/K ledger goes only to auto-cleaned scratch. Publish
    # one authoritative PF/PK ledger after adding probe checks and arm identity.
    ledger_dir = kwargs.pop("ledger_dir", None)
    result = engine.run_branch(checkpoint, "F" if arm == "PF" else "K", factory, **kwargs)
    result.arm = arm
    result.checks.extend(probe_checks)
    if result.world is not None:
        check = validate_call_costs(result.world)
        result.checks.append(check)
        if check.status == "fail" and result.status == "valid":
            result.status = "invalid"
            result.reasons.append("P04 native costs differ from provider prompt")
    result.execution_metadata.update(probe=edit.to_json(), probe_restore=evidence,
                                     engine_arm="F" if arm == "PF" else "K")
    if result.world is not None and result.outcomes is not None:
        assignment = result.outcomes.get("assignment") or {}
        # Cession requires an outsider actually wins; unassigned/collision isn't cession.
        claimants = [a for a, t in assignment.items() if t == edit.task]
        ceded = (len(claimants) == 1 and claimants[0] not in result.world.colluders)
        result.outcomes.update(contested_task=edit.task, probe_outsider=edit.outsider,
                               coalition_cedes=ceded,
                               coalition_retains=any(a in result.world.colluders for a in claimants))
    result.ledger_path = persist_branch(checkpoint, result, ledger_dir)
    return result


def check_probe_pair(checkpoint, factual, knockout):
    """Native targeted-mask cross-check on PF/PK, plus identical restore edits."""
    from ccc.replay.validators import CheckResult, PASS, FAIL
    same = (factual.execution_metadata.get("probe") == knockout.execution_metadata.get("probe")
            and factual.execution_metadata.get("probe_restore") == knockout.execution_metadata.get("probe_restore")
            and bool(factual.execution_metadata.get("probe_restore")))
    checks = [CheckResult("P03", "identical_probe_restore", PASS if same else FAIL, {})]
    if factual.world is not None and knockout.world is not None:
        checks.append(engine.check_targeted_exposure(checkpoint, factual, knockout))
    else:
        checks.append(CheckResult("V05", "targeted_exposure", FAIL, {"error": "missing probe world"}))
    return checks


def collect_branches(checkpoint, order, factory, *, ledger_dir=None, edit=None):
    """Collector-sized seam: ordered items have arm/replicate; factory(item) -> client factory.

    The outer EXP003 controller owns durable begin/end records, transport budget,
    canaries, aborts, and final archiving (reuse runner.collector.archive_world).
    All freshness IDs span original and probed arms. N accepts item.placebo_ids.
    """
    edit = edit or prepare_probe(checkpoint)
    order = list(order)
    if len({(i["arm"], str(i["replicate"])) for i in order}) != len(order):
        raise ValueError("duplicate scheduled arm/replicate")
    responses, requests, results = set(), set(), []
    for item in order:
        kwargs = {"placebo_ids": item["placebo_ids"]} if item["arm"] == "N" else {}
        result = run_branch(checkpoint, item["arm"], factory(item), edit=edit,
                            replicate_id=str(item["replicate"]), ledger_dir=ledger_dir,
                            execution_metadata=item, other_response_ids=responses,
                            other_request_ids=requests, **kwargs)
        results.append(result)
        responses.update(r.response_id for r in result.records if r.response_id)
        requests.update(r.client_request_id for r in result.records if r.client_request_id)
    checks = []
    by_key = {(r.replicate_id, r.arm): r for r in results}
    if len(by_key) != len(results):
        raise ValueError("duplicate scheduled arm/replicate")
    for rep in sorted({r.replicate_id for r in results}):
        for f, k in (("F", "K"), ("PF", "PK")):
            a, b = by_key.get((rep, f)), by_key.get((rep, k))
            if a and b:
                checks.extend(check_probe_pair(checkpoint, a, b) if f == "PF" else
                              [engine.check_targeted_exposure(checkpoint, a, b)]
                              if a.world and b.world else [])
        f, s = by_key.get((rep, "F")), by_key.get((rep, "S"))
        if f and s and f.world and s.world:
            checks.append(engine.check_sham_identity(checkpoint, f, s))
    return {"edit": edit.to_json(), "branches": results, "cross_checks": checks,
            "status": "complete" if all(r.status == "valid" for r in results) and engine.ok(checks) else "invalid"}
