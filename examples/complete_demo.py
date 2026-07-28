"""
Complete demonstration of the RRAI refactoring verification framework.

This example executes

1. Proof obligation verification
2. Behavioural validation
3. Scalability evaluation

Run:

    python examples/complete_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))


from analysis import (
    behavioural_validation,
    scalability,
)
from reporting import (
    save_behavioural_results,
    save_proof_results,
    save_scalability_results,
    plot_divergence_positions,
)
from validation import proof_obligations


def main():

    print("=" * 70)
    print("Reactive Rule-Based AI Refactoring Verification Framework")
    print("=" * 70)

    print("\n[1] Proof obligation verification")
    proof_results = proof_obligations()

    for result in proof_results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{result.name:<35} {status}")

    print("\n[2] Behavioural validation")

    behavioural_results, counterexamples, divergence_positions = (
        behavioural_validation(
            number_of_traces=10000,
            trace_length=20,
            seed=20260723,
        )
    )

    for row in behavioural_results:
        print(
            f"{row['transformation']:<35}"
            f"{row['rate_percent']:6.2f}% divergence"
        )

    print("\n[3] Scalability evaluation")

    scalability_results = scalability()

    for row in scalability_results:
        print(
            f"{row['traces']:>6} traces"
            f" -> {row['mean_seconds']:.3f} s"
        )

    print("\nSaving results...")

    save_proof_results(proof_results)

    save_behavioural_results(behavioural_results)

    save_scalability_results(scalability_results)

    plot_divergence_positions(divergence_positions)

    print("\nDone.")

    print("\nResults written to results/ directory.")


if __name__ == "__main__":
    main()
