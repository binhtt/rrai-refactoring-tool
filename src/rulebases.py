"""
Rule bases and refactoring scenarios used by the
RRAI Refactoring Verification Framework.

This module defines:

Valid scenarios
---------------
- decomposition
- merging
- elimination
- priority adjustment

Negative-control scenarios
--------------------------
- unsafe decomposition
- invalid merge
- invalid priority adjustment

It also defines the rule-correspondence relations used for
behavioural validation.
"""

from __future__ import annotations

from typing import Set, Tuple

from core import Rule, RuleBase


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_rule(
    name: str,
    event: str,
    guard: str,
    action: str,
) -> Rule:
    """
    Construct a reactive rule.

    This short helper keeps the rule-base declarations compact and readable.
    """

    return Rule(
        name=name,
        event=event,
        guard=guard,
        action=action,
    )


# ---------------------------------------------------------------------------
# Original rule base
# ---------------------------------------------------------------------------

ORIGINAL_RULES = [
    make_rule(
        "r3",
        "sensor",
        "obstacleDetected and highSpeed",
        "emergencyStop",
    ),
    make_rule(
        "r8",
        "sensor",
        "collisionRisk",
        "evade",
    ),
    make_rule(
        "r12",
        "sensor",
        "cliffDetected",
        "stop",
    ),
    make_rule(
        "r5",
        "sensor",
        "batteryCritical",
        "shutdown",
    ),
    make_rule(
        "r2",
        "sensor",
        "batteryLow",
        "returnToCharge",
    ),
    make_rule(
        "r14",
        "sensor",
        "chargingStationNear",
        "dock",
    ),
    make_rule(
        "r1",
        "sensor",
        "pathBlocked",
        "reroute",
    ),
    make_rule(
        "r9",
        "sensor",
        "obstacleDetected",
        "turnLeft",
    ),
    make_rule(
        "r6",
        "sensor",
        "narrowCorridor",
        "reduceSpeed",
    ),
    make_rule(
        "r11",
        "sensor",
        "goalVisible",
        "moveForward",
    ),
    make_rule(
        "r4",
        "timer",
        "idle and goalVisible",
        "moveForward",
    ),
    make_rule(
        "r7",
        "watchdog",
        "communicationLost",
        "safeMode",
    ),
    make_rule(
        "r10",
        "watchdog",
        "sensorFailure",
        "restartSensor",
    ),
    make_rule(
        "r13",
        "watchdog",
        "localizationLost",
        "relocalize",
    ),
]


ORIGINAL_PRIORITY: Set[Tuple[str, str]] = {
    ("r2", "r3"),
    ("r9", "r3"),
    ("r1", "r8"),
    ("r2", "r5"),
    ("r6", "r11"),
    ("r10", "r7"),
}


ORIGINAL = RuleBase(
    rules=list(ORIGINAL_RULES),
    priority=set(ORIGINAL_PRIORITY),
)


# ---------------------------------------------------------------------------
# Valid priority adjustment
# ---------------------------------------------------------------------------

PRIORITY_ADJUSTED = RuleBase(
    rules=list(ORIGINAL_RULES),
    priority=set(ORIGINAL_PRIORITY) | {
        ("r6", "r4"),
    },
)


# ---------------------------------------------------------------------------
# Valid merging
# ---------------------------------------------------------------------------

MERGED_RULES = [
    rule
    for rule in ORIGINAL_RULES
    if rule.name not in {"r11", "r4"}
] + [
    make_rule(
        "r15_sensor",
        "sensor",
        "goalVisible",
        "moveForward",
    ),
    make_rule(
        "r15_timer",
        "timer",
        "idle and goalVisible",
        "moveForward",
    ),
]


MERGED_PRIORITY: Set[Tuple[str, str]] = {
    ("r2", "r3"),
    ("r9", "r3"),
    ("r1", "r8"),
    ("r2", "r5"),
    ("r6", "r15_sensor"),
    ("r6", "r15_timer"),
    ("r10", "r7"),
}


MERGED = RuleBase(
    rules=MERGED_RULES,
    priority=MERGED_PRIORITY,
)


# ---------------------------------------------------------------------------
# Valid decomposition
# ---------------------------------------------------------------------------

DECOMPOSED_RULES = [
    rule
    for rule in ORIGINAL_RULES
    if rule.name != "r3"
] + [
    make_rule(
        "r3a",
        "sensor",
        (
            "obstacleDetected "
            "and highSpeed "
            "and frontObstacle"
        ),
        "emergencyStop",
    ),
    make_rule(
        "r3b",
        "sensor",
        (
            "obstacleDetected "
            "and highSpeed "
            "and not frontObstacle"
        ),
        "emergencyStop",
    ),
]


DECOMPOSED_PRIORITY: Set[Tuple[str, str]] = {
    ("r2", "r3a"),
    ("r2", "r3b"),
    ("r9", "r3a"),
    ("r9", "r3b"),
    ("r1", "r8"),
    ("r2", "r5"),
    ("r6", "r11"),
    ("r10", "r7"),
}


DECOMPOSED = RuleBase(
    rules=DECOMPOSED_RULES,
    priority=DECOMPOSED_PRIORITY,
)


# ---------------------------------------------------------------------------
# Valid elimination
# ---------------------------------------------------------------------------

ELIMINATION_ORIGINAL_RULES = list(ORIGINAL_RULES) + [
    make_rule(
        "r16",
        "sensor",
        "goalVisible",
        "moveForward",
    ),
]


