"""
Rule bases and refactoring scenarios used by the
RRAI Refactoring Verification Framework.

This module defines:

Valid scenarios
---------------
- priority adjustment
- merging
- decomposition
- elimination

Negative-control scenarios
--------------------------
- invalid merge
- invalid priority adjustment
- unsafe decomposition

The main preservation-valid sequence is:

    ORIGINAL
        -> PRIORITY_ADJUSTED
        -> MERGED
        -> DECOMPOSED

The elimination case is evaluated independently.
"""

from __future__ import annotations

from typing import Set, Tuple

from core import R, Rule, RuleBase


# ---------------------------------------------------------------------------
# Original rule base
# ---------------------------------------------------------------------------

ORIGINAL_RULES = [
    R(
        "r3",
        "sensor",
        "obstacleDetected and highSpeed",
        "emergencyStop",
    ),
    R(
        "r8",
        "sensor",
        "collisionRisk",
        "evade",
    ),
    R(
        "r12",
        "sensor",
        "cliffDetected",
        "stop",
    ),
    R(
        "r5",
        "sensor",
        "batteryCritical",
        "shutdown",
    ),
    R(
        "r2",
        "sensor",
        "batteryLow",
        "returnToCharge",
    ),
    R(
        "r14",
        "sensor",
        "chargingStationNear",
        "dock",
    ),
    R(
        "r1",
        "sensor",
        "pathBlocked",
        "reroute",
    ),
    R(
        "r9",
        "sensor",
        "obstacleDetected",
        "turnLeft",
    ),
    R(
        "r6",
        "sensor",
        "narrowCorridor",
        "reduceSpeed",
    ),
    R(
        "r11",
        "sensor",
        "goalVisible",
        "moveForward",
    ),
    R(
        "r4",
        "timer",
        "idle and goalVisible",
        "moveForward",
    ),
    R(
        "r7",
        "watchdog",
        "communicationLost",
        "safeMode",
    ),
    R(
        "r10",
        "watchdog",
        "sensorFailure",
        "restartSensor",
    ),
    R(
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
    list(ORIGINAL_RULES),
    set(ORIGINAL_PRIORITY),
)


# ---------------------------------------------------------------------------
# Valid priority adjustment
# ---------------------------------------------------------------------------

# 14 rules, 7 explicit priority relations.
PRIORITY_ADJUSTED = RuleBase(
    list(ORIGINAL_RULES),
    set(ORIGINAL_PRIORITY) | {
        ("r6", "r4"),
    },
)


# ---------------------------------------------------------------------------
# Valid merging
# ---------------------------------------------------------------------------

# Cardinality-changing merge:
#
#     r11, r4 -> r15
#
# This is one logical Rule object with a guard over S x E.
R15 = Rule(
    "r15",
    "((event == 'sensor') and goalVisible) or "
    "((event == 'timer') and idle and goalVisible)",
    "moveForward",
)


MERGED = RuleBase(
    [
        rule
        for rule in PRIORITY_ADJUSTED.rules
        if rule.name not in {"r11", "r4"}
    ]
    + [R15],
    {
        ("r2", "r3"),
        ("r9", "r3"),
        ("r1", "r8"),
        ("r2", "r5"),
        ("r6", "r15"),
        ("r10", "r7"),
    },
)


# ---------------------------------------------------------------------------
# Valid decomposition
# ---------------------------------------------------------------------------

# This is the next stage of the main sequence:
#
#     13 rules -> 14 rules
#
# It therefore starts from MERGED rather than ORIGINAL.
DECOMPOSED = RuleBase(
    [
        rule
        for rule in MERGED.rules
        if rule.name != "r3"
    ]
    + [
        R(
            "r3a",
            "sensor",
            "obstacleDetected and highSpeed and frontObstacle",
            "emergencyStop",
        ),
        R(
            "r3b",
            "sensor",
            "obstacleDetected and highSpeed and not frontObstacle",
            "emergencyStop",
        ),
    ],
    {
        ("r2", "r3a"),
        ("r2", "r3b"),
        ("r9", "r3a"),
        ("r9", "r3b"),
        ("r1", "r8"),
        ("r2", "r5"),
        ("r6", "r15"),
        ("r10", "r7"),
    },
)


# ---------------------------------------------------------------------------
# Valid elimination
# ---------------------------------------------------------------------------

# Elimination is evaluated independently from the main
# priority-adjustment -> merge -> decomposition sequence.
ELIM_ORIGINAL = RuleBase(
    list(ORIGINAL_RULES)
    + [
        R(
            "r16",
            "sensor",
            "goalVisible",
            "moveForward",
        )
    ],
    set(ORIGINAL_PRIORITY)
    | {
        ("r16", "r11"),
    },
)


ELIMINATED = RuleBase(
    list(ORIGINAL_RULES),
    set(ORIGINAL_PRIORITY),
)


# Backward-compatible name used by earlier modular code.
ELIMINATION_ORIGINAL = ELIM_ORIGINAL


# ---------------------------------------------------------------------------
# Negative control: unsafe decomposition
# ---------------------------------------------------------------------------

UNSAFE_DECOMPOSITION = RuleBase(
    [
        rule
        for rule in ORIGINAL_RULES
        if rule.name != "r3"
    ]
    + [
        R(
            "r3u1",
            "sensor",
            "obstacleDetected",
            "hazardFlag",
        ),
        R(
            "r3u2",
            "sensor",
            "hazardFlag and highSpeed",
            "emergencyStop",
        ),
    ],
    {
        ("r2", "r3u1"),
        ("r2", "r3u2"),
        ("r9", "r3u1"),
        ("r9", "r3u2"),
        ("r1", "r8"),
        ("r2", "r5"),
        ("r6", "r11"),
        ("r10", "r7"),
    },
)


# ---------------------------------------------------------------------------
# Negative control: invalid priority adjustment
# ---------------------------------------------------------------------------

# Remove r9 < r3 exactly as described in the manuscript.
# The reverse relation r3 < r9 is NOT introduced.
INVALID_PRIORITY = RuleBase(
    list(ORIGINAL_RULES),
    set(ORIGINAL_PRIORITY)
    - {
        ("r9", "r3"),
    },
)


# ---------------------------------------------------------------------------
# Negative control: invalid merge
# ---------------------------------------------------------------------------

# Create one logical merged rule r15u but deliberately omit
# the inherited priority relation involving the merged rule.
#
# Priority relations incident to the removed rules are not retained,
# so the resulting target rule base contains no dangling relation.
R15U = Rule(
    "r15u",
    "((event == 'sensor') and goalVisible) or "
    "((event == 'timer') and idle and goalVisible)",
    "moveForward",
)


INVALID_MERGE = RuleBase(
    [
        rule
        for rule in ORIGINAL.rules
        if rule.name not in {"r11", "r4"}
    ]
    + [R15U],
    {
        ("r2", "r3"),
        ("r9", "r3"),
        ("r1", "r8"),
        ("r2", "r5"),

        # Deliberately omitted:
        # ("r6", "r15u")

        ("r10", "r7"),
    },
)


# ---------------------------------------------------------------------------
# Rule-correspondence relations
# ---------------------------------------------------------------------------

# These constants are retained for compatibility with the modular
# implementation. The revised Algorithm 1 implementation constructs
# the same relations automatically from the detected transformation.

Correspondence = Set[Tuple[str, str]]


def identity_correspondence(
    before: RuleBase,
    after: RuleBase,
) -> Correspondence:
    """Identity pairs for rules retained in both rule bases."""

    common_names = (
        set(before.by_name())
        & set(after.by_name())
    )

    return {
        (name, name)
        for name in common_names
    }


# Backward-compatible alias.
identity_corr = identity_correspondence


# Priority adjustment:
#
#     ORIGINAL -> PRIORITY_ADJUSTED
#
CORR_PRIORITY_ADJUSTMENT: Correspondence = (
    identity_correspondence(
        ORIGINAL,
        PRIORITY_ADJUSTED,
    )
)


# Merge:
#
#     PRIORITY_ADJUSTED -> MERGED
#
# Genuine many-to-one correspondence:
#
#     (r11, r15)
#     (r4,  r15)
#
CORR_MERGING: Correspondence = (
    identity_correspondence(
        PRIORITY_ADJUSTED,
        MERGED,
    )
    | {
        ("r11", "r15"),
        ("r4", "r15"),
    }
)


# Decomposition:
#
#     MERGED -> DECOMPOSED
#
CORR_DECOMPOSITION: Correspondence = (
    identity_correspondence(
        MERGED,
        DECOMPOSED,
    )
    | {
        ("r3", "r3a"),
        ("r3", "r3b"),
    }
)


# Elimination:
#
#     ELIM_ORIGINAL -> ELIMINATED
#
CORR_ELIMINATION: Correspondence = (
    identity_correspondence(
        ELIM_ORIGINAL,
        ELIMINATED,
    )
)


# Invalid merge:
#
#     ORIGINAL -> INVALID_MERGE
#
CORR_INVALID_MERGE: Correspondence = (
    identity_correspondence(
        ORIGINAL,
        INVALID_MERGE,
    )
    | {
        ("r11", "r15u"),
        ("r4", "r15u"),
    }
)


# Invalid priority adjustment:
#
#     ORIGINAL -> INVALID_PRIORITY
#
CORR_INVALID_PRIORITY: Correspondence = (
    identity_correspondence(
        ORIGINAL,
        INVALID_PRIORITY,
    )
)


# Unsafe decomposition:
#
#     ORIGINAL -> UNSAFE_DECOMPOSITION
#
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
