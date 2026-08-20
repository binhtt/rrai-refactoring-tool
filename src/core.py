"""
Core data structures and state-manipulation functions for the
RRAI Refactoring Verification Framework.

This module defines:

- Rule
- RuleBase
- Transition
- FailureRecord
- VerificationResult
- GuardEvaluator
- eval_guard
- event_guard
- R
- apply_action

Execution semantics such as enabled-rule computation, priority handling,
rule selection, and trace execution are implemented in semantics.py.
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

State = Dict[str, bool]
PriorityRelation = Set[Tuple[str, str]]
FrozenState = Tuple[Tuple[str, bool], ...]


# ---------------------------------------------------------------------------
# Core rule-base model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Rule:
    """
    Reactive rule r = (g_r, a_r).

    The guard is evaluated over both state and event. Event conditions are
    therefore represented inside the guard expression, matching the manuscript's
    formal type g_r : S x E -> {true,false}.
    """

    name: str
    guard: str
    action: str


@dataclass
class RuleBase:
    """
    A reactive rule base with a strict partial priority relation.

    The priority relation contains pairs of the form:

        (lower_priority_rule, higher_priority_rule)

    Therefore, a pair ("r1", "r2") means that r2 has priority
    over r1 whenever both rules are enabled.
    """

    rules: List[Rule]
    priority: PriorityRelation

    def by_name(self) -> Dict[str, Rule]:
        return {r.name: r for r in self.rules}


@dataclass(frozen=True)
class Transition:
    """
    A single transition produced during rule-base execution.
    """

    event: str
    rule: Optional[str]
    action: str
    before: FrozenState
    after: FrozenState


@dataclass
class FailureRecord:
    obligation: str
    witness: Any


@dataclass
class VerificationResult:
    status: str  # Pass | Fail | Unsupported
    transformation: str
    failed: List[FailureRecord]
    counterexample: Optional[dict]
    changed_rules: dict
    correspondence: Set[Tuple[str, str]]
    domain_size: int

    @property
    def passed(self) -> bool:
        return self.status == "Pass"

    def to_jsonable(self) -> dict:
        return {
            "status": self.status,
            "transformation": self.transformation,
            "failed": [asdict(x) for x in self.failed],
            "counterexample": self.counterexample,
            "changed_rules": self.changed_rules,
            "correspondence": sorted(
                [list(x) for x in self.correspondence]
            ),
            "domain_size": self.domain_size,
        }


# ---------------------------------------------------------------------------
# Guard evaluation
# ---------------------------------------------------------------------------

class GuardEvaluator(ast.NodeVisitor):
    """Safe evaluator for the Boolean guard fragment used by the artifact."""

    def __init__(self, state: Mapping[str, bool], event: str):
        self.state = state
        self.event = event

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Name(self, node):
        if node.id == "event":
            return self.event

        if node.id in ("True", "False"):
            return node.id == "True"

        return bool(self.state.get(node.id, False))

    def visit_Constant(self, node):
        if isinstance(node.value, (bool, str)):
            return node.value

        raise ValueError(
            "Only Boolean and string constants are supported"
        )

    def visit_BoolOp(self, node):
        vals = [bool(self.visit(v)) for v in node.values]

        if isinstance(node.op, ast.And):
            return all(vals)

        if isinstance(node.op, ast.Or):
            return any(vals)

        raise ValueError("Unsupported Boolean operator")

    def visit_UnaryOp(self, node):
        if isinstance(node.op, ast.Not):
            return not bool(self.visit(node.operand))

        raise ValueError("Unsupported unary operator")

    def visit_Compare(self, node):
        # The artifact only needs event == "..." and event != "...".
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise ValueError("Only single comparisons are supported")

        left = self.visit(node.left)
        right = self.visit(node.comparators[0])
        op = node.ops[0]

        if isinstance(op, ast.Eq):
            return left == right

        if isinstance(op, ast.NotEq):
            return left != right

        raise ValueError("Only == and != comparisons are supported")

    def generic_visit(self, node):
        raise ValueError(
            f"Unsupported guard syntax: {ast.dump(node)}"
        )


@lru_cache(maxsize=None)
def _parse_guard(expr: str):
    return ast.parse(expr, mode="eval")


@lru_cache(maxsize=None)
def _compile_guard(expr: str):
    """
    Validate the small guard language once, then compile it for efficient
    repeated evaluation during exhaustive checking and Monte-Carlo runs.
    """

    tree = _parse_guard(expr)

    allowed = (
        ast.Expression,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.BoolOp,
        ast.And,
        ast.Or,
        ast.UnaryOp,
        ast.Not,
        ast.Compare,
        ast.Eq,
        ast.NotEq,
    )

    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError(
                f"Unsupported guard syntax: {ast.dump(node)}"
            )

        if (
            isinstance(node, ast.Constant)
            and not isinstance(node.value, (bool, str))
        ):
            raise ValueError(
                "Only Boolean and string constants are supported"
            )

    return compile(tree, "<guard>", "eval")


def eval_guard(
    expr: str,
    state: Mapping[str, bool],
    event: str,
) -> bool:
    env = dict(state)
    env["event"] = event

    code = _compile_guard(expr)

    return bool(
        eval(
            code,
            {"__builtins__": {}},
            env,
        )
    )


def event_guard(
    event: str,
    state_guard: str = "True",
) -> str:
    """Convenience syntax for Table-1-style rules with one triggering event."""

    return f"(event == {event!r}) and ({state_guard})"


def R(
    name: str,
    event: str,
    guard: str,
    action: str,
) -> Rule:
    return Rule(
        name=name,
        guard=event_guard(event, guard),
        action=action,
    )


# ---------------------------------------------------------------------------
# State conversion helpers
# ---------------------------------------------------------------------------

def freeze_state(state: Mapping[str, bool]) -> FrozenState:
    return tuple(
        sorted(
            (name, bool(value))
            for name, value in state.items()
        )
    )


def thaw_state(state: FrozenState) -> State:
    return dict(state)


# ---------------------------------------------------------------------------
# Action semantics
# ---------------------------------------------------------------------------

def apply_action(
    state: Mapping[str, bool],
    action: str,
) -> State:
    s = dict(state)

    if action == "emergencyStop":
        s["highSpeed"] = False
        s["idle"] = True

    elif action == "moveForward":
        s["idle"] = False

    elif action in ("turnLeft", "reroute", "evade"):
        s["pathBlocked"] = False

    elif action == "returnToCharge":
        s["batteryLow"] = False

    elif action == "shutdown":
        s["idle"] = True
        s["highSpeed"] = False

    elif action == "dock":
        s["batteryLow"] = False
        s["batteryCritical"] = False

    elif action == "hazardFlag":
        s["hazardFlag"] = True

    elif action == "safeMode":
        s["idle"] = True

    # stop, reduceSpeed, restartSensor, relocalize are observable actions
    # whose state abstraction is unchanged in this case study.

    return s
