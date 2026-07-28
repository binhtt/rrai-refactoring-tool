"""
Operational semantics for reactive rule-based AI systems.

This module implements

- enabled rule computation
- transitive closure of priorities
- maximal enabled rules
- deterministic rule selection
- one-step execution
- trace execution
- behavioural correspondence checking
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Sequence, Set, Tuple, Optional

from core import (
    Rule,
    RuleBase,
    State,
    Transition,
    eval_guard,
    apply_action,
    freeze_state,
)


# --------------------------------------------------------------------
# Enabled rules
# --------------------------------------------------------------------

def enabled_rules(
    rulebase: RuleBase,
    state: State,
    event: str,
) -> List[Rule]:
    """
    Return all enabled rules for one event.
    """

    return [
        rule
        for rule in rulebase.rules
        if rule.event == event
        and eval_guard(rule.guard, state)
    ]


# --------------------------------------------------------------------
# Priority relation
# --------------------------------------------------------------------

@lru_cache(maxsize=None)
def _closure_cached(priority_tuple):

    closure = set(priority_tuple)

    changed = True

    while changed:

        changed = False
        new = set(closure)

        for a, b in closure:
            for c, d in closure:

                if b == c and (a, d) not in new:
                    new.add((a, d))
                    changed = True

        closure = new

    return frozenset(closure)


def transitive_closure(
    priority: Set[Tuple[str, str]]
) -> Set[Tuple[str, str]]:

    return set(
        _closure_cached(tuple(sorted(priority)))
    )


# --------------------------------------------------------------------
# Maximal enabled rules
# --------------------------------------------------------------------

def maximal_enabled(
    rulebase: RuleBase,
    state: State,
    event: str,
) -> List[Rule]:

    enabled = enabled_rules(rulebase, state, event)

    closure = transitive_closure(rulebase.priority)

    maximal = []

    for rule in enabled:

        dominated = any(

            (rule.name, other.name) in closure

            for other in enabled

            if other.name != rule.name

        )

        if not dominated:
            maximal.append(rule)

    return sorted(
        maximal,
        key=lambda r: r.name,
    )


# --------------------------------------------------------------------
# Rule selection
# --------------------------------------------------------------------

def select_rule(
    rulebase: RuleBase,
    state: State,
    event: str,
) -> Optional[Rule]:
    """
    Deterministic selection.

    If multiple incomparable maximal rules exist,
    choose the lexicographically smallest name.
    """

    maximal = maximal_enabled(
        rulebase,
        state,
        event,
    )

    if not maximal:
        return None

    return maximal[0]


# --------------------------------------------------------------------
# One execution step
# --------------------------------------------------------------------

def step(
    rulebase: RuleBase,
    state: State,
    event: str,
):

    rule = select_rule(
        rulebase,
        state,
        event,
    )

    before = freeze_state(state)

    if rule is None:

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
        rule.action,
    )

    transition = Transition(

        event=event,
        rule=rule.name,
        action=rule.action,
        before=before,
        after=freeze_state(after),
    )

    return after, transition


# --------------------------------------------------------------------
# Execute one trace
# --------------------------------------------------------------------

def run_trace(
    rulebase: RuleBase,
    initial_state: State,
    events: Sequence[str],
):

    state = dict(initial_state)

    trace = []

    for event in events:

        state, transition = step(
            rulebase,
            state,
            event,
        )

        trace.append(transition)

    return trace


# --------------------------------------------------------------------
# Behavioural correspondence
# --------------------------------------------------------------------

def transitions_correspond(
    t1: Transition,
    t2: Transition,
    correspondence,
) -> bool:

    if t1.event != t2.event:
        return False

    if t1.action != t2.action:
        return False

    if t1.after != t2.after:
        return False

    if t1.rule is None or t2.rule is None:

        return (
            t1.rule is None
            and
            t2.rule is None
        )

    return (
        t1.rule,
        t2.rule,
    ) in correspondence


def traces_correspond(
    trace1,
    trace2,
    correspondence,
):

    if len(trace1) != len(trace2):
        return False

    return all(

        transitions_correspond(
            t1,
            t2,
            correspondence,
        )

        for t1, t2

        in zip(trace1, trace2)

    )


# --------------------------------------------------------------------
# Bidirectional behavioural validation
# --------------------------------------------------------------------

def run_corresponding_trace_pair(
    rb1: RuleBase,
    rb2: RuleBase,
    initial_state: State,
    events: Sequence[str],
    correspondence,
):
    """
    Execute two corresponding rule bases simultaneously.

    Returns

        trace1
        trace2
        first_divergence_position
    """

    s1 = dict(initial_state)
    s2 = dict(initial_state)

    trace1 = []
    trace2 = []

    for position, event in enumerate(events, start=1):

        maximal1 = maximal_enabled(rb1, s1, event)
        maximal2 = maximal_enabled(rb2, s2, event)

        #
        # tau transition
        #

        if not maximal1 and not maximal2:

            b1 = freeze_state(s1)
            b2 = freeze_state(s2)

            t1 = Transition(
                event,
                None,
                "tau",
                b1,
                b1,
            )

            t2 = Transition(
                event,
                None,
                "tau",
                b2,
                b2,
            )

            trace1.append(t1)
            trace2.append(t2)

            continue

        matches = []

        matched1 = set()
        matched2 = set()

        for r1 in maximal1:

            for r2 in maximal2:

                if (
                    r1.name,
                    r2.name,
                ) not in correspondence:
                    continue

                if r1.action != r2.action:
                    continue

                ns1 = apply_action(
                    s1,
                    r1.action,
                )

                ns2 = apply_action(
                    s2,
                    r2.action,
                )

                if ns1 != ns2:
                    continue

                matches.append(
                    (
                        r1,
                        r2,
                        ns1,
                        ns2,
                    )
                )

                matched1.add(r1.name)
                matched2.add(r2.name)

        #
        # bidirectional checking
        #

        if (
            {r.name for r in maximal1} != matched1
            or
            {r.name for r in maximal2} != matched2
        ):

            return (
                trace1,
                trace2,
                position,
            )

        #
        # continue execution
        #

        r1, r2, ns1, ns2 = sorted(

            matches,

            key=lambda x: (
                x[0].name,
                x[1].name,
            ),

        )[0]

        t1 = Transition(
            event,
            r1.name,
            r1.action,
            freeze_state(s1),
            freeze_state(ns1),
        )

        t2 = Transition(
            event,
            r2.name,
            r2.action,
            freeze_state(s2),
            freeze_state(ns2),
        )

        trace1.append(t1)
        trace2.append(t2)

        s1 = ns1
        s2 = ns2

    return (
        trace1,
        trace2,
        None,
    )
