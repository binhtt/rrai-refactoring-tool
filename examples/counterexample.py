# ============================================================
# UNSAFE REFACTORING COUNTEREXAMPLE
# ============================================================

from src.rulebases import (
    ORIGINAL_RB,
    UNSAFE_PRIORITY_RB
)

from src.semantics import (
    PreservationChecker
)

from src.analysis import (
    DivergenceAnalysis
)


def main():

    checker = PreservationChecker(
        ORIGINAL_RB,
        UNSAFE_PRIORITY_RB
    )

    result = checker.run(
        iterations=5000
    )

    print("\nCOUNTEREXAMPLE")
    print("=" * 50)

    for k, v in result.items():

        if k != "divergences":
            print(f"{k}: {v}")

    print("\nDIVERGENCE SUMMARY")
    print("=" * 50)

    summary = DivergenceAnalysis.summary(
        result["divergences"]
    )

    for k, v in summary.items():
        print(f"{k}: {v}")

    DivergenceAnalysis.histogram(
        result["divergences"]
    )


if __name__ == "__main__":
    main()
