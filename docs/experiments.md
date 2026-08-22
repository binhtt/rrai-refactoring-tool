# Experimental Evaluation

## Overview

This document describes the experimental evaluation of the
RRAI Refactoring Verification Framework and provides instructions
for reproducing the reported results.

The evaluation consists of three complementary components:

1. finite-domain proof-obligation verification;
2. execution-based behavioural validation;
3. scalability evaluation of complete correspondence-based
   behavioural validation.

The experiments use the autonomous mobile robot rule base described
in the accompanying paper.

---

## Requirements

The experiments require:

- Python 3.10 or later;
- NumPy;
- pandas;
- Matplotlib.

Install the required packages using:

```bash
pip install -r requirements.txt
```

---

## Running the Experiments

Run the complete evaluation with:

```bash
python src/main.py
```

The default configuration uses:

- 10,000 sampled traces per behavioural-validation case;
- trace length 20;
- random seed `20260723`;
- 30 repetitions for each scalability workload;
- scalability workloads of 100, 500, 1,000, 2,000, 5,000,
  and 10,000 traces.

The command-line interface also allows these parameters to be changed.

---

# Experiment 1: Finite-Domain Proof-Obligation Verification

## Purpose

This experiment evaluates the preservation conditions associated with
the four supported refactoring classes:

- decomposition;
- merging;
- elimination;
- priority adjustment.

Three intentionally invalid transformations are evaluated as negative
controls:

- invalid merge;
- invalid priority adjustment;
- unsafe decomposition.

## Verification Domain

The verifier constructs the complete finite state-event domain

\[
D = S \times E.
\]

The Boolean state space is generated from the predicates occurring in
the case-study rule bases and action semantics. All Boolean valuations
are enumerated and paired with every event in

\[
E = \{sensor, timer, watchdog\}.
\]

The resulting complete verification domain contains 196,608
state-event contexts.

Using the complete domain avoids relying on manually selected
transformation-specific predicate subsets. Consequently, every
state-event context of the finite case-study model is checked for each
applicable proof obligation.

## Verification Procedure

The verification workflow:

1. checks rule-base well-formedness;
2. detects the refactoring type;
3. identifies the changed rules;
4. checks unchanged-frame conditions;
5. evaluates the applicable refactoring-specific proof obligations;
6. constructs the refactoring-induced rule correspondence;
7. records failed obligations and witnesses;
8. searches the finite verification domain for a diagnostic one-step
   behavioural counterexample when an applicable proof obligation fails.

The diagnostic counterexample search is distinct from the sampled
behavioural validation described in Experiment 2. It is used to provide
a concrete witness for a failed transformation and is not used to
establish equivalence.

The expected verification results are:

| Transformation | Expected Result |
|---|---|
| Decomposition | PASS |
| Merging | PASS |
| Elimination | PASS |
| Priority adjustment | PASS |
| Invalid merge | FAIL |
| Invalid priority adjustment | FAIL |
| Unsafe decomposition | FAIL |

The complete verification results are provided in:

```text
results/proof_obligations.csv
```

For the current case study, all four preservation-valid transformations
pass their applicable proof obligations over the complete finite domain.
The three negative controls fail the intended preservation conditions:

| Transformation | Failed condition(s) |
|---|---|
| Invalid merge | PriorityCompatibility |
| Invalid priority adjustment | MaximalRulePreservation |
| Unsafe decomposition | GuardPartition; ActionPreservation |

---

# Experiment 2: Execution-Based Behavioural Validation

## Purpose

Behavioural validation provides execution-based evidence complementary
to proof-obligation verification.

For each transformation, the original and transformed rule bases are
evaluated under identical initial states and event sequences.

The default experiment uses:

| Parameter | Value |
|---|---:|
| Number of traces | 10,000 |
| Trace length | 20 |
| Random seed | 20260723 |

## Input Generation

Boolean state variables are sampled independently with equal
probabilities for `True` and `False`, except for the case-study
initialisation constraints defined by the experiment.

Events are sampled uniformly from:

```text
sensor
timer
watchdog
```

