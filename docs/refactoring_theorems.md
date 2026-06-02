# Refactoring Correctness Theorems

## Lemma 1: Safe Decomposition

A rule

r = (g,a,p)

may be decomposed into

r1 = (g1,a,p)

r2 = (g2,a,p)

iff

g1 ∨ g2 = g

and

g1 ∧ g2 = False

and action and priority remain unchanged.

Result:

Observable behavior is preserved.

Experimental result:

Equivalent = True

---

## Lemma 2: Safe Merge

Two rules may be merged iff

- identical action
- identical priority

Merged rule:

(g1 ∨ g2, a, p)

Experimental result:

Merge example in benchmark produced divergences because actions differed.

Equivalent = False

---

## Lemma 3: Dead Rule Elimination

A rule may be removed iff

its guard is unsatisfiable.

Example:

guard = False

Such a rule can never fire.

Result:

Observable behavior is preserved.

Experimental result:

Equivalent = True

---

## Lemma 4: Priority Preservation

Behavior is preserved only if relative priority ordering remains unchanged.

Changing maximal enabled rule selection can alter execution.

Experimental result:

Equivalent = False

---

## Counterexample

Consider

r1:
priority = 100
action = moveForward

r2:
priority = 50
action = turnLeft

Changing priority ordering changes selected actions.

Result:

Behavior changes.

Experimental result:

Equivalent = False
