# ============================================================
# DECOMPOSITION EXAMPLE
# ============================================================

from src.rulebases import (
    ORIGINAL_RB,
    SAFE_DECOMPOSITION_RB
)

from src.semantics import (
    PreservationChecker
)


def main():

    checker = PreservationChecker(
        ORIGINAL_RB,
        SAFE_DECOMPOSITION_RB
    )

    result = checker.run(
        iterations=1000
    )

    print("\nSAFE DECOMPOSITION")
    print("=" * 50)

    for k, v in result.items():

        if k != "divergences":
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
