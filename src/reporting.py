"""
Result reporting and artifact generation.

This module provides utilities for:

- writing tabular results to CSV files;
- writing counterexamples to JSON;
- displaying experiment summaries;
- plotting first-divergence-position distributions;
- creating the output directory structure.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------

DEFAULT_RESULTS_DIR = Path("results")

PROOF_RESULTS_FILE = "proof_obligations.csv"
BEHAVIOURAL_RESULTS_FILE = "behavioural_validation.csv"
SCALABILITY_RESULTS_FILE = "scalability.csv"
COUNTEREXAMPLES_FILE = "counterexamples.json"
DIVERGENCE_PLOT_FILE = "divergence_positions.png"


def ensure_results_directory(
    output_directory: Path | str = DEFAULT_RESULTS_DIR,
) -> Path:
    """
    Create and return the result-output directory.
    """

    output_path = Path(output_directory)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return output_path


# ---------------------------------------------------------------------------
# CSV reporting
# ---------------------------------------------------------------------------

def write_csv(
    rows: Sequence[Mapping[str, object]],
    path: Path | str,
) -> Path:
    """
    Write a sequence of dictionaries to a CSV file.

    The column order follows the first row. Additional keys found in later
    rows are appended in first-occurrence order.

    Parameters
    ----------
    rows:
        Tabular rows represented as mappings.

    path:
        Destination CSV path.

    Returns
    -------
    Path
        Written file path.
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

    fieldnames: List[str] = []

    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)

    with destination.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    return destination


# ---------------------------------------------------------------------------
# Proof-obligation reporting
# ---------------------------------------------------------------------------

def proof_results_to_rows(
    verification_results: Mapping[str, object],
) -> List[Dict[str, object]]:
    """
    Convert proof-obligation results to flat CSV rows.

    Each input value is expected to expose:

    - ``passed``;
    - ``details``.
    """

    rows: List[Dict[str, object]] = []

    for transformation, result in verification_results.items():
        details = getattr(
            result,
            "details",
            {},
        )

        row: Dict[str, object] = {
            "transformation": transformation,
            "passed": getattr(
                result,
                "passed",
                False,
            ),
        }

        for obligation, outcome in details.items():
            row[obligation] = outcome

        rows.append(row)

    return rows


def write_proof_results(
    verification_results: Mapping[str, object],
    output_directory: Path | str = DEFAULT_RESULTS_DIR,
) -> Path:
    """
    Write proof-obligation results to CSV.
    """

    output_path = ensure_results_directory(
        output_directory
    )

    rows = proof_results_to_rows(
        verification_results
    )

    return write_csv(
        rows,
        output_path / PROOF_RESULTS_FILE,
    )


# ---------------------------------------------------------------------------
# Counterexample reporting
# ---------------------------------------------------------------------------

def write_counterexamples(
    counterexamples: Mapping[
        str,
        Optional[Mapping[str, object]],
    ],
    path: Path | str,
) -> Path:
    """
    Write first counterexamples to a formatted JSON file.
    """

    destination = Path(path)
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with destination.open(
        "w",
        encoding="utf-8",
    ) as json_file:
        json.dump(
            counterexamples,
            json_file,
            indent=2,
            ensure_ascii=False,
        )

    return destination


# ---------------------------------------------------------------------------
# Divergence-position plot
# ---------------------------------------------------------------------------

