# Experimental Results

## Formal Validation

| Theorem | Failures |
|----------|----------|
| Decomposition | 0 |
| Merge | 1 |

---

## Monte-Carlo Verification

| Transformation | Equivalent | Divergences | Rate |
|---------------|------------|------------|------|
| Decomposition | True | 0 | 0.0000 |
| Merge | False | 449 | 0.0898 |
| Elimination | True | 0 | 0.0000 |
| Priority Preservation | False | 508 | 0.1016 |
| Counterexample | False | 4762 | 0.9524 |

---

## Statistical Analysis

Runtime Mean:

1.592053

95% CI:

[1.470522, 1.713583]

Divergence Mean:

0.0

---

## Scalability Analysis

| Samples | Runtime (s) |
|----------|------------|
| 100 | 0.143783 |
| 500 | 0.714832 |
| 1000 | 1.391385 |
| 2000 | 2.807918 |
| 5000 | 8.335045 |
| 10000 | 15.903181 |

---

## Summary

Total Experiments:

5

Equivalent:

2

Non-equivalent:

3

---

## Generated Artifacts

Results:

- benchmark_results.csv
- theorem_results.csv
- scalability_results.csv

Figures:

- runtime_scalability.png
- divergence_rate.png
- benchmark_runtime_bar.png
- divergence_histogram.png
