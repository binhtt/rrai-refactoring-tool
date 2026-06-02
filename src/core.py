# ============================================================
# core.py
#
# Core Data Structures
# Rule Model
# Transition System
# Rule Base
# ============================================================

import copy
import random

import numpy as np

from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional


# ============================================================
# GLOBAL RANDOM SEED
# ============================================================

GLOBAL_SEED = 42

random.seed(GLOBAL_SEED)
np.random.seed(GLOBAL_SEED)


# ============================================================
# TRACE ELEMENT
# ============================================================

@dataclass(frozen=True)
class TraceStep:

    event: str
    rule: str
    action: str


# ============================================================
# RULE
# ============================================================

@dataclass
class Rule:

    name: str
    event: str
    guard: str
    action: str
    priority: int

    def enabled(
        self,
        state: Dict
    ) -> bool:

        try:

            return bool(
                eval(
                    self.guard,
                    {},
                    state
                )
            )

        except Exception:

            return False


# ============================================================
# TRANSITION SYSTEM
# ============================================================

class TransitionSystem:

    def __init__(self):

        self.action_effects = {

            "moveForward": {
                "moving": True
            },

            "turnLeft": {
                "direction": "left"
            },

            "turnRight": {
                "direction": "right"
            },

            "emergencyStop": {
                "moving": False,
                "emergency": True
            },

            "returnToCharge": {
                "charging": True
            },

            "dock": {
                "docked": True
            },

            "evade": {
                "evading": True
            },

            "hazardFlag": {
                "hazard": True
            },

            "grant": {
                "access": True
            },

            "deny": {
                "access": False
            }
        }

    def delta(
        self,
        state: Dict,
        action: str
    ) -> Dict:

        next_state = copy.deepcopy(
            state
        )

        if action in self.action_effects:

            next_state.update(
                self.action_effects[action]
            )

        return next_state


# ============================================================
# RULE BASE
# ============================================================

class RuleBase:

    def __init__(
        self,
        rules: List[Rule]
    ):

        self.rules = rules

    def enabled_rules(
        self,
        state: Dict,
        event: str
    ) -> List[Rule]:

        enabled = []

        for rule in self.rules:

            if rule.event != event:
                continue

            if rule.enabled(state):
                enabled.append(rule)

        return enabled

    def maximal_enabled(
        self,
        state: Dict,
        event: str
    ) -> List[Rule]:

        enabled = self.enabled_rules(
            state,
            event
        )

        if len(enabled) == 0:
            return []

        max_priority = max(
            rule.priority
            for rule in enabled
        )

        maximal = [

            rule

            for rule in enabled

            if rule.priority == max_priority
        ]

        return maximal

    def select(
        self,
        state: Dict,
        event: str
    ) -> Optional[Rule]:

        maximal = self.maximal_enabled(
            state,
            event
        )

        if len(maximal) == 0:
            return None

        maximal.sort(
            key=lambda r: r.name
        )

        return maximal[0]


# ============================================================
# RULE BASE FACTORY
# ============================================================

def build_rulebase(
    specs: List[Dict]
) -> RuleBase:

    rules = []

    for spec in specs:

        rules.append(

            Rule(
                name=spec["name"],
                event=spec["event"],
                guard=spec["guard"],
                action=spec["action"],
                priority=spec["priority"]
            )
        )

    return RuleBase(rules)


# ============================================================
# EVENT DOMAIN
# ============================================================

EVENTS = [

    "sensor",

    "timer",

    "watchdog"
]


# ============================================================
# RANDOM STATE GENERATOR
# ============================================================

def random_state() -> Dict:

    return {

        "obstacle":
            random.choice([True, False]),

        "highSpeed":
            random.choice([True, False]),

        "frontObstacle":
            random.choice([True, False]),

        "collisionRisk":
            random.choice([True, False]),

        "batteryLow":
            random.choice([True, False]),

        "chargingStationNear":
            random.choice([True, False]),

        "goalVisible":
            random.choice([True, False]),

        "idle":
            random.choice([True, False]),

        "admin":
            random.choice([True, False]),

        "untrustedNetwork":
            random.choice([True, False])
    }


# ============================================================
# RANDOM EVENT TRACE
# ============================================================

def random_event_trace(
    length: int = 20
) -> List[str]:

    return [

        random.choice(EVENTS)

        for _ in range(length)
    ]
