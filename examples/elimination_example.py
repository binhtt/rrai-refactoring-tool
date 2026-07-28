"""
Example: correctness-preserving rule elimination.

This script verifies that rule r16 can be safely removed because it is
never a maximal enabled rule.

Run from the repository root:

    python examples/elimination_example.py
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


from rulebases import (
    ELIMINATED,
    ELIMINATION_ORIGINAL,
)
from validation import (
    domain,
    verify_elimination,
)


def main() -> None:
    """
    Verify safe elimination of rule r16.
    """

    verification_domain = domain(
        predicates=[
            "goalVisible",
            "narrowCorridor",
        ],
        events=[
            "sensor",
            "timer",
            "watchdog",
        ],
    )

    result = verify_elimination(
        original_rulebase=ELIMINATION_ORIGINAL,
        transformed_rulebase=ELIMINATED,
        verification_domain=verification_domain,
        rule_name="r16",
    )

    print("Rule elimination verification")
    print("=============================")
    print("Eliminated rule: r16")
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
