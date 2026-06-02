# Experimental Evaluation

## Experiment 1

Formal Validation

Purpose:

Exhaustively validate theorem conditions over constructed state spaces.

Output:

- decomposition failures
- merge failures

---

## Experiment 2

Monte-Carlo Preservation Verification

Purpose:

Estimate behavioral equivalence over randomly generated states and traces.

Parameters:

- 5000 executions
- trace length = 20

Metrics:

- divergence count
- divergence rate
- average divergence position

---

## Experiment 3

Scalability Analysis

Sample sizes:

100
500
1000
2000
5000
10000

Metrics:

- runtime
- divergence rate

---

## Experiment 4

Statistical Analysis

30 repeated executions.

Metrics:

- mean runtime
- 95% confidence interval
- divergence confidence interval

---

## Experiment 5

Divergence Distribution

Unsafe refactorings are analyzed using

- first divergence position
- histogram visualization

---

## Complexity

Single trace execution

O(k·n)

Monte-Carlo verification

O(m·k·n)

Memory

O(k)

where

k = trace length

n = number of rules

m = number of samples
