"""
Finite-domain verification of correctness-preserving rule refactorings.

This module implements Algorithm 1 as an end-to-end procedure:

- construction of the complete finite state-event domain D = S x E;
- automatic refactoring-type detection;
- changed-rule identification;
- structural well-formedness checking;
- frame-preservation checking;
- transformation-specific proof obligations;
- refactoring-induced correspondence construction;
- witness generation;
- exhaustive counterexample search.

All supported transformations are checked over the same complete
represented finite domain of 196,608 state-event contexts.
"""

from __future__ import annotations

from dataclasses import asdict
from itertools import product
from typing import Dict, List, Optional, Sequence, Set, Tuple

from core import (
    FailureRecord,
    PriorityRelation,
    Rule,
    RuleBase,
    State,
    VerificationResult,
    eval_guard,
)

from rulebases import (
    DECOMPOSED,
    ELIMINATED,
    ELIM_ORIGINAL,
    INVALID_MERGE,
    INVALID_PRIORITY,
    MERGED,
    ORIGINAL,
    PRIORITY_ADJUSTED,
    UNSAFE_DECOMPOSITION,
)

from semantics import (
    _maximal_choice_matches,
    maximal_enabled,
    transition_for_rule,
    transitive_closure,
    validate_rulebase,
)


# ---------------------------------------------------------------------------
# Complete finite verification domain
# ---------------------------------------------------------------------------

EVENTS = [
    "sensor",
    "timer",
    "watchdog",
]


PREDICATES = [
    "obstacleDetected",
    "highSpeed",
    "frontObstacle",
    "collisionRisk",
    "cliffDetected",
    "batteryCritical",
    "batteryLow",
    "chargingStationNear",
    "pathBlocked",
    "narrowCorridor",
    "goalVisible",
    "idle",
    "communicationLost",
    "sensorFailure",
    "localizationLost",
    "hazardFlag",
]


class FiniteDomain:
    """
    Re-iterable complete finite domain D = S x E.

    State dictionaries are stored once, while state-event pairs are
    generated lazily during iteration.
    """

    def __init__(
        self,
        states: List[State],
        events: Sequence[str],
    ):
        self.states = states
        self.events = tuple(events)

    def __len__(self) -> int:
        return len(self.states) * len(self.events)

    def __iter__(self):
        for state in self.states:
            for event in self.events:
                yield state, event


Domain = FiniteDomain


def all_states(
    predicates: Sequence[str],
) -> List[State]:
    """
    Generate all Boolean valuations over the supplied predicates.
    """

    return [
        dict(zip(predicates, bits))
        for bits in product(
            [False, True],
            repeat=len(predicates),
        )
    ]


def complete_domain() -> FiniteDomain:
    """
    Construct the complete represented finite domain D = S x E.

    The case-study state contains 16 Boolean predicates and the event
    set contains three events. Therefore,

        |S| = 2^16 = 65,536
        |E| = 3
        |D| = 196,608.

    Only the 65,536 state dictionaries are stored; state-event pairs
    are produced lazily.
    """

    return FiniteDomain(
        all_states(PREDICATES),
        EVENTS,
    )


FULL_DOMAIN: FiniteDomain = complete_domain()


DOMAINS: Dict[str, FiniteDomain] = {
    "Decomposition": FULL_DOMAIN,
    "Merging": FULL_DOMAIN,
    "Elimination": FULL_DOMAIN,
    "Priority adjustment": FULL_DOMAIN,
    "Invalid merge": FULL_DOMAIN,
    "Invalid priority adjustment": FULL_DOMAIN,
    "Unsafe decomposition": FULL_DOMAIN,
}


# ---------------------------------------------------------------------------
# Algorithm 1: refactoring types
# ---------------------------------------------------------------------------

DECOMPOSITION = "Decomposition"
MERGE = "Merge"
ELIMINATION = "Elimination"
PRIORITY_ADJUSTMENT = "PriorityAdjustment"
UNSUPPORTED = "Unsupported"


