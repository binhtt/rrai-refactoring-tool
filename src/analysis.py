"""
Execution-based behavioural validation and scalability experiments.

This module provides:

- deterministic generation of initial states and event sequences;
- correspondence-based behavioural validation for valid and invalid
  refactorings;
- collection of first-divergence positions;
- extraction of sampled counterexamples;
- repeated scalability experiments measuring the complete
  correspondence-based behavioural-validation procedure.

Execution-based validation complements proof-obligation checking.
It provides empirical evidence and concrete counterexamples, but it is
not treated as a formal proof of behavioural equivalence.
"""

from __future__ import annotations

from dataclasses import asdict
import random
import statistics
import time
from typing import Dict, List, Optional, Sequence, Tuple

from core import State

from rulebases import (
    DECOMPOSED,
    MERGED,
)

from semantics import (
    run_corresponding_trace_pair,
)

from validation import (
    CASES,
    EVENTS,
    PREDICATES,
    correspondence_for,
)


# ---------------------------------------------------------------------------
# Default experimental configuration
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Random input generation
# ---------------------------------------------------------------------------

def random_state(
    rng: random.Random,
) -> State:
    """
    Generate one random Boolean state.

    All state predicates are independently sampled with equal
    probabilities, except hazardFlag, which is initially False.
    """

    state = {
        predicate: bool(rng.getrandbits(1))
        for predicate in PREDICATES
    }

    state["hazardFlag"] = False

    return state


def random_events(
    rng: random.Random,
    length: int,
) -> List[str]:
    """
    Generate one random event sequence.
    """

    return [
        rng.choice(EVENTS)
        for _ in range(length)
    ]


def generate_inputs(
    number_of_traces: int,
    trace_length: int,
    seed: int,
) -> List[Tuple[State, List[str]]]:
    """
    Generate deterministic experimental inputs.

    The same collection of initial states and event sequences can be
    reused across transformation cases.
    """

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
# Behavioural validation
# ---------------------------------------------------------------------------

def behavioural_validation(
    num_traces: int = DEFAULT_TRACE_COUNT,
    trace_length: int = DEFAULT_TRACE_LENGTH,
    seed: int = DEFAULT_SEED,
):
    """
    Perform Monte-Carlo behavioural validation.

    The same sampled inputs are reused across all transformations,
    consistently with the experimental setup in the manuscript.

    At each execution position, maximal-rule choices are compared
    bidirectionally under the transformation-induced correspondence.

    Returns
    -------
    rows:
        Aggregate behavioural-validation results.

    counterexamples:
        First sampled behavioural counterexample for each transformation.

    divergence_positions:
        First-divergence positions for all divergent sampled executions.
    """

    rng = random.Random(seed)

    inputs = [
        (
            random_state(rng),
            random_events(
                rng,
                trace_length,
            ),
        )
        for _ in range(num_traces)
    ]

    rows = []
    counterexamples = {}
    divergence_positions = {}

    for (
        name,
        before,
        after,
        correspondence,
    ) in CASES:

        divergences = 0
        positions = []
        first_counterexample = None

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
                before,
                after,
                initial_state,
                events,
                correspondence,
            )

            if first_divergence is None:
                continue

            divergences += 1
            positions.append(
                first_divergence
            )

            if first_counterexample is None:
                first_counterexample = {
                    "sample": sample_index,
                    "initial_state": initial_state,
                    "events": events,
                    "divergence_position":
                        first_divergence,
                    "original_transition":
                        asdict(
                            original_trace[
                                first_divergence - 1
                            ]
                        ),
                    "transformed_transition":
                        asdict(
                            transformed_trace[
                                first_divergence - 1
                            ]
                        ),
                }

        elapsed = (
            time.perf_counter()
            - start_time
        )

        rows.append(
            {
                "transformation":
                    name,
                "executions":
                    num_traces,
                "divergences":
                    divergences,
                "rate_percent":
                    round(
                        100
                        * divergences
                        / num_traces,
                        4,
                    ),
                "elapsed_s":
                    round(
                        elapsed,
                        6,
                    ),
            }
        )

        counterexamples[
            name
        ] = first_counterexample

        divergence_positions[
            name
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
):
    """
    Measure the complete correspondence-based behavioural-validation
    procedure.

    The timed region invokes run_corresponding_trace_pair for the valid
    decomposition MERGED -> DECOMPOSED.

    Each timed run therefore includes:

    - rule enabling;
    - maximal-rule computation;
    - bidirectional correspondence checking;
    - action and successor-state comparison;
    - deterministic continuation of the sampled trace.

    Input generation is intentionally performed outside the timed region.

    Only the number of sampled traces varies; the rule-base structure and
    trace length remain fixed.

    Returns
    -------
    aggregate_rows:
        Mean, standard deviation, minimum, and maximum execution times
        for each trace-count configuration.

    raw_rows:
        One row for every timing repetition. With six trace-count settings
        and 30 repetitions, this contains 180 rows.
    """

    correspondence = correspondence_for(
        MERGED,
        DECOMPOSED,
    )

    aggregate_rows = []
    raw_rows = []

    for number_of_traces in sizes:

        elapsed_times = []

        for repetition in range(
            repetitions
        ):

            seed = (
                base_seed
                + repetition
            )

            rng = random.Random(
                seed
            )

            inputs = [
                (
                    random_state(rng),
                    random_events(
                        rng,
                        trace_length,
                    ),
                )
                for _ in range(
                    number_of_traces
                )
            ]

            # Input generation above is intentionally excluded
            # from the measured region.
            start_time = time.perf_counter()

            divergences = 0

            for state, events in inputs:

                (
                    _,
                    _,
                    first_divergence,
                ) = run_corresponding_trace_pair(
                    MERGED,
                    DECOMPOSED,
                    state,
                    events,
                    correspondence,
                )

                if (
                    first_divergence
                    is not None
                ):
                    divergences += 1

            elapsed = (
                time.perf_counter()
                - start_time
            )

            # The scalability benchmark uses a preservation-valid
            # transformation. Any divergence therefore indicates
            # an implementation error.
            if divergences != 0:
                raise AssertionError(
                    "Valid decomposition diverged "
                    "in scalability run: "
                    f"{divergences}"
                )

            elapsed_times.append(
                elapsed
            )

            raw_rows.append(
                {
                    "traces":
                        number_of_traces,
                    "trace_length":
                        trace_length,
                    "repetition":
                        repetition + 1,
                    "seed":
                        seed,
                    "elapsed_s":
                        round(
                            elapsed,
                            9,
                        ),
                }
            )

        aggregate_rows.append(
            {
                "traces":
                    number_of_traces,
                "trace_length":
                    trace_length,
                "repetitions":
                    repetitions,
                "mean_time_s":
                    round(
                        statistics.mean(
                            elapsed_times
                        ),
                        6,
                    ),
                "sd_time_s":
                    round(
                        statistics.stdev(
                            elapsed_times
                        )
                        if len(
                            elapsed_times
                        ) > 1
                        else 0.0,
                        6,
                    ),
                "min_time_s":
                    round(
                        min(
                            elapsed_times
                        ),
                        6,
                    ),
                "max_time_s":
                    round(
                        max(
                            elapsed_times
                        ),
                        6,
                    ),
                "measured_operation":
                    (
                        "full_correspondence_based_"
                        "behavioural_validation"
                    ),
            }
        )

    return (
        aggregate_rows,
        raw_rows,
    )
