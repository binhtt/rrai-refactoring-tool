# RRAI Refactoring Verification Framework

A Python framework for formally verifying correctness-preserving rule refactorings in reactive rule-based artificial intelligence systems.

This repository accompanies the paper:

> **A Calculus of Correctness-Preserving Rule Refactorings for Reactive Rule-Based Artificial Intelligence Systems**

The framework combines finite-domain proof-obligation verification with execution-based behavioural validation to determine whether rule transformations preserve observable system behaviour.

---

## Features

- Formal proof-obligation verification
  - Rule decomposition
  - Rule merging
  - Rule elimination
  - Priority adjustment

- Execution-based behavioural validation using Monte Carlo simulation

- Automatic counterexample generation for invalid refactorings

- Scalability evaluation

- Automatic generation of CSV reports and visualization

---

## Repository Structure

```text
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
├── examples
│   ├── decomposition_example.py
│   ├── merge_example.py
│   ├── elimination_example.py
│   ├── priority_example.py
│   ├── counterexample.py
│   └── complete_demo.py
│
├── docs
│   ├── architecture.md
│   ├── semantics.md
│   ├── refactoring_theorems.md
│   ├── experiments.md
│   └── results.md
│
├── results
│   ├── proof_obligations.csv
│   ├── behavioural_results.csv
│   ├── scalability_results.csv
│   └── divergence_positions.png
│
├── requirements.txt
└── README.md
```

---

## Implemented Refactorings

### Correctness-Preserving Refactorings

- Rule decomposition
- Rule merging
- Rule elimination
- Priority adjustment

### Negative Controls

- Unsafe decomposition
- Invalid merge
- Invalid priority adjustment

---

## Experimental Evaluation

The framework performs three complementary experiments.

### 1. Proof-Obligation Verification

The proposed correctness conditions are verified over a finite verification domain.

Output

```text
results/proof_obligations.csv
```

Expected results

| Transformation | Result |
|---------------|--------|
| Decomposition | PASS |
| Merging | PASS |
| Elimination | PASS |
| Priority Adjustment | PASS |
| Invalid Merge | FAIL |
| Invalid Priority Adjustment | FAIL |
| Unsafe Decomposition | FAIL |

---

### 2. Behavioural Validation

The framework executes 10,000 randomly generated traces to compare the behaviour of the original and transformed rule bases.

Output

```text
results/behavioural_results.csv
```

Typical results

| Transformation | Divergences |
|---------------|------------:|
| Decomposition | 0 |
| Merging | 0 |
| Elimination | 0 |
| Priority Adjustment | 0 |
| Invalid Merge | 2466 |
| Invalid Priority Adjustment | 3081 |
| Unsafe Decomposition | 4929 |

---

### 3. Scalability Evaluation

Execution time is measured for increasing numbers of execution traces.

Output

```text
results/scalability_results.csv
```

Typical workloads

- 100 traces
- 500 traces
- 1,000 traces
- 2,000 traces
- 5,000 traces
- 10,000 traces

---

## Divergence Analysis

The framework automatically generates

```text
results/divergence_positions.png
```

The figure illustrates the distribution of the first behavioural divergence for each negative-control refactoring.

Correctness-preserving refactorings should produce no divergence.

---

## Running the Framework

Run the complete experimental evaluation

```bash
python src/main.py
```

or execute the demonstration

```bash
python examples/complete_demo.py
```

---

## Requirements

- Python 3.10 or later

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Documentation

Additional documentation is available in the `docs/` directory.

- `architecture.md` — framework architecture
- `semantics.md` — operational semantics
- `refactoring_theorems.md` — correctness-preserving refactorings
- `experiments.md` — experimental methodology
- `results.md` — interpretation of generated results

---

## Citation

If you use this framework in your research, please cite the accompanying paper.

```bibtex
@article{Trinh2026,
  author  = {Thanh-Binh Trinh and Van Cuong Nguyen and Nguyen Viet Ha},
  title   = {A Calculus of Correctness-Preserving Rule Refactorings for Reactive Rule-Based Artificial Intelligence Systems},
  year    = {2026},
  note    = {Preprint}
}
```

> **Note:** Please update the citation with the journal name, volume, pages, and DOI once the paper is officially published.

---

## License

This project is released under the MIT License.
