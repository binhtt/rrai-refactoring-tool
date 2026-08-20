# RRAI Refactoring Verification Framework

A Python framework for verifying correctness-preserving rule refactorings in reactive rule-based artificial intelligence (RRAI) systems.

This repository accompanies the paper:

> **A Calculus of Correctness-Preserving Rule Refactorings for Reactive Rule-Based Artificial Intelligence Systems**

The framework combines exhaustive finite-domain proof-obligation verification with execution-based behavioural validation to evaluate whether structural rule transformations preserve observable system behaviour.

---

## Features

- End-to-end refactoring verification
  - Automatic refactoring-type detection
  - Automatic identification of changed rules
  - Rule-base well-formedness and frame checks
  - Exhaustive proof-obligation checking
  - Structured witnesses for failed obligations
  - Counterexample generation

- Supported refactoring classes
  - Rule decomposition
  - Rule merging
  - Rule elimination
  - Priority adjustment

- Correspondence-based behavioural validation
  - Bidirectional comparison of maximal-rule choices
  - Rule-correspondence checking
  - Action and successor-state comparison
  - First-divergence detection

- Negative-control experiments
  - Unsafe decomposition
  - Invalid merge
  - Invalid priority adjustment

- Reproducibility support
  - Manuscript-ready Tables 2--6
  - Figure 3 in PNG and PDF formats
  - Raw scalability measurements
  - Algorithm-1 verification results
  - Experimental metadata

---

## Repository Structure

```text
.
├── src
│   ├── core.py
│   ├── semantics.py
│   ├── rulebases.py
│   ├── validation.py
│   ├── analysis.py
│   ├── reporting.py
│   └── main.py
│
├── examples
│   ├── decomposition_example.py
│   ├── merge_example.py
│   ├── elimination_example.py
│   ├── priority_example.py
│   ├── counterexample.py
│   └── complete_demo.py
│
├── docs
│   ├── architecture.md
│   ├── semantics.md
│   ├── refactoring_theorems.md
│   ├── experiments.md
│   └── results.md
│
├── results
│   ├── algorithm_results.json
│   ├── behavioural_validation.csv
│   ├── counterexamples.json
│   ├── divergence_positions.json
│   ├── experiment_metadata.json
│   ├── figure3_divergence_positions.pdf
│   ├── figure3_divergence_positions.png
│   ├── main_sequence.json
│   ├── proof_obligations.csv
│   ├── scalability.csv
│   ├── scalability_runs.csv
│   ├── table2_structural_changes.csv
│   ├── table3_valid_transformations.csv
│   ├── table4_invalid_transformations.csv
│   ├── table5_counterexamples.csv
│   └── table6_scalability.csv
│
├── requirements.txt
└── README.md
```

---

## Implemented Refactorings

### Correctness-Preserving Refactorings

The artifact evaluates four preservation-valid transformations:

- Rule decomposition
- Rule merging
- Rule elimination
- Priority adjustment

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

The merge is implemented as an actual two-to-one transformation:

```text
r11 ----\
         >---- r15
r4  ----/
```

Thus, the implementation directly represents the many-to-one correspondence

```text
(r11, r15)
(r4,  r15)
```

and reproduces the cardinality-changing merge described in the manuscript.

### Negative Controls

Three intentionally invalid transformations are included:

- Invalid merge
- Invalid priority adjustment
- Unsafe decomposition

The invalid priority-adjustment control removes the priority relation

```text
r9 < r3
```

without introducing the reverse relation. Therefore, `r9` and `r3` become incomparable when both are enabled, matching the intervention described in the manuscript.

The invalid-merge rule base is kept structurally well formed: priority relations incident to removed rules are removed before the intended priority-compatibility violation is introduced.

---

## Complete Finite Verification Domain

Algorithm 1 is evaluated over the complete finite state-event domain

```text
D = S x E
```

rather than transformation-specific projected domains.

The case study contains 16 Boolean state predicates and three events:

```text
E = {sensor, timer, watchdog}
```

Therefore,