# ---------------------------------------------------------------------------
# Refactoring detection
# ---------------------------------------------------------------------------

def detect_refactoring(
    before: RuleBase,
    after: RuleBase,
) -> str:
    """
    DetectRefactoring(R, R') from Algorithm 1.
    """

    before_rules = before.by_name()
    after_rules = after.by_name()

    removed = (
        set(before_rules)
        - set(after_rules)
    )

    added = (
        set(after_rules)
        - set(before_rules)
    )

    common = (
        set(before_rules)
        & set(after_rules)
    )

    common_rules_unchanged = all(
        before_rules[name] == after_rules[name]
        for name in common
    )

    # Same rule set and same rule definitions, but changed
    # priority relation.
    if (
        not removed
        and not added
        and common_rules_unchanged
    ):
        if (
            transitive_closure(before.priority)
            != transitive_closure(after.priority)
        ):
            return PRIORITY_ADJUSTMENT

        # Identity/no refactoring.
        return UNSUPPORTED

    # One rule is replaced by two or more rules.
    if (
        len(removed) == 1
        and len(added) >= 2
        and common_rules_unchanged
    ):
        return DECOMPOSITION

    # Two or more rules are replaced by one rule.
    if (
        len(removed) >= 2
        and len(added) == 1
        and common_rules_unchanged
    ):
        return MERGE

    # One rule disappears without replacement.
    if (
        len(removed) == 1
        and len(added) == 0
        and common_rules_unchanged
    ):
        return ELIMINATION

    return UNSUPPORTED


# ---------------------------------------------------------------------------
# Changed-rule identification
# ---------------------------------------------------------------------------

def identify_changed_rules(
    before: RuleBase,
    after: RuleBase,
) -> dict:
    """
    IdentifyChangedRules(R, R') from Algorithm 1.
    """

    before_names = set(
        before.by_name()
    )

    after_names = set(
        after.by_name()
    )

    return {
        "removed": sorted(
            before_names - after_names
        ),
        "added": sorted(
            after_names - before_names
        ),
        "retained": sorted(
            before_names & after_names
        ),
    }


# ---------------------------------------------------------------------------
# Refactoring-induced correspondence
# ---------------------------------------------------------------------------

def build_correspondence(
    transformation: str,
    before: RuleBase,
    after: RuleBase,
    changed: dict,
) -> Set[Tuple[str, str]]:
    """
    BuildCorrespondence(T, R, R') from Algorithm 1.
    """

    common = (
        set(before.by_name())
        & set(after.by_name())
    )

    correspondence = {
        (name, name)
        for name in common
    }

    removed = changed["removed"]
    added = changed["added"]

    if transformation == DECOMPOSITION:
        original = removed[0]

        correspondence |= {
            (original, part)
            for part in added
        }

    elif transformation == MERGE:
        merged = added[0]

        correspondence |= {
            (original, merged)
            for original in removed
        }

    # Elimination:
    # the removed rule has no image.
    #
    # Priority adjustment:
    # the identity relation is already complete.

    return correspondence


def correspondence_for(
    before: RuleBase,
    after: RuleBase,
) -> Set[Tuple[str, str]]:
    """
    Construct the correspondence automatically for a rule-base pair.
    """

    transformation = detect_refactoring(
        before,
        after,
    )

    changed = identify_changed_rules(
        before,
        after,
    )

    return build_correspondence(
        transformation,
        before,
        after,
        changed,
    )


# ---------------------------------------------------------------------------
# Priority helpers
# ---------------------------------------------------------------------------

def _priority_relation(
    rulebase: RuleBase,
) -> PriorityRelation:
    """
    Return the semantic priority relation obtained by transitive closure.
    """

    return transitive_closure(
        rulebase.priority
    )


# ---------------------------------------------------------------------------
# Frame preservation
# ---------------------------------------------------------------------------

