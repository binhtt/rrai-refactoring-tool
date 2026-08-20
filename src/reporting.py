"""
Result reporting and reproducible artifact generation.

This module provides utilities for:

- writing tabular results to CSV files;
- writing structured results and counterexamples to JSON;
- generating manuscript-ready Tables 2--6;
- plotting Figure 3;
- recording experimental metadata;
- displaying generated outputs in Colab/Jupyter;
- maintaining a single consistent set of artifact filenames.
"""

from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Set, Tuple

import matplotlib.pyplot as plt

from core import VerificationResult

from rulebases import (
    DECOMPOSED,
    MERGED,
    ORIGINAL,
    PRIORITY_ADJUSTED,
)

from validation import (
    EVENTS,
    FULL_DOMAIN,
    PREDICATES,
    proof_obligations,
    verify_refactoring,
)


# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------

DEFAULT_RESULTS_DIR = Path("results")

PROOF_RESULTS_FILE = "proof_obligations.csv"
ALGORITHM_RESULTS_FILE = "algorithm_results.json"

BEHAVIOURAL_RESULTS_FILE = "behavioural_validation.csv"

COUNTEREXAMPLES_FILE = "counterexamples.json"
DIVERGENCE_POSITIONS_FILE = "divergence_positions.json"

FIGURE3_PNG_FILE = "figure3_divergence_positions.png"
FIGURE3_PDF_FILE = "figure3_divergence_positions.pdf"

SCALABILITY_RESULTS_FILE = "scalability.csv"
SCALABILITY_RUNS_FILE = "scalability_runs.csv"

TABLE2_FILE = "table2_structural_changes.csv"
TABLE3_FILE = "table3_valid_transformations.csv"
TABLE4_FILE = "table4_invalid_transformations.csv"
TABLE5_FILE = "table5_counterexamples.csv"
TABLE6_FILE = "table6_scalability.csv"

MAIN_SEQUENCE_FILE = "main_sequence.json"
EXPERIMENT_METADATA_FILE = "experiment_metadata.json"


# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------

def ensure_results_directory(
    output_directory: Path | str = DEFAULT_RESULTS_DIR,
) -> Path:
    """
    Create and return the result-output directory.
    """

    output_path = Path(
        output_directory
    )

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return output_path


# ---------------------------------------------------------------------------
# CSV / JSON helpers
# ---------------------------------------------------------------------------

def write_csv(
    path: Path | str,
    rows: Sequence[Mapping[str, object]],
) -> Path:
    """
    Write a sequence of dictionaries to CSV.

    Column order follows the first row.
    """

    destination = Path(path)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not rows:
        destination.write_text(
            "",
            encoding="utf-8",
        )
        return destination

    fieldnames = list(
        rows[0].keys()
    )

    with destination.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    return destination


def write_json(
    path: Path | str,
    data: object,
) -> Path:
    """
    Write JSON data using deterministic formatted output.
    """

    destination = Path(path)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        json.dumps(
            data,
            indent=2,
        ),
        encoding="utf-8",
    )

    return destination


# ---------------------------------------------------------------------------
# Algorithm-1 proof-obligation reporting
# ---------------------------------------------------------------------------

def proof_results_to_rows(
    verification_results: Mapping[
        str,
        VerificationResult,
    ],
) -> List[dict]:
    """
    Convert Algorithm-1 results into proof_obligations.csv rows.
    """

    rows = []

    for name, result in verification_results.items():

        obligations = []

        for failure in result.failed:
            if (
                failure.obligation
                not in obligations
            ):
                obligations.append(
                    failure.obligation
                )

        rows.append(
            {
                "transformation":
                    name,
                "detected_type":
                    result.transformation,
                "status":
                    result.status,
                "domain_size":
                    result.domain_size,
                "failed_obligations":
                    "; ".join(
                        obligations
                    ),
                "counterexample_found":
                    (
                        result.counterexample
                        is not None
                    ),
            }
        )

    return rows


