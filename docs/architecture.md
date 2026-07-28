# RRAI Refactoring Verification Framework Architecture

## Overview

The RRAI Refactoring Verification Framework is a lightweight Python
implementation for verifying correctness-preserving rule refactorings in
reactive rule-based artificial intelligence systems.

The framework provides three complementary capabilities:

- verification of proof obligations for each refactoring theorem;
- execution-based behavioural validation through Monte Carlo simulation;
- scalability evaluation of the verification process.

The implementation follows a modular architecture in which each component
has a single responsibility.

---

## Repository Structure

```
rrai-refactoring-tool/

├── src/
│   ├── core.py
│   ├── semantics.py
│   ├── rulebases.py
│   ├── validation.py
│   ├── analysis.py
│   ├── reporting.py
│   └── main.py
│
├── examples/
│   ├── decomposition_example.py
│   ├── merge_example.py
│   ├── elimination_example.py
│   ├── priority_example.py
│   ├── counterexample.py
│   └── complete_demo.py
│
├── results/
│
├── docs/
│
└── README.md
```

---

## Component Responsibilities

### core.py

Defines the basic data structures used throughout the framework.

Main classes include

- Rule
- RuleBase
- Transition
- VerificationResult

The module also provides utility functions for evaluating guards and
executing rule actions.

---

### semantics.py

Implements the operational semantics of reactive rule systems.

Main functions include

- enabled_rules()
- maximal_enabled()
- select_rule()
- step()
- run_trace()
- run_corresponding_trace_pair()

These functions provide the execution model used by behavioural validation.

---

### rulebases.py

Contains all benchmark rule bases used in the experiments.

The repository includes

- original system
- decomposed system
- merged system
- eliminated system
- priority-adjusted system

and three intentionally incorrect refactorings

- invalid merge
- invalid priority adjustment
- unsafe decomposition

---

### validation.py

Implements theorem-based verification.

This module checks all proof obligations defined in the paper for

- decomposition
- merging
- elimination
- priority adjustment

It also provides

- proof_obligations()

which executes every verification theorem.

---

### analysis.py

Implements empirical evaluation.

Three analyses are supported.

1. Behavioural validation

Random executions compare corresponding rule bases and detect behavioural
divergence.

2. Counterexample generation

The first divergence trace is recorded whenever behavioural equivalence
fails.

3. Scalability evaluation

Execution time is measured for increasing numbers of traces.

---

### reporting.py

Exports experimental results.

Generated files include

- proof_obligations.csv
- behavioural_results.csv
- scalability_results.csv
- divergence_positions.png

---

### main.py

Coordinates the complete workflow.

Running

```
python src/main.py
```

automatically performs

1. proof obligation verification;

2. behavioural validation;

3. scalability evaluation;

4. result generation.

---

## Execution Workflow

The overall workflow consists of three stages.

```
Rule Bases
      │
      ▼
Proof Obligation Verification
      │
      ▼
Behavioural Validation
      │
      ▼
Scalability Evaluation
      │
      ▼
CSV Reports + Figures
```

---

## Design Principles

The framework follows several software engineering principles.

- modular implementation;
- separation of concerns;
- deterministic theorem verification;
- reproducible experimental evaluation;
- reusable components for future rule transformations.

These principles make the implementation suitable both for research
experiments and for extending with additional correctness-preserving
refactoring rules.
