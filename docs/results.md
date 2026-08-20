# Experimental Results

## Overview

This document summarizes the experimental results of the
RRAI Refactoring Verification Framework and explains the result files
provided with the accompanying paper.

The evaluation combines:

- finite-domain proof-obligation verification;
- execution-based correspondence-based behavioural validation;
- counterexample and first-divergence analysis;
- scalability measurement of complete correspondence-based behavioural
  validation.

The manuscript-level result files are stored in the `results/` directory.

---

# Result Files

The repository contains the following principal experimental artifacts:

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

These files provide the data supporting Tables 2--6 and Figure 3 of the
accompanying manuscript, together with the detailed proof-obligation
verification results.

---

# Structural Transformation Results

The file

```text
results/table2_structural_changes.csv
```

records the structural changes produced by the valid transformation
sequence.

| Stage | Rules | Priority Relations | Structural Change | Formal Basis |
|---|---:|---:|---|---|
| Original | 14 | 6 | - | - |
| Priority adjustment | 14 | 7 | Add `r6 < r4` | Lemma 4 |
| Merging | 13 | 6 | `r11,r4 -> r15` | Lemma 2 |
| Decomposition | 14 | 8 | `r3 -> {r3a,r3b}` | Lemma 1 |

The merging transformation is a genuine 2-to-1 transformation:
`r11` and `r4` are represented by one logical merged rule `r15`.
Consequently, the number of rules decreases from 14 to 13 at the
merging stage.

---

# Proof-Obligation Verification

The file

```text
results/proof_obligations.csv
```

contains the detailed finite-domain verification results.

The complete verification domain contains 196,608 state-event contexts
for each evaluated transformation.

The expected outcomes are:

| Transformation | Status | Failed Obligation |
|---|---|---|
| Priority adjustment | PASS | - |
| Merging | PASS | - |
| Decomposition | PASS | - |
| Elimination | PASS | - |
| Invalid merge | FAIL | PriorityCompatibility |
| Invalid priority adjustment | FAIL | MaximalRulePreservation |
| Unsafe decomposition | FAIL | GuardPartition; ActionPreservation |

A `PASS` result indicates that the applicable preservation conditions
are satisfied throughout the finite verification domain.

A `FAIL` result identifies one or more violated preservation conditions
and records available diagnostic information.

---

# Valid Transformations

The file

```text
results/table3_valid_transformations.csv
```

contains the verification and behavioural-validation results for the
four preservation-valid transformations.

| Transformation | Proof-Obligation Result | Divergences | Rate (%) |
|---|---|---:|---:|
| Decomposition | Pass | 0 | 0.00 |
| Merging | Pass | 0 | 0.00 |
| Elimination | Pass | 0 | 0.00 |
| Priority adjustment | Pass | 0 | 0.00 |

All four transformations satisfy their applicable proof obligations.

No behavioural divergence was observed in the 10,000 sampled executions
for any preservation-valid transformation.

The absence of sampled divergence provides complementary execution-based
evidence; the formal preservation claim is based on satisfaction of the
applicable proof obligations rather than on Monte Carlo testing alone.

---

# Intentionally Invalid Transformations

The file

```text
results/table4_invalid_transformations.csv
```

contains the negative-control results.

| Transformation | Failed Proof Obligation | Divergences | Rate (%) |
|---|---|---:|---:|
| Invalid merge | PC | 2,466 | 24.66 |
| Invalid priority adjustment | MRP | 2,459 | 24.59 |
| Unsafe decomposition | GP, AP | 4,929 | 49.29 |

where:

- `PC` = PriorityCompatibility;
- `MRP` = MaximalRulePreservation;
- `GP` = GuardPartition;
- `AP` = ActionPreservation.

The invalid merge fails priority compatibility and produces 2,466
divergent executions.

The invalid priority-adjustment experiment removes the relation

```text
r9 < r3
```

without introducing the reverse relation. The resulting incomparability
causes 2,459 divergences, corresponding to a divergence rate of 24.59%.

The unsafe decomposition violates both guard partitioning and action
preservation and produces the largest observed divergence rate,
49.29%.

---

# Counterexample Results

The file

```text
results/table5_counterexamples.csv
```

summarizes counterexample availability for the intentionally invalid
transformations.

