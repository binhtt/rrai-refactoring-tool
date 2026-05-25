from observable import execute_trace

from simulator import (
    random_state,
    random_event_trace
)


def check_equivalence(
    original_rules,
    refactored_rules,
    iterations=10000
):

    for _ in range(iterations):

        state = random_state()

        events = random_event_trace(20)

        sem1, obs1 = execute_trace(
            original_rules,
            state,
            events
        )

        sem2, obs2 = execute_trace(
            refactored_rules,
            state,
            events
        )

        if obs1 != obs2:

            print("\n================================================")
            print("COUNTEREXAMPLE FOUND")
            print("================================================")

            print("\nInitial state:")
            print(state)

            print("\nEvents:")
            print(events)

            print("\nOriginal semantic trace:")
            print(sem1)

            print("\nRefactored semantic trace:")
            print(sem2)

            print("\nOriginal observable trace:")
            print(obs1)

            print("\nRefactored observable trace:")
            print(obs2)

            return False

    return True