def check_frame_preservation(
    before: RuleBase,
    after: RuleBase,
    changed: dict,
) -> List[FailureRecord]:
    """
    Ensure that retained rules and retained-to-retained priority
    relationships remain unchanged.

    This prevents changes outside the transformation identified by
    Algorithm 1.
    """

    failures: List[FailureRecord] = []

    before_rules = before.by_name()
    after_rules = after.by_name()

    retained = set(
        changed["retained"]
    )

    changed_retained = [
        name
        for name in retained
        if before_rules[name] != after_rules[name]
    ]

    if changed_retained:
        failures.append(
            FailureRecord(
                "FramePreservation",
                {
                    "changed_retained_rules":
                        sorted(changed_retained),
                },
            )
        )

    before_priority = _priority_relation(
        before
    )

    after_priority = _priority_relation(
        after
    )

    for first in sorted(retained):
        for second in sorted(retained):
            if first == second:
                continue

            before_value = (
                first,
                second,
            ) in before_priority

            after_value = (
                first,
                second,
            ) in after_priority

            if before_value != after_value:
                failures.append(
                    FailureRecord(
                        "FramePreservation",
                        {
                            "priority_pair": [
                                first,
                                second,
                            ],
                            "before":
                                before_value,
                            "after":
                                after_value,
                        },
                    )
                )

                return failures

    return failures


# ---------------------------------------------------------------------------
# Decomposition obligations
# ---------------------------------------------------------------------------

def check_guard_partition(
    original: Rule,
    parts: List[Rule],
    domain: Domain,
) -> List[FailureRecord]:
    """
    Check exact guard partitioning for decomposition.
    """

    failures: List[FailureRecord] = []

    seen = {
        part.name: False
        for part in parts
    }

    for state, event in domain:
        original_enabled = eval_guard(
            original.guard,
            state,
            event,
        )

        enabled_parts = [
            part
            for part in parts
            if eval_guard(
                part.guard,
                state,
                event,
            )
        ]

        for part in enabled_parts:
            seen[part.name] = True

        # Union equivalence.
        if (
            original_enabled
            != bool(enabled_parts)
        ):
            failures.append(
                FailureRecord(
                    "GuardPartition",
                    {
                        "reason":
                            "union_not_equivalent",
                        "state":
                            state,
                        "event":
                            event,
                        "original_enabled":
                            original_enabled,
                        "enabled_parts": [
                            part.name
                            for part in enabled_parts
                        ],
                    },
                )
            )

            break

        # Pairwise disjointness.
        if len(enabled_parts) > 1:
            failures.append(
                FailureRecord(
                    "GuardPartition",
                    {
                        "reason":
                            "parts_not_disjoint",
                        "state":
                            state,
                        "event":
                            event,
                        "enabled_parts": [
                            part.name
                            for part in enabled_parts
                        ],
                    },
                )
            )

            break

    missing = sorted(
        name
        for name, was_seen in seen.items()
        if not was_seen
    )

    if missing:
        failures.append(
            FailureRecord(
                "GuardPartition",
                {
                    "reason":
                        "empty_partition_component",
                    "rules":
                        missing,
                },
            )
        )

    return failures


def check_action_preservation(
    original: Rule,
    parts: List[Rule],
) -> List[FailureRecord]:
    """
    Check action preservation for decomposition.
    """

    mismatching = [
        part.name
        for part in parts
        if part.action != original.action
    ]

    if not mismatching:
        return []

    return [
        FailureRecord(
            "ActionPreservation",
            {
                "original_rule":
                    original.name,
                "original_action":
                    original.action,
                "mismatching_rules": {
                    part.name: part.action
                    for part in parts
                    if part.name in mismatching
                },
            },
        )
    ]


