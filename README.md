# RRAI Refactoring Verification Framework

A Python framework for verifying correctness-preserving rule refactorings
in reactive rule-based artificial intelligence (RRAI) systems.

This repository accompanies the paper:

> **A Calculus of Correctness-Preserving Rule Refactorings for Reactive
> Rule-Based Artificial Intelligence Systems**

The framework combines exhaustive finite-domain proof-obligation
verification with correspondence-based behavioural validation to evaluate
whether structural rule transformations preserve observable system
behaviour.

---

## Features

- End-to-end refactoring verification
  - automatic refactoring-type detection;
  - automatic identification of changed rules;
  - rule-base well-formedness and frame checks;
  - exhaustive proof-obligation checking;
  - structured witnesses for failed obligations;
  - counterexample generation.

- Supported refactorings
  - rule decomposition;
  - rule merging;
  - rule elimination;
  - priority adjustment.

- Correspondence-based behavioural validation
  - bidirectional comparison of maximal-rule choices;
  - refactoring-induced rule correspondence;
  - action and successor-state comparison;
  - first-divergence detection.

- Negative-control experiments
  - invalid merge;
  - invalid priority adjustment;
  - unsafe decomposition.

- Experimental evaluation
  - complete finite-domain verification;
  - 10,000-trace behavioural validation;
  - first-divergence-position analysis;
  - scalability evaluation of complete correspondence-based
    behavioural validation.

---

## Repository Structure

```text
rrai-refactoring-tool/
├── docs/
│   ├── architecture.md
│   ├── experiments.md
│   ├── refactoring_theorems.md
│   ├── results.md
│   └── semantics.md
│
├── examples/
│   ├── complete_demo.py
│   ├── counterexample.py
│   ├── decomposition_example.py
│   ├── elimination_example.py
│   ├── merge_example.py
│   └── priority_example.py
│
├── results/
│   ├── divergence.png
│   ├── proof_obligations.csv
│   ├── table2_structural_changes.csv
│   ├── table3_valid_transformations.csv
│   ├── table4_invalid_transformations.csv
│   ├── table5_counterexamples.csv
│   └── table6_scalability.csv
│
├── src/
│   ├── analysis.py
│   ├── core.py
│   ├── main.py
│   ├── reporting.py
│   ├── rulebases.py
│   ├── semantics.py
│   └── validation.py
│
├── LICENSE
├── README.md
└── requirements.txt
```

The `results/` directory contains the manuscript-facing tables and
figure checked into the repository.

---

## Correctness-Preserving Refactorings

The artifact evaluates four preservation-valid transformations:

- decomposition;
- merging;
- elimination;
- priority adjustment.

The main case-study sequence is:

```text
Original
   |
   | Priority adjustment
   v
Priority-adjusted system
   |
   | Merge r11,r4 -> r15
   v
Merged system
   |
   | Decompose r3 -> {r3a,r3b}
   v
Decomposed system
```

### Rule Merging

The merge is implemented as a genuine two-to-one transformation:

```text
r11 ----\
         >---- r15
r4  ----/
```

The refactoring-induced correspondence contains:

```text
(r11, r15)
(r4,  r15)
```

The implementation therefore directly represents the
cardinality-changing merge formalised in the paper.

The structural effect is:

```text
14 rules -> 13 rules
7 priority relations -> 6 priority relations
```

at the merging stage.

---

## Negative Controls

Three intentionally invalid transformations are evaluated:

- invalid merge;
- invalid priority adjustment;
- unsafe decomposition.

### Invalid Priority Adjustment

The invalid-priority experiment removes:

```text
r9 < r3
```

without adding the reverse relation.

Thus, `r9` and `r3` become incomparable when both are enabled.

This corresponds to the intervention described in the manuscript rather
than priority reversal.

### Invalid Merge

The invalid-merge target is kept structurally well formed.

Priority relations incident to removed rules are not retained as
dangling relations. The negative control deliberately violates the
required priority-compatibility condition involving the merged rule.

---

## Complete Finite Verification Domain

Proof-obligation verification is performed over the complete finite
state-event domain

```text
D = S x E
```

rather than transformation-specific projected domains.

