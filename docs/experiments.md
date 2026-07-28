# Experimental Evaluation

## Experiment 1

Formal Validation

Purpose:

Exhaustively validate theorem conditions over constructed state spaces.

Output:

- decomposition failures
- merge failures

---

## Experiment 2
# Experimental Evaluation

## Overview

This document describes how to reproduce the experimental results
reported in the accompanying paper.

The evaluation consists of three complementary experiments.

1. Proof obligation verification
2. Behavioural validation
3. Scalability evaluation

All experiments are implemented in Python and can be executed directly
from the repository.

---

# Requirements

The experiments require

- Python 3.10 or later

Required Python packages

```
matplotlib
numpy
pandas
```

Install dependencies using

```bash
pip install -r requirements.txt
```

---

# Running All Experiments

To execute the complete evaluation, run

```bash
python src/main.py
```

Alternatively,

```bash
python examples/complete_demo.py
```

Both commands perform

- proof obligation verification;
- behavioural validation;
- scalability evaluation;
- result generation.

---

# Experiment 1: Proof Obligation Verification

This experiment checks the correctness conditions defined for each
supported refactoring theorem.

The following transformations are verified.

| Transformation | Expected Result |
|----------------|-----------------|
| Decomposition | PASS |
| Merging | PASS |
| Elimination | PASS |
| Priority Adjustment | PASS |
| Invalid Merge | FAIL |
| Invalid Priority Adjustment | FAIL |
| Unsafe Decomposition | FAIL |

The generated report is

```
results/proof_obligations.csv
```

---

# Experiment 2: Behavioural Validation

Behavioural validation compares the original and transformed rule bases
through repeated execution.

Each experiment

- generates random initial states;
- generates random event sequences;
- executes both rule bases;
- compares execution traces.

Whenever behavioural equivalence is violated, the framework records

- divergence position;
- counterexample;
- conflicting execution traces.

Typical execution parameters are

| Parameter | Value |
|-----------|------:|
| Number of traces | 10000 |
| Trace length | 20 |
| Random seed | 20260723 |

The generated report is

```
results/behavioural_results.csv
```

---

# Experiment 3: Scalability Evaluation

The scalability experiment measures the execution time required for
behavioural validation.

The framework executes increasing numbers of traces and records the
average running time.

Typical workloads include

| Number of Traces |
|-----------------:|
| 100 |
| 500 |
| 1000 |
| 2000 |
| 5000 |
| 10000 |

The generated report is

```
results/scalability_results.csv
```

---

# Generated Figures

The framework automatically generates a visualization showing where
behavioural divergence first occurs.

Generated figure

```
results/divergence_positions.png
```

This figure illustrates the distribution of the first divergence
position for each incorrect refactoring.

---

# Expected Outputs

After all experiments finish, the repository contains

```
results/

proof_obligations.csv
behavioural_results.csv
scalability_results.csv
divergence_positions.png
```

---

# Reproducibility

The framework uses a fixed random seed by default.

Consequently,

- theorem verification is deterministic;
- behavioural validation is reproducible;
- scalability measurements can be replicated under the same execution
environment.

Changing the random seed allows additional behavioural validation while
preserving the verification methodology.

---

# Notes

The reported experiments are intended to demonstrate

- correctness-preserving rule refactoring;
- automatic proof obligation checking;
- execution-based behavioural equivalence;
- scalability of the proposed verification framework.

The implementation is modular and can be extended with additional rule
transformations and verification theorems in future work.
Monte-Carlo Preservation Verification

Purpose:

Estimate behavioral equivalence over randomly generated states and traces.

Parameters:

- 5000 executions
- trace length = 20

Metrics:

- divergence count
- divergence rate
- average divergence position

---

## Experiment 3

Scalability Analysis

Sample sizes:

100
500
1000
2000
5000
10000

Metrics:

- runtime
- divergence rate

---

## Experiment 4

Statistical Analysis

30 repeated executions.

Metrics:

- mean runtime
- 95% confidence interval
- divergence confidence interval

---

## Experiment 5

Divergence Distribution

Unsafe refactorings are analyzed using

- first divergence position
- histogram visualization

---

## Complexity

Single trace execution

O(k·n)

Monte-Carlo verification

O(m·k·n)

Memory

O(k)

where

k = trace length

n = number of rules

m = number of samples
