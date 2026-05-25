from rules import build_rules
from observable import execute_trace


robot_specs = [

    {
        "name": "avoidObstacle",
        "event": "sensor",
        "condition":
            "obstacle",
        "action":
            "turnLeft",
        "priority":
            90
    },

    {
        "name": "moveToGoal",
        "event": "sensor",
        "condition":
            "goalVisible",
        "action":
            "moveForward",
        "priority":
            50
    },

    {
        "name": "dockBattery",
        "event": "sensor",
        "condition":
            "batteryLow",
        "action":
            "returnToCharge",
        "priority":
            100
    }
]


def run_robot_navigation():

    rules = build_rules(
        robot_specs
    )

    initial_state = {

        "obstacle": False,
        "goalVisible": True,
        "batteryLow": False
    }

    events = [
        "sensor",
        "sensor",
        "sensor"
    ]

    semantic_trace, observable_trace = execute_trace(
        rules,
        initial_state,
        events
    )

    print("\n================================================")
    print("ROBOT NAVIGATION EXAMPLE")
    print("================================================")

    print("\nSemantic trace:")

    for step in semantic_trace:
        print(step)

    print("\nObservable trace:")

    for step in observable_trace:
        print(step)


if __name__ == "__main__":

    run_robot_navigation()
