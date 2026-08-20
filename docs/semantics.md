# Operational Semantics

## Overview

This document describes the operational semantics implemented by the
RRAI Refactoring Verification Framework.

The semantics define how reactive rules are enabled, how priority affects
maximal rule choices, how state transitions are produced, and how
original and refactored systems are compared using a refactoring-induced
rule-correspondence relation.

The implementation is primarily provided by `src/core.py` and
`src/semantics.py`.

---

# Rule Model

A reactive rule is represented as

\[
r=(id,event,guard,action),
\]

where:

- \(id\) uniquely identifies the rule;
- \(event\) specifies the triggering event;
- \(guard\) is a Boolean predicate over the current state;
- \(action\) specifies the state transition performed when the rule is
  selected.

In the implementation, these components are represented by the `Rule`
data structure in `src/core.py`.

Priority is not stored as an attribute of an individual rule.
Instead, a rule base is represented by a set of rules together with a
separate strict priority relation

\[
\prec\ \subseteq R\times R.
\]

A pair

\[
(r_i,r_j)\in\prec
\]

means that \(r_j\) has higher priority than \(r_i\) whenever both rules
are enabled.

---

# System State

A system state is a Boolean valuation of the predicates used by the
case-study model.

Formally,

\[
s:P\rightarrow\{\textit{true},\textit{false}\},
\]

where \(P\) is the finite predicate set.

The implementation represents a state as a mapping from predicate names
to Boolean values.

Actions transform the current state into a successor state:

\[
s' = A_r(s),
\]

where \(A_r\) denotes the state-transition function associated with
rule \(r\).

Actions that do not explicitly modify a state predicate are treated as
observational actions and leave the state unchanged.

---

# Events

The case study uses the finite event set

\[
E=\{sensor,timer,watchdog\}.
\]

Rule enabling therefore depends on both the current state and the
currently processed event.

---

# Enabled Rules

For a rule base \(R\), state \(s\), and event \(e\), the enabled-rule
set is

\[
Enabled_R(s,e)=
\{r\in R
\mid event(r)=e
\land guard(r,s)=\textit{true}\}.
\]

Thus, a rule is enabled only when:

1. its triggering event matches the current event; and
2. its guard evaluates to true in the current state.

Enabled-rule computation is implemented in `src/semantics.py`.

---

# Maximal Enabled Rules

Several rules may be enabled for the same state-event context.

The priority relation is used to determine which enabled rules are
maximal.

For a priority relation \(\prec\),

\[
MaxEnabled_R(s,e)=
\left\{
r\in Enabled_R(s,e)
\mid
\nexists r'\in Enabled_R(s,e):
r\prec r'
\right\}.
\]

A pair

\[
r\prec r'
\]

