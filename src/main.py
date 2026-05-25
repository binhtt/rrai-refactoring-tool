from rules import (
    original_specs,
    safe_specs,
    unsafe_specs,
    build_rules
)

from equivalence import check_equivalence

import random


if __name__ == "__main__":

    random.seed(42)

    original_rules = build_rules(original_specs)

    safe_rules = build_rules(safe_specs)

    unsafe_rules = build_rules(unsafe_specs)

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
