# ============================================================
# RRAI REFACTORING VERIFICATION FRAMEWORK
# IEEE ACCESS VERSION
#
# rulebases.py
#
# PART 3/7
# Rule Bases
# Original System
# Safe Refactorings
# Unsafe Counterexample
# ============================================================

from core import build_rulebase


# ============================================================
# ORIGINAL RULE BASE
#
# Reference System R
# ============================================================

ORIGINAL_SPECS = [

    {
        "name": "r3",
        "event": "sensor",
        "guard": "obstacle and highSpeed",
        "action": "emergencyStop",
        "priority": 100
    },

    {
        "name": "r8",
        "event": "sensor",
        "guard": "collisionRisk",
        "action": "evade",
        "priority": 95
    },

    {
        "name": "r5",
        "event": "sensor",
        "guard": "batteryLow",
        "action": "returnToCharge",
        "priority": 70
    },

    {
        "name": "r14",
        "event": "sensor",
        "guard": "chargingStationNear",
        "action": "dock",
        "priority": 65
    },

    {
        "name": "r4",
        "event": "sensor",
        "guard": "obstacle",
        "action": "turnLeft",
        "priority": 55
    },

    {
        "name": "r2",
        "event": "sensor",
        "guard": "goalVisible",
        "action": "moveForward",
        "priority": 50
    },

    {
        "name": "r9",
        "event": "timer",
        "guard": "idle and goalVisible",
        "action": "moveForward",
        "priority": 50
    }
]

ORIGINAL_RB = build_rulebase(
    ORIGINAL_SPECS
)


# ============================================================
# LEMMA 1
# SAFE DECOMPOSITION
#
# r3
#
# =>
#
# r3a + r3b
#
# Same observable action
# Same priority
# Partition of guard
# ============================================================

SAFE_DECOMPOSITION_SPECS = [

    {
        "name": "r3a",
        "event": "sensor",
        "guard":
            "obstacle and highSpeed and frontObstacle",
        "action":
            "emergencyStop",
        "priority":
            100
    },

    {
        "name": "r3b",
        "event": "sensor",
        "guard":
            "obstacle and highSpeed and not frontObstacle",
        "action":
            "emergencyStop",
        "priority":
            100
    },

    {
        "name": "r8",
        "event": "sensor",
        "guard":
            "collisionRisk",
        "action":
            "evade",
        "priority":
            95
    },

    {
        "name": "r5",
        "event": "sensor",
        "guard":
            "batteryLow",
        "action":
            "returnToCharge",
        "priority":
            70
    },

    {
        "name": "r14",
        "event": "sensor",
        "guard":
            "chargingStationNear",
        "action":
            "dock",
        "priority":
            65
    },

    {
        "name": "r4",
        "event": "sensor",
        "guard":
            "obstacle",
        "action":
            "turnLeft",
        "priority":
            55
    },

    {
        "name": "r2",
        "event": "sensor",
        "guard":
            "goalVisible",
        "action":
            "moveForward",
        "priority":
            50
    },

    {
        "name": "r9",
        "event": "timer",
        "guard":
            "idle and goalVisible",
        "action":
            "moveForward",
        "priority":
            50
    }
]

SAFE_DECOMPOSITION_RB = build_rulebase(
    SAFE_DECOMPOSITION_SPECS
)


# ============================================================
# LEMMA 2
# SAFE MERGE
#
# Merge rules having:
#
# same action
# same priority
#
# into one rule
# ============================================================

