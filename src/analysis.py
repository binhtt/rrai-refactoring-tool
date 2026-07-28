"""
Execution-based behavioural validation and scalability experiments.

This module provides:

- deterministic generation of initial states and event sequences;
- behavioural validation for valid and invalid refactorings;
- collection of first-divergence positions;
- extraction of counterexamples;
- repeated scalability experiments.

Execution-based validation complements proof-obligation checking. It
provides empirical evidence and concrete counterexamples, but it is not
treated as a formal proof of behavioural equivalence.
"""

from __future__ import annotations

import random
import statistics
import time
from typing import Dict, List, Optional, Sequence, Set, Tuple

from core import RuleBase, State, Transition
from rulebases import (
    CORR_DECOMPOSITION,
    CORR_ELIMINATION,
    CORR_INVALID_MERGE,
    CORR_INVALID_PRIORITY,
    CORR_MERGING,
    CORR_PRIORITY_ADJUSTMENT,
    CORR_UNSAFE_DECOMPOSITION,
    DECOMPOSED,
    ELIMINATED,
    ELIMINATION_ORIGINAL,
    INVALID_MERGE,
    INVALID_PRIORITY,
    MERGED,
    ORIGINAL,
    PRIORITY_ADJUSTED,
    UNSAFE_DECOMPOSITION,
)
from semantics import (
    run_corresponding_trace_pair,
    run_trace,
)


# ---------------------------------------------------------------------------
# Default experimental configuration
# ---------------------------------------------------------------------------

EVENTS: Tuple[str, ...] = (
    "sensor",
    "timer",
    "watchdog",
)


PREDICATES: Tuple[str, ...] = (
    "obstacleDetected",
    "highSpeed",
    "frontObstacle",
    "collisionRisk",
    "cliffDetected",
    "batteryCritical",
    "batteryLow",
    "chargingStationNear",
    "pathBlocked",
    "narrowCorridor",
    "goalVisible",
    "idle",
    "communicationLost",
    "sensorFailure",
    "localizationLost",
    "hazardFlag",
)


DEFAULT_SEED = 20260723
DEFAULT_TRACE_COUNT = 10_000
DEFAULT_TRACE_LENGTH = 20
DEFAULT_REPETITIONS = 30

DEFAULT_SCALABILITY_SIZES: Tuple[int, ...] = (
    100,
    500,
    1_000,
    2_000,
    5_000,
    10_000,
)


Correspondence = Set[Tuple[str, str]]

BehaviouralCase = Tuple[
    str,
    RuleBase,
    RuleBase,
    Correspondence,
]


# ---------------------------------------------------------------------------
# Experimental cases
# ---------------------------------------------------------------------------

CASES: Tuple[BehaviouralCase, ...] = (
    (
        "Decomposition",
        ORIGINAL,
        DECOMPOSED,
        CORR_DECOMPOSITION,
    ),
    (
        "Merging",
        PRIORITY_ADJUSTED,
        MERGED,
        CORR_MERGING,
    ),
    (
        "Elimination",
        ELIMINATION_ORIGINAL,
        ELIMINATED,
        CORR_ELIMINATION,
    ),
    (
        "Priority adjustment",
        ORIGINAL,
        PRIORITY_ADJUSTED,
        CORR_PRIORITY_ADJUSTMENT,
    ),
    (
        "Invalid merge",
        ORIGINAL,
        INVALID_MERGE,
        CORR_INVALID_MERGE,
    ),
    (
        "Invalid priority adjustment",
        ORIGINAL,
        INVALID_PRIORITY,
        CORR_INVALID_PRIORITY,
    ),
    (
        "Unsafe decomposition",
        ORIGINAL,
        UNSAFE_DECOMPOSITION,
        CORR_UNSAFE_DECOMPOSITION,
    ),
)


# ---------------------------------------------------------------------------
# Random input generation
# ---------------------------------------------------------------------------

