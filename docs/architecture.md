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

A rule is represented by its name, guard, and action. Guards are evaluated
over the combined state-event context, corresponding to the formal type

```text
g_r : S x E -> {true, false}.
```

Event conditions are therefore represented directly within guard
expressions rather than as a separate rule field. This representation
supports refactorings whose guards combine conditions associated with
different triggering events.

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

- enabled-rule computation over state-event contexts;
- transitive priority handling;
- maximal-rule computation under the priority relation;
- deterministic rule selection when required for sampled execution;
- single-step execution;
- trace execution;
- correspondence-based comparison of original and transformed executions.

During behavioural comparison, all maximal rule choices in both systems are
considered. Every maximal choice in the original system must have a
corresponding maximal choice in the transformed system, and vice versa.
A deterministic corresponding pair is selected only after this
bidirectional check and is used to continue the sampled execution prefix.

These functions provide the execution semantics used by behavioural
validation and sampled counterexample generation.

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

The module also defines refactoring-induced rule-correspondence relations
used during behavioural comparison.

The main sequential refactoring scenario is:

```text
ORIGINAL
   |
   | Priority adjustment
   v
PRIORITY_ADJUSTED
   |
   | Merging
   v
MERGED
   |
   | Decomposition
   v
DECOMPOSED
```

The elimination scenario is evaluated independently.

#### Cardinality-changing merge

In the merging scenario, the two source rules `r11` and `r4` are replaced
by a single `Rule` object `r15`. The guard of `r15` is the disjunction of
the effective state-event guards of `r11` and `r4`.

The transformation is therefore implemented as the exact
cardinality-changing merge

```text
r11, r4 -> r15
```

rather than by separate event-specific rule objects.

Consequently, the number of rules changes from 14 to 13 at the merging
stage. The refactoring-induced correspondence is many-to-one:

```text
(r11, r15)
(r4,  r15)
```

The priority relation inherited by the merged rule is represented directly
in the transformed rule base.

#### Negative controls

The invalid-merge negative control retains a single merged rule but
intentionally violates the required priority inheritance. It therefore
tests the merge priority-compatibility condition without relying on a
malformed rule base or a dangling priority edge.

The invalid-priority negative control removes the original priority relation
without introducing its reverse, thereby implementing the edge-deletion
intervention evaluated in the manuscript.

The unsafe-decomposition negative control intentionally violates the
decomposition preservation conditions and is used to demonstrate detection
of non-preserving transformations.

---

### validation.py

Implements finite-domain proof-obligation verification.

The verification workflow supports:

- rule-base well-formedness checking;
- refactoring-type detection;
- identification of changed rules;
- construction of the finite verification domain;
- frame-preservation checking;
- decomposition obligations;
- merging obligations;
- elimination obligations;
- maximal-rule preservation for priority adjustment;
- construction of refactoring-induced rule correspondence;
- structured failure records and witnesses;
- counterexample generation when applicable.

For merging, the verifier checks the applicable conditions for:

- exact guard union;
- guard disjointness;
- common action;
- priority compatibility and inheritance.

For decomposition, it checks the applicable conditions for:

- exact guard partition;
- pairwise disjointness;
- non-empty partition components;
- action preservation;
- priority inheritance.

For elimination, the verifier checks that the removed rule is never a
maximal enabled rule over the verification domain.

For priority adjustment, it checks preservation of the maximal-enabled-rule
set before and after the priority change.

The verification procedure evaluates the applicable preservation conditions
over the complete finite state-event domain used by the case study.

For the case study, the domain contains 16 Boolean state predicates and
three events, giving

```text
2^16 x 3 = 196,608
```

state-event contexts.

The main experimental entry point is:

```text
proof_obligations()
```

which evaluates all preservation-valid transformations and negative
controls.

---

### analysis.py

Implements execution-based experimental evaluation.

The module provides two principal analyses.

#### Behavioural validation

Original and transformed rule bases are executed under identical generated
initial states and event sequences.

At each execution step, behavioural comparison checks bidirectional
correspondence between the maximal rule choices of the two systems before
continuing execution.

A divergence is recorded if the required correspondence between maximal
choices or their resulting transitions fails.

The default manuscript experiment uses:

```text
10,000 traces per transformation
trace length = 20
seed = 20260723
```

The same generated execution inputs are used for the original and
transformed systems and are shared across the transformation cases within a
behavioural-validation run.

Behavioural validation is complementary to proof-obligation verification.
It provides execution-based evidence for preservation-valid transformations
and sampled behavioural counterexamples for intentionally invalid
transformations.

#### Scalability evaluation

The scalability experiment measures the execution time of the complete
correspondence-based behavioural-validation procedure for increasing numbers
of sampled traces.

The measured operation therefore includes:

- execution of the compared rule bases;
- maximal-rule computation;
- bidirectional correspondence checking;
- transition comparison.