```text
|S| = 2^16 = 65,536
|E| = 3
|D| = 65,536 x 3 = 196,608
```

state-event contexts are exhaustively considered for each transformation.

This removes the need for manually selected transformation-specific verification domains.

---

## Algorithm 1 Verification

The implementation provides an end-to-end verification procedure that:

1. checks rule-base well-formedness;
2. detects the refactoring type;
3. identifies the changed rules;
4. constructs the transformation-induced correspondence;
5. checks the applicable preservation obligations over the complete finite domain;
6. records witnesses for failed obligations; and
7. generates a behavioural counterexample when one is found.

The complete structured results are stored in:

```text
results/algorithm_results.json
```

A tabular summary is stored in:

```text
results/proof_obligations.csv
```

Expected results:

| Transformation | Detected Type | Status |
|---|---|---|
| Priority adjustment | PriorityAdjustment | Pass |
| Merging | Merge | Pass |
| Decomposition | Decomposition | Pass |
| Elimination | Elimination | Pass |
| Invalid merge | Merge | Fail |
| Invalid priority adjustment | PriorityAdjustment | Fail |
| Unsafe decomposition | Decomposition | Fail |

The intentionally invalid transformations fail the expected preservation obligations:

| Transformation | Failed obligation(s) |
|---|---|
| Invalid merge | PriorityCompatibility |
| Invalid priority adjustment | MaximalRulePreservation |
| Unsafe decomposition | GuardPartition; ActionPreservation |

---

## Structural Validation

The generated structural summary is stored in:

```text
results/table2_structural_changes.csv
```

It reproduces the structural changes reported in Table 2:

| Stage | Rules | Priority relations | Structural change |
|---|---:|---:|---|
| Original | 14 | 6 | - |
| Priority adjustment | 14 | 7 | Add `r6 < r4` |
| Merging | 13 | 6 | `r11,r4 -> r15` |
| Decomposition | 14 | 8 | `r3 -> {r3a,r3b}` |

In particular, the merge changes the rule-base cardinality from 14 to 13 rules.

---

## Behavioural Validation

Execution-based behavioural validation complements the exhaustive proof-obligation verification.

For the default experiment, the framework generates:

```text
10,000 traces
20 events per trace
seed = 20260723
```

The same generated initial states and event sequences are reused for all transformation cases.

At each execution step, behavioural validation compares the maximal-rule choices of the original and transformed systems bidirectionally under the transformation-induced correspondence relation. It additionally compares the executed actions and successor states.

The aggregate results are stored in:

```text
results/behavioural_validation.csv
```

The manuscript-facing valid-transformation results are stored in:

```text
results/table3_valid_transformations.csv
```

Expected results:

| Transformation | Proof obligations | Divergences | Rate |
|---|---|---:|---:|
| Decomposition | Pass | 0 | 0.00% |
| Merging | Pass | 0 | 0.00% |
| Elimination | Pass | 0 | 0.00% |
| Priority adjustment | Pass | 0 | 0.00% |

All four preservation-valid transformations therefore exhibit zero behavioural divergences in the 10,000 sampled executions.

---

## Negative-Control Results

Results for intentionally invalid transformations are stored in:

```text
results/table4_invalid_transformations.csv
```

Expected results:

| Transformation | Failed obligation(s) | Divergences | Rate |
|---|---|---:|---:|
| Invalid merge | PC | 2466 | 24.66% |
| Invalid priority adjustment | MRP | 2459 | 24.59% |
| Unsafe decomposition | GP, AP | 4929 | 49.29% |

where:

- `PC` = PriorityCompatibility
- `MRP` = MaximalRulePreservation
- `GP` = GuardPartition
- `AP` = ActionPreservation

The invalid-priority result corresponds to deletion of `r9 < r3`, not priority reversal.

Structured proof-obligation and behavioural counterexamples are stored in:

```text
results/counterexamples.json
```

A manuscript-facing counterexample summary is stored in:

```text
results/table5_counterexamples.csv
```

---

## First-Divergence Analysis

