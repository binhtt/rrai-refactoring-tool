"""
Example: correctness-preserving priority adjustment.

This script verifies that adding the priority relation

    r6 < r4

preserves the set of maximal enabled rules over the complete finite
state-event domain.

Run from the repository root:

    python examples/priority_example.py
"""

from __future__ import annotations

import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Repository paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


# ---------------------------------------------------------------------------
# Framework imports
# ---------------------------------------------------------------------------

from rulebases import (
    ORIGINAL,
    PRIORITY_ADJUSTED,
)

from validation import (
    FULL_DOMAIN,
    verify_refactoring,
)


# ---------------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Verify the correctness-preserving priority adjustment.
    """

    result = verify_refactoring(
        ORIGINAL,
        PRIORITY_ADJUSTED,
        FULL_DOMAIN,
    )

    print("Priority adjustment verification")
    print("===============================")

    print(
        "Transformation: add r6 < r4"
    )

    print(
        f"Detected type: "
        f"{result.transformation}"
    )

    print(
        f"Verification domain: "
        f"{result.domain_size} contexts"
    )

    print(
        f"Overall result: "
        f"{result.status}"
    )

    print()

    print("Changed rules")
    print("-------------")

    print(
        "Removed:",
        ", ".join(
            result.changed_rules[
                "removed"
            ]
        )
        or "-",
    )

    print(
        "Added:",
        ", ".join(
            result.changed_rules[
                "added"
            ]
        )
        or "-",
    )

    print()

    if result.failed:

        print("Failed proof obligations")
        print("------------------------")

        for failure in result.failed:

            print(
                f"{failure.obligation}: "
                f"{failure.witness}"
            )

    else:

        print(
            "MaximalRulePreservation is satisfied "
            "over the complete finite domain."
        )

    if result.counterexample is not None:

        print()
        print("Counterexample")
        print("--------------")
        print(
            result.counterexample
        )


if __name__ == "__main__":
    main()
