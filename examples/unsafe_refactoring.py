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


unsafe_specs = [

    {
        "name": "r3a",
        "event": "sensor",
        "condition":
            "obstacle",
        "action":
            "hazardFlag",
        "priority":
            100
    },

    {
        "name": "r3b",
        "event": "sensor",
        "condition":
            "hazard and highSpeed",
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


def run_unsafe_refactoring():

    original_rules = build_rules(
        original_specs
    )

    unsafe_rules = build_rules(
        unsafe_specs
    )

    result = check_equivalence(
        original_rules,
        unsafe_rules
    )

    print("\n================================================")
    print("UNSAFE REFACTORING")
    print("================================================")

    print(
        "\nObservable equivalence:",
        result
    )


if __name__ == "__main__":

    run_unsafe_refactoring()