def random_state(
    rng: random.Random,
    predicates: Sequence[str] = PREDICATES,
) -> State:
    """
    Generate one random Boolean state.

    ``hazardFlag`` is initially set to False because it is introduced as an
    intermediate state variable only by the unsafe-decomposition scenario.
    """

    state: State = {
        predicate: bool(rng.getrandbits(1))
        for predicate in predicates
    }

    if "hazardFlag" in state:
        state["hazardFlag"] = False

    return state


def random_events(
    rng: random.Random,
    length: int,
    events: Sequence[str] = EVENTS,
) -> List[str]:
    """
    Generate one random sequence of events.
    """

    if length <= 0:
        raise ValueError(
            "Trace length must be greater than zero"
        )

    if not events:
        raise ValueError(
            "At least one event type is required"
        )

    return [
        rng.choice(events)
        for _ in range(length)
    ]


def generate_inputs(
    number_of_traces: int,
    trace_length: int,
    seed: int,
) -> List[Tuple[State, List[str]]]:
    """
    Generate deterministic experimental inputs.

    The same states and event sequences are reused for every transformation
    case, ensuring that all rule-base pairs are evaluated under identical
    conditions.
    """

    if number_of_traces <= 0:
        raise ValueError(
            "Number of traces must be greater than zero"
        )

    if trace_length <= 0:
        raise ValueError(
            "Trace length must be greater than zero"
        )

    rng = random.Random(seed)

    return [
        (
            random_state(rng),
            random_events(
                rng,
                trace_length,
            ),
        )
        for _ in range(number_of_traces)
    ]


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def transition_to_dict(
    transition: Optional[Transition],
) -> Optional[Dict[str, object]]:
    """
    Convert a transition to a JSON-serializable dictionary.
    """

    if transition is None:
        return None

    return {
        "event": transition.event,
        "rule": transition.rule,
        "action": transition.action,
        "before": dict(transition.before),
        "after": dict(transition.after),
    }


def extract_divergence_transition(
    trace: Sequence[Transition],
    divergence_position: int,
) -> Optional[Transition]:
    """
    Return the transition at a one-based divergence position.
    """

    index = divergence_position - 1

    if index < 0 or index >= len(trace):
        return None

    return trace[index]


# ---------------------------------------------------------------------------
# Behavioural validation
# ---------------------------------------------------------------------------

def behavioural_validation(
    number_of_traces: int = DEFAULT_TRACE_COUNT,
    trace_length: int = DEFAULT_TRACE_LENGTH,
    seed: int = DEFAULT_SEED,
    cases: Sequence[BehaviouralCase] = CASES,
) -> Tuple[
    List[Dict[str, object]],
    Dict[str, Optional[Dict[str, object]]],
    Dict[str, List[int]],
]:
    """
    Perform execution-based validation for all transformation cases.

    Each pair of rule bases is executed under the same initial states and
    event sequences. At every event position, maximal enabled transitions
    are compared bidirectionally under the supplied rule correspondence.

    Returns
    -------
    rows:
        Tabular summaries for CSV reporting.

    counterexamples:
        The first observed counterexample for every transformation. The value
        is None when no divergence is detected.

    divergence_positions:
        All first-divergence positions observed for each transformation.
    """

    inputs = generate_inputs(
        number_of_traces=number_of_traces,
        trace_length=trace_length,
        seed=seed,
    )

    rows: List[Dict[str, object]] = []

    counterexamples: Dict[
        str,
        Optional[Dict[str, object]],
    ] = {}

    divergence_positions: Dict[
        str,
        List[int],
    ] = {}

    for (
        transformation_name,
        original_rulebase,
        transformed_rulebase,
        correspondence,
    ) in cases:
        divergence_count = 0
        positions: List[int] = []

        first_counterexample: Optional[
            Dict[str, object]
        ] = None

        start_time = time.perf_counter()

        for sample_index, (
            initial_state,
            events,
        ) in enumerate(inputs):
            (
                original_trace,
                transformed_trace,
                first_divergence,
            ) = run_corresponding_trace_pair(
                rb1=original_rulebase,
                rb2=transformed_rulebase,
                initial_state=initial_state,
                events=events,
                correspondence=correspondence,
            )

            if first_divergence is None:
                continue

            divergence_count += 1
            positions.append(first_divergence)

            if first_counterexample is not None:
                continue

            original_transition = (
                extract_divergence_transition(
                    original_trace,
                    first_divergence,
                )
            )

            transformed_transition = (
                extract_divergence_transition(
                    transformed_trace,
                    first_divergence,
                )
            )

            first_counterexample = {
                "sample_index": sample_index,
                "initial_state": dict(initial_state),
                "events": list(events),
                "divergence_position": first_divergence,
                "original_transition": transition_to_dict(
                    original_transition
                ),
                "transformed_transition": transition_to_dict(
                    transformed_transition
                ),
            }

        elapsed_seconds = (
            time.perf_counter()
            - start_time
        )

        divergence_rate = (
            divergence_count
            / number_of_traces
            * 100.0
        )

        rows.append(
            {
                "transformation": transformation_name,
                "executions": number_of_traces,
                "trace_length": trace_length,
                "seed": seed,
                "divergences": divergence_count,
                "rate_percent": round(
                    divergence_rate,
                    4,
                ),
                "elapsed_s": round(
                    elapsed_seconds,
                    6,
                ),
            }
        )

        counterexamples[
            transformation_name
        ] = first_counterexample

        divergence_positions[
            transformation_name
        ] = positions

    return (
        rows,
        counterexamples,
        divergence_positions,
    )


