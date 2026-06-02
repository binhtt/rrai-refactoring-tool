# ============================================================
# RRAI REFACTORING VERIFICATION FRAMEWORK
# IEEE ACCESS VERSION
#
# validation.py
#
# PART 4/7
# Formal Validation
# Benchmark Runner
# Theorem Experiments
# ============================================================

from semantics import (
    TraceExecutor,
    TraceEquivalence,
    PreservationChecker
)

from rulebases import (
    ORIGINAL_RB,
    SAFE_DECOMPOSITION_RB,
    SAFE_MERGE_RB,
    ORIGINAL_WITH_DEAD_RULE,
    SAFE_ELIMINATION_RB,
    SAFE_PRIORITY_RB,
    UNSAFE_PRIORITY_RB
)


# ============================================================
# FORMAL VALIDATOR
#
# Exhaustive theorem-based validation
# ============================================================

class FormalValidator:

    @staticmethod
    def validate(
        original_rb,
        refactored_rb,
        states
    ):

        exec1 = TraceExecutor(
            original_rb
        )

        exec2 = TraceExecutor(
            refactored_rb
        )

        failures = 0

        for state in states:

            events = ["sensor"]

            trace1 = exec1.execute(
                state,
                events
            )

            trace2 = exec2.execute(
                state,
                events
            )

            if not TraceEquivalence.equivalent(
                trace1,
                trace2
            ):
                failures += 1

        return failures


# ============================================================
# THEOREM-DRIVEN TEST SUITES
# ============================================================

class TheoremDrivenTests:

    @staticmethod
    def decomposition_states():

        states = []

        for obstacle in [False, True]:

            for speed in [False, True]:

                for front in [False, True]:

                    states.append({

                        "obstacle":
                            obstacle,

                        "highSpeed":
                            speed,

                        "frontObstacle":
                            front,

                        "collisionRisk":
                            False,

                        "batteryLow":
                            False,

                        "chargingStationNear":
                            False,

                        "goalVisible":
                            False,

                        "idle":
                            False,

                        "admin":
                            False,

                        "untrustedNetwork":
                            False
                    })

        return states

    @staticmethod
    def merge_states():

        states = []

        for battery in [False, True]:

            for station in [False, True]:

                states.append({

                    "obstacle":
                        False,

                    "highSpeed":
                        False,

                    "frontObstacle":
                        False,

                    "collisionRisk":
                        False,

                    "batteryLow":
                        battery,

                    "chargingStationNear":
                        station,

                    "goalVisible":
                        False,

                    "idle":
                        False,

                    "admin":
                        False,

                    "untrustedNetwork":
                        False
                })

        return states


# ============================================================
# BENCHMARK RUNNER
# ============================================================

class BenchmarkRunner:

    def __init__(self):

        self.results = {}

    def evaluate_pair(
        self,
        name,
        rb1,
        rb2
    ):

        checker = PreservationChecker(
            rb1,
            rb2
        )

        result = checker.run(
            iterations=5000
        )

        self.results[name] = result

        print("\n" + "=" * 60)
        print(name)
        print("=" * 60)

        print(
            "Equivalent:",
            result["equivalent"]
        )

        print(
            "Divergences:",
            result["divergence_count"]
        )

        print(
            "Divergence Rate:",
            round(
                result["divergence_rate"],
                4
            )
        )

        print(
            "Runtime:",
            round(
                result["execution_time"],
                4
            )
        )

        return result

    def run_all(self):

        self.evaluate_pair(
            "Lemma 1: Decomposition",
            ORIGINAL_RB,
            SAFE_DECOMPOSITION_RB
        )

        self.evaluate_pair(
            "Lemma 2: Merge",
            ORIGINAL_RB,
            SAFE_MERGE_RB
        )

        self.evaluate_pair(
            "Lemma 3: Elimination",
            ORIGINAL_WITH_DEAD_RULE,
            SAFE_ELIMINATION_RB
        )

        self.evaluate_pair(
            "Lemma 4: Priority Preservation",
            ORIGINAL_RB,
            SAFE_PRIORITY_RB
        )

        self.evaluate_pair(
            "Counterexample",
            ORIGINAL_RB,
            UNSAFE_PRIORITY_RB
        )

        return self.results


# ============================================================
# THEOREM EXPERIMENTS
# ============================================================

class TheoremExperiments:

    @staticmethod
    def run():

        print("\n")
        print("=" * 60)
        print("FORMAL VALIDATION")
        print("=" * 60)

        failures_decomposition = (
            FormalValidator.validate(
                ORIGINAL_RB,
                SAFE_DECOMPOSITION_RB,
                TheoremDrivenTests
                .decomposition_states()
            )
        )

        failures_merge = (
            FormalValidator.validate(
                ORIGINAL_RB,
                SAFE_MERGE_RB,
                TheoremDrivenTests
                .merge_states()
            )
        )

        print(
            "Decomposition Failures:",
            failures_decomposition
        )

        print(
            "Merge Failures:",
            failures_merge
        )

        return {

            "decomposition":
                failures_decomposition,

            "merge":
                failures_merge
        }


# ============================================================
# SANITY TEST
# ============================================================

if __name__ == "__main__":

    print("PART 4 OK")
