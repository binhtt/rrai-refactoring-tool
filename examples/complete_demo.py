"""
Complete demonstration of the
RRAI Refactoring Verification Framework.

This example executes:

1. complete finite-domain proof-obligation verification;
2. correspondence-based behavioural validation;
3. scalability evaluation of complete behavioural validation;
4. generation of reproducible experimental artifacts.

Run from the repository root:

    python examples/complete_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Repository paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"
RESULTS_DIRECTORY = PROJECT_ROOT / "results"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


# ---------------------------------------------------------------------------
# Framework imports
# ---------------------------------------------------------------------------

from analysis import (
    DEFAULT_REPETITIONS,
    DEFAULT_SCALABILITY_SIZES,
    DEFAULT_SEED,
    DEFAULT_TRACE_COUNT,
    DEFAULT_TRACE_LENGTH,
    behavioural_validation,
    scalability,
)

from reporting import (
    save_all_results,
)

from validation import (
    proof_obligations,
)


# ---------------------------------------------------------------------------
# Complete demonstration
# ---------------------------------------------------------------------------

def main() -> None:

    print("=" * 70)
    print(
        "RRAI Refactoring Verification Framework"
    )
    print("=" * 70)

    # ------------------------------------------------------------
    # 1. Proof-obligation verification
    # ------------------------------------------------------------

    print(
        "\n[1] Complete finite-domain "
        "proof-obligation verification"
    )

    proof_results = proof_obligations()

    for name, result in proof_results.items():

        failed = "; ".join(
            dict.fromkeys(
                failure.obligation
                for failure in result.failed
            )
        )

        print(
            f"{name:<35}"
            f"{result.status:<8}"
            f"domain={result.domain_size:<8}"
            f"{failed}"
        )

    # ------------------------------------------------------------
    # 2. Behavioural validation
    # ------------------------------------------------------------

    print(
        "\n[2] Correspondence-based "
        "behavioural validation"
    )

    (
        behavioural_rows,
        sampled_counterexamples,
        divergence_positions,
    ) = behavioural_validation(
        num_traces=DEFAULT_TRACE_COUNT,
        trace_length=DEFAULT_TRACE_LENGTH,
        seed=DEFAULT_SEED,
    )

    for row in behavioural_rows:

        print(
            f"{row['transformation']:<35}"
            f"{row['divergences']:>5} divergences "
            f"({row['rate_percent']:>6.2f}%)"
        )

    # ------------------------------------------------------------
    # 3. Scalability evaluation
    # ------------------------------------------------------------

    print(
        "\n[3] Complete correspondence-based "
        "behavioural-validation scalability"
    )

    (
        scalability_rows,
        scalability_run_rows,
    ) = scalability(
        sizes=DEFAULT_SCALABILITY_SIZES,
        trace_length=DEFAULT_TRACE_LENGTH,
        repetitions=DEFAULT_REPETITIONS,
        base_seed=DEFAULT_SEED,
    )

    for row in scalability_rows:

        print(
            f"{row['traces']:>6} traces "
            f"-> "
            f"{row['mean_time_s']:.6f} "
            f"+/- "
            f"{row['sd_time_s']:.6f} s"
        )

    # ------------------------------------------------------------
    # 4. Save reproducible outputs
    # ------------------------------------------------------------

    print(
        "\n[4] Writing reproducible artifacts"
    )

    generated = save_all_results(
        checks=proof_results,
        behavioural_rows=behavioural_rows,
        sampled_counterexamples=
            sampled_counterexamples,
        divergence_positions=
            divergence_positions,
        scalability_rows=
            scalability_rows,
        scalability_run_rows=
            scalability_run_rows,
        num_traces=
            DEFAULT_TRACE_COUNT,
        trace_length=
            DEFAULT_TRACE_LENGTH,
        seed=
            DEFAULT_SEED,
        scalability_sizes=
            DEFAULT_SCALABILITY_SIZES,
        scalability_repetitions=
            DEFAULT_REPETITIONS,
        output_directory=
            RESULTS_DIRECTORY,
    )

    print(
        "\nGenerated files:"
    )

    for name, path in generated.items():
        print(
            f" - {name}: {path}"
        )

    # ------------------------------------------------------------
    # 5. Expected verification outcomes
    # ------------------------------------------------------------

    valid_cases = {
        "Decomposition",
        "Merging",
        "Elimination",
        "Priority adjustment",
    }

    invalid_cases = {
        "Invalid merge",
        "Invalid priority adjustment",
        "Unsafe decomposition",
    }

    valid_ok = all(
        proof_results[
            name
        ].status == "Pass"
        for name in valid_cases
    )

    invalid_ok = all(
        proof_results[
            name
        ].status == "Fail"
        for name in invalid_cases
    )

    print()

    if valid_ok and invalid_ok:

        print(
            "Complete demonstration finished "
            "with the expected verification outcomes."
        )

    else:

        print(
            "Warning: one or more verification "
            "outcomes differ from the expected results."
        )

    print(
        f"\nResults directory: "
        f"{RESULTS_DIRECTORY.resolve()}"
    )


if __name__ == "__main__":
    main()