means that \(r'\) has higher priority than \(r\).

If several incomparable maximal rules remain, the operational model
permits multiple possible maximal choices.

This nondeterminism is important for correspondence-based behavioural
comparison.

---

# Rule Selection for Sampled Execution

Behavioural validation must continue along a concrete execution after
the maximal-rule sets have been computed.

The implementation therefore uses deterministic lexicographic ordering
only as an execution mechanism for selecting a corresponding rule pair
after the complete maximal-choice correspondence check has succeeded.

This deterministic continuation policy does not replace the
system-level nondeterministic semantics.

Before a sampled execution is continued, the framework checks
bidirectional correspondence between all maximal choices in the original
and transformed systems.

---

# State Transition

For state \(s\), event \(e\), selected rule \(r\), action \(a\), and
successor state \(s'\), a labelled transition has the form

\[
s\xrightarrow{e,r,a}s'.
\]

The implementation records:

- the triggering event;
- the selected rule;
- the executed action;
- the state before execution;
- the state after execution.

If no rule is selected for an event, the execution uses a no-operation
transition with action `tau`, leaving the state unchanged.

Single-step execution and the associated transition construction are
implemented in `src/semantics.py`.

---

# Execution Traces

A finite execution trace consists of a sequence of labelled transitions:

\[
s_0
\xrightarrow{e_1,r_1,a_1}
s_1
\xrightarrow{e_2,r_2,a_2}
\cdots
\xrightarrow{e_k,r_k,a_k}
s_k.
\]

The event sequence is supplied as an execution input.

During behavioural validation, the original and transformed systems are
executed from the same initial state and under the same event sequence.

---

# Refactoring-Induced Rule Correspondence

Structural refactoring may change rule identities and rule cardinality.
Consequently, behavioural equivalence cannot in general require
identical rule names.

The framework therefore uses a refactoring-induced correspondence
relation

\[
C_{Ref}\subseteq R\times R',
\]

where \(R\) is the original rule set and \(R'\) is the transformed rule
set.

Unchanged rules normally correspond by identity.

For decomposition, one original rule may correspond to several
transformed rules. For example,

\[
(r3,r3a)\in C_{Ref}
\]

and

\[
(r3,r3b)\in C_{Ref}.
\]

For merging, several original rules may correspond to one transformed
rule. In the case study,

\[
(r11,r15)\in C_{Ref}
\]

and

\[
(r4,r15)\in C_{Ref}.
\]

Thus, the correspondence relation explicitly supports changes in rule
cardinality.

---

# Correspondence of Maximal Choices

For each state-event context, behavioural comparison first computes the
maximal enabled sets of the original and transformed systems.

Let

\[
M=MaxEnabled_R(s,e)
\]

and

\[
M'=MaxEnabled_{R'}(s,e).
\]

The framework checks bidirectional correspondence:

- every rule in \(M\) must have a corresponding rule in \(M'\);
- every rule in \(M'\) must have a corresponding rule in \(M\).

This prevents deterministic tie-breaking from hiding a behavioural
difference between the sets of possible maximal choices.

Only after this check succeeds is a corresponding rule pair selected to
continue the sampled execution.

---

# Behavioural Comparison

The original and transformed systems are compared under identical
initial states and event sequences.

A corresponding transition pair has the form

\[
s\xrightarrow{e,r,a}s'
\]

and

\[
s\xrightarrow{e,r',a'}s'',
\]

where the selected rules satisfy

\[
(r,r')\in C_{Ref}.
\]

Behavioural comparison considers:

- the triggering event;
- bidirectional correspondence of maximal rule choices;
- correspondence of the selected rules under \(C_{Ref}\);
- executed actions;
- successor states.

A behavioural mismatch is reported when the required transition
correspondence fails.

Therefore, refactored executions are not required to use identical rule
identifiers. They are required to use rules related by the
refactoring-induced correspondence relation.

---

# Counterexamples

When a behavioural divergence is identified, the framework records
diagnostic information about the first non-corresponding transition.

A counterexample may identify a mismatch involving:

- maximal-rule correspondence;
- selected-rule correspondence;
- executed actions;
- successor states.

For the experimental negative controls, the framework also records the
position at which the first behavioural divergence occurs.

These counterexamples provide diagnostic evidence for failed
transformations.

---

# Proof-Obligation Verification

Operational semantics are also used by the finite-domain verification
procedure.

The verifier evaluates the applicable preservation conditions over the
complete finite state-event domain

\[
D=S\times E.
\]

For the case study, this domain contains 196,608 state-event contexts.

Proof-obligation verification and execution-based behavioural validation
serve different purposes:

- proof-obligation verification checks the sufficient conditions of the
  applicable preservation result;
- behavioural validation evaluates sampled executions and provides
  complementary empirical and diagnostic evidence.

Sampled behavioural validation is therefore not used as a substitute for
the formal preservation conditions.

---

# Reproducibility

Finite-domain proof-obligation verification is deterministic.

Behavioural validation uses pseudo-randomly generated initial states and
event sequences with a fixed default seed:

```text
20260723
```

The same generated execution inputs are reused for the original and
transformed systems.

This fixed seed allows the behavioural-validation inputs and divergence
counts reported for the experiment to be reproduced.

Wall-clock timing measurements are environment dependent and may vary
between executions even when the same random seed and experimental
configuration are used.

---

# Relation to the Paper

The implementation follows the operational model used by the
correctness-preservation framework in the accompanying paper.

In particular, it preserves the distinction between:

- rule-local guards and actions;
- the rule-base-level priority relation;
- maximal-rule nondeterminism;
- refactoring-induced rule correspondence;
- exhaustive proof-obligation verification;
- sampled behavioural validation.

These semantics provide the common execution basis for the
proof-obligation checks, behavioural comparison, counterexample
generation, and scalability experiment.
