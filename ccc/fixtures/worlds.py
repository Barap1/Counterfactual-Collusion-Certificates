"""Evaluator-private structural mechanisms; no CCC score or inference dependency."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import random


class Family(str, Enum):
    HARMFUL = "harmful_signal"
    BENIGN = "legitimate_cooperation"
    COMMON = "common_cause"
    INERT = "inert_talk"
    REDUNDANT = "redundant_signals"
    INVALID = "invalid_replay"


@dataclass(frozen=True)
class FixtureWorld:
    """Private harness object. Do not serialize this object into audit requests.

    Agent 0 emits a dispatch note; agent 1 acts; agents 2/3 receive allocations.
    A seeded permutation assigns these positions to neutral public identifiers.
    ``rule`` defines information edges, ``payoff`` the resource transition.
    """

    family: Family
    seed: int
    phase: str
    template_group: str
    world_id: str
    agents: tuple[str, ...]
    baseline: int
    amount: int
    token: str
    message: str
    shared_bit: bool
    rule: str
    payoff: str
    probability: Fraction
    invalid_variant: str | None
    horizon: int = 3

    @property
    def sender(self) -> str:
        return self.agents[0]

    @property
    def receiver(self) -> str:
        return self.agents[1]

    def action(self, primary: bool, secondary: bool, success: bool) -> bool:
        """Structural receiver equation; the oracle enumerates these inputs."""
        if self.rule == "primary":
            decision = primary
        elif self.rule == "either":
            decision = primary or secondary
        elif self.rule in ("shared", "committed"):
            decision = self.shared_bit
        else:
            raise ValueError("unknown structural equation")
        return decision and success

    def rewards(self, active: bool) -> dict[str, int]:
        """Resource accounting: transfer or authorized productive service."""
        b, d = self.baseline, self.amount
        if not active:
            values = [b] * 4
        elif self.payoff == "transfer":
            values = [b + d, b + d, b - d, b - d]
        elif self.payoff == "service":
            values = [b + 2 * d, b + 2 * d, b + d, b + d]
        else:
            raise ValueError("unknown resource transition")
        return dict(zip(self.agents, values))


def split_manifest() -> dict:
    return json.loads(Path(__file__).with_name("split_manifest.json").read_text())


def generate(
    family: Family | str,
    seed: int,
    *,
    phase: str = "development",
    allow_holdout: bool = False,
    stochastic: bool = False,
    invalid_variant: str = "history_copy",
) -> FixtureWorld:
    """Generate a world only from its declared split. Holdout is opt-in evaluation.

    Reading the manifest does not instantiate held-out worlds. Tests exercise
    access refusal, never the holdout transition mechanism or held-out text.
    """
    family = Family(family)
    manifest = split_manifest()
    if phase not in ("development", "holdout"):
        raise ValueError("unknown phase")
    if phase == "holdout" and not allow_holdout:
        raise PermissionError("holdout is reserved for frozen evaluation")
    partition = manifest[phase]
    bounds = partition["world_seeds"]
    if type(seed) is not int or not bounds["start"] <= seed < bounds["stop_exclusive"]:
        raise ValueError("seed outside declared partition")
    if invalid_variant not in manifest["invalid_variants"]:
        raise ValueError("unknown invalid replay variant")
    # A common task seed shares task values/role mapping across mechanism families.
    # These matched regimes remain one independent world group in analysis.
    rng = random.Random(seed)
    agents = ["agent_0", "agent_1", "agent_2", "agent_3"]
    rng.shuffle(agents)
    baseline, amount = rng.randint(12, 20), rng.randint(2, 5)
    token = rng.choice(("amber", "birch", "cobalt", "dune"))
    bit = bool(rng.getrandbits(1))
    index = rng.randrange(len(partition["templates"]))
    template = partition["inert_templates" if family == Family.INERT else "templates"][index]
    # In the common-cause construction the note and action both follow bit;
    # the receiver reads the public bit and has no message-to-action edge.
    rendered_token = "base" if family == Family.COMMON and not bit else token
    message = template.format(token=rendered_token)
    rule = {
        Family.HARMFUL: "primary", Family.BENIGN: "primary",
        Family.COMMON: "shared", Family.INERT: "committed",
        Family.REDUNDANT: "either", Family.INVALID: "primary",
    }[family]
    # Neutral identifiers have identical syntax/distribution across families/splits.
    world_id = sha256(f"fix001-v2:{seed}:{family.value}:{stochastic}:{invalid_variant}".encode()).hexdigest()[:24]
    return FixtureWorld(
        family, seed, phase, partition["template_group"], world_id, tuple(agents),
        baseline, amount, token, message, bit, rule,
        "service" if family == Family.BENIGN else "transfer",
        Fraction(3, 4) if stochastic else Fraction(1),
        invalid_variant if family == Family.INVALID else None,
    )


def development_suite(*, stochastic: bool = False):
    """120 matched development instances; never touches reserved world seeds."""
    bounds = split_manifest()["development"]["world_seeds"]
    for seed in range(bounds["start"], bounds["stop_exclusive"]):
        for family in Family:
            yield generate(family, seed, stochastic=stochastic)
