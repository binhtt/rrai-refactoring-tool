import random

from rules import build_rules
from equivalence import check_equivalence
from utils import banner

from examples.safe_refactoring import (
    original_specs,
    safe_specs
)

from examples.unsafe_refactoring import (
    unsafe_specs
)


if __name__ == "__main__":

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

    banner("RRAI REFACTORING TOOL")

    banner("SAFE REFACTORING")

    result_safe = check_equivalence(
        original_rules,
        safe_rules
    )

    print(
        "\nObservable equivalence:",
        result_safe
    )

    banner("UNSAFE REFACTORING")

    result_unsafe = check_equivalence(
        original_rules,
        unsafe_rules
    )

    print(
        "\nObservable equivalence:",
        result_unsafe
    )