def plot_divergence_positions(
    divergence_positions: Mapping[
        str,
        Sequence[int],
    ],
    path: Path | str,
) -> Optional[Path]:
    """
    Plot the frequency of first-divergence positions.

    Only transformations containing at least one divergence are included.
    A grouped bar chart is used so that distributions across negative
    controls can be compared at each trace position.

    Returns None when no divergence positions are available.
    """

    non_empty = {
        name: list(positions)
        for name, positions in divergence_positions.items()
        if positions
    }

    if not non_empty:
        return None

    destination = Path(path)
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_positions = sorted(
        {
            position
            for positions in non_empty.values()
            for position in positions
        }
    )

    transformations = list(
        non_empty.keys()
    )

    number_of_series = len(
        transformations
    )

    total_group_width = 0.8
    bar_width = (
        total_group_width
        / number_of_series
    )

    base_x = list(
        range(len(all_positions))
    )

    plt.figure(
        figsize=(10, 6)
    )

    for series_index, transformation in enumerate(
        transformations
    ):
        frequencies = [
            non_empty[transformation].count(
                position
            )
            for position in all_positions
        ]

        offset = (
            series_index
            - (number_of_series - 1) / 2
        ) * bar_width

        x_positions = [
            x + offset
            for x in base_x
        ]

        plt.bar(
            x_positions,
            frequencies,
            width=bar_width,
            label=transformation,
        )

    plt.xlabel(
        "First divergence position"
    )

    plt.ylabel(
        "Number of divergent executions"
    )

    plt.title(
        "Distribution of first divergence positions"
    )

    plt.xticks(
        base_x,
        all_positions,
    )

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        destination,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    return destination


# ---------------------------------------------------------------------------
# Console display
# ---------------------------------------------------------------------------

def _format_value(
    value: object,
) -> str:
    """
    Format a table value for console display.
    """

    if isinstance(value, bool):
        return (
            "PASS"
            if value
            else "FAIL"
        )

    if isinstance(value, float):
        return f"{value:.6f}"

    return str(value)


def show_table(
    title: str,
    rows: Sequence[Mapping[str, object]],
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

    columns: List[str] = []

    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)

    widths = {
        column: max(
            len(column),
            max(
                len(
                    _format_value(
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
                _format_value(
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
    proof_results: Mapping[str, object],
    behavioural_rows: Sequence[
        Mapping[str, object]
    ],
    scalability_rows: Sequence[
        Mapping[str, object]
    ],
) -> None:
    """
    Display all experiment summaries.
    """

    proof_rows = proof_results_to_rows(
        proof_results
    )

    show_table(
        "Proof-obligation verification",
        proof_rows,
    )

    show_table(
        "Behavioural validation",
        behavioural_rows,
    )

    show_table(
        "Scalability experiment",
        scalability_rows,
    )


# ---------------------------------------------------------------------------
# Complete artifact writing
# ---------------------------------------------------------------------------

def save_all_results(
    proof_results: Mapping[str, object],
    behavioural_rows: Sequence[
        Mapping[str, object]
    ],
    scalability_rows: Sequence[
        Mapping[str, object]
    ],
    counterexamples: Mapping[
        str,
        Optional[Mapping[str, object]],
    ],
    divergence_positions: Mapping[
        str,
        Sequence[int],
    ],
    output_directory: Path | str = DEFAULT_RESULTS_DIR,
) -> Dict[str, Optional[Path]]:
    """
    Write all generated experiment artifacts.

    Returns a dictionary containing the written paths.
    """

    output_path = ensure_results_directory(
        output_directory
    )

    proof_path = write_proof_results(
        proof_results,
        output_path,
    )

    behavioural_path = write_csv(
        behavioural_rows,
        output_path
        / BEHAVIOURAL_RESULTS_FILE,
    )

    scalability_path = write_csv(
        scalability_rows,
        output_path
        / SCALABILITY_RESULTS_FILE,
    )

    counterexample_path = write_counterexamples(
        counterexamples,
        output_path
        / COUNTEREXAMPLES_FILE,
    )

    plot_path = plot_divergence_positions(
        divergence_positions,
        output_path
        / DIVERGENCE_PLOT_FILE,
    )

    return {
        "proof_results": proof_path,
        "behavioural_results": behavioural_path,
        "scalability_results": scalability_path,
        "counterexamples": counterexample_path,
        "divergence_plot": plot_path,
    }
