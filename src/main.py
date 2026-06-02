# ============================================================
# RRAI REFACTORING VERIFICATION FRAMEWORK
# IEEE ACCESS VERSION
#
# main.py
#
# PART 7/7
# Main Program
# ============================================================

import pandas as pd

from validation import (
    TheoremExperiments,
    BenchmarkRunner
)

from analysis import (
    ComplexityAnalysis,
    StatisticalAnalysis,
    ScalabilityExperiment,
    DivergenceAnalysis
)

from reporting import (
    PaperTables,
    Exporter,
    FigureGenerator,
    SummaryReport
)

from rulebases import (
    ORIGINAL_RB,
    SAFE_DECOMPOSITION_RB,
    UNSAFE_PRIORITY_RB
)

from semantics import (
    PreservationChecker
)


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("RRAI REFACTORING VERIFICATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Formal validation
    # --------------------------------------------------------

    theorem_results = (
        TheoremExperiments.run()
    )

    # --------------------------------------------------------
    # Monte-Carlo benchmark
    # --------------------------------------------------------

    benchmark_runner = (
        BenchmarkRunner()
    )

    benchmark_results = (
        benchmark_runner.run_all()
    )

    # --------------------------------------------------------
    # Complexity analysis
    # --------------------------------------------------------

    ComplexityAnalysis.print_summary()

    # --------------------------------------------------------
    # Statistical analysis
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("STATISTICAL ANALYSIS")
    print("=" * 60)

    stats = (
        StatisticalAnalysis
        .repeated_runs(
            ORIGINAL_RB,
            SAFE_DECOMPOSITION_RB,
            repetitions=30,
            iterations=1000
        )
    )

    for k, v in stats.items():

        print(
            f"{k}: "
            f"{round(v, 6)}"
        )

    # --------------------------------------------------------
    # Scalability analysis
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("SCALABILITY ANALYSIS")
    print("=" * 60)

    scalability_result = (
        ScalabilityExperiment.run(
            ORIGINAL_RB,
            SAFE_DECOMPOSITION_RB
        )
    )

    scalability_df = pd.DataFrame({

        "Samples":
            scalability_result["sizes"],

        "Runtime":
            scalability_result["runtime"],

        "DivergenceRate":
            scalability_result[
                "divergence_rate"
            ]
    })

    print(
        scalability_df.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Paper tables
    # --------------------------------------------------------

    benchmark_df, theorem_df = (

        PaperTables.build(
            benchmark_results,
            theorem_results
        )
    )

    # --------------------------------------------------------
    # Export CSV
    # --------------------------------------------------------

    Exporter.export_benchmark(
        benchmark_results
    )

    Exporter.export_theorem(
        theorem_results
    )

    scalability_df.to_csv(
        "scalability_results.csv",
        index=False
    )

    print(
        "Saved: scalability_results.csv"
    )

    # --------------------------------------------------------
    # Figures
    # --------------------------------------------------------

    FigureGenerator.generate_all(
        benchmark_results
    )

    unsafe_checker = (
        PreservationChecker(
            ORIGINAL_RB,
            UNSAFE_PRIORITY_RB
        )
    )

    unsafe_result = (
        unsafe_checker.run(
            iterations=5000
        )
    )

    DivergenceAnalysis.histogram(

        unsafe_result[
            "divergences"
        ]
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = (
        SummaryReport.build(
            benchmark_results
        )
    )

    print("\n")
    print("=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    print(
        "Total Experiments:",
        summary["total"]
    )

    print(
        "Equivalent:",
        summary["equivalent"]
    )

    print(
        "Non-equivalent:",
        summary["non_equivalent"]
    )

    print("\n")
    print("=" * 60)
    print("EXECUTION COMPLETED")
    print("=" * 60)