A single generated collection of initial states and event sequences is
reused across the evaluated transformations so that corresponding
systems receive identical execution inputs.

This common-input design makes the behavioural results directly
comparable across the evaluated transformations.

## Correspondence-Based Comparison

Behavioural validation does not merely execute the original and
transformed systems independently.

At each execution step, the framework:

1. computes the enabled rules;
2. computes the maximal enabled rules under the applicable priority
   relation;
3. checks bidirectional correspondence between the maximal choices of
   the original and transformed systems;
4. verifies correspondence of the resulting labelled transitions and
   successor states;
5. selects a deterministic corresponding pair only after the
   bidirectional maximal-choice check succeeds, in order to continue
   the sampled execution prefix.

Thus, deterministic selection is used only to continue a sampled trace.
It does not replace the bidirectional comparison of all maximal rule
choices at the current execution step.

A behavioural divergence is recorded when the required correspondence
between the two systems fails.

For each divergent execution, the framework records the first
non-corresponding transition. These observations are also used to
construct the first-divergence-position distribution.

## Preservation-Valid Transformations

The four preservation-valid transformations are:

- decomposition;
- merging;
- elimination;
- priority adjustment.

All four transformations pass their applicable proof obligations and
produce zero behavioural divergences in the 10,000 sampled executions.

The merging experiment evaluates the exact cardinality-changing
transformation

```text
r11, r4 -> r15
```

in which the two source rules are replaced by a single merged rule.
The corresponding many-to-one rule relation contains:

```text
(r11, r15)
(r4,  r15)
```

Thus, the behavioural validation of merging evaluates the actual
2-to-1 transformation rather than an implementation-level 2-to-2
representation.

## Negative Controls

The invalid merge deliberately violates priority compatibility while
retaining a well-formed rule base and a single merged rule.

The invalid priority adjustment removes the priority relation

```text
r9 < r3
```

without adding the reverse relation. Thus, `r9` and `r3` become
incomparable when both are enabled.

The unsafe decomposition violates guard partitioning and action
preservation.

With the fixed behavioural-validation inputs, the reported divergence
results are:

| Transformation | Divergences | Rate |
|---|---:|---:|
| Invalid merge | 2,466 | 24.66% |
| Invalid priority adjustment | 2,459 | 24.59% |
| Unsafe decomposition | 4,929 | 49.29% |

These negative controls demonstrate that the experimental procedure
detects observable behavioural differences when the corresponding
preservation conditions are violated.

The manuscript-level behavioural results are provided in:

```text
results/table3_valid_transformations.csv
results/table4_invalid_transformations.csv
results/table5_counterexamples.csv
```

---

# Experiment 3: Scalability and Execution Cost

## Purpose

The scalability experiment measures execution cost as the number of
sampled traces increases while keeping the rule base and trace length
fixed.

Importantly, the measured operation is the complete
correspondence-based behavioural-validation procedure.

It therefore includes:

- execution of the original system;
- execution of the transformed system;
- enabled-rule computation;
- maximal-rule computation;
- bidirectional rule-correspondence checking;
- transition comparison.

It is not a measurement of trace generation alone.

Input generation is performed outside the timed region so that the
reported measurements characterise the cost of the behavioural
comparison itself.

## Configuration

The evaluated workloads are:

| Number of traces |
|---:|
| 100 |
| 500 |
| 1,000 |
| 2,000 |
| 5,000 |
| 10,000 |

Each workload uses:

- trace length 20;
- 30 independent timing repetitions.

The scalability experiment uses a preservation-valid decomposition
scenario and performs the complete correspondence-based behavioural
comparison for each generated workload.

For every workload, the mean execution time, standard deviation,
minimum time, and maximum time are retained.

## Reported Results

| Number of traces | Execution time (s), mean ± SD |
|---:|---:|
| 100 | 0.163 ± 0.050 |
| 500 | 0.746 ± 0.179 |
| 1,000 | 1.520 ± 0.358 |
| 2,000 | 3.031 ± 0.568 |
| 5,000 | 7.638 ± 0.731 |
| 10,000 | 15.266 ± 0.361 |

