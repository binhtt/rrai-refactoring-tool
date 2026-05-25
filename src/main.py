# ============================================================
# RRAI REFACTORING TOOL
# ============================================================
#
# Main entry point for:
#
# 1. Loading original rules
# 2. Loading refactored rules
# 3. Generating execution traces
# 4. Checking observable equivalence
# 5. Producing counterexamples
#
# ============================================================

import random

from rules import (
    original_specs,
    safe_specs,
    unsafe_specs,
)

from semantics import build_rules

from equivalence import check_equivalence


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    random.seed(42)

    original_rules = build_rules(
        original_specs
    )

    safe_rules = build_rules(
        safe_specs
    )

    unsafe_rules = build_rules(
        unsafe_specs
    )

    print("\n================================================")
    print("RRAI REFACTORING TOOL")
    print("================================================")

    print("\n1. Load original rules")
    print("2. Load refactored rules")
    print("3. Generate traces")
    print("4. Check equivalence")
    print("5. Produce counterexamples")

    # --------------------------------------------------------
    # SAFE
    # --------------------------------------------------------

    print("\n================================================")
    print("SAFE REFACTORING")
    print("================================================")

    result_safe = check_equivalence(
        original_rules,
        safe_rules,
        iterations=10000
    )

    print("\nObservable equivalence:", result_safe)

    # --------------------------------------------------------
    # UNSAFE
    # --------------------------------------------------------

    print("\n================================================")
    print("UNSAFE REFACTORING")
    print("================================================")

    result_unsafe = check_equivalence(
        original_rules,
        unsafe_rules,
        iterations=10000
    )

    print("\nObservable equivalence:", result_unsafe)


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    main()
