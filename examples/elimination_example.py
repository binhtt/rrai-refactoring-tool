"""
Example: correctness-preserving rule elimination.

This script verifies that rule r16 can be safely removed because it is
never a maximal enabled rule.

The verification uses the end-to-end refactoring verifier over the
complete finite state-event domain.

Run from the repository root:

    python examples/elimination_example.py
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
    ELIMINATED,
    ELIMINATION_ORIGINAL,
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
    Verify safe elimination of rule r16.
    """

    result = verify_refactoring(
        ELIMINATION_ORIGINAL,
        ELIMINATED,
        FULL_DOMAIN,
    )

    print("Rule elimination verification")
    print("=============================")

    print(
        "Transformation: remove r16"
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
            "The elimination condition is satisfied: "
            "r16 is never a maximal enabled rule "
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
