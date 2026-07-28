"""
Example: correctness-preserving priority adjustment.

This script verifies that the added priority relation preserves the set of
maximal enabled rules over the finite verification domain.

Run from the repository root:

    python examples/priority_example.py
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


from rulebases import ORIGINAL, PRIORITY_ADJUSTED
from validation import domain, verify_priority


def main() -> None:
    """
    Verify the correctness-preserving priority adjustment.
    """

    verification_domain = domain(
        predicates=[
            "goalVisible",
            "idle",
            "narrowCorridor",
        ],
        events=[
            "sensor",
            "timer",
            "watchdog",
        ],
    )

    result = verify_priority(
        before=ORIGINAL,
        after=PRIORITY_ADJUSTED,
        verification_domain=verification_domain,
    )

    print("Priority adjustment verification")
    print("===============================")
    print("Added priority relation: r6 < r4")
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
