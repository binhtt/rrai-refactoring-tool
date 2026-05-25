from rules import build_rules
from equivalence import check_equivalence

from examples.safe_refactoring import (
    original_specs,
    safe_specs
)

from examples.unsafe_refactoring import (
    unsafe_specs
)


def test_safe_refactoring_equivalence():

    original_rules = build_rules(
        original_specs
    )

    safe_rules = build_rules(
        safe_specs
    )

    result = check_equivalence(
        original_rules,
        safe_rules,
        iterations=100
    )

    assert result is True


def test_unsafe_refactoring_non_equivalence():

    original_rules = build_rules(
        original_specs
    )

    unsafe_rules = build_rules(
        unsafe_specs
    )

    result = check_equivalence(
        original_rules,
        unsafe_rules,
        iterations=100
    )

    assert result is False