The case study contains 16 Boolean state predicates and three events:

```text
E = {sensor, timer, watchdog}
```

Therefore:

```text
|S| = 2^16 = 65,536
|E| = 3
|D| = 65,536 x 3 = 196,608
```

All 196,608 state-event contexts are exhaustively considered for every
preservation-valid and intentionally invalid transformation.

---

## End-to-End Verification

The verification implementation performs the following workflow:

1. validates rule-base well-formedness;
2. detects the refactoring type;
3. identifies changed rules;
4. checks applicable frame conditions;
5. evaluates transformation-specific proof obligations;
6. constructs the refactoring-induced rule correspondence;
7. records failed obligations and witnesses;
8. searches for a behavioural counterexample when applicable.

The detailed summary is stored in:

```text
results/proof_obligations.csv
```

Expected results are:

| Transformation | Detected Type | Status |
|---|---|---|
| Priority adjustment | PriorityAdjustment | Pass |
| Merging | Merge | Pass |
| Decomposition | Decomposition | Pass |
| Elimination | Elimination | Pass |
| Invalid merge | Merge | Fail |
| Invalid priority adjustment | PriorityAdjustment | Fail |
| Unsafe decomposition | Decomposition | Fail |

The negative controls fail the expected preservation conditions:

| Transformation | Failed obligation(s) |
|---|---|
| Invalid merge | PriorityCompatibility |
| Invalid priority adjustment | MaximalRulePreservation |
| Unsafe decomposition | GuardPartition; ActionPreservation |

---

## Manuscript Results

### Table 2 — Structural Changes

Data:

```text
results/table2_structural_changes.csv
```

| Stage | Rules | Priority relations | Structural change |
|---|---:|---:|---|
| Original | 14 | 6 | - |
| Priority adjustment | 14 | 7 | Add `r6 < r4` |
| Merging | 13 | 6 | `r11,r4 -> r15` |
| Decomposition | 14 | 8 | `r3 -> {r3a,r3b}` |

---

### Table 3 — Preservation-Valid Transformations

Data:

```text
results/table3_valid_transformations.csv
```

| Transformation | Proof obligations | Divergences | Rate |
|---|---|---:|---:|
| Decomposition | Pass | 0 | 0.00% |
| Merging | Pass | 0 | 0.00% |
| Elimination | Pass | 0 | 0.00% |
| Priority adjustment | Pass | 0 | 0.00% |

All four preservation-valid transformations produce zero divergence in
the 10,000 sampled executions.

---

### Table 4 — Intentionally Invalid Transformations

Data:

```text
results/table4_invalid_transformations.csv
```

| Transformation | Failed obligation(s) | Divergences | Rate |
|---|---|---:|---:|
| Invalid merge | PC | 2466 | 24.66% |
| Invalid priority adjustment | MRP | 2459 | 24.59% |
| Unsafe decomposition | GP, AP | 4929 | 49.29% |

where:

- `PC` = PriorityCompatibility;
- `MRP` = MaximalRulePreservation;
- `GP` = GuardPartition;
- `AP` = ActionPreservation.

---

### Table 5 — Counterexamples

Data:

```text
results/table5_counterexamples.csv
```

| Transformation | Proof obligations | Violated condition | Counterexample |
|---|---|---|---|
| Invalid merge | Fail | PriorityCompatibility | Found |
| Invalid priority adjustment | Fail | MaximalRulePreservation | Found |
| Unsafe decomposition | Fail | GuardPartition; ActionPreservation | Found |

Counterexamples provide diagnostic evidence for transformations that
violate preservation conditions.

---

### Table 6 — Scalability and Execution Cost

Data:

```text
results/table6_scalability.csv
```

The measured operation is:

```text
full_correspondence_based_behavioural_validation
```

Each workload uses traces of length 20 and is repeated 30 times.

| Number of traces | Execution time (s), mean ± SD |
|---:|---:|
| 100 | 0.163 ± 0.050 |
| 500 | 0.746 ± 0.179 |
| 1,000 | 1.520 ± 0.358 |
| 2,000 | 3.031 ± 0.568 |
| 5,000 | 7.638 ± 0.731 |
| 10,000 | 15.266 ± 0.361 |

