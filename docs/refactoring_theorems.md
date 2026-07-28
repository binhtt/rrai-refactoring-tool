# Correctness-Preserving Refactoring Theorems

## Overview

This document summarizes the correctness-preserving rule refactorings
implemented in the RRAI Refactoring Verification Framework.

Each transformation is accompanied by a set of proof obligations that
must hold before the transformation is considered behaviour-preserving.

The framework automatically checks these obligations using the functions
provided in `src/validation.py`.

---

# Supported Refactorings

The framework currently supports four correctness-preserving
transformations.

- Rule decomposition
- Rule merging
- Rule elimination
- Priority adjustment

Each transformation has a corresponding verification procedure.

---

# 1. Rule Decomposition

## Description

A complex rule is replaced by multiple simpler rules whose combined
behaviour is equivalent to the original rule.

Example

```
r3
      ↓

r3a
r3b
```

## Proof Obligations

The framework verifies that

- the decomposed guards form a complete partition of the original guard;
- the combined actions preserve the behaviour of the original rule;
- the priority relations are correctly inherited.

Verification function

```
verify_decomposition()
```

---

# 2. Rule Merging

## Description

Several rules with identical behaviour are merged into a more compact
representation.

Example

```
r11
r4
      ↓

r15_sensor
r15_timer
```

## Proof Obligations

The framework checks

- guard union correctness;
- action equivalence;
- priority compatibility.

Verification function

```
verify_merge()
```

---

# 3. Rule Elimination

## Description

A redundant rule is removed without affecting observable behaviour.

Example

```
r16

↓

removed
```

## Proof Obligations

The eliminated rule must

- never become a maximal enabled rule;
- never influence the selected execution.

Verification function

```
verify_elimination()
```

---

# 4. Priority Adjustment

## Description

Priority relations are modified while preserving the set of maximal
enabled rules.

Example

```
Before

r6
r4

After

r6 < r4
```

## Proof Obligations

The framework verifies that

- the maximal enabled rule set remains unchanged.

Verification function

```
verify_priority()
```

---

# Global Verification

The function

```
proof_obligations()
```

executes every supported theorem and returns a collection of
verification results.

The generated report is written to

```
results/proof_obligations.csv
```

---

# Behavioural Validation

The theorem verification is complemented by execution-based behavioural
validation.

For every verified transformation, the framework executes corresponding
rule bases under identical initial states and event sequences.

Behavioural equivalence requires

- identical rule execution;
- identical state transitions;
- identical final states.

Any mismatch is reported as a behavioural divergence.

---

# Negative Controls

The repository also includes intentionally incorrect transformations.

These examples demonstrate situations in which the proof obligations are
violated.

## Invalid Merge

Two incompatible rules are merged.

Expected result

```
FAIL
```

Behavioural validation should detect execution divergence.

---

## Invalid Priority Adjustment

An incorrect priority relation changes the selected maximal rule.

Expected result

```
FAIL
```

Behavioural validation should produce counterexamples.

---

## Unsafe Decomposition

A rule is decomposed without preserving its original semantics.

Expected result

```
FAIL
```

Behavioural divergence should be observed.

---

# Experimental Validation

Each theorem is validated using two complementary approaches.

1. Proof obligation verification

The formal conditions defined above are checked exhaustively over the
finite verification domain.

2. Behavioural validation

Monte Carlo execution compares the original and transformed rule bases
under randomly generated executions.

A transformation is considered correctness-preserving only when both
verification stages succeed.

---

# Summary

The framework combines theorem-based verification with execution-based
validation.

This combination provides stronger confidence than using either
technique independently and enables automatic verification of
correctness-preserving rule refactorings for reactive rule-based AI
systems.