def check_priority_inheritance(
    before: RuleBase,
    after: RuleBase,
    original_name: str,
    part_names: List[str],
) -> List[FailureRecord]:
    """
    Check exact external-priority inheritance for decomposition.
    """

    before_priority = _priority_relation(
        before
    )

    after_priority = _priority_relation(
        after
    )

    external = (
        set(before.by_name())
        - {original_name}
    )

    for external_rule in sorted(external):
        for part in sorted(part_names):
            expected_part_below_external = (
                original_name,
                external_rule,
            ) in before_priority

            actual_part_below_external = (
                part,
                external_rule,
            ) in after_priority

            expected_external_below_part = (
                external_rule,
                original_name,
            ) in before_priority

            actual_external_below_part = (
                external_rule,
                part,
            ) in after_priority

            if (
                expected_part_below_external
                != actual_part_below_external
                or expected_external_below_part
                != actual_external_below_part
            ):
                return [
                    FailureRecord(
                        "PriorityInheritance",
                        {
                            "original":
                                original_name,
                            "part":
                                part,
                            "external_rule":
                                external_rule,
                            "expected_part_below_external":
                                expected_part_below_external,
                            "actual_part_below_external":
                                actual_part_below_external,
                            "expected_external_below_part":
                                expected_external_below_part,
                            "actual_external_below_part":
                                actual_external_below_part,
                        },
                    )
                ]

    # No priority relation is allowed between the decomposition parts.
    for first in part_names:
        for second in part_names:
            if (
                first != second
                and (
                    first,
                    second,
                ) in after_priority
            ):
                return [
                    FailureRecord(
                        "PriorityInheritance",
                        {
                            "reason":
                                "priority_between_decomposed_parts",
                            "pair": [
                                first,
                                second,
                            ],
                        },
                    )
                ]

    return []


# ---------------------------------------------------------------------------
# Merge obligations
# ---------------------------------------------------------------------------

def check_merge_guards(
    originals: List[Rule],
    merged: Rule,
    domain: Domain,
) -> List[FailureRecord]:
    """
    Check guard-union equivalence and pairwise disjointness of the
    original rules participating in a merge.
    """

    for state, event in domain:
        enabled_originals = [
            rule
            for rule in originals
            if eval_guard(
                rule.guard,
                state,
                event,
            )
        ]

        merged_enabled = eval_guard(
            merged.guard,
            state,
            event,
        )

        if (
            bool(enabled_originals)
            != merged_enabled
        ):
            return [
                FailureRecord(
                    "MergeGuards",
                    {
                        "reason":
                            "union_not_equivalent",
                        "state":
                            state,
                        "event":
                            event,
                        "enabled_originals": [
                            rule.name
                            for rule in enabled_originals
                        ],
                        "merged_enabled":
                            merged_enabled,
                    },
                )
            ]

        if len(enabled_originals) > 1:
            return [
                FailureRecord(
                    "MergeGuards",
                    {
                        "reason":
                            "original_guards_not_disjoint",
                        "state":
                            state,
                        "event":
                            event,
                        "enabled_originals": [
                            rule.name
                            for rule in enabled_originals
                        ],
                    },
                )
            ]

    return []


def check_common_action(
    originals: List[Rule],
    merged: Rule,
) -> List[FailureRecord]:
    """
    Check that the original rules and the merged rule have one common action.
    """

    actions = {
        rule.action
        for rule in originals
    } | {
        merged.action
    }

    if len(actions) == 1:
        return []

    return [
        FailureRecord(
            "CommonAction",
            {
                "original_actions": {
                    rule.name: rule.action
                    for rule in originals
                },
                "merged_rule":
                    merged.name,
                "merged_action":
                    merged.action,
            },
        )
    ]