For each divergent execution, the framework records the first trace position at which the original and transformed systems cease to correspond.

The raw positions are stored in:

```text
results/divergence_positions.json
```

Figure 3 is generated as:

```text
results/figure3_divergence_positions.png
results/figure3_divergence_positions.pdf
```

Only the three intentionally invalid transformations are included in this figure because the preservation-valid transformations exhibit no behavioural divergence.

---

## Scalability Evaluation

The scalability experiment measures the execution time of the **complete correspondence-based behavioural-validation procedure**.

The timed operation includes:

- enabled-rule computation;
- maximal-rule computation;
- bidirectional rule-correspondence checking;
- action comparison;
- successor-state comparison; and
- continuation of the corresponding execution traces.

Random input generation is performed outside the timed region.

The experiment uses the preservation-valid decomposition transformation and keeps the rule-base structure and trace length fixed while varying only the number of sampled traces.

The evaluated workloads are:

```text
100
500
1000
2000
5000
10000
```

traces, with:

```text
trace length = 20
repetitions = 30
```

Aggregate timing results are stored in:

```text
results/scalability.csv
results/table6_scalability.csv
```

The exact timing of every repetition is stored in:

```text
results/scalability_runs.csv
```

The default experiment therefore records:

```text
6 workloads x 30 repetitions = 180 raw timing runs
```

The submitted Table 6 is generated directly from these raw measurements.

---

## Reproducibility

### Requirements

Python 3.10 or later is recommended.

Install the dependencies from a clean environment:

```bash
python -m pip install -r requirements.txt
```

The dependency file contains:

```text
numpy>=1.24
matplotlib>=3.8
pandas>=2.0
pytest>=7.0
```

### Run the Complete Experiment

From the repository root, execute:

```bash
python src/main.py
```

The default run performs:

```text
complete finite-domain proof-obligation verification
10,000 behavioural-validation traces per transformation
20 events per trace
30 scalability repetitions per workload
```

and regenerates the complete contents of the `results/` directory.

### Smaller Development Run

For a faster development check:

```bash
python src/main.py \
    --traces 1000 \
    --trace-length 20 \
    --repetitions 5
```

These reduced settings are intended only for development and do not reproduce the manuscript results.

---

## Reproducing the Manuscript Results

To reproduce the submitted experimental results:

```bash
python -m pip install -r requirements.txt
python src/main.py
```

The command regenerates:

```text
Table 2 -> results/table2_structural_changes.csv
Table 3 -> results/table3_valid_transformations.csv
Table 4 -> results/table4_invalid_transformations.csv
Table 5 -> results/table5_counterexamples.csv
Table 6 -> results/table6_scalability.csv
Figure 3 -> results/figure3_divergence_positions.png
            results/figure3_divergence_positions.pdf
```

Supporting raw and structured data are also regenerated:

```text
results/algorithm_results.json
results/proof_obligations.csv
results/behavioural_validation.csv
results/counterexamples.json
results/divergence_positions.json
results/scalability.csv
results/scalability_runs.csv
results/main_sequence.json
results/experiment_metadata.json
```

`experiment_metadata.json` records the verification-domain configuration, behavioural-validation parameters, scalability settings, and measured operation.

---

## Documentation

Additional documentation is available in the `docs/` directory:

- `architecture.md` — framework architecture
- `semantics.md` — operational semantics
- `refactoring_theorems.md` — correctness-preserving refactorings
- `experiments.md` — experimental methodology
- `results.md` — interpretation of generated results

---

## Citation

If you use this framework in your research, please cite the accompanying paper.

```bibtex
@article{Trinh2026,
  author = {Thanh-Binh Trinh and Van Cuong Nguyen and Nguyen Viet Ha},
  title  = {A Calculus of Correctness-Preserving Rule Refactorings for Reactive Rule-Based Artificial Intelligence Systems},
  year   = {2026},
  note   = {Preprint}
}
```

Please update the citation with the journal, volume, pages, and DOI after publication.

---

## License

This project is released under the MIT License.