def algorithm_results_to_json(
    verification_results: Mapping[
        str,
        VerificationResult,
    ],
) -> Dict[str, dict]:
    """
    Convert complete Algorithm-1 results to JSON-serializable form.
    """

    return {
        name: result.to_jsonable()
        for name, result
        in verification_results.items()
    }


# ---------------------------------------------------------------------------
# Figure 3
# ---------------------------------------------------------------------------

def plot_divergence_positions(
    divergence_positions: Mapping[
        str,
        Sequence[int],
    ],
    trace_length: int = 20,
    output_directory: Path | str = DEFAULT_RESULTS_DIR,
) -> Path:
    """
    Plot the distribution of first-divergence positions for the three
    intentionally invalid transformations.

    Both PNG and PDF versions are generated.
    """

    output_path = ensure_results_directory(
        output_directory
    )

    invalid_cases = [
        "Invalid merge",
        "Invalid priority adjustment",
        "Unsafe decomposition",
    ]

    positions = list(
        range(
            1,
            trace_length + 1,
        )
    )

    plt.figure(
        figsize=(8, 5)
    )

    for name in invalid_cases:

        counts = Counter(
            divergence_positions.get(
                name,
                [],
            )
        )

        frequencies = [
            counts.get(
                position,
                0,
            )
            for position in positions
        ]

        plt.plot(
            positions,
            frequencies,
            marker="o",
            linewidth=1.8,
            label=name,
        )

    plt.xlabel(
        "First-divergence position"
    )

    plt.ylabel(
        "Number of divergent executions"
    )

    plt.xticks(
        positions
    )

    plt.legend()

    plt.grid(
        True,
        linestyle="--",
        alpha=0.3,
    )

    plt.tight_layout()

    png_path = (
        output_path
        / FIGURE3_PNG_FILE
    )

    pdf_path = (
        output_path
        / FIGURE3_PDF_FILE
    )

    plt.savefig(
        png_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.savefig(
        pdf_path,
        bbox_inches="tight",
    )

    plt.close()

    return png_path


# ---------------------------------------------------------------------------
# Table 2
# ---------------------------------------------------------------------------

def structural_summary() -> List[dict]:
    """
    Table-2-ready structural summary of the sequential refactoring.
    """

    return [
        {
            "stage":
                "Original",
            "rules":
                len(ORIGINAL.rules),
            "priority_relations":
                len(ORIGINAL.priority),
            "structural_change":
                "-",
            "formal_basis":
                "-",
        },
        {
            "stage":
                "Priority adjustment",
            "rules":
                len(
                    PRIORITY_ADJUSTED.rules
                ),
            "priority_relations":
                len(
                    PRIORITY_ADJUSTED.priority
                ),
            "structural_change":
                "Add r6 < r4",
            "formal_basis":
                "Lemma 4",
        },
        {
            "stage":
                "Merging",
            "rules":
                len(MERGED.rules),
            "priority_relations":
                len(MERGED.priority),
            "structural_change":
                "r11,r4 -> r15",
            "formal_basis":
                "Lemma 2",
        },
        {
            "stage":
                "Decomposition",
            "rules":
                len(DECOMPOSED.rules),
            "priority_relations":
                len(DECOMPOSED.priority),
            "structural_change":
                "r3 -> {r3a,r3b}",
            "formal_basis":
                "Lemma 1",
        },
    ]


# ---------------------------------------------------------------------------
# Sequential correspondence / Theorem 2 support
# ---------------------------------------------------------------------------

def compose_correspondence(
    left: Set[Tuple[str, str]],
    right: Set[Tuple[str, str]],
) -> Set[Tuple[str, str]]:
    """
    Relational composition used by Theorem 2.
    """

    return {
        (first, third)
        for first, middle1 in left
        for middle2, third in right
        if middle1 == middle2
    }


def main_sequence_summary() -> dict:
    """
    Machine-check the three preservation-valid stages reported in Table 2.
    """

    result1 = verify_refactoring(
        ORIGINAL,
        PRIORITY_ADJUSTED,
        FULL_DOMAIN,
    )

    result2 = verify_refactoring(
        PRIORITY_ADJUSTED,
        MERGED,
        FULL_DOMAIN,
    )

    result3 = verify_refactoring(
        MERGED,
        DECOMPOSED,
        FULL_DOMAIN,
    )

    composed = compose_correspondence(
        compose_correspondence(
            result1.correspondence,
            result2.correspondence,
        ),
        result3.correspondence,
    )

    return {
        "all_stages_pass":
            all(
                result.status == "Pass"
                for result in (
                    result1,
                    result2,
                    result3,
                )
            ),
        "stage_status": [
            result1.status,
            result2.status,
            result3.status,
        ],
        "composed_correspondence":
            sorted(
                [
                    list(pair)
                    for pair in composed
                ]
            ),
    }


# ---------------------------------------------------------------------------
# Table 3--5 helpers
# ---------------------------------------------------------------------------

OBLIGATION_CODES = {
    "PriorityCompatibility":
        "PC",
    "MaximalRulePreservation":
        "MRP",
    "GuardPartition":
        "GP",
    "ActionPreservation":
        "AP",
    "PriorityInheritance":
        "PI",
    "MergeGuards":
        "MG",
    "CommonAction":
        "CA",
    "EliminationCondition":
        "EC",
    "FramePreservation":
        "FP",
    "WellFormedness":
        "WF",
}


def failed_codes(
    result: VerificationResult,
) -> str:
    """
    Return abbreviated unique failed-obligation names.
    """

    obligations = []

    for failure in result.failed:

        if (
            failure.obligation
            not in obligations
        ):
            obligations.append(
                failure.obligation
            )

    return ", ".join(
        OBLIGATION_CODES.get(
            obligation,
            obligation,
        )
        for obligation in obligations
    )


def build_table3(
    checks: Mapping[
        str,
        VerificationResult,
    ],
    behavioural_rows: Sequence[
        Mapping[str, object]
    ],
) -> List[dict]:
    """
    Build manuscript Table 3.
    """

    behavioural_by_name = {
        row["transformation"]: row
        for row in behavioural_rows
    }

    valid_names = [
        "Decomposition",
        "Merging",
        "Elimination",
        "Priority adjustment",
    ]

    return [
        {
            "transformation":
                name,
            "proof_obligation_result":
                checks[name].status,
            "divergences":
                behavioural_by_name[
                    name
                ]["divergences"],
            "rate_percent":
                behavioural_by_name[
                    name
                ]["rate_percent"],
        }
        for name in valid_names
    ]


def build_table4(
    checks: Mapping[
        str,
        VerificationResult,
    ],
    behavioural_rows: Sequence[
        Mapping[str, object]
    ],
) -> List[dict]:
    """
    Build manuscript Table 4.
    """

    behavioural_by_name = {
        row["transformation"]: row
        for row in behavioural_rows
    }

    invalid_names = [
        "Invalid merge",
        "Invalid priority adjustment",
        "Unsafe decomposition",
    ]

    return [
        {
            "transformation":
                name,
            "failed_proof_obligations":
                failed_codes(
                    checks[name]
                ),
            "divergences":
                behavioural_by_name[
                    name
                ]["divergences"],
            "rate_percent":
                behavioural_by_name[
                    name
                ]["rate_percent"],
        }
        for name in invalid_names
    ]


def build_table5(
    checks: Mapping[
        str,
        VerificationResult,
    ],
) -> List[dict]:
    """
    Build manuscript Table 5.
    """

    invalid_names = [
        "Invalid merge",
        "Invalid priority adjustment",
        "Unsafe decomposition",
    ]

    return [
        {
            "transformation":
                name,
            "proof_obligations":
                checks[name].status,
            "violated_condition":
                "; ".join(
                    dict.fromkeys(
                        failure.obligation
                        for failure
                        in checks[name].failed
                    )
                ),
            "counterexample":
                (
                    "Found"
                    if checks[
                        name
                    ].counterexample
                    else "None"
                ),
        }
        for name in invalid_names
    ]


# ---------------------------------------------------------------------------
# Complete artifact output
# ---------------------------------------------------------------------------

def save_all_results(
    checks: Mapping[
        str,
        VerificationResult,
    ],
    behavioural_rows: Sequence[
        Mapping[str, object]
    ],
    sampled_counterexamples: Mapping[
        str,
        object,
    ],
    divergence_positions: Mapping[
        str,
        Sequence[int],
    ],
    scalability_rows: Sequence[
        Mapping[str, object]
    ],
    scalability_run_rows: Sequence[
        Mapping[str, object]
    ],
    num_traces: int,
    trace_length: int,
    seed: int,
    scalability_sizes: Sequence[int],
    scalability_repetitions: int,
    output_directory: Path | str = DEFAULT_RESULTS_DIR,
) -> Dict[str, Path]:
    """
    Write every file required to reproduce the manuscript tables
    and Figure 3.
    """

    output_path = ensure_results_directory(
        output_directory
    )

    generated: Dict[
        str,
        Path,
    ] = {}

    # ------------------------------------------------------------
    # Algorithm 1
    # ------------------------------------------------------------

    proof_rows = proof_results_to_rows(
        checks
    )

    generated[
        "proof_obligations"
    ] = write_csv(
        output_path
        / PROOF_RESULTS_FILE,
        proof_rows,
    )

    generated[
        "algorithm_results"
    ] = write_json(
        output_path
        / ALGORITHM_RESULTS_FILE,
        algorithm_results_to_json(
            checks
        ),
    )

    # ------------------------------------------------------------
    # Behavioural validation
    # ------------------------------------------------------------

    generated[
        "behavioural_validation"
    ] = write_csv(
        output_path
        / BEHAVIOURAL_RESULTS_FILE,
        behavioural_rows,
    )

    combined_counterexamples = {
        name: {
            "algorithm1_counterexample":
                checks[
                    name
                ].counterexample,
            "sampled_counterexample":
                sampled_counterexamples.get(
                    name
                ),
        }
        for name in checks
    }

    generated[
        "counterexamples"
    ] = write_json(
        output_path
        / COUNTEREXAMPLES_FILE,
        combined_counterexamples,
    )

    generated[
        "divergence_positions"
    ] = write_json(
        output_path
        / DIVERGENCE_POSITIONS_FILE,
        divergence_positions,
    )

    generated[
        "figure3"
    ] = plot_divergence_positions(
        divergence_positions,
        trace_length=
            trace_length,
        output_directory=
            output_path,
    )

    generated[
        "figure3_pdf"
    ] = (
        output_path
        / FIGURE3_PDF_FILE
    )

    # ------------------------------------------------------------
    # Scalability
    # ------------------------------------------------------------

    generated[
        "scalability"
    ] = write_csv(
        output_path
        / SCALABILITY_RESULTS_FILE,
        scalability_rows,
    )

    generated[
        "scalability_runs"
    ] = write_csv(
        output_path
        / SCALABILITY_RUNS_FILE,
        scalability_run_rows,
    )

    # ------------------------------------------------------------
    # Manuscript tables
    # ------------------------------------------------------------

    table2 = structural_summary()

    generated[
        "table2"
    ] = write_csv(
        output_path
        / TABLE2_FILE,
        table2,
    )

    table3 = build_table3(
        checks,
        behavioural_rows,
    )

    generated[
        "table3"
    ] = write_csv(
        output_path
        / TABLE3_FILE,
        table3,
    )

    table4 = build_table4(
        checks,
        behavioural_rows,
    )

    generated[
        "table4"
    ] = write_csv(
        output_path
        / TABLE4_FILE,
        table4,
    )

    table5 = build_table5(
        checks
    )

    generated[
        "table5"
    ] = write_csv(
        output_path
        / TABLE5_FILE,
        table5,
    )

    # Table 6 directly uses the aggregate scalability rows.
    generated[
        "table6"
    ] = write_csv(
        output_path
        / TABLE6_FILE,
        scalability_rows,
    )

    # ------------------------------------------------------------
    # Sequential preservation
    # ------------------------------------------------------------

    generated[
        "main_sequence"
    ] = write_json(
        output_path
        / MAIN_SEQUENCE_FILE,
        main_sequence_summary(),
    )

    # ------------------------------------------------------------
    # Reproducibility metadata
    # ------------------------------------------------------------

    metadata = {
        "verification_domain": {
            "state_predicates":
                list(PREDICATES),
            "events":
                list(EVENTS),
            "states":
                2 ** len(PREDICATES),
            "contexts":
                len(FULL_DOMAIN),
            "kind":
                "complete_S_cross_E",
        },
        "behavioural_validation": {
            "num_traces":
                num_traces,
            "trace_length":
                trace_length,
            "seed":
                seed,
        },
        "scalability": {
            "sizes":
                list(
                    scalability_sizes
                ),
            "repetitions":
                scalability_repetitions,
            "measured_operation":
                (
                    "full_correspondence_based_"
                    "behavioural_validation"
                ),
            "input_generation_timed":
                False,
        },
        "figure3":
            str(
                output_path
                / FIGURE3_PNG_FILE
            ),
    }

    generated[
        "experiment_metadata"
    ] = write_json(
        output_path
        / EXPERIMENT_METADATA_FILE,
        metadata,
    )

    return generated


# ---------------------------------------------------------------------------
# Console display
# ---------------------------------------------------------------------------

def show_table(
    title: str,
    rows: Sequence[
        Mapping[str, object]
    ],
) -> None:
    """
    Print rows as a compact text table.
    """

    print()
    print(title)
    print("=" * len(title))

    if not rows:
        print("No results.")
        return

    columns = list(
        rows[0].keys()
    )

    widths = {
        column: max(
            len(column),
            max(
                len(
                    str(
                        row.get(
                            column,
                            "",
                        )
                    )
                )
                for row in rows
            ),
        )
        for column in columns
    }

    header = " | ".join(
        column.ljust(
            widths[column]
        )
        for column in columns
    )

    separator = "-+-".join(
        "-" * widths[column]
        for column in columns
    )

    print(header)
    print(separator)

    for row in rows:

        print(
            " | ".join(
                str(
                    row.get(
                        column,
                        "",
                    )
                ).ljust(
                    widths[column]
                )
                for column in columns
            )
        )


def show_results(
    output_directory: Path | str = DEFAULT_RESULTS_DIR,
) -> None:
    """
    Colab/Jupyter preview of every manuscript-facing output,
    including Figure 3.
    """

    output_path = Path(
        output_directory
    )

    try:
        import pandas as pd
        from IPython.display import (
            Image,
            display,
        )

        csv_files = [
            TABLE2_FILE,
            PROOF_RESULTS_FILE,
            TABLE3_FILE,
            TABLE4_FILE,
            TABLE5_FILE,
            TABLE6_FILE,
            BEHAVIOURAL_RESULTS_FILE,
            SCALABILITY_RUNS_FILE,
        ]

        for filename in csv_files:

            path = (
                output_path
                / filename
            )

            if path.exists():

                print(
                    "\n"
                    + "=" * 70
                )

                print(
                    filename
                )

                print(
                    "=" * 70
                )

                display(
                    pd.read_csv(
                        path
                    )
                )

        figure = (
            output_path
            / FIGURE3_PNG_FILE
        )

        if figure.exists():

            print(
                "\n"
                + "=" * 70
            )

            print(
                "Figure 3: "
                "first-divergence-position "
                "distribution"
            )

            print(
                "=" * 70
            )

            display(
                Image(
                    filename=
                        str(
                            figure
                        )
                )
            )

        print(
            "\nGenerated artifact files:"
        )

        for path in sorted(
            output_path.iterdir()
        ):
            print(
                " -",
                path.name,
            )

    except Exception as exc:
        print(
            "Result preview skipped:",
            exc,
        )