def check_priority_compatibility(
    before: RuleBase,
    after: RuleBase,
    original_names: List[str],
    merged_name: str,
) -> List[FailureRecord]:
    """
    Check the merge priority-compatibility condition.

    All original rules participating in the merge must have the same
    external priority relationships, and the single merged rule must
    inherit those relationships.
    """

    before_priority = _priority_relation(
        before
    )

    after_priority = _priority_relation(
        after
    )

    external = (
        set(before.by_name())
        - set(original_names)
    )

    for external_rule in sorted(external):
        originals_below_external = [
            (
                original,
                (
                    original,
                    external_rule,
                ) in before_priority,
            )
            for original in original_names
        ]

        external_below_originals = [
            (
                original,
                (
                    external_rule,
                    original,
                ) in before_priority,
            )
            for original in original_names
        ]

        lower_values = {
            value
            for _, value
            in originals_below_external
        }

        higher_values = {
            value
            for _, value
            in external_below_originals
        }

        # The original rules are not priority-compatible.
        if (
            len(lower_values) > 1
            or len(higher_values) > 1
        ):
            return [
                FailureRecord(
                    "PriorityCompatibility",
                    {
                        "reason":
                            "original_rules_have_incompatible_external_priorities",
                        "external_rule":
                            external_rule,
                        "original_below_external":
                            dict(
                                originals_below_external
                            ),
                        "external_below_original":
                            dict(
                                external_below_originals
                            ),
                    },
                )
            ]

        expected_merged_below_external = next(
            iter(lower_values)
        )

        expected_external_below_merged = next(
            iter(higher_values)
        )

        actual_merged_below_external = (
            merged_name,
            external_rule,
        ) in after_priority

        actual_external_below_merged = (
            external_rule,
            merged_name,
        ) in after_priority

        if (
            expected_merged_below_external
            != actual_merged_below_external
            or expected_external_below_merged
            != actual_external_below_merged
        ):
            return [
                FailureRecord(
                    "PriorityCompatibility",
                    {
                        "reason":
                            "merged_rule_does_not_inherit_common_priority",
                        "external_rule":
                            external_rule,
                        "merged_rule":
                            merged_name,
                        "expected_merged_below_external":
                            expected_merged_below_external,
                        "actual_merged_below_external":
                            actual_merged_below_external,
                        "expected_external_below_merged":
                            expected_external_below_merged,
                        "actual_external_below_merged":
                            actual_external_below_merged,
                    },
                )
            ]

    return []


# ---------------------------------------------------------------------------
# Elimination obligation
# ---------------------------------------------------------------------------

def check_elimination(
    before: RuleBase,
    name: str,
    domain: Domain,
) -> List[FailureRecord]:
    """
    Check that the eliminated rule is never maximal enabled.
    """

    for state, event in domain:
        maximal = {
            rule.name
            for rule in maximal_enabled(
                before,
                state,
                event,
            )
        }

        if name in maximal:
            return [
                FailureRecord(
                    "EliminationCondition",
                    {
                        "rule":
                            name,
                        "state":
                            state,
                        "event":
                            event,
                        "maximal_enabled":
                            sorted(maximal),
                    },
                )
            ]

    return []


# ---------------------------------------------------------------------------
# Priority-adjustment obligation
# ---------------------------------------------------------------------------

def check_maximal_rule_preservation(
    before: RuleBase,
    after: RuleBase,
    domain: Domain,
) -> List[FailureRecord]:
    """
    Check preservation of maximal enabled rule sets.
    """

    for state, event in domain:
        before_maximal = {
            rule.name
            for rule in maximal_enabled(
                before,
                state,
                event,
            )
        }

        after_maximal = {
            rule.name
            for rule in maximal_enabled(
                after,
                state,
                event,
            )
        }

        if before_maximal != after_maximal:
            return [
                FailureRecord(
                    "MaximalRulePreservation",
                    {
                        "state":
                            state,
                        "event":
                            event,
                        "before":
                            sorted(before_maximal),
                        "after":
                            sorted(after_maximal),
                    },
                )
            ]

    return []


# ---------------------------------------------------------------------------
# Counterexample generation
# ---------------------------------------------------------------------------

