# ============================================================
# RRAI REFACTORING VERIFICATION FRAMEWORK
# IEEE ACCESS VERSION
#
# analysis.py
#
# PART 5/7
# Scalability Analysis
# Statistical Analysis
# Divergence Analysis
# ============================================================

import numpy as np
import matplotlib.pyplot as plt

from semantics import PreservationChecker

from rulebases import (
    ORIGINAL_RB,
    SAFE_DECOMPOSITION_RB,
    UNSAFE_PRIORITY_RB,
    EXPERIMENT_SIZES
)


# ============================================================
# SCALABILITY EXPERIMENT
# ============================================================

class ScalabilityExperiment:

    @staticmethod
    def run(
        original_rb,
        refactored_rb,
        sizes=EXPERIMENT_SIZES
    ):

        runtimes = []

        divergence_rates = []

        for n in sizes:

            checker = PreservationChecker(
                original_rb,
                refactored_rb
            )

            result = checker.run(
                iterations=n
            )

            runtimes.append(
                result["execution_time"]
            )

            divergence_rates.append(
                result["divergence_rate"]
            )

        return {

            "sizes":
                sizes,

            "runtime":
                runtimes,

            "divergence_rate":
                divergence_rates
        }


# ============================================================
# STATISTICAL ANALYSIS
# ============================================================

class StatisticalAnalysis:

    @staticmethod
    def confidence_interval(
        values
    ):

        values = np.array(values)

        mean = np.mean(values)

        if len(values) <= 1:

            return (
                mean,
                mean,
                mean
            )

        std = np.std(
            values,
            ddof=1
        )

        margin = (

            1.96

            * std

            / np.sqrt(
                len(values)
            )
        )

        return (

            mean,

            mean - margin,

            mean + margin
        )

    @staticmethod
    def repeated_runs(
        rb1,
        rb2,
        repetitions=30,
        iterations=1000
    ):

        runtimes = []

        divergences = []

        for _ in range(repetitions):

            checker = PreservationChecker(
                rb1,
                rb2
            )

            result = checker.run(
                iterations=iterations
            )

            runtimes.append(
                result["execution_time"]
            )

            divergences.append(
                result["divergence_count"]
            )

        runtime_stats = (

            StatisticalAnalysis
            .confidence_interval(
                runtimes
            )
        )

        divergence_stats = (

            StatisticalAnalysis
            .confidence_interval(
                divergences
            )
        )

        return {

            "runtime_mean":
                runtime_stats[0],

            "runtime_ci_low":
                runtime_stats[1],

            "runtime_ci_high":
                runtime_stats[2],

            "div_mean":
                divergence_stats[0],

            "div_ci_low":
                divergence_stats[1],

            "div_ci_high":
                divergence_stats[2]
        }


# ============================================================
# DIVERGENCE ANALYSIS
# ============================================================

class DivergenceAnalysis:

    @staticmethod
    def summary(
        divergences
    ):

        if len(divergences) == 0:

            return {

                "mean": 0,

                "median": 0,

                "min": 0,

                "max": 0
            }

        return {

            "mean":
                float(
                    np.mean(
                        divergences
                    )
                ),

            "median":
                float(
                    np.median(
                        divergences
                    )
                ),

            "min":
                int(
                    np.min(
                        divergences
                    )
                ),

            "max":
                int(
                    np.max(
                        divergences
                    )
                )
        }

    @staticmethod
    def histogram(
        divergences
    ):

        if len(divergences) == 0:

            print(
                "No divergences detected."
            )

            return

        plt.figure(
            figsize=(7, 5)
        )

        plt.hist(
            divergences,
            bins=20
        )

        plt.xlabel(
            "First Divergence Position"
        )

        plt.ylabel(
            "Frequency"
        )

        plt.title(
            "Distribution of Divergence Positions"
        )

        plt.grid(True)

        plt.tight_layout()

        plt.show()


# ============================================================
# COMPLEXITY ANALYSIS
# ============================================================

class ComplexityAnalysis:

    @staticmethod
    def print_summary():

        print("\n")
        print("=" * 60)
        print("THEORETICAL COMPLEXITY")
        print("=" * 60)

        print()

        print(
            "Single Trace Execution:"
        )

        print(
            "O(k * n)"
        )

        print()

        print(
            "Monte-Carlo Verification:"
        )

        print(
            "O(m * k * n)"
        )

        print()

        print(
            "Memory Complexity:"
        )

        print(
            "O(k)"
        )

        print()

        print(
            "where"
        )

        print(
            "k = trace length"
        )

        print(
            "n = number of rules"
        )

        print(
            "m = Monte-Carlo samples"
        )


# ============================================================
# RUNTIME GROWTH EXPERIMENT
# ============================================================

class RuntimeGrowthExperiment:

    @staticmethod
    def compare():

        safe_result = (

            ScalabilityExperiment.run(
                ORIGINAL_RB,
                SAFE_DECOMPOSITION_RB
            )
        )

        unsafe_result = (

            ScalabilityExperiment.run(
                ORIGINAL_RB,
                UNSAFE_PRIORITY_RB
            )
        )

        return {

            "safe":
                safe_result,

            "unsafe":
                unsafe_result
        }


# ============================================================
# SANITY TEST
# ============================================================

if __name__ == "__main__":

    print("PART 5 OK")
