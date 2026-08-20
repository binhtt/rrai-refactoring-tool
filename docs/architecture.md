# RRAI Refactoring Verification Framework Architecture

## Overview

The RRAI Refactoring Verification Framework is a Python implementation
supporting the verification and experimental evaluation of
correctness-preserving rule refactorings in reactive rule-based artificial
intelligence systems.

The framework provides three complementary capabilities:

- finite-domain verification of refactoring-specific proof obligations;
- execution-based behavioural validation using rule correspondence;
- scalability evaluation of complete correspondence-based behavioural
  validation.

The implementation follows a modular architecture in which rule modelling,
operational semantics, verification, behavioural analysis, and reporting are
separated into dedicated components.

---

## Repository Structure

```text
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
│   ├── proof_obligations.csv
│   ├── table2_structural_changes.csv
│   ├── table3_valid_transformations.csv
│   ├── table4_invalid_transformations.csv
│   ├── table5_counterexamples.csv
│   ├── table6_scalability.csv
│   └── divergence.png
│
├── docs/
│   ├── architecture.md
│   ├── semantics.md
│   ├── refactoring_theorems.md
│   ├── experiments.md
│   └── results.md
│
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Component Responsibilities

### core.py

Defines the basic data structures and state-manipulation functions used
throughout the framework.

The main data structures are:

- `Rule`
- `RuleBase`
- `Transition`

The module also provides:

- safe Boolean guard evaluation;
- immutable and mutable state conversion;
- action-transition semantics.

Operational rule selection and trace execution are intentionally separated
from this module and implemented in `semantics.py`.

---

### semantics.py

Implements the operational semantics of reactive rule-based systems.

Its responsibilities include:

- enabled-rule computation;
- maximal-rule computation under the priority relation;
- deterministic rule selection when required for sampled execution;
- single-step execution;
- trace execution;
- correspondence-based comparison of original and transformed executions.

These functions provide the execution semantics used by behavioural
validation and counterexample generation.

---

### rulebases.py

Defines the autonomous mobile robot rule bases and the refactoring scenarios
used in the experiments.

The valid scenarios are:

- decomposition;
- merging;
- elimination;
- priority adjustment.

The negative-control scenarios are:

- invalid merge;
- invalid priority adjustment;
- unsafe decomposition.

The module also defines the refactoring-induced rule-correspondence relations
used during behavioural comparison.

In the merging scenario, the two source rules are represented by one logical
merged rule whose guard is the disjunction of their effective guards. The
implementation therefore preserves the 2-to-1 rule-cardinality change
specified by the merging transformation.

The invalid-priority negative control removes the original priority relation
without introducing its reverse, thereby implementing the edge-deletion
intervention evaluated in the manuscript.

---

### validation.py

Implements finite-domain proof-obligation verification.

The verification workflow supports:

- refactoring-type detection;
- identification of changed rules;
- construction of the finite verification domain;
- decomposition obligations;
- merging obligations;
- elimination obligations;
- maximal-rule preservation for priority adjustment;
- frame and well-formedness checks;
- structured failure records and witnesses;
- counterexample generation when applicable.

The verification procedure evaluates the applicable preservation conditions
over the complete finite state-event domain used by the case study.

The main experimental entry point is:

```text
proof_obligations()
```

which evaluates all preservation-valid transformations and negative controls.

---

### analysis.py

Implements execution-based experimental evaluation.

The module provides two principal analyses.

#### Behavioural validation

Original and transformed rule bases are executed under identical generated
initial states and event sequences.

At each execution step, behavioural comparison checks bidirectional
correspondence between maximal rule choices before continuing execution.
A divergence is recorded when the transition correspondence required by the
formal model fails.

#### Scalability evaluation

The scalability experiment measures the execution time of the complete
correspondence-based behavioural-validation procedure for increasing numbers
of sampled traces.

The experiment therefore measures more than trace generation or independent
execution of two rule bases: it includes the correspondence checks used by
behavioural validation.

---

### reporting.py

Produces the experimental artifacts used to support the reported results.

The repository retains the following principal result files:

- `proof_obligations.csv`
- `table2_structural_changes.csv`
- `table3_valid_transformations.csv`
- `table4_invalid_transformations.csv`
- `table5_counterexamples.csv`
- `table6_scalability.csv`
- `divergence.png`

These files provide the proof-obligation results, manuscript table data, and
first-divergence-position figure associated with the experimental evaluation.

---

### main.py

Provides the command-line entry point and coordinates the complete
experimental workflow.

Running

```bash
python src/main.py
```

performs:

1. finite-domain proof-obligation verification;
2. execution-based behavioural validation;
3. complete correspondence-based scalability evaluation;
4. generation of CSV, JSON, and graphical artifacts;
5. console reporting of the experimental results.

Command-line options allow the number of traces, trace length, random seed,
scalability sample sizes, number of repetitions, and output directory to be
configured.

---

## Execution Workflow

The overall workflow is:

```text
Original and Refactored Rule Bases
              │
              ▼
     Refactoring Detection
              │
              ▼
     Changed-Rule Identification
              │
              ▼
Finite-Domain Proof-Obligation Verification
              │
              ▼
Correspondence-Based Behavioural Validation
              │
              ▼
Counterexample / Divergence Analysis
              │
              ▼
Complete Behavioural-Validation Timing
              │
              ▼
      CSV Results + Figure
```

Proof-obligation verification and behavioural validation have distinct
roles. Passing the applicable proof obligations establishes the hypotheses
of the corresponding preservation result over the finite verification
domain. Behavioural validation provides complementary execution-based
evidence and counterexamples for intentionally invalid transformations.

---

## Design Principles

The framework follows several implementation principles:

- separation between rule representation and operational semantics;
- explicit representation of refactoring-induced rule correspondence;
- exhaustive proof-obligation checking over the finite verification domain;
- explicit distinction between formal verification and sampled behavioural
  validation;
- deterministic random seeds for reproducible behavioural experiments;
- identical execution inputs for original and transformed systems;
- complete correspondence-based comparison during behavioural validation;
- machine-readable result generation for direct comparison with the
  manuscript.

These principles are intended to maintain consistency between the formal
preservation framework, its executable implementation, and the experimental
results reported in the accompanying manuscript.
