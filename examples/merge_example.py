"""
Example: correctness-preserving rule merging.

This script verifies the cardinality-changing merge

    r11, r4 -> r15

using the end-to-end refactoring verifier over the complete finite
state-event domain.

Run from the repository root:

    python examples/merge_example.py
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
    MERGED,
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
    Verify the merging of r11 and r4 into the single rule r15.
    """

    result = verify_refactoring(
        PRIORITY_ADJUSTED,
        MERGED,
        FULL_DOMAIN,
    )

    print("Rule merging verification")
    print("=========================")

    print(
        "Transformation: r11, r4 -> r15"
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

    print("Rule correspondence")
    print("-------------------")

    relevant_pairs = {
        ("r11", "r15"),
        ("r4", "r15"),
    }

    for pair in sorted(
        result.correspondence
    ):

        if pair in relevant_pairs:

            print(
                f"({pair[0]}, "
                f"{pair[1]})"
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
            "All applicable merge proof "
            "obligations are satisfied."
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
