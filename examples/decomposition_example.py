"""
Example: correctness-preserving rule decomposition.

This script verifies the decomposition

    r3 -> {r3a, r3b}

using the end-to-end refactoring verifier over the complete finite
state-event domain.

Run from the repository root:

    python examples/decomposition_example.py
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
    DECOMPOSED,
    MERGED,
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
    Verify the decomposition of r3 into r3a and r3b.
    """

    result = verify_refactoring(
        MERGED,
        DECOMPOSED,
        FULL_DOMAIN,
    )

    print("Rule decomposition verification")
    print("===============================")

    print(
        "Transformation:"
        " r3 -> {r3a, r3b}"
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

    for original, transformed in sorted(
        result.correspondence
    ):
        if original == "r3":
            print(
                f"({original}, "
                f"{transformed})"
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
            "All applicable decomposition "
            "proof obligations are satisfied."
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
