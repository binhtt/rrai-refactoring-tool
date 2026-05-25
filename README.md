# RRAI Refactoring Tool

Formal verification framework for correctness-preserving refactorings in Reactive Rule-Based AI (RRAI) systems.

---

## Overview

This repository provides a prototype implementation for:

- Reactive Rule-Based AI (RRAI) semantics
- Observable trace generation
- Rule refactoring operators
- Observable trace equivalence checking
- Counterexample generation
- Experimental scalability evaluation

The implementation accompanies the paper:

> *A Calculus of Correctness-Preserving Refactorings for Reactive Rule-Based AI Systems*

---

# Features

- Labelled transition semantics
- Observable trace semantics
- Priority-based rule execution
- Refactoring correctness checking
- Safe vs unsafe transformation analysis
- Counterexample extraction
- Randomized execution testing
- Scalability benchmarking

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
├── docs/
│   ├── semantics.md
│   ├── observable_equivalence.md
│   └── refactoring_rules.md
│
└── paper/
    └── einformatica.pdf
```

---


```

---

# Installation

```bash
git clone https://github.com/yourname/rrai-refactoring-tool.git
cd rrai-refactoring-tool
pip install -r requirements.txt
```

---

# Requirements

```text
Python >= 3.10
z3-solver
numpy
networkx
matplotlib
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

- scalability experiments
- randomized rule generation
- equivalence benchmarks
- execution time analysis

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

# Suggested GitHub Topics

```text
formal-methods
rule-based-systems
reactive-systems
event-b
trace-equivalence
software-refactoring
runtime-verification
model-checking
ai-systems
```

---

# Citation

```bibtex
@article{trinh2026rrai,
  title={A Calculus of Correctness-Preserving Refactorings for Reactive Rule-Based AI Systems},
  author={Trinh, Thanh-Binh and others},
  journal={e-Informatica Software Engineering Journal},
  year={2026}
}
```

---

# License

MIT License

---

# Authors

- Thanh-Binh Trinh
- Collaborators and contributors

---

