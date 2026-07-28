# RRAI Refactoring Verification Framework

A Python framework for formally verifying correctness-preserving rule refactorings in reactive rule-based artificial intelligence systems.

This repository accompanies the paper:

> **A Calculus of Correctness-Preserving Rule Refactorings for Reactive Rule-Based Artificial Intelligence Systems**

The framework combines finite-domain proof-obligation checking with execution-based behavioural validation to verify whether rule transformations preserve observable system behaviour.

---

## Features

- Formal proof-obligation verification
  - Rule decomposition
  - Rule merging
  - Rule elimination
  - Priority adjustment

- Execution-based behavioural validation

- Automatic counterexample generation for invalid refactorings

- Scalability evaluation

---

## Repository Structure

```
.
├── src
│   ├── core.py
│   ├── semantics.py
│   ├── rulebases.py
│   ├── validation.py
│   ├── analysis.py
│   ├── reporting.py
│   └── main.py
│
├── results
│   ├── theorem_results.csv
│   ├── benchmark_results.csv
│   ├── scalability_results.csv
│   └── divergence_positions.png
│
├── requirements.txt
└── README.md
```

---

## Implemented Refactorings

### Correctness-preserving

- Rule decomposition
- Rule merging
- Rule elimination
- Priority adjustment

### Negative controls

- Unsafe decomposition
- Invalid merge
- Invalid priority adjustment

---

## Experimental Evaluation

The framework performs three experiments.

### 1. Proof-obligation verification

Finite-domain verification of the proposed correctness conditions.

Output:

```
results/theorem_results.csv
```

---

### 2. Behavioural validation

10,000 randomly generated executions are used to compare the original and transformed rule bases.

Output:

```
results/benchmark_results.csv
```

Summary

| Transformation | Divergences |
|---------------|------------:|
| Decomposition | 0 |
| Merging | 0 |
| Elimination | 0 |
| Priority adjustment | 0 |
| Invalid merge | 2466 |
| Invalid priority adjustment | 3081 |
| Unsafe decomposition | 4929 |

---

### 3. Scalability

Execution time is measured over increasing numbers of traces.

Output

```
results/scalability_results.csv
```

---

## Divergence Analysis

The repository reports where behavioural divergence first appears for incorrect refactorings.

```
results/divergence_positions.png
```

The figure shows the distribution of first-divergence positions for the three negative-control transformations.

---

## Running

Execute the complete experiment.

```bash
python src/main.py
```

or

```bash
python src/main.py \
    --traces 10000 \
    --trace-length 20 \
    --repetitions 30
```

---

## Requirements

Python 3.10+

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Citation

If you use this framework, please cite the corresponding paper.

```bibtex
@article{Trinh2026RRAI,
  title={A Calculus of Correctness-Preserving Rule Refactorings for Reactive Rule-Based Artificial Intelligence Systems},
  author={Trinh, Thanh-Binh and Ha, Nguyen Viet},
  year={2026}
}
```

---

## License

MIT License.
