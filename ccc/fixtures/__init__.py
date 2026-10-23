"""Offline Tier-A worlds. Only ``detector_input`` crosses the blinding boundary.

Generator instances and oracle records are evaluator-private, never detector inputs.
"""

from .worlds import Family, FixtureWorld, generate, development_suite
from .runner import detector_input, run_branch, validate_inputs
from .oracle import mechanism_truth
from .jira import generate_jira, exact_oracle, run_jira_branch, assert_jira_blinded

__all__ = [
    "Family", "FixtureWorld", "generate", "development_suite",
    "detector_input", "run_branch", "validate_inputs", "mechanism_truth",
    "generate_jira", "exact_oracle", "run_jira_branch", "assert_jira_blinded",
]