It does not measure only trace generation or independent execution of the
two systems.

Input generation is performed outside the timed region.

The default scalability experiment evaluates:

```text
100
500
1,000
2,000
5,000
10,000
```

traces, using a trace length of 20 and 30 repetitions for each setting.

---

### reporting.py

Produces the experimental artifacts used to support the reported results.

Among the generated artifacts, the principal manuscript-facing result files
are:

- `proof_obligations.csv`
- `table2_structural_changes.csv`
- `table3_valid_transformations.csv`
- `table4_invalid_transformations.csv`
- `table5_counterexamples.csv`
- `table6_scalability.csv`
- `divergence.png`

The reporting workflow also generates supporting machine-readable and
reproducibility artifacts, including structured verification results,
sampled counterexamples, raw scalability measurements, reproducibility
metadata, and graphical output where applicable.

The manuscript tables are generated from the rule-base structures and
experimental results rather than from manually entered result values.

For example, the structural counts in Table 2 are obtained directly from
the corresponding rule bases. The merging stage therefore reports the
actual cardinality change from 14 rules to 13 rules produced by replacing
`r11` and `r4` with the single rule `r15`.

The divergence figure is generated from the recorded first-divergence
positions of the negative-control behavioural executions.

---

### main.py

Provides the command-line entry point and coordinates the complete
experimental workflow.

Running

```bash
python src/main.py
```

performs:

1. complete finite-domain proof-obligation verification;
2. execution-based correspondence-based behavioural validation;
3. scalability measurement of complete correspondence-based behavioural
   validation;
4. generation of manuscript-ready Tables 2--6;
5. generation of Algorithm-1 results and counterexamples;
6. generation of the divergence figure;
7. generation of reproducibility metadata and raw timing data;
8. console or Jupyter-friendly result display.

Command-line options allow the number of traces, trace length, random seed,
scalability sample sizes, number of repetitions, and output directory to be
configured.

The program also checks the expected proof-obligation outcomes. The four
preservation-valid transformations are expected to pass, whereas the three
negative controls are expected to fail their applicable preservation
conditions.

---

## Example Programs

The `examples/` directory provides focused executable demonstrations of the
framework.

### decomposition_example.py

Verifies

```text
r3 -> {r3a, r3b}
```

over the complete finite verification domain.

### merge_example.py

Verifies the exact cardinality-changing merge

```text
r11, r4 -> r15
```

and displays the automatically constructed many-to-one correspondence

```text
(r11, r15)
(r4,  r15)
```

for the changed rules.

### elimination_example.py

Verifies that `r16` can be safely removed because it is never a maximal
enabled rule over the complete finite verification domain.

### priority_example.py

Verifies that adding

```text
r6 < r4
```

preserves the maximal-enabled-rule set over the complete finite verification
domain.

### counterexample.py

Runs sampled behavioural validation for the negative controls and displays
the first sampled behavioural counterexample found for each invalid
transformation.

### complete_demo.py

Runs the complete verification and experimental workflow using the default
experimental configuration and regenerates the associated result artifacts.

---

## Execution Workflow

The overall workflow is:

```text
Original and Refactored Rule Bases
              |
              v
     Well-Formedness Checking
              |
              v
     Refactoring Detection
              |
              v
     Changed-Rule Identification
              |
              v
Finite-Domain Proof-Obligation Verification
              |
              v
   Rule-Correspondence Construction
              |
              v
Correspondence-Based Behavioural Validation
              |
              v
Counterexample / Divergence Analysis
              |
              v
Complete Behavioural-Validation Timing
              |
              v
      CSV / JSON Results + Figure
```

Proof-obligation verification and behavioural validation have distinct
roles.

Passing the applicable proof obligations establishes the hypotheses of the
corresponding preservation result over the finite verification domain.
Behavioural validation provides complementary execution-based evidence and
sampled counterexamples for intentionally invalid transformations.

The sampled behavioural experiments are therefore not used as a substitute
for proof-obligation verification.

---

## Design Principles

The framework follows several implementation principles:

- separation between rule representation and operational semantics;
- guards defined over combined state-event contexts;
- exact implementation of cardinality-changing refactorings;
- explicit representation of refactoring-induced rule correspondence;
- exhaustive proof-obligation checking over the finite verification domain;
- explicit distinction between proof-obligation verification and sampled
  behavioural validation;
- bidirectional maximal-choice correspondence checking during behavioural
  validation;
- deterministic random seeds for reproducible behavioural experiments;
- identical execution inputs for original and transformed systems;
- complete correspondence-based comparison during behavioural validation;
- separation of input generation from the timed scalability region;
- machine-readable result generation for direct comparison with the
  manuscript.

These principles are intended to maintain consistency between the formal
preservation framework, its executable implementation, and the experimental
results reported in the accompanying manuscript.