The timing experiment measures complete correspondence-based behavioural
validation rather than trace generation alone.

Wall-clock timing may vary across machines and executions. The checked-in
CSV contains the aggregate measurements used in the accompanying
manuscript.

---

## Figure 3 — First-Divergence Positions

The manuscript figure is stored in:

```text
results/divergence.png
```

The x-axis represents the first-divergence position in the execution
trace.

The y-axis represents the number of divergent executions whose first
observable behavioural difference occurs at that position.

The figure includes:

- invalid merge;
- invalid priority adjustment;
- unsafe decomposition.

The preservation-valid transformations are excluded because no sampled
behavioural divergence was observed.

---

## Behavioural Validation

The default behavioural experiment uses:

```text
number of traces = 10,000
trace length     = 20
random seed      = 20260723
```

The same generated initial states and event sequences are reused across
the evaluated transformations.

At every execution step, the framework:

1. computes enabled rules;
2. computes maximal enabled rules;
3. compares maximal choices bidirectionally under the refactoring-induced
   correspondence relation;
4. compares selected-rule correspondence, actions, and successor states;
5. continues the sampled trace using a deterministic corresponding rule
   pair when all maximal choices correspond.

Execution-based validation provides complementary empirical evidence.
It is not used as a substitute for proof-obligation verification.

---

## Scalability Evaluation

The scalability experiment measures complete correspondence-based
behavioural validation.

The timed procedure includes:

- rule enabling;
- maximal-rule computation;
- bidirectional correspondence checking;
- action comparison;
- successor-state comparison;
- deterministic continuation of corresponding sampled traces.

Input generation is performed outside the timed region.

The evaluated workloads are:

```text
100
500
1000
2000
5000
10000
```

with:

```text
trace length = 20
repetitions  = 30
```

The checked-in aggregate measurements are provided in:

```text
results/table6_scalability.csv
```

---

## Running the Framework

### Requirements

Python 3.10 or later is recommended.

Install dependencies using:

```bash
python -m pip install -r requirements.txt
```

The dependency file includes:

```text
numpy>=1.24
matplotlib>=3.8
pandas>=2.0
pytest>=7.0
```

### Complete Workflow

From the repository root:

```bash
python src/main.py
```

The default configuration performs:

```text
complete finite-domain proof-obligation verification
10,000 behavioural-validation traces per transformation
trace length = 20
30 scalability repetitions per workload
```

### Complete Demonstration

```bash
python examples/complete_demo.py
```

### Individual Examples

```bash
python examples/decomposition_example.py
python examples/merge_example.py
python examples/elimination_example.py
python examples/priority_example.py
python examples/counterexample.py
```

The refactoring examples use the same complete finite verification
domain as the principal verification workflow.

---

## Documentation

Additional documentation is available in:

```text
docs/
├── architecture.md
├── experiments.md
├── refactoring_theorems.md
├── results.md
└── semantics.md
```

- `architecture.md` — framework architecture;
- `experiments.md` — experimental methodology;
- `refactoring_theorems.md` — preservation conditions;
- `results.md` — interpretation of the experimental results;
- `semantics.md` — operational semantics.

---

## Reproducibility

The checked-in `results/` directory contains the exact manuscript-facing
CSV files and Figure 3 used in the revised paper.

Finite-domain proof-obligation checking is deterministic.

Behavioural validation uses a fixed random seed, so its sampled execution
inputs and divergence counts can be regenerated.

Scalability results measure wall-clock execution time and may therefore
vary across machines or repeated executions. Re-execution reproduces the
experimental procedure, while the checked-in Table 6 CSV records the
measurements reported in the manuscript.

---

## Citation

If you use this framework in your research, please cite the accompanying
paper.

```bibtex
@article{Trinh2026,
  author = {Thanh-Binh Trinh and Van Cuong Nguyen and Nguyen Viet Ha},
  title  = {A Calculus of Correctness-Preserving Rule Refactorings for Reactive Rule-Based Artificial Intelligence Systems},
  year   = {2026},
  note   = {Preprint}
}
```

Please update the citation with the journal, volume, pages, and DOI after
publication.

---

## License

This project is released under the MIT License.
