# Correctness-Preserving Refactoring Theorems

## Overview

This document summarizes the correctness-preserving rule refactorings
supported by the RRAI Refactoring Verification Framework.

Each transformation is associated with preservation conditions derived
from the formal results presented in the accompanying paper. The
implementation checks these conditions over the complete finite
state-event domain of the case study.

Execution-based behavioural validation is used as complementary evidence
and for counterexample generation. It is not used as the formal basis for
establishing correctness preservation.

---

# Supported Refactorings

The framework supports four refactoring classes:

- rule decomposition;
- rule merging;
- rule elimination;
- priority adjustment.

The corresponding verification procedures are implemented in
`src/validation.py`.

---

# 1. Rule Decomposition

## Description

Rule decomposition replaces one rule by multiple rules while preserving
the behaviour represented by the original rule.

In the case study:

```text
r3
 |
 +--> r3a
 |
 +--> r3b
```

The original rule is:

```text
r3:
(sensor, obstacleDetected and highSpeed)
    -> emergencyStop
```

and is decomposed into:

```text
r3a:
(sensor, obstacleDetected and highSpeed and frontObstacle)
    -> emergencyStop

r3b:
(sensor, obstacleDetected and highSpeed and not frontObstacle)
    -> emergencyStop
```

The correspondence relation therefore contains:

```text
(r3, r3a)
(r3, r3b)
```

## Proof Obligations

The verifier checks:

- `GuardPartition`: the new guards form an exact partition of the
  original effective guard;
- `ActionPreservation`: the decomposed rules preserve the action of the
  original rule;
- `PriorityInheritance`: priority relationships involving the original
  rule are inherited by the decomposed rules;
- applicable well-formedness and unchanged-frame conditions.

Verification is performed over the finite verification domain.

---

# 2. Rule Merging

## Description

Rule merging replaces multiple behaviourally compatible rules by one
logical rule.

In the case study, after the valid priority adjustment, rules `r11` and
`r4` are merged:

```text
r11:
(e = sensor) and goalVisible
    -> moveForward

r4:
(e = timer) and idle and goalVisible
    -> moveForward
```

into the single rule:

```text
r15:
((e = sensor) and goalVisible)
or
((e = timer) and idle and goalVisible)
    -> moveForward
```

Thus, the transformation is a genuine 2-to-1 merge:

```text
r11 ──┐
      ├──> r15
r4  ──┘
```

and the correspondence relation contains:

```text
(r11, r15)
(r4, r15)
```

The event-specific clauses in the guard of `r15` are implementation
conditions of one logical rule; they are not represented as separate
rules.

## Proof Obligations

The verifier checks:

- `MergeGuards`: the merged guard is equivalent to the union of the
  source effective guards and the source guards satisfy the required
  compatibility conditions;
- `CommonAction`: the source rules and merged rule preserve the same
  action;
- `PriorityCompatibility`: external priority relationships are
  preserved consistently for the merged rule;
- applicable well-formedness and unchanged-frame conditions.

For the valid case-study transformation, the rule-base cardinality
therefore changes from 14 rules to 13 rules.

---

# 3. Rule Elimination

## Description

Rule elimination removes a rule that cannot affect observable execution
behaviour.

In the case study, the auxiliary rule `r16` is eliminated:

```text
r16
 |
 +--> removed
```

The remaining rules retain identity correspondence between the original
and transformed systems.

## Proof Obligation

The verifier checks the elimination condition over the complete finite
state-event domain.

The eliminated rule must not occur as a maximal enabled rule in any
state-event context relevant to the transformation. Consequently,
removing it cannot change the maximal executable behaviour.

---

# 4. Priority Adjustment

## Description

Priority adjustment changes the priority relation while preserving the
maximal enabled rule choices.

In the valid case-study transformation, the relation

```text
r6 < r4
```

is added.

The rules themselves remain unchanged.

## Proof Obligation

For every state-event context in the finite verification domain, the
verifier checks:

