"""
Example: counterexample generation for invalid refactorings.

This script runs execution-based behavioural validation and prints the
first detected counterexample for each negative-control transformation.

Run from the repository root:

    python examples/counterexample.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


from analysis import behavioural_validation


NEGATIVE_CONTROLS = (
    "Invalid merge",
    "Invalid priority adjustment",
    "Unsafe decomposition",
)


def main() -> None:
    """
    Generate and display sampled behavioural counterexamples
    for intentionally invalid refactorings.
    """

    (
        rows,
        counterexamples,
        divergence_positions,
    ) = behavioural_validation(
        num_traces=1_000,
        trace_length=20,
        seed=20260723,
    )

    print("Negative-control behavioural validation")
    print("=======================================")

    for row in rows:

        transformation = row["transformation"]

        if transformation not in NEGATIVE_CONTROLS:
            continue

        print()
        print(transformation)
        print("-" * len(transformation))

        print(
            f"Executions: {row['executions']}"
        )

        print(
            f"Divergences: {row['divergences']}"
        )

        print(
            "Divergence rate: "
            f"{row['rate_percent']:.2f}%"
        )

        positions = divergence_positions.get(
            transformation,
            [],
        )

        if positions:

            print(
                "First observed divergence position: "
                f"{positions[0]}"
            )

        counterexample = counterexamples.get(
            transformation
        )

        if counterexample is None:

            print(
                "No sampled counterexample found."
            )

            continue

        print(
            "First sampled counterexample:"
        )

        print(
            json.dumps(
                counterexample,
                indent=2,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