SAFE_MERGE_SPECS = [

    {
        "name": "r3",
        "event": "sensor",
        "guard":
            "obstacle and highSpeed",
        "action":
            "emergencyStop",
        "priority":
            100
    },

    {
        "name": "r8",
        "event": "sensor",
        "guard":
            "collisionRisk",
        "action":
            "evade",
        "priority":
            95
    },

    {
        "name": "rBatteryDock",
        "event": "sensor",
        "guard":
            "batteryLow or chargingStationNear",
        "action":
            "returnToCharge",
        "priority":
            70
    },

    {
        "name": "r4",
        "event": "sensor",
        "guard":
            "obstacle",
        "action":
            "turnLeft",
        "priority":
            55
    },

    {
        "name": "r2",
        "event": "sensor",
        "guard":
            "goalVisible",
        "action":
            "moveForward",
        "priority":
            50
    },

    {
        "name": "r9",
        "event": "timer",
        "guard":
            "idle and goalVisible",
        "action":
            "moveForward",
        "priority":
            50
    }
]

SAFE_MERGE_RB = build_rulebase(
    SAFE_MERGE_SPECS
)


# ============================================================
# LEMMA 3
# SAFE ELIMINATION
#
# Remove dead rule
# ============================================================

DEAD_RULE_SPECS = [

    {
        "name": "rDead",
        "event": "watchdog",
        "guard": "False",
        "action": "hazardFlag",
        "priority": 999
    }
]

ORIGINAL_WITH_DEAD_RULE = build_rulebase(

    ORIGINAL_SPECS +

    DEAD_RULE_SPECS
)

SAFE_ELIMINATION_RB = build_rulebase(
    ORIGINAL_SPECS
)


# ============================================================
# LEMMA 4
# PRIORITY PRESERVATION
#
# Relative ordering preserved
# ============================================================

SAFE_PRIORITY_SPECS = [

    {
        "name": "r3",
        "event": "sensor",
        "guard":
            "obstacle and highSpeed",
        "action":
            "emergencyStop",
        "priority":
            100
    },

    {
        "name": "r8",
        "event": "sensor",
        "guard":
            "collisionRisk",
        "action":
            "evade",
        "priority":
            95
    },

    {
        "name": "r5",
        "event": "sensor",
        "guard":
            "batteryLow",
        "action":
            "returnToCharge",
        "priority":
            70
    },

    {
        "name": "r14",
        "event": "sensor",
        "guard":
            "chargingStationNear",
        "action":
            "dock",
        "priority":
            70
    },

    {
        "name": "r4",
        "event": "sensor",
        "guard":
            "obstacle",
        "action":
            "turnLeft",
        "priority":
            55
    },

    {
        "name": "r2",
        "event": "sensor",
        "guard":
            "goalVisible",
        "action":
            "moveForward",
        "priority":
            50
    },

    {
        "name": "r9",
        "event": "timer",
        "guard":
            "idle and goalVisible",
        "action":
            "moveForward",
        "priority":
            50
    }
]

SAFE_PRIORITY_RB = build_rulebase(
    SAFE_PRIORITY_SPECS
)


# ============================================================
# UNSAFE COUNTEREXAMPLE
#
# Behaviour intentionally changed
# ============================================================

UNSAFE_PRIORITY_SPECS = [

    {
        "name": "grant",
        "event": "sensor",
        "guard":
            "goalVisible",
        "action":
            "moveForward",
        "priority":
            100
    },

    {
        "name": "deny",
        "event": "sensor",
        "guard":
            "goalVisible",
        "action":
            "turnLeft",
        "priority":
            50
    }
]

UNSAFE_PRIORITY_RB = build_rulebase(
    UNSAFE_PRIORITY_SPECS
)


# ============================================================
# EXPERIMENT SIZES
# ============================================================

EXPERIMENT_SIZES = [

    100,
    500,
    1000,
    2000,
    5000,
    10000
]


# ============================================================
# SANITY CHECK
# ============================================================

if __name__ == "__main__":

    print("PART 3 OK")

    print(
        "Original Rules:",
        len(ORIGINAL_RB.rules)
    )

    print(
        "Safe Decomposition Rules:",
        len(SAFE_DECOMPOSITION_RB.rules)
    )

    print(
        "Safe Merge Rules:",
        len(SAFE_MERGE_RB.rules)
    )

    print(
        "Unsafe Rules:",
        len(UNSAFE_PRIORITY_RB.rules)
    )