def generate_counterexample(
    before: RuleBase,
    after: RuleBase,
    domain: Domain,
    correspondence: Set[Tuple[str, str]],
) -> Optional[dict]:
    """
    Exhaustively search the finite verification domain for a one-step
    behavioural counterexample.

    Counterexample generation is diagnostic and is not used to
    establish equivalence.
    """

    for state, event in domain:
        (
            maximal1,
            maximal2,
            _,
            matched1,
            matched2,
        ) = _maximal_choice_matches(
            before,
            after,
            state,
            state,
            event,
            correspondence,
        )

        names1 = {
            rule.name
            for rule in maximal1
        }

        names2 = {
            rule.name
            for rule in maximal2
        }

        if (
            not maximal1
            and not maximal2
        ):
            continue

        if (
            names1 != matched1
            or names2 != matched2
        ):
            rule1 = next(
                (
                    rule
                    for rule in maximal1
                    if rule.name not in matched1
                ),
                maximal1[0]
                if maximal1
                else None,
            )

            rule2 = next(
                (
                    rule
                    for rule in maximal2
                    if rule.name not in matched2
                ),
                maximal2[0]
                if maximal2
                else None,
            )

            transition1 = transition_for_rule(
                state,
                event,
                rule1,
            )

            transition2 = transition_for_rule(
                state,
                event,
                rule2,
            )

            return {
                "state":
                    state,
                "event":
                    event,
                "original_transition":
                    asdict(transition1),
                "transformed_transition":
                    asdict(transition2),
                "original_maximal":
                    sorted(names1),
                "transformed_maximal":
                    sorted(names2),
            }

    return None


# ---------------------------------------------------------------------------
# Algorithm 1: end-to-end verifier
# ---------------------------------------------------------------------------

def verify_refactoring(
    before: RuleBase,
    after: RuleBase,
    domain: Domain,
) -> VerificationResult:
    """
    Algorithm 1: Verification of Correctness-Preserving Rule Refactorings.

    The procedure:

    1. validates structural well-formedness;
    2. detects the refactoring type;
    3. identifies changed rules;
    4. validates frame preservation;
    5. checks the applicable proof obligations;
    6. builds C_Ref;
    7. records witnesses;
    8. generates a behavioural counterexample when one is found.
    """

    # Structural well-formedness is checked before interpreting
    # transformation-specific preservation conditions.
    structural_errors = {
        "before":
            validate_rulebase(before),
        "after":
            validate_rulebase(after),
    }

    if (
        structural_errors["before"]
        or structural_errors["after"]
    ):
        return VerificationResult(
            status="Fail",
            transformation="IllFormed",
            failed=[
                FailureRecord(
                    "WellFormedness",
                    structural_errors,
                )
            ],
            counterexample=None,
            changed_rules=identify_changed_rules(
                before,
                after,
            ),
            correspondence=set(),
            domain_size=len(domain),
        )

    transformation = detect_refactoring(
        before,
        after,
    )

    changed = identify_changed_rules(
        before,
        after,
    )

    if transformation == UNSUPPORTED:
        return VerificationResult(
            status="Unsupported",
            transformation=
                transformation,
            failed=[
                FailureRecord(
                    "UnsupportedRefactoring",
                    {
                        "changed_rules":
                            changed,
                    },
                )
            ],
            counterexample=None,
            changed_rules=changed,
            correspondence=set(),
            domain_size=len(domain),
        )

    failures: List[FailureRecord] = []

    # For decomposition, merge, and elimination, retained rules and
    # retained-to-retained priority relations form the frame.
    #
    # For priority adjustment, changing the priority relation is the
    # transformation itself; unchanged rule definitions are already
    # enforced by transformation detection.
    if transformation != PRIORITY_ADJUSTMENT:
        failures.extend(
            check_frame_preservation(
                before,
                after,
                changed,
            )
        )

    before_rules = before.by_name()
    after_rules = after.by_name()

    # ------------------------------------------------------------------
    # Decomposition
    # ------------------------------------------------------------------

    if transformation == DECOMPOSITION:
        original_name = (
            changed["removed"][0]
        )

        part_names = (
            changed["added"]
        )

        original = (
            before_rules[
                original_name
            ]
        )

        parts = [
            after_rules[name]
            for name in part_names
        ]

        failures.extend(
            check_guard_partition(
                original,
                parts,
                domain,
            )
        )

        failures.extend(
            check_action_preservation(
                original,
                parts,
            )
        )

        failures.extend(
            check_priority_inheritance(
                before,
                after,
                original_name,
                part_names,
            )
        )

    # ------------------------------------------------------------------
    # Merge
    # ------------------------------------------------------------------

    elif transformation == MERGE:
        original_names = (
            changed["removed"]
        )

        merged_name = (
            changed["added"][0]
        )

        originals = [
            before_rules[name]
            for name in original_names
        ]

        merged = (
            after_rules[
                merged_name
            ]
        )

        failures.extend(
            check_merge_guards(
                originals,
                merged,
                domain,
            )
        )

        failures.extend(
            check_common_action(
                originals,
                merged,
            )
        )

        failures.extend(
            check_priority_compatibility(
                before,
                after,
                original_names,
                merged_name,
            )
        )

    # ------------------------------------------------------------------
    # Elimination
    # ------------------------------------------------------------------

    elif transformation == ELIMINATION:
        eliminated_name = (
            changed["removed"][0]
        )

        failures.extend(
            check_elimination(
                before,
                eliminated_name,
                domain,
            )
        )

    # ------------------------------------------------------------------
    # Priority adjustment
    # ------------------------------------------------------------------

    elif transformation == PRIORITY_ADJUSTMENT:
        failures.extend(
            check_maximal_rule_preservation(
                before,
                after,
                domain,
            )
        )

    # Construct the transformation-induced correspondence automatically.
    correspondence = build_correspondence(
        transformation,
        before,
        after,
        changed,
    )

    if not failures:
        return VerificationResult(
            status="Pass",
            transformation=
                transformation,
            failed=[],
            counterexample=None,
            changed_rules=changed,
            correspondence=
                correspondence,
            domain_size=len(domain),
        )

    # A failed proof obligation causes diagnostic counterexample search.
    counterexample = generate_counterexample(
        before,
        after,
        domain,
        correspondence,
    )

    return VerificationResult(
        status="Fail",
        transformation=
            transformation,
        failed=failures,
        counterexample=
            counterexample,
        changed_rules=changed,
        correspondence=
            correspondence,
        domain_size=len(domain),
    )


