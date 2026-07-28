"""
Core data structures and state-manipulation functions for the
RRAI Refactoring Verification Framework.

This module defines:

- Rule
- RuleBase
- Transition
- GuardEvaluator
- eval_guard
- apply_action

Execution semantics such as enabled-rule computation, priority handling,
rule selection, and trace execution are implemented in semantics.py.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Mapping, Optional, Set, Tuple


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
    A reactive rule.

    Attributes
    ----------
    name:
        Unique rule identifier.

    event:
        Event that triggers evaluation of the rule.

    guard:
        Boolean expression evaluated over the current state.

    action:
        Action executed when the rule is selected.
    """

    name: str
    event: str
    guard: str
    action: str


@dataclass
class RuleBase:
    """
    A reactive rule base with a strict partial priority relation.

    The priority relation contains pairs of the form:

        (lower_priority_rule, higher_priority_rule)

    Therefore, a pair ``("r1", "r2")`` means that ``r2`` has priority
    over ``r1`` whenever both rules are enabled.
    """

    rules: List[Rule]
    priority: PriorityRelation

    def by_name(self) -> Dict[str, Rule]:
        """
        Return a dictionary mapping rule names to Rule objects.

        Raises
        ------
        ValueError
            If duplicate rule names are detected.
        """

        mapping: Dict[str, Rule] = {}

        for rule in self.rules:
            if rule.name in mapping:
                raise ValueError(f"Duplicate rule name: {rule.name}")

            mapping[rule.name] = rule

        return mapping


@dataclass(frozen=True)
class Transition:
    """
    A single transition produced during rule-base execution.

    Attributes
    ----------
    event:
        Input event processed at this transition.

    rule:
        Name of the selected rule, or None when no rule is selected.

    action:
        Executed action. The special action ``tau`` represents a
        no-operation transition.

    before:
        State before execution, represented as a sorted immutable tuple.

    after:
        State after execution, represented as a sorted immutable tuple.
    """

    event: str
    rule: Optional[str]
    action: str
    before: FrozenState
    after: FrozenState


# ---------------------------------------------------------------------------
# Guard evaluation
# ---------------------------------------------------------------------------

class GuardEvaluator(ast.NodeVisitor):
    """
    Safe evaluator for Boolean rule guards.

    Supported syntax
    ----------------
    - Boolean variables
    - True and False
    - and
    - or
    - not

    Arbitrary Python expressions, function calls, comparisons, arithmetic,
    attribute access, and other unsupported syntax are rejected.
    """

    def __init__(self, state: Mapping[str, bool]) -> None:
        self.state = state

    def visit_Expression(self, node: ast.Expression) -> bool:
        return bool(self.visit(node.body))

    def visit_Name(self, node: ast.Name) -> bool:
        if node.id == "True":
            return True

        if node.id == "False":
            return False

        return bool(self.state.get(node.id, False))

    def visit_Constant(self, node: ast.Constant) -> bool:
        if isinstance(node.value, bool):
            return node.value

        raise ValueError(
            "Only Boolean constants True and False are supported in guards"
        )

    def visit_BoolOp(self, node: ast.BoolOp) -> bool:
        values = [bool(self.visit(value)) for value in node.values]

        if isinstance(node.op, ast.And):
            return all(values)

        if isinstance(node.op, ast.Or):
            return any(values)

        raise ValueError(
            f"Unsupported Boolean operator: {type(node.op).__name__}"
        )

    def visit_UnaryOp(self, node: ast.UnaryOp) -> bool:
        if isinstance(node.op, ast.Not):
            return not bool(self.visit(node.operand))

        raise ValueError(
            f"Unsupported unary operator: {type(node.op).__name__}"
        )

    def generic_visit(self, node: ast.AST) -> bool:
        raise ValueError(
            f"Unsupported guard syntax: {ast.dump(node)}"
        )


@lru_cache(maxsize=None)
def _parse_guard(expression: str) -> ast.Expression:
    """
    Parse and cache a Boolean guard expression.

    Parameters
    ----------
    expression:
        Guard expression written using Python Boolean syntax.

    Returns
    -------
    ast.Expression
        Parsed abstract syntax tree.

    Raises
    ------
    ValueError
        If the expression is empty or syntactically invalid.
    """

    if not expression or not expression.strip():
        raise ValueError("Guard expression must not be empty")

    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(
            f"Invalid guard expression: {expression!r}"
        ) from exc

    if not isinstance(parsed, ast.Expression):
        raise ValueError(
            f"Expected an expression guard, received: {expression!r}"
        )

    return parsed


def eval_guard(expression: str, state: Mapping[str, bool]) -> bool:
    """
    Evaluate a Boolean rule guard over a state.

    Missing state variables are interpreted as False.

    Parameters
    ----------
    expression:
        Boolean guard expression.

    state:
        Mapping from predicate names to Boolean values.

    Returns
    -------
    bool
        Evaluation result.
    """

    parsed = _parse_guard(expression)
    evaluator = GuardEvaluator(state)

    return bool(evaluator.visit(parsed))


# ---------------------------------------------------------------------------
# State conversion helpers
# ---------------------------------------------------------------------------

def freeze_state(state: Mapping[str, bool]) -> FrozenState:
    """
    Convert a mutable state mapping to a deterministic immutable form.
    """

    return tuple(sorted((name, bool(value)) for name, value in state.items()))


def thaw_state(state: FrozenState) -> State:
    """
    Convert an immutable transition state back to a mutable dictionary.
    """

    return dict(state)


# ---------------------------------------------------------------------------
# Action semantics
# ---------------------------------------------------------------------------

def apply_action(state: Mapping[str, bool], action: str) -> State:
    """
    Apply an action to a state.

    A fresh dictionary is always returned; the input state is never modified.

    Parameters
    ----------
    state:
        Current Boolean state.

    action:
        Action name to execute.

    Returns
    -------
    State
        Updated state.

    Notes
    -----
    Actions not explicitly associated with a state update are treated as
    observational actions and leave the state unchanged. This includes,
    for example, ``stop``, ``reduceSpeed``, ``restartSensor``, and
    ``relocalize`` in the current case study.
    """

    updated_state: State = {
        name: bool(value)
        for name, value in state.items()
    }

    if action == "emergencyStop":
        updated_state["highSpeed"] = False
        updated_state["idle"] = True

    elif action == "moveForward":
        updated_state["idle"] = False

    elif action in {"turnLeft", "reroute", "evade"}:
        updated_state["pathBlocked"] = False

    elif action == "returnToCharge":
        updated_state["batteryLow"] = False

    elif action == "shutdown":
        updated_state["idle"] = True
        updated_state["highSpeed"] = False

    elif action == "dock":
        updated_state["batteryLow"] = False
        updated_state["batteryCritical"] = False

    elif action == "hazardFlag":
        updated_state["hazardFlag"] = True

    elif action == "safeMode":
        updated_state["idle"] = True

    elif action == "tau":
        pass

    return updated_state
