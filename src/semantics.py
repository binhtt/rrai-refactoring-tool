"""
Operational semantics for reactive rule-based AI systems.

This module implements:

- enabled-rule computation;
- transitive closure of priority relations;
- maximal enabled rules;
- deterministic rule selection;
- single-step execution;
- trace execution;
- transition and trace correspondence;
- bidirectional behavioural validation.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Optional, Sequence, Set, Tuple

from core import (
    Rule,
    RuleBase,
    State,
    Transition,
    apply_action,
    eval_guard,
    freeze_state,
)


# ---------------------------------------------------------------------------
# Enabled rules
# ---------------------------------------------------------------------------

def enabled_rules(
    rulebase: RuleBase,
    state: State,
    event: str,
) -> List[Rule]:
    """
    Return all rules enabled by the supplied state and event.
    """

    return [
        rule
        for rule in rulebase.rules
        if (
            rule.event == event
            and eval_guard(rule.guard, state)
        )
    ]


# ---------------------------------------------------------------------------
# Priority relation
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _closure_cached(
    priority_tuple: Tuple[Tuple[str, str], ...],
) -> frozenset[Tuple[str, str]]:
    """
    Compute and cache the transitive closure of a priority relation.
    """

    closure = set(priority_tuple)

    changed = True

    while changed:
        changed = False
        expanded = set(closure)

        for lower1, higher1 in closure:
            for lower2, higher2 in closure:
                if (
                    higher1 == lower2
                    and (lower1, higher2) not in expanded
                ):
                    expanded.add(
                        (lower1, higher2)
                    )
                    changed = True

        closure = expanded

    return frozenset(closure)


def transitive_closure(
    priority: Set[Tuple[str, str]],
) -> Set[Tuple[str, str]]:
    """
    Return the transitive closure of a strict priority relation.

    A pair ``(r1, r2)`` means that ``r2`` has higher priority than ``r1``.
    """

    priority_tuple = tuple(
        sorted(priority)
    )

    return set(
        _closure_cached(priority_tuple)
    )


# ---------------------------------------------------------------------------
# Maximal enabled rules
# ---------------------------------------------------------------------------

def maximal_enabled(
    rulebase: RuleBase,
    state: State,
    event: str,
) -> List[Rule]:
    """
    Return enabled rules that are not dominated by another enabled rule.
    """

    enabled = enabled_rules(
        rulebase,
        state,
        event,
    )

    closure = transitive_closure(
        rulebase.priority
    )

    maximal_rules: List[Rule] = []

    for rule in enabled:
        is_dominated = any(
            (
                rule.name,
                other.name,
            ) in closure
            for other in enabled
            if other.name != rule.name
        )

        if not is_dominated:
            maximal_rules.append(rule)

    return sorted(
        maximal_rules,
        key=lambda item: item.name,
    )


# ---------------------------------------------------------------------------
# Rule selection
# ---------------------------------------------------------------------------

def select_rule(
    rulebase: RuleBase,
    state: State,
    event: str,
) -> Optional[Rule]:
    """
    Select one maximal enabled rule deterministically.

    When several incomparable maximal rules exist, the lexicographically
    smallest rule name is selected.
    """

    maximal_rules = maximal_enabled(
        rulebase,
        state,
        event,
    )

    if not maximal_rules:
        return None

    return maximal_rules[0]


# ---------------------------------------------------------------------------
# Single-step execution
# ---------------------------------------------------------------------------

def step(
    rulebase: RuleBase,
    state: State,
    event: str,
) -> Tuple[State, Transition]:
    """
    Execute one event-processing step.
    """

    selected_rule = select_rule(
        rulebase,
        state,
        event,
    )

    before = freeze_state(state)

    if selected_rule is None:
        after = dict(state)

        transition = Transition(
            event=event,
            rule=None,
            action="tau",
            before=before,
            after=freeze_state(after),
        )

        return after, transition

    after = apply_action(
        state,
        selected_rule.action,
    )

    transition = Transition(
        event=event,
        rule=selected_rule.name,
        action=selected_rule.action,
        before=before,
        after=freeze_state(after),
    )

    return after, transition


# ---------------------------------------------------------------------------
# Trace execution
# ---------------------------------------------------------------------------

def run_trace(
    rulebase: RuleBase,
    initial_state: State,
    events: Sequence[str],
) -> List[Transition]:
    """
    Execute a complete event sequence.
    """

    state = dict(initial_state)
    trace: List[Transition] = []

    for event in events:
        state, transition = step(
            rulebase,
            state,
            event,
        )

        trace.append(transition)

    return trace


# ---------------------------------------------------------------------------
# Transition and trace correspondence
# ---------------------------------------------------------------------------

def transitions_correspond(
    transition1: Transition,
    transition2: Transition,
    correspondence: Set[Tuple[str, str]],
) -> bool:
    """
    Check whether two transitions correspond.
    """

    if transition1.event != transition2.event:
        return False

    if transition1.action != transition2.action:
        return False

    if transition1.after != transition2.after:
        return False

    if (
        transition1.rule is None
        or transition2.rule is None
    ):
        return (
            transition1.rule is None
            and transition2.rule is None
        )

    return (
        transition1.rule,
        transition2.rule,
    ) in correspondence


def traces_correspond(
    trace1: Sequence[Transition],
    trace2: Sequence[Transition],
    correspondence: Set[Tuple[str, str]],
) -> bool:
    """
    Check whether two complete traces correspond.
    """

    if len(trace1) != len(trace2):
        return False

    return all(
        transitions_correspond(
            transition1,
            transition2,
            correspondence,
        )
        for transition1, transition2
        in zip(trace1, trace2)
    )


# ---------------------------------------------------------------------------
# Bidirectional behavioural validation
# ---------------------------------------------------------------------------

def run_corresponding_trace_pair(
    rb1: RuleBase,
    rb2: RuleBase,
    initial_state: State,
    events: Sequence[str],
    correspondence: Set[Tuple[str, str]],
) -> Tuple[
    List[Transition],
    List[Transition],
    Optional[int],
]:
    """
    Execute two rule bases under the same initial state and event sequence.

    At each position, every maximal transition in either rule base must have
    a corresponding maximal transition in the other rule base with:

    - a corresponding rule;
    - the same event;
    - the same action;
    - the same successor state.

    The check is bidirectional and therefore detects additional
    nondeterministic behaviour introduced by a transformation.

    Returns
    -------
    trace1:
        Execution prefix for the first rule base.

    trace2:
        Execution prefix for the second rule base.

    first_divergence_position:
        One-based position of the first divergence, or None when no
        divergence is detected.
    """

    state1 = dict(initial_state)
    state2 = dict(initial_state)

    trace1: List[Transition] = []
    trace2: List[Transition] = []

    for position, event in enumerate(
        events,
        start=1,
    ):
        maximal1 = maximal_enabled(
            rb1,
            state1,
            event,
        )

        maximal2 = maximal_enabled(
            rb2,
            state2,
            event,
        )

        # Both systems perform a tau transition.
        if not maximal1 and not maximal2:
            before1 = freeze_state(state1)
            before2 = freeze_state(state2)

            transition1 = Transition(
                event=event,
                rule=None,
                action="tau",
                before=before1,
                after=before1,
            )

            transition2 = Transition(
                event=event,
                rule=None,
                action="tau",
                before=before2,
                after=before2,
            )

            trace1.append(transition1)
            trace2.append(transition2)

            continue

        matches = []

        matched_rule_names1: Set[str] = set()
        matched_rule_names2: Set[str] = set()

        for rule1 in maximal1:
            for rule2 in maximal2:
                if (
                    rule1.name,
                    rule2.name,
                ) not in correspondence:
                    continue

                if rule1.action != rule2.action:
                    continue

                next_state1 = apply_action(
                    state1,
                    rule1.action,
                )

                next_state2 = apply_action(
                    state2,
                    rule2.action,
                )

                if next_state1 != next_state2:
                    continue

                matches.append(
                    (
                        rule1.name,
                        rule2.name,
                        rule1,
                        rule2,
                        next_state1,
                        next_state2,
                    )
                )

                matched_rule_names1.add(
                    rule1.name
                )

                matched_rule_names2.add(
                    rule2.name
                )

        maximal_rule_names1 = {
            rule.name
            for rule in maximal1
        }

        maximal_rule_names2 = {
            rule.name
            for rule in maximal2
        }

        # A divergence occurs if at least one maximal rule in either system
        # has no corresponding maximal rule in the other system.
        if (
            maximal_rule_names1
            != matched_rule_names1
            or maximal_rule_names2
            != matched_rule_names2
        ):
            unmatched_rule1 = next(
                (
                    rule
                    for rule in maximal1
                    if rule.name
                    not in matched_rule_names1
                ),
                maximal1[0]
                if maximal1
                else None,
            )

            unmatched_rule2 = next(
                (
                    rule
                    for rule in maximal2
                    if rule.name
                    not in matched_rule_names2
                ),
                maximal2[0]
                if maximal2
                else None,
            )

            next_state1 = (
                dict(state1)
                if unmatched_rule1 is None
                else apply_action(
                    state1,
                    unmatched_rule1.action,
                )
            )

            next_state2 = (
                dict(state2)
                if unmatched_rule2 is None
                else apply_action(
                    state2,
                    unmatched_rule2.action,
                )
            )

            transition1 = Transition(
                event=event,
                rule=(
                    None
                    if unmatched_rule1 is None
                    else unmatched_rule1.name
                ),
                action=(
                    "tau"
                    if unmatched_rule1 is None
                    else unmatched_rule1.action
                ),
                before=freeze_state(state1),
                after=freeze_state(next_state1),
            )

            transition2 = Transition(
                event=event,
                rule=(
                    None
                    if unmatched_rule2 is None
                    else unmatched_rule2.name
                ),
                action=(
                    "tau"
                    if unmatched_rule2 is None
                    else unmatched_rule2.action
                ),
                before=freeze_state(state2),
                after=freeze_state(next_state2),
            )

            trace1.append(transition1)
            trace2.append(transition2)

            return (
                trace1,
                trace2,
                position,
            )

        # Continue with one corresponding maximal-rule pair.
        (
            _,
            _,
            selected_rule1,
            selected_rule2,
            next_state1,
            next_state2,
        ) = sorted(
            matches,
            key=lambda item: (
                item[0],
                item[1],
            ),
        )[0]

        transition1 = Transition(
            event=event,
            rule=selected_rule1.name,
            action=selected_rule1.action,
            before=freeze_state(state1),
            after=freeze_state(next_state1),
        )

        transition2 = Transition(
            event=event,
            rule=selected_rule2.name,
            action=selected_rule2.action,
            before=freeze_state(state2),
            after=freeze_state(next_state2),
        )

        trace1.append(transition1)
        trace2.append(transition2)

        state1 = next_state1
        state2 = next_state2

    return (
        trace1,
        trace2,
        None,
    )