| Transformation | Proof Obligations | Violated Condition | Counterexample |
|---|---|---|---|
| Invalid merge | Fail | PriorityCompatibility | Found |
| Invalid priority adjustment | Fail | MaximalRulePreservation | Found |
| Unsafe decomposition | Fail | GuardPartition; ActionPreservation | Found |

For each negative control, the failed proof-obligation result is
accompanied by an observable behavioural counterexample.

Counterexamples provide diagnostic evidence of the executional
consequences of violated preservation conditions. They are not used as
the formal basis for establishing correctness preservation.

---

# Scalability and Execution Cost

The file

```text
results/table6_scalability.csv
```

contains the exact aggregate timing data reported in Table 6 of the
manuscript.

The measured operation is:

```text
full_correspondence_based_behavioural_validation
```

Each workload uses traces of length 20 and is repeated 30 times.

| Number of Traces | Mean Time (s) | SD (s) |
|---:|---:|---:|
| 100 | 0.163146 | 0.049757 |
| 500 | 0.746226 | 0.179139 |
| 1,000 | 1.520056 | 0.357556 |
| 2,000 | 3.030822 | 0.568327 |
| 5,000 | 7.638017 | 0.730837 |
| 10,000 | 15.265603 | 0.361065 |

Rounded to three decimal places, these values correspond to the
manuscript table:

| Number of Traces | Execution Time (s), mean ± SD |
|---:|---:|
| 100 | 0.163 ± 0.050 |
| 500 | 0.746 ± 0.179 |
| 1,000 | 1.520 ± 0.358 |
| 2,000 | 3.031 ± 0.568 |
| 5,000 | 7.638 ± 0.731 |
| 10,000 | 15.266 ± 0.361 |

The measured operation includes complete correspondence-based
behavioural comparison rather than trace generation alone.

Because these values measure wall-clock execution time, rerunning the
experiment on another runtime or machine may produce different timing
values. The checked-in CSV contains the aggregate measurements used in
the submitted manuscript.

---

# First-Divergence-Position Analysis

The file

```text
results/divergence.png
```

contains the first-divergence-position distribution reported as
Figure 3.

The x-axis represents the position of the first non-corresponding
transition in a divergent execution.

The y-axis represents the number of divergent executions whose first
observable mismatch occurs at that position.

The figure includes:

- invalid merge;
- invalid priority adjustment;
- unsafe decomposition.

Only executions in which a divergence was detected are included.
Preservation-valid transformations are excluded because they produced
no behavioural divergence in the sampled executions.

The distribution complements the aggregate divergence rates by showing
when the first observable behavioural difference emerges.

---

# Interpretation

The experimental results illustrate the complementary roles of formal
verification and execution-based validation.

## Proof-Obligation Verification

Proof-obligation checking evaluates the sufficient preservation
conditions over the complete finite verification domain.

All four preservation-valid transformations satisfy their applicable
conditions, whereas each intentionally invalid transformation violates
the condition or conditions deliberately targeted by the negative
control.

## Behavioural Validation

Correspondence-based behavioural validation compares the original and
transformed systems under identical sampled execution inputs.

The preservation-valid transformations exhibit zero sampled
divergences, while all three negative controls produce observable
behavioural divergence.

Behavioural validation therefore provides complementary empirical and
diagnostic evidence rather than replacing the formal preservation
argument.

## Scalability Evaluation

The scalability experiment measures the cost of complete
correspondence-based behavioural validation while increasing the number
of sampled traces.

For the fixed case-study rule base and trace length, execution time
increases approximately with the number of sampled executions.

The experiment characterizes scalability with respect to sampled trace
count; it does not establish scalability with respect to rule-base size,
guard complexity, or priority-relation density.

---

# Expected Outcome

The checked-in results satisfy the following properties:

- all four preservation-valid transformations pass proof-obligation
  verification;
- all four preservation-valid transformations produce zero divergence
  in 10,000 sampled executions;
- all three negative controls fail their targeted proof obligations;
- all three negative controls produce behavioural counterexamples;
- the invalid-priority result corresponds to deletion of `r9 < r3`,
  rather than priority reversal;
- the merging result represents a 2-to-1 transformation producing one
  logical rule `r15`;
- Table 6 reports the execution cost of complete correspondence-based
  behavioural validation.

Together, these results maintain consistency between the formal model,
the executable artifact, and the experimental evidence reported in the
accompanying manuscript.
