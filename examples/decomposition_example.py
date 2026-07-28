"""
Example: correctness-preserving rule decomposition.

This script verifies that rule r3 in the original rule base is safely
decomposed into r3a and r3b.

Run from the repository root:

    python examples/decomposition_example.py
"""

from __future__ import annotations

import sys
from pathlib import Path


# Allow the example to import modules from src/ when executed from
# the repository root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


from rulebases import DECOMPOSED, ORIGINAL
from validation import domain, verify_decomposition


def main() -> None:
    """
    Verify the decomposition of r3 into r3a and r3b.
    """

    verification_domain = domain(
        predicates=[
            "obstacleDetected",
            "highSpeed",
            "frontObstacle",
            "batteryLow",
        ],
        events=[
            "sensor",
            "timer",
            "watchdog",
        ],
    )

    result = verify_decomposition(
        original_rulebase=ORIGINAL,
        transformed_rulebase=DECOMPOSED,
        verification_domain=verification_domain,
        original_name="r3",
        part_names=[
            "r3a",
            "r3b",
        ],
    )

    print("Rule decomposition verification")
    print("===============================")
    print("Original rule: r3")
    print("Decomposed rules: r3a, r3b")
    print()

    for obligation, passed in result.details.items():
        status = "PASS" if passed else "FAIL"
        print(f"{obligation}: {status}")

    print()
    print(
        "Overall result:",
        "PASS" if result.passed else "FAIL",
    )


if __name__ == "__main__":
    main()
