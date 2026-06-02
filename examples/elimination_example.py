# ============================================================
# DEAD RULE ELIMINATION EXAMPLE
# ============================================================

from src.rulebases import (
    ORIGINAL_WITH_DEAD_RULE,
    SAFE_ELIMINATION_RB
)

from src.semantics import (
    PreservationChecker
)


def main():

    checker = PreservationChecker(
        ORIGINAL_WITH_DEAD_RULE,
        SAFE_ELIMINATION_RB
    )

    result = checker.run(
        iterations=1000
    )

    print("\nDEAD RULE ELIMINATION")
    print("=" * 50)

    for k, v in result.items():

        if k != "divergences":
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
