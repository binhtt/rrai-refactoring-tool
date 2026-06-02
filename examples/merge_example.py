# ============================================================
# MERGE EXAMPLE
# ============================================================

from src.rulebases import (
    ORIGINAL_RB,
    SAFE_MERGE_RB
)

from src.semantics import (
    PreservationChecker
)


def main():

    checker = PreservationChecker(
        ORIGINAL_RB,
        SAFE_MERGE_RB
    )

    result = checker.run(
        iterations=1000
    )

    print("\nMERGE EXAMPLE")
    print("=" * 50)

    for k, v in result.items():

        if k != "divergences":
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