# ---------------------------------------------------------------------------
# Scalability experiment
# ---------------------------------------------------------------------------

def scalability(
    sizes: Sequence[int] = DEFAULT_SCALABILITY_SIZES,
    trace_length: int = DEFAULT_TRACE_LENGTH,
    repetitions: int = DEFAULT_REPETITIONS,
    base_seed: int = DEFAULT_SEED,
) -> List[Dict[str, object]]:
    """
    Measure execution time for increasing numbers of sampled traces.

    For each trace-count setting:

    - the experiment is repeated several times;
    - each repetition uses a deterministic but distinct seed;
    - the same generated inputs are applied to ORIGINAL and DECOMPOSED;
    - elapsed execution time is recorded;
    - mean, sample standard deviation, minimum, and maximum are reported.

    Only the number of traces changes. The rule bases, trace length, event
    set, and predicate set remain fixed.
    """

    if trace_length <= 0:
        raise ValueError(
            "Trace length must be greater than zero"
        )

    if repetitions <= 0:
        raise ValueError(
            "Number of repetitions must be greater than zero"
        )

    if not sizes:
        raise ValueError(
            "At least one scalability size is required"
        )

    if any(size <= 0 for size in sizes):
        raise ValueError(
            "Every scalability size must be greater than zero"
        )

    rows: List[Dict[str, object]] = []

    for number_of_traces in sizes:
        elapsed_times: List[float] = []

        for repetition in range(repetitions):
            seed = base_seed + repetition

            inputs = generate_inputs(
                number_of_traces=number_of_traces,
                trace_length=trace_length,
                seed=seed,
            )

            start_time = time.perf_counter()

            for initial_state, events in inputs:
                run_trace(
                    ORIGINAL,
                    initial_state,
                    events,
                )

                run_trace(
                    DECOMPOSED,
                    initial_state,
                    events,
                )

            elapsed_time = (
                time.perf_counter()
                - start_time
            )

            elapsed_times.append(
                elapsed_time
            )

        mean_time = statistics.mean(
            elapsed_times
        )

        standard_deviation = (
            statistics.stdev(elapsed_times)
            if len(elapsed_times) > 1
            else 0.0
        )

        rows.append(
            {
                "traces": number_of_traces,
                "trace_length": trace_length,
                "repetitions": repetitions,
                "base_seed": base_seed,
                "mean_time_s": round(
                    mean_time,
                    6,
                ),
                "sd_time_s": round(
                    standard_deviation,
                    6,
                ),
                "min_time_s": round(
                    min(elapsed_times),
                    6,
                ),
                "max_time_s": round(
                    max(elapsed_times),
                    6,
                ),
            }
        )

    return rows