The measurements show an approximately linear increase in execution
time as the number of sampled traces increases while trace length and
rule-base structure remain fixed.

The exact aggregate values supporting the manuscript table are stored in:

```text
results/table6_scalability.csv
```

The CSV explicitly identifies the measured operation as:

```text
full_correspondence_based_behavioural_validation
```

Timing values may vary across machines and executions because they
measure wall-clock execution time. The checked-in aggregate data are
the values used for Table 6 of the accompanying manuscript.

---

# Divergence-Position Analysis

For each divergent execution of an intentionally invalid
transformation, the framework records the position of the first
non-corresponding transition.

The submitted first-divergence-position distribution is stored as:

```text
results/divergence.png
```

Only executions exhibiting behavioural divergence contribute to this
distribution. Preservation-valid transformations are therefore
excluded.

The figure complements the aggregate divergence rates by showing when
the first observable difference between the original and transformed
systems emerges.

The divergence-position analysis is descriptive and execution-based.
It is not used to establish the proof-obligation results.

---

# Manuscript Result Files

The `results/` directory contains the principal data used to support the
tables and figure reported in the accompanying manuscript:

```text
results/
├── proof_obligations.csv
├── table2_structural_changes.csv
├── table3_valid_transformations.csv
├── table4_invalid_transformations.csv
├── table5_counterexamples.csv
├── table6_scalability.csv
└── divergence.png
```

The files correspond to:

- `table2_structural_changes.csv` — structural changes produced by the
  valid transformation sequence;
- `proof_obligations.csv` — detailed finite-domain verification results;
- `table3_valid_transformations.csv` — verification and behavioural
  results for preservation-valid transformations;
- `table4_invalid_transformations.csv` — results for the negative
  controls;
- `table5_counterexamples.csv` — failed proof obligations and
  counterexample availability;
- `table6_scalability.csv` — exact aggregate timing data reported in
  Table 6;
- `divergence.png` — first-divergence-position distribution reported
  as Figure 3.

Additional machine-readable outputs, raw scalability measurements,
reproducibility metadata, and graphical formats may also be generated
by the reporting workflow.

---

# Reproducibility

Proof-obligation verification is exhaustive over the complete finite
state-event domain and is deterministic.

Behavioural validation uses a fixed pseudo-random seed by default,
allowing the same sampled initial states and event sequences to be
regenerated.

The same behavioural input collection is reused across the
transformation cases within a run, allowing direct comparison under
identical sampled inputs.

The checked-in result files provide the exact manuscript-level
experimental results.

Wall-clock timing measurements may vary across executions and hardware.
For this reason, rerunning the scalability experiment is expected to
produce similar scaling behaviour but not necessarily numerically
identical timing measurements.

The random seed controls generated experimental inputs; it does not
eliminate variation in wall-clock execution time.

---

# Complexity

Let:

- \(m\) be the number of sampled traces;
- \(k\) be the number of events per trace;
- \(n\) be the number of rules.

At an abstract level, evaluating enabledness requires examining up to
\(n\) rules at each execution step.

Under a general partial priority relation, straightforward maximal-rule
computation may require up to \(O(n^2)\) rule-pair checks per execution
step. Treating priority-processing costs as part of maximal-rule
computation, a corresponding worst-case bound for sampled behavioural
validation is therefore

\[
O(m \times k \times n^2).
\]

If maximal-rule selection can be resolved in linear time for a
particular priority representation or rule-base structure, the
corresponding execution cost reduces to

\[
O(m \times k \times n).
\]

These bounds characterise the dependence on the number of sampled
executions, trace length, and rule-base size at an abstract algorithmic
level. They are not intended as a fine-grained complexity model of
Python interpreter overhead or wall-clock timing.

The scalability experiment varies \(m\) while keeping \(k\), \(n\), and
the rule-base structure fixed. It therefore characterises empirical
scalability with respect to the number of sampled executions rather
than rule-base size, guard complexity, or priority-relation density.
