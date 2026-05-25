from rules import build_rules


def test_rule_loading():

    specs = [

        {
            "name": "r1",
            "event": "sensor",
            "condition": "True",
            "action": "moveForward",
            "priority": 1
        }
    ]

    rules = build_rules(specs)

    assert len(rules) == 1

    assert rules[0].name == "r1"

    assert rules[0].event == "sensor"

    assert rules[0].action == "moveForward"


def test_condition_compilation():

    specs = [

        {
            "name": "r2",
            "event": "sensor",
            "condition": "obstacle and highSpeed",
            "action": "emergencyStop",
            "priority": 10
        }
    ]

    rules = build_rules(specs)

    state = {

        "obstacle": True,
        "highSpeed": True
    }

    assert rules[0].condition(state) is True
