from typing import Any, List, Callable

import math
from dataclasses import dataclass, field

###############################################################################
"""
Scores are assigned to a policy based on how much we want to encourage teams to
take advantage of them.

Rule of thumb:
- LOW for things we encourage
- MEDIUM for things that should be in place
- HIGH for things that must be in place
"""

LOW = 1
MEDIUM = 3
HIGH = 9

WEIGHT_LOW = 1
WEIGHT_MEDIUM = 2
WEIGHT_HIGH = 3

###############################################################################


@dataclass
class Policy:
    """
    A policy could have different types of checks assigned, some which will be evaluated,
    and some that are qualifiers (e.g. if policy is relevant for entity)

    example:
    qualifier: entity is a Repository object
    check: code scanning is enabled (depending on context, this could also be a qualifier)
    """

    name: str
    points: int
    qualifiers: list[Callable[[Any], bool]]
    checks: list[Callable[[Any], bool]]

    def __post_init__(self):
        if not self.checks:
            raise ValueError("The checks list must contain at least one valid element.")
        if self.points <= 0:
            raise ValueError("Points must be integer larger than 0.")

    def get_points(self, obj: Any) -> int:
        return self.points if all(check(obj) for check in self.checks) else 0

    def qualify_policy(self, obj: Any) -> bool:
        return all(qualifier(obj) for qualifier in self.qualifiers)


@dataclass(kw_only=True)
class PolicySetResult:
    """Holds the detailed results of evaluating a PolicySet."""

    points_max: int
    points_sum: int
    score: int
    qualified_policies: List[Policy] = field(default_factory=list)
    unqualified_policies: List[Policy] = field(default_factory=list)
    tiers: List[int] = field(default_factory=list)


class PolicySet:
    def __init__(self, policies: list[Policy], weight: int = 2):
        self.policies = policies
        self.weight = weight

    def evaluate(self, obj_to_evaluate: Any) -> PolicySetResult:
        qualified_policies = []
        unqualified_policies = []
        for policy in self.policies:
            if policy.qualify_policy(obj_to_evaluate):
                qualified_policies.append(policy)
            else:
                unqualified_policies.append(policy)
        # TODO: how does this handle empty score/max_score?
        points_max = sum(policy.points for policy in qualified_policies)
        points_sum = sum(policy.get_points(obj_to_evaluate) for policy in qualified_policies)
        if points_max <= 0:  # Changed from score <= 0 to handle cases where max_score is 0
            score = 0
        else:
            score = math.floor((points_sum / points_max) * 100)  # will always floor decimals

        return PolicySetResult(
            points_max=points_max,
            points_sum=points_sum,
            score=score,
            qualified_policies=qualified_policies,
            unqualified_policies=unqualified_policies,
        )


@dataclass
class TierResult(PolicySetResult):
    """Holds the evaluation result for a single tier."""

    points_effective: int
    tier: int


@dataclass
class TieredPolicySetResult:
    """Holds the evaluation result for a single tier."""

    score: int
    policy_set_result: list[TierResult] = field(default_factory=list)

    def points_max(self) -> int:
        return sum(r.points_max for r in self.policy_set_result)

    def points_effective(self) -> int:
        return sum(r.points_effective for r in self.policy_set_result)


class TieredPolicySet:
    """
    Evaluates a series of Policies defined in a dictionary keyed by tier number (1-based).
    Returns a list of TierEvaluationResult objects, ordered by tier number.
    If a tier fails (score != max_score), it and all subsequent tiers get a tiered_score of 0.
    """

    def __init__(self, weight: int = WEIGHT_MEDIUM, tiered_policies: dict[int, list[Policy]] | None = None):
        self.weight = weight
        self.tiered_policies: dict[int, list[Policy]] = {}
        if tiered_policies is not None:
            self.add_tiers(tiered_policies)

    def add_tier(self, tier: int, policies: list[Policy]):
        if tier < 1:
            raise ValueError("Tier must be 1 and higher.")
        if tier in self.tiered_policies:
            raise ValueError(f"Tier {tier} already exist.")
        if self.tiered_policies and tier != max(self.tiered_policies.keys()) + 1:
            raise ValueError("Tier must increment by one from the previous highest tier.")
        self.tiered_policies[tier] = policies

    def add_tiers(self, tiered_policies: dict[int, list[Policy]]):
        if not tiered_policies:
            raise ValueError("The policy_sets dictionary cannot be empty.")

        sorted_tiers = sorted(tiered_policies.keys())
        # Validate keys are integers >= 1 and form a complete sequence 1, 2, ..., n
        if not all(isinstance(k, int) and k >= 1 for k in sorted_tiers) or sorted_tiers != list(
            range(1, len(sorted_tiers) + 1)
        ):
            raise ValueError("Tier keys must be integers forming a complete sequence starting from 1 (e.g., 1, 2, 3).")
        for tier_num, policies in tiered_policies.items():
            self.add_tier(tier_num, policies)

    def evaluate(self, obj_to_evaluate: Any) -> TieredPolicySetResult:
        """
        Evaluates the tiers and returns a list of TierEvaluationResult objects.
        """
        results = []
        preceding_tier_failed = False
        for tier_num in sorted(self.tiered_policies.keys()):
            current_tier_points = 0  # Default to 0 (failed)

            policy_set = PolicySet(self.tiered_policies[tier_num])
            policy_set_result = policy_set.evaluate(obj_to_evaluate)

            # Check if the current tier passes (all qualified policies pass for the inner PolicySet)
            # A tier passes if its points_sum equals its points_max (and points_max > 0)
            if preceding_tier_failed:
                tier_score = 0
            else:
                if 0 < policy_set_result.points_max:
                    current_tier_points = policy_set_result.points_sum
                    tier_score = policy_set_result.score
                    if policy_set_result.points_max != policy_set_result.points_sum:
                        preceding_tier_failed = True
                elif policy_set_result.points_max == 0:
                    # If points_max is 0 (no qualified policies), we still pass the tier.
                    tier_score = 0
                else:
                    # Current tier failed. Mark subsequent tiers as failed.
                    preceding_tier_failed = True
                    tier_score = 0

            results.append(
                TierResult(
                    points_effective=current_tier_points,
                    tier=tier_num,
                    points_max=policy_set_result.points_max,
                    points_sum=policy_set_result.points_sum,
                    score=tier_score,
                    qualified_policies=policy_set_result.qualified_policies,
                    unqualified_policies=policy_set_result.unqualified_policies,
                )
            )

        total_points_max = sum(r.points_max for r in results)
        total_points_effective = sum(r.points_effective for r in results)

        if total_points_max <= 0:  # Changed from score <= 0 to handle cases where max_score is 0
            score = 0
        else:
            score = math.floor((total_points_effective / total_points_max) * 100)  # will always floor decimals

        return TieredPolicySetResult(
            score=score,
            policy_set_result=results,
        )


def combined_policy_set_score(items_to_score: list[PolicySet | TieredPolicySet], obj_to_evaluate: Any) -> int:
    total_weight = 0
    total_score = 0

    for item in items_to_score:
        item_weight = item.weight
        item_score = item.evaluate(obj_to_evaluate).score

        total_score += item_score * item_weight
        total_weight += item_weight

    if total_weight <= 0:
        # Return 0 if total weight is 0, raise error only if it's negative (shouldn't happen with current logic)
        if total_weight == 0:
            return 0
        raise ValueError("The sum of weights must be larger than 0")

    evaluated_score = math.floor(total_score / total_weight)  # will always floor decimals
    return evaluated_score
