# RRAI Refactoring Verification Framework

A research framework for verifying correctness-preserving refactorings in Reactive Rule-Based AI (RRAI) systems.

This repository accompanies our work on formal verification of rule-based AI refactorings using observable trace semantics, theorem-driven validation, and Monte-Carlo behavioral equivalence checking.

---

# Overview

Reactive Rule-Based AI systems are frequently refactored to improve maintainability, modularity, and performance. However, refactorings may unintentionally alter system behavior.

This framework provides:

- Formal operational semantics for RRAI systems
- Observable trace semantics
- Behavioral equivalence checking
- Correctness-preserving refactoring validation
- Monte-Carlo preservation verification
- Scalability and statistical analysis
- Experimental evaluation of safe and unsafe transformations

---

# Framework Architecture

The framework is organized into seven modules.

```text
src/
├── core.py
├── semantics.py
├── rulebases.py
├── validation.py
├── analysis.py
├── reporting.py
└── main.py
```

## Module Responsibilities

### core.py

Core semantic structures:

- Rule
- TraceStep
- TransitionSystem
- RuleBase
- Random state generation

---

### semantics.py

Execution semantics:

- ExecutionEngine
- TraceExecutor
- TraceEquivalence
- PreservationChecker

---

### rulebases.py

Benchmark rule systems:

- Original rule base
- Safe decomposition
- Safe merge
- Dead-rule elimination
- Priority-preserving transformations
- Unsafe counterexample

---

### validation.py

Formal verification:

- FormalValidator
- TheoremDrivenTests
- BenchmarkRunner
- TheoremExperiments

---

### analysis.py

Experimental evaluation:

- ScalabilityExperiment
- StatisticalAnalysis
- DivergenceAnalysis
- ComplexityAnalysis

---

### reporting.py

Reporting and visualization:

- Result tables
- Figure generation
- CSV export
- Summary reports

---

### main.py

End-to-end experimental pipeline.

---

# Formal Semantics

The framework follows an observable operational semantics.

A rule is represented as:

R = (event, guard, action, priority)

Execution semantics:

(s,e) → (s',a)

where

- s is the current state
- e is the triggering event
- a is the selected action
- s' is the successor state

Conflict resolution is priority-based.

Observable traces are projected onto:

(event, action)

pairs.

Two executions are behaviorally equivalent iff their observable traces are identical.

---

# Supported Refactorings

The framework evaluates the following transformations.

## Lemma 1

Safe Decomposition

A rule may be split into multiple rules if:

- guards form a partition
- action remains unchanged
- priority remains unchanged

Expected result:

Equivalent = True

---

## Lemma 2

Rule Merge

Rules are merged using guard disjunction.

Expected result:

May preserve or violate behavior depending on actions and priorities.

---

## Lemma 3

Dead Rule Elimination

Removes rules that can never fire.

Expected result:

Equivalent = True

---

## Lemma 4

Priority Preservation

Behavior is preserved only if maximal enabled rule ordering remains unchanged.

Expected result:

Equivalent only under strict ordering preservation.

---

## Counterexample

Unsafe priority modifications intentionally alter behavior.

Expected result:

Equivalent = False

---

# Repository Structure

```text
RRAI-Refactoring-Verification/
│
├── README.md
├── LICENSE
├── requirements.txt
│
├── src/
│   ├── core.py
│   ├── semantics.py
│   ├── rulebases.py
│   ├── validation.py
│   ├── analysis.py
│   ├── reporting.py
│   └── main.py
│
├── results/
│   ├── benchmark_results.csv
│   ├── theorem_results.csv
│   ├── scalability_results.csv
│   ├── runtime_scalability.png
│   ├── divergence_rate.png
│   ├── benchmark_runtime_bar.png
│   └── divergence_histogram.png
│
├── docs/
│   ├── architecture.md
│   ├── semantics.md
│   ├── refactoring_theorems.md
│   ├── experiments.md
│   └── results.md
│
└── examples/
    ├── decomposition_example.py
    ├── merge_example.py
    ├── elimination_example.py
    ├── priority_example.py
    └── counterexample.py
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/binhtt/rrai-refactoring-tool.git
cd rrai-refactoring-tool
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Requirements

```text
Python >= 3.10

numpy
pandas
matplotlib
```

---

# Running the Framework

Execute the complete experimental pipeline:

```bash
python src/main.py
```

This performs:

1. Formal validation
2. Monte-Carlo verification
3. Statistical analysis
4. Scalability analysis
5. Table generation
6. Figure generation
7. CSV export

---

# Example Output

```text
============================================================
FORMAL VALIDATION
============================================================

Decomposition Failures: 0
Merge Failures: 1

============================================================
Lemma 1: Decomposition
============================================================

Equivalent: True
Divergences: 0
```

---

# Experimental Evaluation

The framework includes:

## Formal Validation

Exhaustive theorem-driven verification.

---

## Monte-Carlo Verification

Randomized behavioral equivalence checking.

---

## Statistical Analysis

Repeated execution with confidence intervals.

---

## Scalability Analysis

Sample sizes:

100
500
1000
2000
5000
10000

---

## Divergence Analysis

Detection and visualization of behavioral differences.

---

# Generated Results

Running the framework produces:

```text
results/

benchmark_results.csv
theorem_results.csv
scalability_results.csv

runtime_scalability.png
divergence_rate.png
benchmark_runtime_bar.png
divergence_histogram.png
```

---

# Complexity

Single Trace Execution

O(k · n)

Monte-Carlo Verification

O(m · k · n)

Memory Complexity

O(k)

where

- k = trace length
- n = number of rules
- m = Monte-Carlo samples

---

# Reproducibility

All experiments use a fixed random seed:

```python
GLOBAL_SEED = 42
```

ensuring deterministic reproduction of published results.

---

# License

MIT License

---

# Authors

Thanh-Binh Trinh

Research on correctness-preserving refactoring verification for Reactive Rule-Based AI systems.
