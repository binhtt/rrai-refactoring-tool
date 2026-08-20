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
    Return all rules enabled by the supplied state-event context.
    """

    return [
        rule
        for rule in rulebase.rules
        if eval_guard(rule.guard, state, event)
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

    A pair (r1, r2) means that r2 has higher priority than r1.
    """

    return set(
        _closure_cached(
            tuple(sorted(priority))
        )
    )


# ---------------------------------------------------------------------------
# Rule-base validation
# ---------------------------------------------------------------------------

def validate_rulebase(
    rulebase: RuleBase,
) -> List[str]:
    """
    Validate structural well-formedness of a rule base.

    The stored priority edges may represent a transitive reduction.
    Their transitive closure is used as the semantic priority relation.
    """

    errors: List[str] = []

    names = {
        rule.name
        for rule in rulebase.rules
    }

    if len(names) != len(rulebase.rules):
        errors.append("Duplicate rule names")

    dangling = [
        (lower, higher)
        for lower, higher in rulebase.priority
        if lower not in names or higher not in names
    ]

    if dangling:
        errors.append(
            f"Dangling priority relations: {sorted(dangling)}"
        )

    closure = transitive_closure(
        rulebase.priority
    )

    cycles = sorted(
        name
        for name in names
        if (name, name) in closure
    )

    if cycles:
        errors.append(
            "Priority relation is not irreflexive/acyclic: "
            f"{cycles}"
        )

    return errors


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

    return maximal_rules[0] if maximal_rules else None


# ---------------------------------------------------------------------------
# Transition helpers
# ---------------------------------------------------------------------------

def transition_for_rule(
    state: State,
    event: str,
    rule: Optional[Rule],
) -> Transition:
    """
    Construct the transition produced by executing the supplied rule.
    """

    before = freeze_state(state)

    if rule is None:
        return Transition(
            event=event,
            rule=None,
            action="tau",
            before=before,
            after=before,
        )

    after_state = apply_action(
        state,
        rule.action,
    )

    return Transition(
        event=event,
        rule=rule.name,
        action=rule.action,
        before=before,
        after=freeze_state(after_state),
    )


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

    transition = transition_for_rule(
        state,
        event,
        selected_rule,
    )

    return dict(transition.after), transition


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
    Check whether two labelled transitions correspond.
    """

    if (
        transition1.event != transition2.event
        or transition1.action != transition2.action
        or transition1.before != transition2.before
        or transition1.after != transition2.after
    ):
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
# Bidirectional maximal-choice correspondence
# ---------------------------------------------------------------------------

def _maximal_choice_matches(
    rb1: RuleBase,
    rb2: RuleBase,
    state1: State,
    state2: State,
    event: str,
    correspondence: Set[Tuple[str, str]],
):
    """
    Check both directions of the correspondence relation at one
    execution context.

    Returns maximal choices, matching pairs, and matched rule names.
    """

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

    matches = []

    matched1: Set[str] = set()
    matched2: Set[str] = set()

    if not maximal1 and not maximal2:
        return (
            maximal1,
            maximal2,
            matches,
            matched1,
            matched2,
        )

    for rule1 in maximal1:
        for rule2 in maximal2:
            if (
                rule1.name,
                rule2.name,
            ) not in correspondence:
                continue

            transition1 = transition_for_rule(
                state1,
                event,
                rule1,
            )

            transition2 = transition_for_rule(
                state2,
                event,
                rule2,
            )

            if transitions_correspond(
                transition1,
                transition2,
                correspondence,
            ):
                matches.append(
                    (
                        rule1.name,
                        rule2.name,
                        rule1,
                        rule2,
                        dict(transition1.after),
                        dict(transition2.after),
                    )
                )

                matched1.add(
                    rule1.name
                )

                matched2.add(
                    rule2.name
                )

    return (
        maximal1,
        maximal2,
        matches,
        matched1,
        matched2,
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

    At every step, every maximal choice in either system must have a
    corresponding maximal choice in the other system. A deterministic
    corresponding pair is selected only to continue the sampled prefix.

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
        (
            maximal1,
            maximal2,
            matches,
            matched1,
            matched2,
        ) = _maximal_choice_matches(
            rb1,
            rb2,
            state1,
            state2,
            event,
            correspondence,
        )

        if not maximal1 and not maximal2:
            transition1 = transition_for_rule(
                state1,
                event,
                None,
            )

            transition2 = transition_for_rule(
                state2,
                event,
                None,
            )

            trace1.append(
                transition1
            )

            trace2.append(
                transition2
            )

            continue

        maximal_names1 = {
            rule.name
            for rule in maximal1
        }

        maximal_names2 = {
            rule.name
            for rule in maximal2
        }

        if (
            maximal_names1 != matched1
            or maximal_names2 != matched2
        ):
            unmatched_rule1 = next(
                (
                    rule
                    for rule in maximal1
                    if rule.name not in matched1
                ),
                maximal1[0]
                if maximal1
                else None,
            )

            unmatched_rule2 = next(
                (
                    rule
                    for rule in maximal2
                    if rule.name not in matched2
                ),
                maximal2[0]
                if maximal2
                else None,
            )

            transition1 = transition_for_rule(
                state1,
                event,
                unmatched_rule1,
            )

            transition2 = transition_for_rule(
                state2,
                event,
                unmatched_rule2,
            )

            trace1.append(
                transition1
            )

            trace2.append(
                transition2
            )

            return (
                trace1,
                trace2,
                position,
            )

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

        transition1 = transition_for_rule(
            state1,
            event,
            selected_rule1,
        )

        transition2 = transition_for_rule(
            state2,
            event,
            selected_rule2,
        )

        state1 = next_state1
        state2 = next_state2

        trace1.append(
            transition1
        )

        trace2.append(
            transition2
        )

    return (
        trace1,
        trace2,
        None,
    )
