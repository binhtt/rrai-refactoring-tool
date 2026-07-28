"""
Example: correctness-preserving rule merging.

This script verifies that rules r11 and r4 are safely represented by
r15_sensor and r15_timer in the merged rule base.

Run from the repository root:

    python examples/merge_example.py
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


from rulebases import MERGED, PRIORITY_ADJUSTED
from validation import domain, verify_merge


def main() -> None:
    """
    Verify the merging of r11 and r4.
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

    result = verify_merge(
        original_rulebase=PRIORITY_ADJUSTED,
        transformed_rulebase=MERGED,
        verification_domain=verification_domain,
        original_names=[
            "r11",
            "r4",
        ],
        merged_names=[
            "r15_sensor",
            "r15_timer",
        ],
    )

    print("Rule merging verification")
    print("=========================")
    print("Original rules: r11, r4")
    print("Merged representation: r15_sensor, r15_timer")
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
