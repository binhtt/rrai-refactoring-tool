"""
Finite-domain proof-obligation checking for rule refactorings.

This module verifies preservation conditions for:

- rule decomposition;
- rule merging;
- rule elimination;
- priority adjustment.

The checks are performed by exhaustive enumeration over explicitly
constructed finite state-event domains.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Dict, Iterable, List, Sequence, Tuple

from core import Rule, RuleBase, State, eval_guard
from rulebases import (
    DECOMPOSED,
    ELIMINATED,
    ELIMINATION_ORIGINAL,
    INVALID_MERGE,
    INVALID_PRIORITY,
    MERGED,
    ORIGINAL,
    PRIORITY_ADJUSTED,
    UNSAFE_DECOMPOSITION,
)
from semantics import maximal_enabled


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

StateEvent = Tuple[State, str]
VerificationDomain = Sequence[StateEvent]


@dataclass(frozen=True)
class VerificationResult:
    """
    Result of a proof-obligation verification.

    Attributes
    ----------
    passed:
        True when all proof obligations are satisfied.

    details:
        Mapping from obligation names to Boolean outcomes.
    """

    passed: bool
    details: Dict[str, bool]


# ---------------------------------------------------------------------------
# Finite-domain construction
# ---------------------------------------------------------------------------

def all_states(predicates: Sequence[str]) -> List[State]:
    """
    Generate all Boolean valuations over the given predicates.

    Parameters
    ----------
    predicates:
        Predicate names defining the finite state space.

    Returns
    -------
    list of State
        All 2^n Boolean states, where n is the number of predicates.
    """

    return [
        dict(zip(predicates, values))
        for values in product(
            [False, True],
            repeat=len(predicates),
        )
    ]


def build_domain(
    predicates: Sequence[str],
    events: Sequence[str],
) -> List[StateEvent]:
    """
    Construct the Cartesian product of states and events.
    """

    return [
        (state, event)
        for state in all_states(predicates)
        for event in events
    ]


# Backward-compatible helper matching the single-file implementation.
def domain(
    predicates: Sequence[str],
    events: Sequence[str] = (
        "sensor",
        "timer",
        "watchdog",
    ),
) -> List[StateEvent]:
    """
    Construct the default finite verification domain.
    """

    return build_domain(predicates, events)


# ---------------------------------------------------------------------------
# Decomposition obligations
# ---------------------------------------------------------------------------

def check_guard_partition(
    original: Rule,
    parts: Sequence[Rule],
    verification_domain: VerificationDomain,
) -> bool:
    """
    Check that decomposition guards form an exact disjoint partition.

    For each state-event pair:

    - the original rule is enabled iff one decomposition part is enabled;
    - at most one decomposition part is enabled;
    - every decomposition part is reachable somewhere in the domain.
    """

    reached = {
        part.name: False
        for part in parts
    }

    for state, event in verification_domain:
        original_enabled = (
            original.event == event
            and eval_guard(original.guard, state)
        )

        enabled_parts = [
            part
            for part in parts
            if (
                part.event == event
                and eval_guard(part.guard, state)
            )
        ]

        for part in enabled_parts:
            reached[part.name] = True

        exact_union = (
            original_enabled
            == bool(enabled_parts)
        )

        pairwise_disjoint = (
            len(enabled_parts) <= 1
        )

        if not exact_union or not pairwise_disjoint:
            return False

    return all(reached.values())


def check_action_preservation(
    original: Rule,
    parts: Sequence[Rule],
) -> bool:
    """
    Check that every decomposition part preserves the original action.
    """

    return all(
        part.action == original.action
        for part in parts
    )


def check_priority_inheritance(
    original_rulebase: RuleBase,
    transformed_rulebase: RuleBase,
    original_name: str,
    part_names: Sequence[str],
) -> bool:
    """
    Check inheritance of all external priority relationships.

    Each decomposition part must inherit exactly the incoming and outgoing
    priority relations of the original rule. No priority relation is allowed
    between distinct decomposition parts.
    """

    external_names = (
        set(original_rulebase.by_name())
        - {original_name}
    )

    for external_name in external_names:
        for part_name in part_names:
            original_lower = (
                original_name,
                external_name,
            ) in original_rulebase.priority

            part_lower = (
                part_name,
                external_name,
            ) in transformed_rulebase.priority

            if original_lower != part_lower:
                return False

            original_higher = (
                external_name,
                original_name,
            ) in original_rulebase.priority

            part_higher = (
                external_name,
                part_name,
            ) in transformed_rulebase.priority

            if original_higher != part_higher:
                return False

    return all(
        (first, second)
        not in transformed_rulebase.priority
        for first in part_names
        for second in part_names
        if first != second
    )


def verify_decomposition(
    original_rulebase: RuleBase,
    transformed_rulebase: RuleBase,
    verification_domain: VerificationDomain,
    original_name: str,
    part_names: Sequence[str],
) -> VerificationResult:
    """
    Verify all proof obligations for rule decomposition.
    """

    original_rule = original_rulebase.by_name()[original_name]

    parts = [
        transformed_rulebase.by_name()[name]
        for name in part_names
    ]

    details = {
        "guard_partition": check_guard_partition(
            original_rule,
            parts,
            verification_domain,
        ),
        "action_preservation": check_action_preservation(
            original_rule,
            parts,
        ),
        "priority_inheritance": check_priority_inheritance(
            original_rulebase,
            transformed_rulebase,
            original_name,
            part_names,
        ),
    }

    return VerificationResult(
        passed=all(details.values()),
        details=details,
    )


# ---------------------------------------------------------------------------
# Merging obligations
# ---------------------------------------------------------------------------

def check_merge_guards(
    original_rules: Sequence[Rule],
    merged_rules: Sequence[Rule],
    verification_domain: VerificationDomain,
) -> bool:
    """
    Check guard union preservation and disjointness for merging.

    The enabledness of the original rules must equal the enabledness of the
    merged representation for each state-event pair. The original rules must
    not overlap in the verification domain.
    """

    for state, event in verification_domain:
        enabled_originals = [
            rule
            for rule in original_rules
            if (
                rule.event == event
                and eval_guard(rule.guard, state)
            )
        ]

        enabled_merged = [
            rule
            for rule in merged_rules
            if (
                rule.event == event
                and eval_guard(rule.guard, state)
            )
        ]

        union_preserved = (
            bool(enabled_originals)
            == bool(enabled_merged)
        )

        originals_disjoint = (
            len(enabled_originals) <= 1
        )

        merged_disjoint = (
            len(enabled_merged) <= 1
        )

        if not (
            union_preserved
            and originals_disjoint
            and merged_disjoint
        ):
            return False

    return True


def check_common_action(
    original_rules: Sequence[Rule],
    merged_rules: Sequence[Rule],
) -> bool:
    """
    Check that all original and merged rules have the same action.
    """

    actions = {
        rule.action
        for rule in [
            *original_rules,
            *merged_rules,
        ]
    }

    return len(actions) == 1


def check_priority_compatibility(
    original_rulebase: RuleBase,
    transformed_rulebase: RuleBase,
    original_names: Sequence[str],
    merged_names: Sequence[str],
) -> bool:
    """
    Check compatibility and inheritance of external priorities.

    All original rules participating in a merge must have identical incoming
    and outgoing priority relationships with each external rule. Each merged
    rule must inherit those relationships exactly.
    """

    external_names = (
        set(original_rulebase.by_name())
        - set(original_names)
    )

    for external_name in external_names:
        original_lower_relations = {
            (
                original_name,
                external_name,
            ) in original_rulebase.priority
            for original_name in original_names
        }

        original_higher_relations = {
            (
                external_name,
                original_name,
            ) in original_rulebase.priority
            for original_name in original_names
        }

        if len(original_lower_relations) > 1:
            return False

        if len(original_higher_relations) > 1:
            return False

        expected_lower = next(
            iter(original_lower_relations),
            False,
        )

        expected_higher = next(
            iter(original_higher_relations),
            False,
        )

        for merged_name in merged_names:
            actual_lower = (
                merged_name,
                external_name,
            ) in transformed_rulebase.priority

            actual_higher = (
                external_name,
                merged_name,
            ) in transformed_rulebase.priority

            if actual_lower != expected_lower:
                return False

            if actual_higher != expected_higher:
                return False

    return True


def verify_merge(
    original_rulebase: RuleBase,
    transformed_rulebase: RuleBase,
    verification_domain: VerificationDomain,
    original_names: Sequence[str],
    merged_names: Sequence[str],
) -> VerificationResult:
    """
    Verify all proof obligations for rule merging.
    """

    original_rules = [
        original_rulebase.by_name()[name]
        for name in original_names
    ]

    merged_rules = [
        transformed_rulebase.by_name()[name]
        for name in merged_names
    ]

    details = {
        "guard_union_disjointness": check_merge_guards(
            original_rules,
            merged_rules,
            verification_domain,
        ),
        "common_action": check_common_action(
            original_rules,
            merged_rules,
        ),
        "priority_compatibility": check_priority_compatibility(
            original_rulebase,
            transformed_rulebase,
            original_names,
            merged_names,
        ),
    }

    return VerificationResult(
        passed=all(details.values()),
        details=details,
    )


# ---------------------------------------------------------------------------
# Elimination obligation
# ---------------------------------------------------------------------------

def check_elimination(
    original_rulebase: RuleBase,
    rule_name: str,
    verification_domain: VerificationDomain,
) -> bool:
    """
    Check that the eliminated rule is never maximal enabled.
    """

    return all(
        rule_name
        not in {
            rule.name
            for rule in maximal_enabled(
                original_rulebase,
                state,
                event,
            )
        }
        for state, event in verification_domain
    )


def verify_elimination(
    original_rulebase: RuleBase,
    transformed_rulebase: RuleBase,
    verification_domain: VerificationDomain,
    rule_name: str,
) -> VerificationResult:
    """
    Verify the proof obligation for rule elimination.

    The transformed rule base is accepted as a parameter for API consistency
    with the other verification functions.
    """

    if rule_name in transformed_rulebase.by_name():
        removed_from_transformed = False
    else:
        removed_from_transformed = True

    details = {
        "never_maximal": check_elimination(
            original_rulebase,
            rule_name,
            verification_domain,
        ),
        "removed_from_transformed": removed_from_transformed,
    }

    return VerificationResult(
        passed=all(details.values()),
        details=details,
    )


# ---------------------------------------------------------------------------
# Priority-adjustment obligation
# ---------------------------------------------------------------------------

def check_priority_preservation(
    before: RuleBase,
    after: RuleBase,
    verification_domain: VerificationDomain,
) -> bool:
    """
    Check preservation of maximal enabled rule sets.
    """

    return all(
        {
            rule.name
            for rule in maximal_enabled(
                before,
                state,
                event,
            )
        }
        == {
            rule.name
            for rule in maximal_enabled(
                after,
                state,
                event,
            )
        }
        for state, event in verification_domain
    )


# Backward-compatible name matching the single-file implementation.
check_priority = check_priority_preservation


def verify_priority(
    before: RuleBase,
    after: RuleBase,
    verification_domain: VerificationDomain,
) -> VerificationResult:
    """
    Verify preservation under a priority adjustment.
    """

    details = {
        "maximal_enabled_preserved": check_priority_preservation(
            before,
            after,
            verification_domain,
        ),
    }

    return VerificationResult(
        passed=all(details.values()),
        details=details,
    )


# ---------------------------------------------------------------------------
# Complete experimental proof-obligation suite
# ---------------------------------------------------------------------------

def proof_obligations() -> Dict[str, VerificationResult]:
    """
    Run all valid and negative-control proof-obligation checks.

    Returns
    -------
    dict
        Verification results indexed by transformation name.
    """

    return {
        "Decomposition": verify_decomposition(
            original_rulebase=ORIGINAL,
            transformed_rulebase=DECOMPOSED,
            verification_domain=domain(
                [
                    "obstacleDetected",
                    "highSpeed",
                    "frontObstacle",
                    "batteryLow",
                ]
            ),
            original_name="r3",
            part_names=[
                "r3a",
                "r3b",
            ],
        ),

        "Merging": verify_merge(
            original_rulebase=PRIORITY_ADJUSTED,
            transformed_rulebase=MERGED,
            verification_domain=domain(
                [
                    "goalVisible",
                    "idle",
                    "narrowCorridor",
                ]
            ),
            original_names=[
                "r11",
                "r4",
            ],
            merged_names=[
                "r15_sensor",
                "r15_timer",
            ],
        ),

        "Elimination": verify_elimination(
            original_rulebase=ELIMINATION_ORIGINAL,
            transformed_rulebase=ELIMINATED,
            verification_domain=domain(
                [
                    "goalVisible",
                    "narrowCorridor",
                ]
            ),
            rule_name="r16",
        ),

        "Priority adjustment": verify_priority(
            before=ORIGINAL,
            after=PRIORITY_ADJUSTED,
            verification_domain=domain(
                [
                    "goalVisible",
                    "idle",
                    "narrowCorridor",
                ]
            ),
        ),

        "Invalid merge": verify_merge(
            original_rulebase=ORIGINAL,
            transformed_rulebase=INVALID_MERGE,
            verification_domain=domain(
                [
                    "goalVisible",
                    "idle",
                    "narrowCorridor",
                ]
            ),
            original_names=[
                "r11",
                "r4",
            ],
            merged_names=[
                "r15_sensor",
                "r15_timer",
            ],
        ),

        "Invalid priority adjustment": verify_priority(
            before=ORIGINAL,
            after=INVALID_PRIORITY,
            verification_domain=domain(
                [
                    "obstacleDetected",
                    "highSpeed",
                    "batteryLow",
                ]
            ),
        ),

        "Unsafe decomposition": verify_decomposition(
            original_rulebase=ORIGINAL,
            transformed_rulebase=UNSAFE_DECOMPOSITION,
            verification_domain=domain(
                [
                    "obstacleDetected",
                    "highSpeed",
                    "hazardFlag",
                ]
            ),
            original_name="r3",
            part_names=[
                "r3u1",
                "r3u2",
            ],
        ),
    }
