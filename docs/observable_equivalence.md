# Observable Trace Equivalence

## Overview

Observable trace equivalence is used to determine whether two Reactive Rule-Based AI (RRAI) systems exhibit the same externally observable behaviour under all possible event executions.

The equivalence relation is evaluated over observable traces rather than internal semantic transitions.

This approach enables correctness-preserving refactoring analysis while abstracting away from internal implementation details such as rule identifiers.

---

# Observable Semantics

Given an event sequence:

```text
e1, e2, ..., en
```

an RRAI system generates:

- semantic traces
- observable traces

A semantic trace records:

```text
(event, rule, action)
```

where:

- `event` is the triggering event,
- `rule` is the selected rule,
- `action` is the executed action.

An observable trace records:

```text
(event, action, state)
```

where:

- `event` is the observable event,
- `action` is the externally visible action,
- `state` is the resulting observable state.

Rule identifiers are intentionally omitted from observable traces.

---

# Idle Executions and τ-Actions

If no rule is enabled for a given event, the system produces an idle execution represented by:

```text
τ
```

For example:

```text
(sensor, τ, s)
```

indicates that no observable action was executed and the state remained unchanged.

The implementation intentionally preserves repeated τ-transitions in observable traces to maintain operational execution behaviour during trace analysis.

---

# Equivalence Definition

Two RRAI systems:

```text
S1 ≈obs S2
```

are observationally equivalent if, for every initial state and every event sequence, they generate identical observable traces.

Formally:

```text
ObsTrace(S1, s0, E)
=
ObsTrace(S2, s0, E)
```

for all:

- initial states `s0`,
- event sequences `E`.

---

# Counterexample Generation

If two systems are not observationally equivalent, the framework automatically generates a counterexample consisting of:

- the initial state,
- the event sequence,
- the semantic traces,
- the observable traces.

This enables debugging and analysis of unsafe refactorings.

---

# Example

## Original Rule

```text
r3:
event = sensor
condition = obstacle and highSpeed
action = emergencyStop
priority = 100
```

## Safe Refactoring

```text
r3a:
condition = obstacle and highSpeed and frontObstacle

r3b:
condition = obstacle and highSpeed and not frontObstacle
```

The observable behaviour remains unchanged because both transformed rules preserve the same observable action under all reachable states.

Therefore:

```text
Original ≈obs Refactored
```

---

# Implementation

Observable equivalence checking is implemented in:

```text
src/equivalence.py
```

Observable trace generation is implemented in:

```text
src/observable.py
```

Run equivalence checking:

```bash
python src/main.py
```

Run tests:

```bash
pytest tests/
```