ELIMINATION_ORIGINAL_PRIORITY = (
    set(ORIGINAL_PRIORITY)
    | {
        ("r16", "r11"),
    }
)


ELIMINATION_ORIGINAL = RuleBase(
    rules=ELIMINATION_ORIGINAL_RULES,
    priority=ELIMINATION_ORIGINAL_PRIORITY,
)


ELIMINATED = RuleBase(
    rules=list(ORIGINAL_RULES),
    priority=set(ORIGINAL_PRIORITY),
)


# Backward-compatible alias matching the single-file implementation.
ELIM_ORIGINAL = ELIMINATION_ORIGINAL


# ---------------------------------------------------------------------------
# Negative control: unsafe decomposition
# ---------------------------------------------------------------------------

UNSAFE_DECOMPOSITION_RULES = [
    rule
    for rule in ORIGINAL_RULES
    if rule.name != "r3"
] + [
    make_rule(
        "r3u1",
        "sensor",
        "obstacleDetected",
        "hazardFlag",
    ),
    make_rule(
        "r3u2",
        "sensor",
        "hazardFlag and highSpeed",
        "emergencyStop",
    ),
]


UNSAFE_DECOMPOSITION_PRIORITY: Set[Tuple[str, str]] = {
    ("r2", "r3u1"),
    ("r2", "r3u2"),
    ("r9", "r3u1"),
    ("r9", "r3u2"),
    ("r1", "r8"),
    ("r2", "r5"),
    ("r6", "r11"),
    ("r10", "r7"),
}


UNSAFE_DECOMPOSITION = RuleBase(
    rules=UNSAFE_DECOMPOSITION_RULES,
    priority=UNSAFE_DECOMPOSITION_PRIORITY,
)


# ---------------------------------------------------------------------------
# Negative control: invalid priority adjustment
# ---------------------------------------------------------------------------

INVALID_PRIORITY_RELATION = (
    set(ORIGINAL_PRIORITY)
    - {
        ("r9", "r3"),
    }
) | {
    ("r3", "r9"),
}


INVALID_PRIORITY = RuleBase(
    rules=list(ORIGINAL_RULES),
    priority=INVALID_PRIORITY_RELATION,
)


# ---------------------------------------------------------------------------
# Negative control: invalid merge
# ---------------------------------------------------------------------------

INVALID_MERGE_RULES = [
    rule
    for rule in ORIGINAL_RULES
    if rule.name not in {"r11", "r4"}
] + [
    make_rule(
        "r15_sensor",
        "sensor",
        "goalVisible",
        "moveForward",
    ),
    make_rule(
        "r15_timer",
        "timer",
        "idle and goalVisible",
        "moveForward",
    ),
]


INVALID_MERGE = RuleBase(
    rules=INVALID_MERGE_RULES,
    priority=set(ORIGINAL_PRIORITY),
)


# ---------------------------------------------------------------------------
# Rule-correspondence relations
# ---------------------------------------------------------------------------

Correspondence = Set[Tuple[str, str]]


def identity_correspondence(
    before: RuleBase,
    after: RuleBase,
) -> Correspondence:
    """
    Construct identity correspondences for rules occurring in both systems.
    """

    common_names = (
        set(before.by_name())
        & set(after.by_name())
    )

    return {
        (name, name)
        for name in common_names
    }


# Backward-compatible alias matching the original implementation.
identity_corr = identity_correspondence


CORR_DECOMPOSITION: Correspondence = (
    identity_correspondence(
        ORIGINAL,
        DECOMPOSED,
    )
    | {
        ("r3", "r3a"),
        ("r3", "r3b"),
    }
)


CORR_PRIORITY_ADJUSTMENT: Correspondence = (
    identity_correspondence(
        ORIGINAL,
        PRIORITY_ADJUSTED,
    )
)


CORR_ELIMINATION: Correspondence = (
    identity_correspondence(
        ELIMINATION_ORIGINAL,
        ELIMINATED,
    )
)


CORR_MERGING: Correspondence = (
    identity_correspondence(
        PRIORITY_ADJUSTED,
        MERGED,
    )
    | {
        ("r11", "r15_sensor"),
        ("r4", "r15_timer"),
    }
)


CORR_INVALID_MERGE: Correspondence = (
    identity_correspondence(
        ORIGINAL,
        INVALID_MERGE,
    )
    | {
        ("r11", "r15_sensor"),
        ("r4", "r15_timer"),
    }
)


CORR_INVALID_PRIORITY: Correspondence = (
    identity_correspondence(
        ORIGINAL,
        INVALID_PRIORITY,
    )
)


CORR_UNSAFE_DECOMPOSITION: Correspondence = (
    identity_correspondence(
        ORIGINAL,
        UNSAFE_DECOMPOSITION,
    )
    | {
        ("r3", "r3u1"),
        ("r3", "r3u2"),
    }
)


# ---------------------------------------------------------------------------
# Backward-compatible correspondence aliases
# ---------------------------------------------------------------------------

CORR_DECOMP = CORR_DECOMPOSITION
CORR_PRIORITY = CORR_PRIORITY_ADJUSTMENT
CORR_ELIM = CORR_ELIMINATION
CORR_MERGE = CORR_MERGING
CORR_UNSAFE_DECOMP = CORR_UNSAFE_DECOMPOSITION