```text
MaxEnabled_before(s,e) = MaxEnabled_after(s,e)
```

This condition is reported as:

```text
MaximalRulePreservation
```

If the maximal enabled sets remain unchanged for every context, the
priority adjustment satisfies the applicable preservation condition.

---

# Verification Workflow

The verification implementation follows the end-to-end structure of the
verification procedure described in the accompanying paper.

For an original rule base and a transformed rule base, the verifier:

1. determines the refactoring type;
2. identifies the changed rules;
3. validates applicable structural and frame conditions;
4. constructs the finite verification domain;
5. evaluates the refactoring-specific proof obligations;
6. records failed obligations together with available witnesses;
7. searches for a behavioural counterexample when applicable.

The complete case-study verification domain contains 196,608
state-event contexts.

The aggregate verification results are stored in:

```text
results/proof_obligations.csv
```

---

# Behavioural Validation

Proof-obligation verification is complemented by execution-based
behavioural validation.

The original and transformed systems are executed under identical
sampled initial states and event sequences.

At each execution step, the framework compares the sets of maximal
enabled rules using the refactoring-induced correspondence relation
`C_Ref`.

Behavioural comparison checks:

- bidirectional correspondence between maximal rule choices;
- triggering events;
- corresponding selected rules;
- executed actions;
- successor states.

When all maximal choices correspond, a corresponding rule pair is
selected to continue the sampled execution.

A mismatch is recorded as a behavioural divergence, and the first
non-corresponding transition can be retained as a counterexample.

Behavioural validation provides diagnostic and empirical evidence. It
does not replace proof-obligation verification as the basis for
establishing the preservation result.

---

# Negative Controls

The repository contains three intentionally invalid transformations.
They are used to demonstrate the consequences of violating preservation
conditions.

## Invalid Merge

The invalid merge deliberately violates:

```text
PriorityCompatibility
```

Priority relations incident to the removed source rules are first
removed so that the transformed rule base remains well formed. The
required inherited priority relation involving the new merged rule is
then deliberately omitted.

Expected proof-obligation result:

```text
FAIL
```

The fixed behavioural experiment produces:

```text
2,466 divergences
24.66%
```

---

## Invalid Priority Adjustment

The invalid priority-adjustment control removes:

```text
r9 < r3
```

from the original priority relation.

No reverse relation is added.

Consequently, `r9` and `r3` become incomparable when both are enabled,
which can change the set of maximal enabled rules.

The violated condition is:

```text
MaximalRulePreservation
```

Expected proof-obligation result:

```text
FAIL
```

The fixed behavioural experiment produces:

```text
2,459 divergences
24.59%
```

---

## Unsafe Decomposition

The unsafe decomposition intentionally fails to preserve the original
decomposition semantics.

The violated conditions are:

```text
GuardPartition
ActionPreservation
```

Expected proof-obligation result:

```text
FAIL
```

The fixed behavioural experiment produces:

```text
4,929 divergences
49.29%
```

---

# Relationship Between Verification and Behavioural Evidence

The framework deliberately separates formal verification from sampled
behavioural validation.

Proof-obligation checking evaluates the sufficient preservation
conditions over the complete finite verification domain. When the
applicable conditions hold, the corresponding preservation result can
be applied.

Behavioural validation instead evaluates sampled executions. It provides
complementary empirical evidence and concrete counterexamples for
transformations that violate preservation conditions.

Therefore, zero sampled divergences alone is not treated as a proof of
correctness preservation, and failure of a sufficient proof obligation
does not logically require that every sampled execution diverge.

---

# Summary

The framework implements four classes of correctness-preserving rule
refactoring:

- decomposition;
- merging;
- elimination;
- priority adjustment.

Their preservation conditions are checked over the complete finite
state-event domain, while correspondence-based behavioural validation
provides complementary execution evidence.

The intentionally invalid transformations demonstrate that violations
of the preservation conditions can lead to observable behavioural
divergence and provide diagnostic counterexamples for the corresponding
failed obligations.
