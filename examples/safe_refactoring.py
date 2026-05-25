from rules import build_rules
from equivalence import check_equivalence


original_specs = [

    {
        "name": "r3",
        "event": "sensor",
        "condition":
            "obstacle and highSpeed",
        "action":
            "emergencyStop",
        "priority":
            100
    },

    {
        "name": "r4",
        "event": "sensor",
        "condition":
            "obstacle",
        "action":
            "turnLeft",
        "priority":
            55
    }
]


safe_specs = [

    {
        "name": "r3a",
        "event": "sensor",
        "condition":
            "obstacle and highSpeed and frontObstacle",
        "action":
            "emergencyStop",
        "priority":
            100
    },

    {
        "name": "r3b",
        "event": "sensor",
        "condition":
            "obstacle and highSpeed and not frontObstacle",
        "action":
            "emergencyStop",
        "priority":
            100
    },

    {
        "name": "r4",
        "event": "sensor",
        "condition":
            "obstacle",
        "action":
            "turnLeft",
        "priority":
            55
    }
]


def run_safe_refactoring():

    original_rules = build_rules(
        original_specs
    )

    safe_rules = build_rules(
        safe_specs
    )

    result = check_equivalence(
        original_rules,
        safe_rules
    )

    print("\n================================================")
    print("SAFE REFACTORING")
    print("================================================")

    print(
        "\nObservable equivalence:",
        result
    )


if __name__ == "__main__":

    run_safe_refactoring()
