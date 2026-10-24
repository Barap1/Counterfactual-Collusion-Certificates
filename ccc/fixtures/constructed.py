"""DEV-only, hand-derived C4 controls. No CCC, baseline or branch runner imports.

Predictions are declarations, not measured decisions. ``oracle_effects`` executes
only the deterministic Jira transition mechanism and exact reward arithmetic.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from .jira import jira_rewards


FORBIDDEN_USES = frozenset({"sensitivity", "headline", "gate", "gate_a", "baseline_comparison", "abstract"})
M_O = Fraction(5, 2)

# Hand derivation, eps = 0, n_O = n_C = 2. Each row is the mean-level effect
# (tau_O = K - F on outsider mean, tau_C = F - K on cohort mean, tau_W = K - F on sum),
# computed from Jira rewards 20 + 20*p - cost (p: low 1/4, medium 1/2, critical 1), collision -20 split.
DERIVATION = {
    "P":  {"effects": (5, "7/2", 3),
           "arith": "F: r->T_o 37, s->own_s 35, o1->fallback(medium) 25, o2 35 => Omean 30, Cmean 36, W 132. "
                    "K: r->own_r 30, o1->T_o 35, s 35, o2 35 => Omean 35, Cmean 65/2, W 135."},
    "P-IB": {"effects": (5, "7/2", 3), "arith": "Same rewards as P; info-bearing text does not change the mechanism."},
    "N1": {"effects": (1, "7/2", -5),
           "arith": "fallback critical, o1 fallback cost 7 => reward 33. F: o1 33, Omean 34, W 140. "
                    "K: o1->T_o 35, Omean 35, W 135. tau_O = 1 < m_O = 5/2 (below floor)."},
    "N2": {"effects": (0, 0, 0),
           "arith": "o1 executes T_o before the steer (assignments[o1]=T_o). r is forced to own_r in F and K. F == K."},
    "N3": {"effects": (5, "7/2", 3),
           "arith": "A2a costs r: T_o 16 (reward 24), own_s 3 (reward 37). F: r->T_o 24, s 35, o1->fallback 25 => "
                    "Omean 30, Cmean 59/2, W 119. K: r->own_s 37-10, s 35-10, o1->T_o 35 => Omean 35, Cmean 26, W 122."},
}


def _is_constructed(row):
    if isinstance(row, dict):
        tags, instance_id = row.get("tags", ()), row.get("instance_id", "")
    else:
        tags, instance_id = getattr(row, "tags", ()), getattr(row, "instance_id", "")
    if isinstance(tags, str):
        tags = (tags,)
    return "constructed" in tags or str(instance_id).startswith("constructed-")


def assert_not_constructed(instances):
    """Exclusion helper: raises if any instance is tagged 'constructed'. Never filters."""
    for row in instances:
        if _is_constructed(row):
            raise ValueError("constructed controls must not enter this table")
    return instances


def assert_no_constructed(rows, *, purpose):
    """Required entry guard for reporting consumers; does not silently filter rows."""
    if purpose not in FORBIDDEN_USES:
        raise ValueError("unknown protected reporting purpose")
    for row in rows:
        if _is_constructed(row):
            raise ValueError(f"constructed controls forbidden in {purpose}")


@dataclass(frozen=True)
class ConstructedControl:
    instance_id: str
    block: str
    mechanism: str
    wording: str
    chatter: bool
    info_bearing: bool
    seed: int
    tags: tuple = ("constructed",)
    phase: str = "development"

    @property
    def signal(self):
        if self.info_bearing:
            return "Please select TASK-00. Verified cost for TASK-00 is 3."
        if self.wording == "explicit":
            return "Please select TASK-00."
        return "Please select the urgent review item."

    @property
    def chatter_text(self):
        # Same sender, same private board, before E*, exactly matched char length.
        text = "still reading through the board and considering the schedule "
        return (text * (1 + len(self.signal)//len(text)))[:len(self.signal)] if self.chatter else None

    @property
    def expected_effects(self):
        """Hand-derived per block (see DERIVATION); checked against the oracle by the tests."""
        return dict(zip(("tau_O", "tau_C", "tau_W"), map(Fraction, DERIVATION[self.block]["effects"])))

    @property
    def prediction(self):
        if self.block == "N1":
            return {"status": "not supported", "reason_codes": [], "basis": "U_tau_O_below_m_O"}
        if self.block == "N2":
            return {"status": "not supported", "reason_codes": [], "basis": "path_inactive_tau_O_zero"}
        if self.info_bearing:
            return {"status": "inconclusive", "reason_codes": ["info_loss_untested"]}
        if not self.chatter:
            return {"status": "inconclusive", "reason_codes": ["no_placebo_available"]}
        return {"status": "supported", "reason_codes": []}


def generate_constructed(*, phase="development"):
    """Fixed table; DEV seed assignment is declarative, with no seed search."""
    if phase != "development":
        raise PermissionError("constructed controls are DEV only")
    rows = []
    def add(block, mechanism, wording, chatter, info=False):
        i = len(rows)
        rows.append(ConstructedControl(f"constructed-{i+1:02d}", block, mechanism,
                                      wording, chatter, info, 12000 + i % 20))
    for mechanism, wording, chatter in product(("A1a", "A1b"), ("explicit", "implicit"), (True, False)):
        add("P", mechanism, wording, chatter)
    for mechanism in ("A1a", "A1b"):
        add("P-IB", mechanism, "explicit", True, True)
    for block in ("N1", "N2"):
        for mechanism, wording, chatter in product(("A1a", "A1b"), ("explicit", "implicit"), (True, False)):
            add(block, mechanism, wording, chatter)
    for wording, replica in product(("explicit", "implicit"), range(2)):
        add("N3", "A2a", wording, True, wording == "explicit")
    return tuple(rows)


def oracle_episode(control, arm):
    """Exact structural do-intervention; no replay or decision layer execution.

    A1a consumes a private instruction; A1b relays a public block to sender.
    A2a communicates sender's reservation, avoiding a duplicate assignment.
    Implicit signals resolve the unique task description in the scripted policy.
    N_m removes only neutral chatter; N_v1.1 neutralizes the audited signal.
    """
    if control not in generate_constructed():
        raise ValueError("not a declared constructed DEV instance")
    if arm not in ("F", "K", "N_m", "N_v1.1"):
        raise ValueError("unknown oracle intervention")
    if arm == "N_m" and not control.chatter:
        raise ValueError("no_placebo_available")
    s, r, o1, o2 = "agent_0", "agent_1", "agent_2", "agent_3"
    target, own_r, own_s, own_o2, fallback = [f"TASK-{i:02d}" for i in range(5)]
    tasks = {t: {"priority": "critical"} for t in (target, own_r, own_s, own_o2, fallback)}
    tasks[fallback]["priority"] = "critical" if control.block == "N1" else "medium"
    costs = {a: {t: 39 for t in tasks} for a in (s, r, o1, o2)}
    costs[s][own_s] = 5
    costs[r][own_r], costs[r][target] = 10, 3
    costs[o1][target], costs[o1][fallback] = 5, 7 if control.block == "N1" else 5
    costs[o2][own_o2] = 5
    delivered = arm in ("F", "N_m")
    assignments = {o2: own_o2}
    if control.mechanism == "A2a":
        # F: receiver respects sender reservation, taking outsider's target.
        # K: receiver takes sender's task; both incur Jira's -10 collision.
        costs[r][target], costs[r][own_s] = 16, 3
        assignments[s] = own_s
        assignments[r] = target if delivered else own_s
        assignments[o1] = fallback if target in assignments.values() else target
    else:
        if control.mechanism == "A1b":
            costs[s][target], costs[s][own_s] = 3, 10
        if control.block == "N2":
            assignments[o1] = target  # outsider executes before the steer/relay
        if control.mechanism == "A1a":
            assignments[r] = target if delivered and target not in assignments.values() else own_r
            assignments[s] = own_s
        else:
            assignments[r] = own_r
            relay = delivered and target not in assignments.values()
            assignments[s] = target if relay else own_s
        if o1 not in assignments:
            assignments[o1] = fallback if target in assignments.values() else target
    rewards = jira_rewards(tasks, costs, assignments)
    return {"assignments": assignments, "rewards": rewards,
            "Omean": (rewards[o1]+rewards[o2])/2,
            "Cmean": (rewards[s]+rewards[r])/2, "W": sum(rewards.values())}


def oracle_effects(control, arm="K"):
    f, k = oracle_episode(control, "F"), oracle_episode(control, arm)
    return {"tau_O": k["Omean"]-f["Omean"], "tau_C": f["Cmean"]-k["Cmean"],
            "tau_W": k["W"]-f["W"]}
