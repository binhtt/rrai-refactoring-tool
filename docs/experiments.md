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

1. detects the refactoring type;
2. identifies the changed rules;
3. checks rule-base well-formedness and unchanged-frame conditions;
4. evaluates the applicable refactoring-specific proof obligations;
5. records failed obligations and witnesses;
6. generates a behavioural counterexample when a failed transformation
   exhibits an observable divergence.

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

## Correspondence-Based Comparison

Behavioural validation does not merely execute the original and
transformed systems independently.

At each execution step, the framework:

1. computes the enabled rules;
2. computes the maximal enabled rules under the applicable priority
   relation;
3. checks bidirectional correspondence between the maximal choices of
   the original and transformed systems;
4. selects corresponding rules for continuation when the maximal
   choices correspond;
5. compares the resulting labelled transitions and successor states.

A behavioural divergence is recorded when the required correspondence
between the two systems fails.

For each divergent execution, the framework records the first
non-corresponding transition. These observations are also used to
construct the first-divergence-position distribution.

## Negative Controls

The invalid merge deliberately violates priority compatibility.

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

All four preservation-valid transformations produce zero behavioural
divergences in the sampled executions.

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
- maximal-rule computation;
- bidirectional rule-correspondence checking;
- transition comparison.

It is not a measurement of trace generation alone.

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

The mean execution time and standard deviation are reported.

## Reported Results

| Number of traces | Execution time (s), mean ± SD |
|---:|---:|
| 100 | 0.163 ± 0.050 |
| 500 | 0.746 ± 0.179 |
| 1,000 | 1.520 ± 0.358 |
| 2,000 | 3.031 ± 0.568 |
| 5,000 | 7.638 ± 0.731 |
| 10,000 | 15.266 ± 0.361 |

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
distribution. Preservation-valid transformations are therefore excluded.

The figure complements the aggregate divergence rates by showing when
the first observable difference between the original and transformed
systems emerges.

---

# Manuscript Result Files

The `results/` directory contains the data used to support the tables
and figure reported in the accompanying manuscript:

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

---

# Reproducibility

Proof-obligation verification is exhaustive over the complete finite
state-event domain and is deterministic.

Behavioural validation uses a fixed pseudo-random seed by default,
allowing the same sampled initial states and event sequences to be
regenerated.

The checked-in result files provide the exact manuscript-level
experimental results.

Wall-clock timing measurements may vary across executions and hardware.
For this reason, rerunning the scalability experiment is expected to
produce similar but not necessarily numerically identical timing
measurements.

---

# Complexity

Let:

- \(m\) be the number of sampled traces;
- \(k\) be the number of events per trace;
- \(n\) be the number of rules.

A straightforward implementation evaluates up to \(n\) rules at each
execution step. Under a general partial priority relation, maximal-rule
computation may require up to \(O(n^2)\) priority comparisons.

The worst-case execution cost of sampled behavioural validation is
therefore:

\[
O(m \times k \times n^2).
\]

When maximal-rule selection can be resolved in linear time, this reduces
to:

\[
O(m \times k \times n).
\]

The scalability experiment varies \(m\) while keeping \(k\), \(n\), and
the rule-base structure fixed. It therefore characterises scalability
with respect to the number of sampled executions rather than rule-base
size, guard complexity, or priority-relation density.
