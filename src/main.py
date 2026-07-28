"""
Command-line entry point for the
RRAI Refactoring Verification Framework.

The program performs:

1. finite-domain proof-obligation verification;
2. execution-based behavioural validation;
3. scalability measurement;
4. CSV, JSON, and PNG artifact generation;
5. console result display.

Example
-------
Run the complete experiment:

    python src/main.py

Run a smaller validation experiment:

    python src/main.py \
        --traces 1000 \
        --trace-length 20 \
        --repetitions 5

Skip the scalability experiment:

    python src/main.py --skip-scalability
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from analysis import (
    DEFAULT_REPETITIONS,
    DEFAULT_SCALABILITY_SIZES,
    DEFAULT_SEED,
    DEFAULT_TRACE_COUNT,
    DEFAULT_TRACE_LENGTH,
    behavioural_validation,
    scalability,
)
from reporting import (
    DEFAULT_RESULTS_DIR,
    save_all_results,
    show_results,
)
from validation import proof_obligations


# ---------------------------------------------------------------------------
# Command-line arguments
# ---------------------------------------------------------------------------

def positive_integer(value: str) -> int:
    """
    Parse a strictly positive integer.
    """

    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Expected an integer, received: {value}"
        ) from exc

    if parsed_value <= 0:
        raise argparse.ArgumentTypeError(
            "The value must be greater than zero"
        )

    return parsed_value


def non_negative_integer(value: str) -> int:
    """
    Parse a non-negative integer.
    """

    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Expected an integer, received: {value}"
        ) from exc

    if parsed_value < 0:
        raise argparse.ArgumentTypeError(
            "The value must be non-negative"
        )

    return parsed_value


def parse_scalability_sizes(
    value: str,
) -> tuple[int, ...]:
    """
    Parse comma-separated scalability trace counts.

    Example
    -------
    ``100,500,1000,5000``
    """

    try:
        sizes = tuple(
            int(item.strip())
            for item in value.split(",")
            if item.strip()
        )
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Scalability sizes must be comma-separated integers"
        ) from exc

    if not sizes:
        raise argparse.ArgumentTypeError(
            "At least one scalability size is required"
        )

    if any(size <= 0 for size in sizes):
        raise argparse.ArgumentTypeError(
            "Every scalability size must be greater than zero"
        )

    return sizes


def build_argument_parser() -> argparse.ArgumentParser:
    """
    Construct the command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Verify correctness-preserving rule refactorings "
            "for reactive rule-based AI systems."
        )
    )

    parser.add_argument(
        "--traces",
        type=positive_integer,
        default=DEFAULT_TRACE_COUNT,
        help=(
            "Number of sampled traces per behavioural case "
            f"(default: {DEFAULT_TRACE_COUNT})"
        ),
    )

    parser.add_argument(
        "--trace-length",
        type=positive_integer,
        default=DEFAULT_TRACE_LENGTH,
        help=(
            "Number of events in each sampled trace "
            f"(default: {DEFAULT_TRACE_LENGTH})"
        ),
    )

    parser.add_argument(
        "--seed",
        type=non_negative_integer,
        default=DEFAULT_SEED,
        help=(
            "Deterministic random seed "
            f"(default: {DEFAULT_SEED})"
        ),
    )

    parser.add_argument(
        "--repetitions",
        type=positive_integer,
        default=DEFAULT_REPETITIONS,
        help=(
            "Number of repetitions for each scalability setting "
            f"(default: {DEFAULT_REPETITIONS})"
        ),
    )

    parser.add_argument(
        "--scalability-sizes",
        type=parse_scalability_sizes,
        default=DEFAULT_SCALABILITY_SIZES,
        help=(
            "Comma-separated trace counts used in the scalability "
            "experiment, for example 100,500,1000,5000"
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help=(
            "Directory used for generated CSV, JSON, and PNG files "
            f"(default: {DEFAULT_RESULTS_DIR})"
        ),
    )

    parser.add_argument(
        "--skip-behavioural",
        action="store_true",
        help="Skip execution-based behavioural validation",
    )

    parser.add_argument(
        "--skip-scalability",
        action="store_true",
        help="Skip the scalability experiment",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Do not display result tables in the terminal",
    )

    return parser


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def print_artifact_paths(
    artifact_paths: dict[str, Path | None],
) -> None:
    """
    Print generated artifact paths.
    """

    print()
    print("Generated artifacts")
    print("===================")

    for artifact_name, artifact_path in artifact_paths.items():
        display_name = artifact_name.replace(
            "_",
            " ",
        ).title()

        if artifact_path is None:
            print(
                f"{display_name}: not generated"
            )
        else:
            print(
                f"{display_name}: "
                f"{artifact_path.resolve()}"
            )


def run(
    argv: Sequence[str] | None = None,
) -> int:
    """
    Run the complete verification and experimentation workflow.

    Parameters
    ----------
    argv:
        Optional argument sequence. When None, command-line arguments
        are read from ``sys.argv``.

    Returns
    -------
    int
        Process exit code.
    """

    parser = build_argument_parser()
    arguments = parser.parse_args(argv)

    print(
        "Running finite-domain proof-obligation verification..."
    )

    proof_results = proof_obligations()

    behavioural_rows = []
    counterexamples = {}
    divergence_positions = {}

    if arguments.skip_behavioural:
        print(
            "Behavioural validation skipped."
        )
    else:
        print(
            "Running execution-based behavioural validation "
            f"with {arguments.traces} traces per case..."
        )

        (
            behavioural_rows,
            counterexamples,
            divergence_positions,
        ) = behavioural_validation(
            number_of_traces=arguments.traces,
            trace_length=arguments.trace_length,
            seed=arguments.seed,
        )

    scalability_rows = []

    if arguments.skip_scalability:
        print(
            "Scalability experiment skipped."
        )
    else:
        print(
            "Running scalability experiment "
            f"with {arguments.repetitions} repetitions..."
        )

        scalability_rows = scalability(
            sizes=arguments.scalability_sizes,
            trace_length=arguments.trace_length,
            repetitions=arguments.repetitions,
            base_seed=arguments.seed,
        )

    artifact_paths = save_all_results(
        proof_results=proof_results,
        behavioural_rows=behavioural_rows,
        scalability_rows=scalability_rows,
        counterexamples=counterexamples,
        divergence_positions=divergence_positions,
        output_directory=arguments.output,
    )

    if not arguments.quiet:
        show_results(
            proof_results=proof_results,
            behavioural_rows=behavioural_rows,
            scalability_rows=scalability_rows,
        )

        print_artifact_paths(
            artifact_paths
        )

    valid_cases = {
        "Decomposition",
        "Merging",
        "Elimination",
        "Priority adjustment",
    }

    invalid_cases = {
        "Invalid merge",
        "Invalid priority adjustment",
        "Unsafe decomposition",
    }

    valid_checks_passed = all(
        proof_results[name].passed
        for name in valid_cases
    )

    negative_controls_rejected = all(
        not proof_results[name].passed
        for name in invalid_cases
    )

    if (
        valid_checks_passed
        and negative_controls_rejected
    ):
        print()
        print(
            "Verification completed successfully."
        )
        return 0

    print()
    print(
        "Verification completed, but one or more expected "
        "proof-obligation outcomes were not obtained."
    )

    return 1


def main() -> None:
    """
    Program entry point.
    """

    try:
        exit_code = run()
    except KeyboardInterrupt:
        print(
            "\nExecution interrupted by the user.",
            file=sys.stderr,
        )
        exit_code = 130
    except Exception as exc:
        print(
            f"\nExecution failed: {exc}",
            file=sys.stderr,
        )
        exit_code = 1

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
