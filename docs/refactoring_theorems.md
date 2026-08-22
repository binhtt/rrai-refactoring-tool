# Correctness-Preserving Refactoring Theorems

## Overview

This document summarizes the correctness-preserving rule refactorings
supported by the RRAI Refactoring Verification Framework.

Each transformation is associated with preservation conditions derived
from the formal results presented in the accompanying paper. The
implementation checks these conditions over the complete finite
state-event domain of the case study.

Execution-based behavioural validation is used as complementary empirical
evidence and for sampled counterexample generation. It is not used as the
formal basis for establishing correctness preservation.

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
(event = sensor) and obstacleDetected and highSpeed
    -> emergencyStop
```

and is decomposed into:

```text
r3a:
(event = sensor) and obstacleDetected and highSpeed and frontObstacle
    -> emergencyStop

r3b:
(event = sensor) and obstacleDetected and highSpeed and not frontObstacle
    -> emergencyStop
```

The refactoring-induced correspondence therefore contains:

```text
(r3, r3a)
(r3, r3b)
```

in addition to identity correspondence for retained rules.

## Proof Obligations

The verifier checks:

- `GuardPartition`: the new guards form an exact partition of the
  original effective guard;
- `ActionPreservation`: the decomposed rules preserve the action of the
  original rule;
- `PriorityInheritance`: external priority relationships involving the
  original rule are inherited by the decomposed rules;
- applicable well-formedness and unchanged-frame conditions.

The guard-partition check includes exact guard coverage, pairwise
disjointness, and non-empty partition components.

Verification is performed over the complete finite verification domain.

---

# 2. Rule Merging

## Description

Rule merging replaces multiple behaviourally compatible source rules by
a single rule.

In the case study, after the valid priority adjustment, rules `r11` and
`r4` are merged:

```text
r11:
(event = sensor) and goalVisible
    -> moveForward

r4:
(event = timer) and idle and goalVisible
    -> moveForward
```

into the single rule:

```text
r15:
((event = sensor) and goalVisible)
or
((event = timer) and idle and goalVisible)
    -> moveForward
```

Thus, the transformation is the exact cardinality-changing 2-to-1
merge:

```text
r11 ──┐
      ├──> r15
r4  ──┘
```

The two source rules `r11` and `r4` are removed and replaced by a
single `Rule` object `r15`.

The refactoring-induced correspondence therefore contains:

```text
(r11, r15)
(r4,  r15)
```

in addition to identity correspondence for retained rules.

The event-specific conditions occur within the guard of the single
merged rule `r15`; they are not represented by separate event-specific
rule objects.

For the valid case-study transformation, the rule-base cardinality
changes from 14 rules to 13 rules.

## Proof Obligations

The verifier checks:

- `MergeGuards`: the guard of the merged rule is exactly equivalent to
  the union of the source effective guards, and the source guards satisfy
  the required disjointness condition;
- `CommonAction`: all source rules and the merged rule have the same
  action;
- `PriorityCompatibility`: the source rules have compatible external
  priority profiles and the merged rule inherits that profile;
- applicable well-formedness and unchanged-frame conditions.

These conditions are evaluated over the complete finite verification
domain.

---

# 3. Rule Elimination

## Description

Rule elimination removes a rule that cannot affect executable behaviour.

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

The eliminated rule must never occur as a maximal enabled rule in any
state-event context in the verification domain.

Consequently, removing the rule does not remove a maximal executable
choice in the finite case-study model.

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

For every state-event context in the complete finite verification
domain, the verifier checks:

```text
MaxEnabled_before(s,e) = MaxEnabled_after(s,e)
```

This condition is reported as:

```text
MaximalRulePreservation
```

If the maximal enabled sets remain unchanged for every context in the
finite verification domain, the priority adjustment satisfies the
applicable preservation condition.

---

# Verification Workflow

The verification implementation follows the end-to-end structure of the
verification procedure described in the accompanying paper.

For an original rule base and a transformed rule base, the verifier:

1. checks rule-base well-formedness;
2. determines the refactoring type;
3. identifies the changed rules;
4. validates applicable structural and unchanged-frame conditions;
5. evaluates the refactoring-specific proof obligations over the finite
   verification domain;
6. constructs the refactoring-induced rule correspondence;
7. records failed obligations together with available witnesses;
8. searches the finite verification domain for a diagnostic one-step
   behavioural counterexample when an applicable proof obligation fails.

For the case study, the complete verification domain contains 16 Boolean
state predicates and three events, giving:

```text
2^16 x 3 = 196,608
```

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

At each execution step, the framework computes the maximal enabled
choices in both systems and compares them using the refactoring-induced
correspondence relation.

Behavioural comparison checks:

- bidirectional correspondence between maximal rule choices;
- equality of triggering events for corresponding transitions;
- correspondence of the fired rules;
- equality of executed actions;
- equality of pre-transition and successor states.

Every maximal choice in the original system must have a corresponding
maximal choice in the transformed system, and every maximal choice in
the transformed system must have a corresponding maximal choice in the
original system.

Only after this bidirectional maximal-choice check succeeds is a
deterministic corresponding pair selected to continue the sampled
execution prefix.

A mismatch is recorded as a behavioural divergence. For a divergent
sampled execution, the first non-corresponding transition can be
retained as a sampled behavioural counterexample.

Behavioural validation provides diagnostic and empirical evidence. It
does not replace proof-obligation verification as the basis for applying
the corresponding preservation result.

---

# Negative Controls

The repository contains three intentionally invalid transformations.
They are used to demonstrate the consequences of violating preservation
conditions.

## Invalid Merge

The invalid merge retains a genuine single-rule merge but deliberately
violates:

```text
PriorityCompatibility
```

Priority relations incident to the removed source rules are removed so
that the transformed rule base remains well formed. The required
inherited priority relation involving the new merged rule is then
deliberately omitted.

Thus, failure is caused by violation of priority compatibility rather
than by a malformed rule base, dangling priority edge, or a 2-to-2
implementation of merging.

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

The framework deliberately separates finite-domain proof-obligation
verification from sampled behavioural validation.

Proof-obligation checking evaluates the applicable sufficient
preservation conditions over the complete finite verification domain.
When these conditions hold, the hypotheses of the corresponding
preservation result are established for the finite case-study model.

Behavioural validation instead evaluates sampled executions. It provides
complementary empirical evidence for preservation-valid transformations
and sampled behavioural counterexamples for transformations that violate
preservation conditions.

The diagnostic one-step counterexample search performed by the verifier
after a failed proof obligation is also distinct from sampled behavioural
validation. It searches the finite verification domain for a concrete
one-step behavioural witness and is not used to establish equivalence.

Therefore, zero sampled divergences alone is not treated as a proof of
correctness preservation. Conversely, failure of a sufficient proof
obligation does not imply that every execution must exhibit behavioural
divergence.

---

# Summary

The framework implements four classes of correctness-preserving rule
refactoring:

- decomposition;
- merging;
- elimination;
- priority adjustment.

Their preservation conditions are checked over the complete finite
state-event domain of the case study, while correspondence-based sampled
behavioural validation provides complementary execution evidence.

In particular, merging is implemented as the exact cardinality-changing
transformation:

```text
r11, r4 -> r15
```

where the two source rules are replaced by one `Rule` object and are
related to that rule through a many-to-one correspondence.

The intentionally invalid transformations demonstrate that violations
of the preservation conditions can produce observable behavioural
divergence and provide diagnostic witnesses for the corresponding failed
obligations.
