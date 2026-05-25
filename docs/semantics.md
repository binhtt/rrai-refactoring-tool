# Operational Semantics

This document describes the operational semantics implemented in the RRAI Refactoring Tool.

The framework models Reactive Rule-Based AI (RRAI) systems using labelled transition semantics with observable execution traces.

---

# Reactive Rule-Based AI Systems

An RRAI system consists of:

- a set of rules,
- an observable state,
- incoming events,
- a deterministic rule-selection mechanism.

Each rule is defined as:

```text
(event, condition, action, priority)
```

where:

- `event` specifies the triggering event,
- `condition` is a Boolean guard,
- `action` modifies the state,
- `priority` determines rule selection.

---

# Rule Model

The implementation represents rules using:

```python
@dataclass
class Rule:

    name: str
    event: str
    condition: Callable[[Dict], bool]
    action: str
    priority: int
```

Rules are evaluated dynamically against the current state.

---

# Transition Semantics

System execution is modelled using labelled transitions.

A transition has the form:

```text
(s, e) ──a──▶ s'
```

where:

- `s` is the current state,
- `e` is the input event,
- `a` is the executed action,
- `s'` is the next state.

---

# Enabled Rules

A rule is enabled if:

```text
r.event = current_event
and
r.condition(state) = True
```

The implementation computes enabled rules using:

```python
def enabled_rules(rules, state, event):
    return [
        r for r in rules
        if r.event == event
        and r.condition(state)
    ]
```

---

# Priority-Based Selection

Among enabled rules, the system selects rules with maximal priority.

```text
max_priority = max(r.priority)
```

If multiple rules share maximal priority, deterministic tie-breaking is applied using rule names.

```python
maximal.sort(key=lambda r: r.name)
```

This ensures deterministic execution behaviour.

---

# Transition Function

State evolution is defined by the transition function:

```text
δ : State × Action → State
```

Example actions include:

```text
moveForward
turnLeft
emergencyStop
returnToCharge
dock
evade
```

Example implementation:

```python
if action == "moveForward":
    new_state["moving"] = True

elif action == "emergencyStop":
    new_state["moving"] = False
    new_state["emergency"] = True
```

---

# Idle Executions

If no rule is enabled for an event, the system performs an idle execution.

The semantic trace records:

```text
(event, ⊥, τ)
```

where:

- `⊥` denotes absence of rule execution,
- `τ` denotes an internal idle action.

The observable trace records:

```text
(event, τ, state)
```

Idle transitions are intentionally preserved in traces.

---

# Semantic Traces

Semantic traces retain detailed execution information.

Each semantic transition records:

```text
(event, rule_name, action)
```

Example:

```text
(sensor, r3, emergencyStop)
```

Semantic traces preserve:

- rule identifiers,
- internal execution decisions,
- operational details.

---

# Observable Traces

Observable traces abstract from internal rule identifiers.

Each observable transition records:

```text
(event, action, observable_state)
```

Example:

```text
(sensor, emergencyStop, state')
```

Observable traces are used for equivalence checking.

---

# Observable Equivalence

Two systems are observably equivalent if they generate identical observable traces for explored executions.

Formally:

```text
ObsTrace(S1) = ObsTrace(S2)
```

Observable equivalence ignores:

- rule names,
- internal decomposition,
- refactoring structure.

Observable equivalence preserves:

- externally visible behaviour,
- executed actions,
- resulting states.

---

# Refactoring Semantics

Correctness-preserving refactorings may alter:

- rule structure,
- rule decomposition,
- internal semantic traces.

However, observable traces must remain unchanged.

Safe transformations include:

- rule extraction,
- rule merging,
- dead rule elimination,
- condition simplification.

Unsafe transformations may introduce observable divergence.

---

# Counterexample Detection

When equivalence fails, the framework reports:

- initial state,
- event sequence,
- semantic traces,
- observable traces.

This supports debugging of unsafe refactorings.

---

# Execution Model

The prototype currently uses:

- randomized initial states,
- randomized event traces,
- bounded execution exploration,
- deterministic maximal-priority selection.

The implementation is intended for experimental semantic analysis rather than exhaustive formal verification.

---

# Current Limitations

The current implementation does not yet support:

- concurrency,
- probabilistic semantics,
- temporal logic verification,
- symbolic execution,
- SMT-based equivalence proofs.

---

# Future Directions

Planned extensions include:

- symbolic equivalence checking,
- Event-B integration,
- automated refactoring synthesis,
- concurrency semantics,
- SMT-assisted verification,
- scalable model checking.
