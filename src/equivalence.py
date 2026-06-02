# ============================================================
# TRACE EQUIVALENCE
#
# IMPORTANT:
#
# Refactoring may rename rules.
#
# Therefore equivalence compares:
#
# (event, action)
#
# instead of
#
# (event, rule, action)
# ============================================================

class TraceEquivalence:

    # --------------------------------------------------------
    # Projection
    # --------------------------------------------------------

    @staticmethod
    def normalize(
        trace: List[TraceStep]
    ):

        return [

            (
                step.event,
                step.action
            )

            for step in trace
        ]

    # --------------------------------------------------------
    # Equivalence
    # --------------------------------------------------------

    @staticmethod
    def equivalent(
        trace1: List[TraceStep],
        trace2: List[TraceStep]
    ) -> bool:

        return (

            TraceEquivalence.normalize(
                trace1
            )

            ==

            TraceEquivalence.normalize(
                trace2
            )
        )

    # --------------------------------------------------------
    # First Divergence
    # --------------------------------------------------------

    @staticmethod
    def first_divergence(
        trace1: List[TraceStep],
        trace2: List[TraceStep]
    ):

        t1 = (
            TraceEquivalence.normalize(
                trace1
            )
        )

        t2 = (
            TraceEquivalence.normalize(
                trace2
            )
        )

        n = min(
            len(t1),
            len(t2)
        )

        for i in range(n):

            if t1[i] != t2[i]:

                return i

        if len(t1) != len(t2):

            return n

        return None


# ============================================================
# PRESERVATION CHECKER
#
# Monte-Carlo behavioural verification
# ============================================================

class PreservationChecker:

    def __init__(
        self,
        original_rb: RuleBase,
        refactored_rb: RuleBase
    ):

        self.original_rb = (
            original_rb
        )

        self.refactored_rb = (
            refactored_rb
        )

    def run(
        self,
        iterations: int = 5000,
        trace_length: int = 20
    ):

        original_exec = (
            TraceExecutor(
                self.original_rb
            )
        )

        refactored_exec = (
            TraceExecutor(
                self.refactored_rb
            )
        )

        divergences = []

        start_time = time.time()

        for _ in range(iterations):

            state = random_state()

            events = random_event_trace(
                trace_length
            )

            trace1 = (
                original_exec.execute(
                    state,
                    events
                )
            )

            trace2 = (
                refactored_exec.execute(
                    state,
                    events
                )
            )

            div = (
                TraceEquivalence
                .first_divergence(
                    trace1,
                    trace2
                )
            )

            if div is not None:

                divergences.append(
                    div
                )

        elapsed = (
            time.time()
            - start_time
        )

        return {

            "equivalent":
                len(divergences) == 0,

            "divergence_count":
                len(divergences),

            "divergence_rate":
                len(divergences)
                / iterations,

            "avg_divergence_position":
                (
                    float(
                        np.mean(
                            divergences
                        )
                    )
                    if divergences
                    else 0.0
                ),

            "execution_time":
                elapsed,

            "divergences":
                divergences
        }
