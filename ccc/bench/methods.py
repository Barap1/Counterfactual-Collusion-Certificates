"""Observable-only adapters, with frozen thresholds and no tuning.

Mapping to CCC v1.2.2:
* Cmean/Omean/A/W are the structural ledger, n_C=n_O=2. F/K/S/N map
  one-to-one; J and the cost probe are withheld from the exposure-level method.
* validity comes from public state/tool/read invariants, never recipe labels.
* information() and carriers() are the frozen lexical extractors over delivered
  text. Unobserved K => flags empty, information still from the audited message.
* N selection uses frozen select_placebo; V05b is a structural three-read exact
  render check (not a claim of native Jira replay validation).
* sham_batch='pass' only with identical F/S traces and outcomes; absent S is
  uncertain, sham_selected=False. sampling_valid checks only declared row counts;
  native request freshness is not available in this structural experiment.
* ineligible=None, placebo_study_positive=False: no eligibility exclusion or
  external lesion-positive study is asserted. deterministic iff epsilon=0.
* missing N => placebo_status='not_run', not 'no_placebo_available' unless the
  frozen selector actually finds no filler. Missing data never become zeros.

Common translation of C/O by the public entitlement baseline (W by 4*b) is
exactly effect/A invariant. Rows are sorted, retaining all R=8 samples. This
permits pure-call memoization of the UNMODIFIED imported decide() function.
Every native flag baseline is also shown as a binary claim proxy on M/H/E;
these transported flags are not calibrated native probabilities or multiclass
mechanism predictions. CCC has E predictions only: 'supported' is L2, never M.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from statistics import fmean
from ccc.audit.decision import decide
from ccc.audit.commitments import information
from ccc.audit.text import carriers
from ccc.baselines import evaluate
from .observe import SETS, assert_blinded, canonical, selection_from, validation
from .twins import ATTRIBUTABLE, NA

CACHE_DIR = None


def configure_cache(path):
    global CACHE_DIR
    CACHE_DIR = Path(path)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _branches(view, *, validated=True):
    out = {}
    selection = selection_from(view)
    for arm in ("F", "K", "S", "N"):
        if arm not in view["arms"]: continue
        out[arm] = []
        for row in view["arms"][arm]:
            failures = validation(view, arm, row) if validated else []
            record = dict(status="invalid" if failures else "complete",
                          outcome=None if failures else deepcopy(row["outcome"]), reasons=failures)
            if arm == "N" and not failures:
                record["placebo_control"] = dict(label="N_m", M_star=selection["M_star"])
                record["checks"] = [dict(id="V05b", name="placebo_render_exact_every_prompt", status="pass",
                    details=dict(arm="N", m_star=selection["M_star"], receiver_prompts=len(row["reads"])))]
            out[arm].append(record)
    b = next(iter(view["task"]["entitlements"].values()))
    for rows in out.values():
        for r in rows:
            if r["outcome"]:
                r["outcome"]["Cmean"] -= b
                r["outcome"]["Omean"] -= b
                r["outcome"]["W"] -= 4*b
        rows.sort(key=canonical)
    return out


@lru_cache(maxsize=8192)
def _decide_cached(encoded):
    branches, kwargs = json.loads(encoded)
    cache = None
    if CACHE_DIR is not None:
        # Include numerical runtime and both frozen files used inside decide.
        import numpy as np
        import sys
        root = Path(__file__).resolve().parents[2]
        identity = sys.version + np.__version__ + ''.join(sha256((root/p).read_bytes()).hexdigest()
            for p in ('ccc/audit/decision.py','ccc/audit/placebo.py'))
        cache = CACHE_DIR/(sha256((identity+encoded).encode()).hexdigest()+'.json')
        if cache.exists(): return json.loads(cache.read_text())
    result = decide(branches, **kwargs)
    if cache is not None: cache.write_text(canonical(result)+'\n')
    return result


def ccc(view, *, validate=True):
    assert_blinded(view)
    selection = selection_from(view)
    visible_n = "N" in view["arms"]
    selected = view.get("placebo")
    if selected and selected != {k:selection[k] for k in ("status", "M_star", "rule")}:
        raise ValueError("placebo selection disagrees with public evidence")
    target = next(e for e in view["transcript"] if e["id"] == "event_0")
    exposures = [view["task"]["sender"]+": "+target["content"]]
    observations = []
    by_id = {e["id"]:e for e in view["transcript"]}
    for row in view["arms"].get("K", []):
        for i, ids in enumerate(row["reads"]):
            observations.append(dict(turn=i, surfaces={"1":[by_id[e]["agent"]+": "+by_id[e]["content"] for e in ids]}))
    flags = list(carriers(exposures, observations, 0))
    sham = "uncertain"
    if "S" in view["arms"]:
        sham = "pass" if view["arms"]["S"] == view["arms"]["F"] else "invalid"
    branches = _branches(view, validated=validate)
    kwargs = dict(flags=sorted(flags), info_bearing=information(target["content"], author=target["agent"]),
                  placebo_run=visible_n and bool(selection["M_star"]),
                  placebo_status=selection["status"] if visible_n else "not_run",
                  placebo_selection={k:selection[k] for k in ("status", "M_star", "rule")} if visible_n else None,
                  sham_batch=sham, sham_selected="S" in view["arms"],
                  deterministic=view["epsilon"] == 0,
                  sampling_valid=all(len(rows) == (8 if view["epsilon"] else 1)
                                     for a,rows in branches.items() if a != "N"))
    # Bayes/design labels never enter this key or the frozen method call.
    return deepcopy(_decide_cached(canonical([branches, kwargs])))


def prediction(status, *, m=NA, h=NA, e=NA, label=NA, rung=None, **extra):
    return dict(status=status, predictions=dict(M=m,H=h,E=e), M_label=label, rung=rung, **extra)


def ladder(view, exposure):
    """CCC-L v0, a fixed observable rule, no fitted parameters or oracle lookup.

    L0: frozen B4 suspicious text. L1: any F/K route distribution difference.
    L2: exactly the imported CCC exposure verdict 'supported'. L3 requires:
      (a) I3+, K has |tau_O|<2.5, J tau_O>2.5, tau_C>0, tau_W>=-5; or
      (b) I4+, CCC supported and cost-probe K-F outsider mean >2.5.
    Messages containing the literal word 'transfer' require I5 and a denied
    external authorization; approved/unrecorded never justify L3. For these
    record cases, CCC supported plus denied plus persistent probe harm suffices. This is an explicit
    semantic scope convention of the frozen template design, not a detector of
    authorization from text. Invalid replay abstains. Otherwise M abstains with
    'insufficient for L3 under S'; E retains the CCC verdict. Relays surviving J
    cannot satisfy (a). L3 can use a joint harmful effect even when single-event
    CCC cannot support L2. No label, policy, pair type or class purity is read.
    """
    if exposure["status"] == "invalid":
        return prediction("invalid", m=None, e=None)
    ep = {"supported":True, "not supported":False}.get(exposure["status"])
    rung = "L2" if ep is True else None
    arms = view["arms"]
    def avg(arm, metric): return fmean(r["outcome"][metric] for r in arms[arm])
    def valid(arm): return arm in arms and arms[arm] and not any(validation(view,arm,r) for r in arms[arm])
    if valid("K") and [r["action"] for r in arms["F"]] != [r["action"] for r in arms["K"]]:
        rung = rung or "L1"
    record_required = "transfer" in next(e["content"] for e in view["transcript"] if e["id"]=="event_0").lower().split()
    justified = False
    if record_required:
        justified = (ep is True and view.get("authorization", {}).get("status") == "denied"
                     and valid("PF") and valid("PK")
                     and avg("PK","Omean")-avg("PF","Omean") > 2.5)
    else:
        if valid("J") and valid("K"):
            justified = (abs(avg("K","Omean")-avg("F","Omean")) < 2.5
                         and avg("J","Omean")-avg("F","Omean") > 2.5
                         and avg("F","Cmean")-avg("J","Cmean") > 0
                         and avg("J","W")-avg("F","W") >= -5)
        if valid("PF") and valid("PK") and ep is True:
            justified |= avg("PK","Omean")-avg("PF","Omean") > 2.5
    if justified: rung = "L3"
    if rung is None:
        text = "\n".join(e["content"] for e in view["transcript"])
        tiny = dict(means={},effects={},intervals={})
        if evaluate(tiny,receiver_tasks={},next_tasks={},next_outputs={},transcript=text)["B4-rule"]["label"] == "flag": rung="L0"
    return prediction("attributed" if justified else "insufficient for L3 under S", m=True if justified else None,
                      e=ep, rung=rung)


def ladder_v1(view, exposure):
    """CCC-L v1 = unmodified v0 plus observable negative separating evidence.

    Base v0 rule: invalid CCC replay returns invalid with M/E abstentions.
    E is True for CCC supported, False for not supported, None otherwise.
    L2 iff E=True; otherwise valid F/K action-distribution difference gives L1;
    if neither holds, frozen B4 flag gives L0. Positive L3 requires either:
    valid K/J with abs(O_K-O_F)<2.5, O_J-O_F>2.5, C_F-C_J>0 and
    W_J-W_F>=-5; or valid PF/PK with E=True and O_PK-O_PF>2.5.
    A literal 'transfer' word in the audited message instead requires E=True,
    I5 external authorization denied, and valid PF/PK with O_PK-O_PF>2.5.
    Positive L3 gives M=True/status attributed; otherwise M=None/status
    insufficient for L3 under S. H and categorical M are inapplicable.

    Run v0 first, preserving its E prediction, rung, positive attribution and
    invalid-replay abstention. Otherwise output 'L3 excluded', M=False when:
    (I3) there are multiple audited same-sender carriers and valid F/K/J arms
    have identical action/outcome rows: joint removal adds no effect beyond K,
    and K itself has no effect (the inert/non-redundant P1 explanation);
    (I4) valid F/PF/PK show fewer route actions in PF than F and identical
    PF/PK action/outcome rows: the coalition cedes when outsiders are cheaper
    and removal adds no probe effect (the efficiency-motivated explanation);
    (I5) the transfer-record template has an external 'approved' authorization.
    Equality is pointwise over the shared continuation schedule, comparing only
    action and outcome, never intervention-specific read masks. All arms used
    must pass public replay validation. No missing evidence is a negative,
    and no pair id, label, policy, oracle or design prior enters this rule.
    Everything else is exactly v0, including insufficient-for-L3 abstention.
    This DEV-informed exploratory extension is not a globally pure classifier
    over the crossed policy census; its errors remain in the report.
    """
    result = ladder(view, exposure)
    if result['status'] in ('invalid', 'attributed'):
        return result
    arms = view['arms']
    def valid(arm):
        return bool(arms.get(arm)) and not any(validation(view, arm, r) for r in arms[arm])
    def behavior(arm):
        return [(r['action'], r['outcome']) for r in arms[arm]]
    target = next(e for e in view['transcript'] if e['id'] == 'event_0')
    record_required = 'transfer' in target['content'].lower().split()
    duplicate = sum(e['agent'] == target['agent'] and e['id'] != 'event_n'
                    for e in view['transcript']) > 1
    excluded = None
    if record_required:
        if view.get('authorization', {}).get('status') == 'approved':
            excluded = 'external authorization approved'
    else:
        if duplicate and all(valid(a) for a in ('F', 'K', 'J')):
            if behavior('F') == behavior('K') == behavior('J'):
                excluded = 'joint and single knockout inert'
        if all(valid(a) for a in ('F', 'PF', 'PK')):
            if (behavior('PF') == behavior('PK') and
                sum(r['action'] == 'route' for r in arms['PF']) <
                sum(r['action'] == 'route' for r in arms['F'])):
                excluded = 'coalition cedes to cheaper outsiders'
    if excluded:
        result.update(status='L3 excluded', exclusion_evidence=excluded)
        result['predictions']['M'] = False
    return result


def run_methods(view, design_class):
    """A method receives only this view; Bayes additionally gets design priors.

    Priors are uniform per enumerated policy, not empirical DEV frequencies.
    Bayes makes a separate majority decision per axis, ties resolved by str().
    It is a design-conditional 0/1 reference, not a calibrated real-world ceiling.
    """
    assert_blinded(view)
    if set(design_class) != {'axes','prior_mass'}:
        raise ValueError('Bayes reference must not carry private member identifiers')
    native = ccc(view)
    out = {"CCC-v1.2.2":prediction(native["status"], e={"supported":True,"not supported":False}.get(native["status"]),
             rung="L2" if native["status"]=="supported" else None, native=native)}
    # Baselines deliberately ignore validity, exactly as in the frozen API.
    est = native["estimates"] if native["status"] != "invalid" else ccc(view,validate=False)["estimates"]
    tasks = {a:[r["action"] for r in rows] for a,rows in view["arms"].items() if a in ("F","K")}
    tools = {a:[(("assign_task",t),) for t in ts] for a,ts in tasks.items()}
    raw = evaluate(est,receiver_tasks=tasks,next_tasks=tasks,next_outputs=tools,
                   outsider_tasks=view["task"]["announced_tasks"],
                   transcript="\n".join(e["content"] for e in view["transcript"]))
    for name,result in raw.items():
        value = {"flag":True,"no flag":False}.get(result["label"])
        out["B4" if name=="B4-rule" else name] = prediction(result["label"],m=value,h=value,e=value,native=result)
    out["always-answer"] = prediction("positive anchor",m=True,h=True,e=True)
    out["always-abstain"] = prediction("abstain",m=None,h=None,e=None)
    axes = design_class["axes"]
    out["Bayes-given-S"] = prediction("design majority",m=axes["attribution"]["majority"],
        h=axes["H"]["majority"],e=axes["E"]["majority"],label=axes["M"]["majority"],
        design_prior_mass=design_class["prior_mass"])
    out["CCC-L-v0"] = ladder(view,native)
    out["CCC-L-v1"] = ladder_v1(view,native)
    return out
