# RRAI Refactoring Tool

Prototype implementation for analysing correctness-preserving refactorings in Reactive Rule-Based AI (RRAI) systems.

---

## Overview

This repository provides a research prototype for:

- Reactive Rule-Based AI (RRAI) semantics
- Observable trace generation
- Rule refactoring operators
- Observable trace equivalence checking
- Counterexample generation
- Experimental scalability evaluation

The implementation follows the observable operational semantics defined in the accompanying research work on correctness-preserving refactorings for reactive rule-based AI systems.

---

# Features

- Labelled transition semantics
- Observable trace semantics
- Priority-based rule execution
- Safe vs unsafe refactoring analysis
- Observable equivalence checking
- Counterexample extraction
- Randomized execution testing
- Scalability benchmarking

---

# Semantic Model

The current implementation follows an observable operational semantics for RRAI systems.

In particular:

- idle executions are represented using τ-actions,
- observable traces are generated from labelled transitions,
- rule identifiers are preserved only at semantic-transition level,
- observable equivalence is evaluated over observable traces,
- repeated τ-transitions are intentionally retained to preserve operational behaviour during execution analysis.

The repository is intended as a research prototype for experimental evaluation and reproducibility.

---

# Repository Structure

```text
rrai-refactoring-tool/
│
├── README.md
├── requirements.txt
├── LICENSE
│
├── src/
│   ├── main.py
│   ├── semantics.py
│   ├── observable.py
│   ├── refactoring.py
│   ├── equivalence.py
│   ├── rules.py
│   ├── simulator.py
│   └── utils.py
│
├── examples/
│   ├── safe_refactoring.py
│   ├── unsafe_refactoring.py
│   └── robot_navigation.py
│
├── experiments/
│   ├── scalability.py
│   ├── benchmark.py
│   └── results/
│
├── tests/
│   ├── test_semantics.py
│   ├── test_equivalence.py
│   └── test_refactoring.py
│
└── docs/
    ├── semantics.md
    ├── observable_equivalence.md
    └── refactoring_rules.md
```

---

# Installation

```bash
git clone https://github.com/binhtt/rrai-refactoring-tool.git
cd rrai-refactoring-tool
pip install -r requirements.txt
```

---

# Requirements

```text
Python >= 3.10
numpy
pytest
```

---

# Running the Tool

```bash
python src/main.py
```

---

# Example Output

## Safe Refactoring

```text
================================================
SAFE REFACTORING
================================================

Observable equivalence: True
```

## Unsafe Refactoring

```text
================================================
COUNTEREXAMPLE FOUND
================================================

Initial state:
{...}

Events:
['sensor', 'timer', 'watchdog']

Observable equivalence: False
```

---

# Refactoring Operators

Currently supported transformations:

- Rule extraction
- Rule merging
- Dead rule elimination
- Condition simplification
- Priority restructuring

---

# Experimental Evaluation

The repository includes:

- scalability experiments,
- randomized rule generation,
- equivalence benchmarks,
- execution time analysis.

Run experiments:

```bash
python experiments/scalability.py
```

---

# Example Workflow

## Run verification

```bash
python src/main.py
```

## Run tests

```bash
pytest tests/
```

## Run scalability benchmark

```bash
python experiments/scalability.py
```

---


---

# License

MIT License

---

# Authors

- Thanh-Binh Trinh
- Contributors and collaborators

---