# ---------------------------------------------------------------------------
# Experimental scenarios
# ---------------------------------------------------------------------------

EXPERIMENTS = {
    "Priority adjustment": (
        ORIGINAL,
        PRIORITY_ADJUSTED,
    ),

    "Merging": (
        PRIORITY_ADJUSTED,
        MERGED,
    ),

    "Decomposition": (
        MERGED,
        DECOMPOSED,
    ),

    "Elimination": (
        ELIM_ORIGINAL,
        ELIMINATED,
    ),

    "Invalid merge": (
        ORIGINAL,
        INVALID_MERGE,
    ),

    "Invalid priority adjustment": (
        ORIGINAL,
        INVALID_PRIORITY,
    ),

    "Unsafe decomposition": (
        ORIGINAL,
        UNSAFE_DECOMPOSITION,
    ),
}


CASES = [
    (
        name,
        before,
        after,
        correspondence_for(
            before,
            after,
        ),
    )
    for name, (
        before,
        after,
    ) in EXPERIMENTS.items()
]


# ---------------------------------------------------------------------------
# Complete proof-obligation suite
# ---------------------------------------------------------------------------

def proof_obligations() -> Dict[
    str,
    VerificationResult,
]:
    """
    Run Algorithm 1 for every valid and negative-control transformation.

    Every transformation is checked over the complete represented
    finite state-event domain of 196,608 contexts.
    """

    return {
        name: verify_refactoring(
            before,
            after,
            DOMAINS[name],
        )
        for name, (
            before,
            after,
        ) in EXPERIMENTS.items()
    }
