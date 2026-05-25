# Refactoring Rules

This document summarises the currently supported correctness-preserving refactoring operators implemented in the RRAI Refactoring Tool.

---

# Overview

Refactoring operators transform a rule-based reactive system while attempting to preserve observable execution behaviour.

The framework analyses whether transformed systems remain observably equivalent to the original specification.

Observable equivalence is evaluated over:

- triggered events,
- observable actions,
- resulting observable states.

Semantic traces may differ internally, while observable traces must remain equivalent.

---

# Supported Refactorings

## 1. Rule Extraction

A complex rule may be decomposed into multiple smaller rules with equivalent combined behaviour.

### Original Rule

```text
r:
event = sensor
condition = obstacle and highSpeed
action = emergencyStop
priority = 100
```

### Refactored Rules

```text
r1:
condition = obstacle and highSpeed and frontObstacle

r2:
condition = obstacle and highSpeed and not frontObstacle
```

Both rules preserve the same observable action.

### Expected Result

```text
Observable equivalence: True
```

---

# 2. Rule Merging

Multiple rules with identical actions and compatible priorities may be merged into a single rule.

### Example

```text
r1:
condition = batteryLow

r2:
condition = chargingStationNear
```

may become:

```text
r:
condition = batteryLow or chargingStationNear
```

provided observable behaviour is preserved.

---

# 3. Dead Rule Elimination

Rules that are never executable may be removed safely.

### Example

```text
condition = False
```

or rules permanently shadowed by higher-priority rules.

### Expected Result

Observable traces remain unchanged.

---

# 4. Condition Simplification

Equivalent logical simplifications may be applied to rule guards.

### Example

```text
(a and b) or (a and not b)
```

simplifies to:

```text
a
```

provided rule priority interactions remain unchanged.

---

# 5. Priority Restructuring

Priorities may be modified when rule-selection behaviour remains observably equivalent.

### Safe Example

Two rules with disjoint conditions may swap priorities safely.

### Unsafe Example

Changing priorities between overlapping rules may alter selected actions and violate equivalence.

---

# Unsafe Refactorings

The framework also detects unsafe transformations.

## Example

### Original Behaviour

```text
obstacle and highSpeed
→ emergencyStop
```

### Unsafe Refactoring

```text
obstacle
→ hazardFlag

hazard and highSpeed
→ emergencyStop
```

This transformation introduces intermediate observable behaviour and changes execution traces.

### Expected Result

```text
COUNTEREXAMPLE FOUND
Observable equivalence: False
```

---

# Observable Equivalence Criterion

Two systems are considered observably equivalent if:

```text
ObsTrace(S1) = ObsTrace(S2)
```

for all explored executions.

Observable traces compare:

- events,
- observable actions,
- observable states.

Internal rule identifiers are intentionally ignored at observable level.

---

# Counterexample Generation

When equivalence fails, the framework reports:

- initial state,
- event sequence,
- original semantic trace,
- refactored semantic trace,
- original observable trace,
- refactored observable trace.

This supports debugging and validation of unsafe refactorings.

---

# Current Limitations

The current prototype uses:

- randomized execution exploration,
- bounded testing,
- deterministic maximal-priority rule selection.

The framework does not yet provide:

- exhaustive symbolic verification,
- temporal logic checking,
- SMT-based proof generation,
- concurrency analysis.

---

# Future Extensions

Planned future work includes:

- symbolic equivalence checking,
- Event-B integration,
- SMT-based reasoning,
- probabilistic rule systems,
- concurrent reactive semantics,
- automated refactoring synthesis.
