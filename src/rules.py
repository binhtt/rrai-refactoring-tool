from dataclasses import dataclass
from typing import Callable, Dict


@dataclass
class Rule:

    name: str
    event: str
    condition: Callable[[Dict], bool]
    action: str
    priority: int


def compile_condition(expr: str):

    def condition(state):

        try:
            return eval(expr, {}, state)

        except Exception:
            return False

    return condition


def build_rules(rule_specs):

    rules = []

    for spec in rule_specs:

        rules.append(

            Rule(
                name=spec["name"],
                event=spec["event"],
                condition=compile_condition(
                    spec["condition"]
                ),
                action=spec["action"],
                priority=spec["priority"]
            )
        )

    return rules


original_specs = [
    {
        "name": "r3",
        "event": "sensor",
        "condition": "obstacle and highSpeed",
        "action": "emergencyStop",
        "priority": 100
    }
]

safe_specs = [
    {
        "name": "r3a",
        "event": "sensor",
        "condition": "obstacle and highSpeed and frontObstacle",
        "action": "emergencyStop",
        "priority": 100
    }
]

unsafe_specs = [
    {
        "name": "r3a",
        "event": "sensor",
        "condition": "obstacle",
        "action": "hazardFlag",
        "priority": 100
    }
]
