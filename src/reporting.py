# ============================================================
# RRAI REFACTORING VERIFICATION FRAMEWORK
# IEEE ACCESS VERSION
#
# reporting.py
#
# PART 6/7
# Result Tables
# Visualization
# Data Export
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt

from analysis import (
    ScalabilityExperiment
)

from rulebases import (
    ORIGINAL_RB,
    SAFE_DECOMPOSITION_RB
)


# ============================================================
# RESULT TABLE GENERATOR
# ============================================================

class ResultTableGenerator:

    @staticmethod
    def benchmark_table(
        benchmark_results
    ):

        rows = []

        for name, result in benchmark_results.items():

            rows.append({

                "Transformation":
                    name,

                "Equivalent":
                    result["equivalent"],

                "Divergences":
                    result["divergence_count"],

                "Rate":
                    round(
                        result["divergence_rate"],
                        6
                    ),

                "Runtime":
                    round(
                        result["execution_time"],
                        6
                    )
            })

        return pd.DataFrame(rows)

    @staticmethod
    def theorem_table(
        theorem_results
    ):

        rows = [

            {
                "Lemma":
                    "Decomposition",

                "Failures":
                    theorem_results[
                        "decomposition"
                    ]
            },

            {
                "Lemma":
                    "Merge",

                "Failures":
                    theorem_results[
                        "merge"
                    ]
            }
        ]

        return pd.DataFrame(rows)


# ============================================================
# VISUALIZATION
# ============================================================

class Visualization:

    @staticmethod
    def runtime_scalability(
        scalability_result,
        title="Runtime Scalability"
    ):

        plt.figure(
            figsize=(8, 5)
        )

        plt.plot(

            scalability_result["sizes"],

            scalability_result["runtime"],

            marker="o"
        )

        plt.xlabel(
            "Monte-Carlo Samples"
        )

        plt.ylabel(
            "Execution Time (s)"
        )

        plt.title(
            title
        )

        plt.grid(True)

        plt.tight_layout()

        plt.show()

    @staticmethod
    def divergence_rate(
        scalability_result,
        title="Divergence Rate"
    ):

        plt.figure(
            figsize=(8, 5)
        )

        plt.plot(

            scalability_result["sizes"],

            scalability_result["divergence_rate"],

            marker="o"
        )

        plt.xlabel(
            "Monte-Carlo Samples"
        )

        plt.ylabel(
            "Divergence Rate"
        )

        plt.title(
            title
        )

        plt.grid(True)

        plt.tight_layout()

        plt.show()

    @staticmethod
    def benchmark_runtime_bar(
        benchmark_results
    ):

        names = list(
            benchmark_results.keys()
        )

        runtimes = [

            benchmark_results[k]
            ["execution_time"]

            for k in names
        ]

        plt.figure(
            figsize=(10, 5)
        )

        plt.bar(
            names,
            runtimes
        )

        plt.xticks(
            rotation=20
        )

        plt.ylabel(
            "Runtime (s)"
        )

        plt.title(
            "Benchmark Runtime Comparison"
        )

        plt.tight_layout()

        plt.show()


# ============================================================
# CSV EXPORT
# ============================================================

class Exporter:

    @staticmethod
    def export_dataframe(
        df,
        filename
    ):

        df.to_csv(
            filename,
            index=False
        )

        print(
            "Saved:",
            filename
        )

    @staticmethod
    def export_benchmark(
        benchmark_results,
        filename=
        "benchmark_results.csv"
    ):

        df = (

            ResultTableGenerator
            .benchmark_table(
                benchmark_results
            )
        )

        Exporter.export_dataframe(
            df,
            filename
        )

    @staticmethod
    def export_theorem(
        theorem_results,
        filename=
        "theorem_results.csv"
    ):

        df = (

            ResultTableGenerator
            .theorem_table(
                theorem_results
            )
        )

        Exporter.export_dataframe(
            df,
            filename
        )


# ============================================================
# PAPER TABLE BUILDER
# ============================================================

class PaperTables:

    @staticmethod
    def build(
        benchmark_results,
        theorem_results
    ):

        benchmark_df = (

            ResultTableGenerator
            .benchmark_table(
                benchmark_results
            )
        )

        theorem_df = (

            ResultTableGenerator
            .theorem_table(
                theorem_results
            )
        )

        print("\n")
        print("=" * 60)
        print("TABLE I")
        print("MONTE-CARLO VERIFICATION")
        print("=" * 60)

        print(
            benchmark_df.to_string(
                index=False
            )
        )

        print("\n")
        print("=" * 60)
        print("TABLE II")
        print("FORMAL VALIDATION")
        print("=" * 60)

        print(
            theorem_df.to_string(
                index=False
            )
        )

        return (

            benchmark_df,
            theorem_df
        )


# ============================================================
# FIGURE GENERATOR
# ============================================================

class FigureGenerator:

    @staticmethod
    def generate_all(
        benchmark_results
    ):

        safe_scalability = (

            ScalabilityExperiment.run(
                ORIGINAL_RB,
                SAFE_DECOMPOSITION_RB
            )
        )

        Visualization.runtime_scalability(
            safe_scalability,
            "Safe Refactoring Runtime"
        )

        Visualization.divergence_rate(
            safe_scalability,
            "Safe Refactoring Divergence Rate"
        )

        Visualization.benchmark_runtime_bar(
            benchmark_results
        )


# ============================================================
# SUMMARY REPORT
# ============================================================

class SummaryReport:

    @staticmethod
    def build(
        benchmark_results
    ):

        total = len(
            benchmark_results
        )

        equivalent = sum(

            1

            for r in
            benchmark_results.values()

            if r["equivalent"]
        )

        non_equivalent = (
            total - equivalent
        )

        return {

            "total":
                total,

            "equivalent":
                equivalent,

            "non_equivalent":
                non_equivalent
        }


# ============================================================
# SANITY TEST
# ============================================================

if __name__ == "__main__":

    print("PART 6 OK")
