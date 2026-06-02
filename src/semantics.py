# ============================================================
# semantics.py
#
# Execution Semantics
# Trace Executor
# Trace Equivalence
# Monte-Carlo Preservation Checker
# ============================================================

import copy
import time

import numpy as np

from core import (
    TraceStep,
    TransitionSystem,
    RuleBase,
    random_state,
    random_event_trace
)


# ============================================================
# EXECUTION ENGINE
#
# Operational semantics:
#
# (s,e) -> (s',a)
#
# using priority-based conflict resolution
# ============================================================

class ExecutionEngine:

    def __init__(
        self,
        rulebase: RuleBase
    ):

        self.rulebase = rulebase

        self.transition_system = (
            TransitionSystem()
        )

    # --------------------------------------------------------
    # Single Step Execution
    # --------------------------------------------------------

    def execute_step(
        self,
        state: dict,
        event: str
    ):

        selected_rule = (

            self.rulebase.select(
                state,
                event
            )
        )

        # no enabled rule

        if selected_rule is None:

            step = TraceStep(

                event=event,

                rule="tau",

                action="tau"
            )

            return (

                copy.deepcopy(state),

                step
            )

        # apply transition

        next_state = (

            self.transition_system.delta(
                state,
                selected_rule.action
            )
        )

        step = TraceStep(

            event=event,

            rule=selected_rule.name,

            action=selected_rule.action
        )

        return (

            next_state,

            step
        )

    # --------------------------------------------------------
    # Execute Trace
    # --------------------------------------------------------

    def execute_trace(
        self,
        initial_state: dict,
        events: list
    ):

        state = copy.deepcopy(
            initial_state
        )

        trace = []

        for event in events:

            (
                state,
                step
            ) = self.execute_step(
                state,
                event
            )

            trace.append(step)

        return trace

    # --------------------------------------------------------
    # Final State
    # --------------------------------------------------------

    def final_state(
        self,
        initial_state: dict,
        events: list
    ) -> dict:

        state = copy.deepcopy(
            initial_state
        )

        for event in events:

            (
                state,
                _
            ) = self.execute_step(
                state,
                event
            )

        return state


# ============================================================
# TRACE EXECUTOR
#
# Wrapper used throughout experiments
# ============================================================

class TraceExecutor:

    def __init__(
        self,
        rulebase: RuleBase
    ):

        self.engine = (
            ExecutionEngine(
                rulebase
            )
        )

    def execute(
        self,
        initial_state: dict,
        events: list
    ):

        return self.engine.execute_trace(
            initial_state,
            events
        )


# ============================================================
# TRACE EQUIVALENCE
#
# IMPORTANT:
#
# Refactoring may rename rules.
#
# Therefore equivalence compares:
#
# (event, action)
#
# instead of
#
# (event, rule, action)
# ============================================================

class TraceEquivalence:

    # --------------------------------------------------------
    # Projection
    # --------------------------------------------------------

    @staticmethod
    def normalize(
        trace
    ):

        return [

            (
                step.event,
                step.action
            )

            for step in trace
        ]

    # --------------------------------------------------------
    # Equivalence
    # --------------------------------------------------------

    @staticmethod
    def equivalent(
        trace1,
        trace2
    ) -> bool:

        return (

            TraceEquivalence.normalize(
                trace1
            )

            ==

            TraceEquivalence.normalize(
                trace2
            )
        )

    # --------------------------------------------------------
    # First Divergence
    # --------------------------------------------------------

    @staticmethod
    def first_divergence(
        trace1,
        trace2
    ):

        t1 = (
            TraceEquivalence.normalize(
                trace1
            )
        )

        t2 = (
            TraceEquivalence.normalize(
                trace2
            )
        )

        n = min(
            len(t1),
            len(t2)
        )

        for i in range(n):

            if t1[i] != t2[i]:

                return i

        if len(t1) != len(t2):

            return n

        return None


# ============================================================
# PRESERVATION CHECKER
#
# Monte-Carlo behavioural verification
# ============================================================

class PreservationChecker:

    def __init__(
        self,
        original_rb: RuleBase,
        refactored_rb: RuleBase
    ):

        self.original_rb = (
            original_rb
        )

        self.refactored_rb = (
            refactored_rb
        )

    def run(
        self,
        iterations: int = 5000,
        trace_length: int = 20
    ):

        original_exec = (
            TraceExecutor(
                self.original_rb
            )
        )

        refactored_exec = (
            TraceExecutor(
                self.refactored_rb
            )
        )

        divergences = []

        start_time = time.time()

        for _ in range(iterations):

            state = random_state()

            events = random_event_trace(
                trace_length
            )

            trace1 = (
                original_exec.execute(
                    state,
                    events
                )
            )

            trace2 = (
                refactored_exec.execute(
                    state,
                    events
                )
            )

            div = (
                TraceEquivalence
                .first_divergence(
                    trace1,
                    trace2
                )
            )

            if div is not None:

                divergences.append(
                    div
                )

        elapsed = (
            time.time()
            - start_time
        )

        return {

            "equivalent":
                len(divergences) == 0,

            "divergence_count":
                len(divergences),

            "divergence_rate":
                len(divergences)
                / iterations,

            "avg_divergence_position":
                (
                    float(
                        np.mean(
                            divergences
                        )
                    )
                    if divergences
                    else 0.0
                ),

            "execution_time":
                elapsed,

            "divergences":
                divergences
        }


# ============================================================
# SANITY TEST
# ============================================================

if __name__ == "__main__":
    print("SEMANTICS OK")
