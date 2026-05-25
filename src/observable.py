from semantics import delta


def execute_trace(rules, initial_state, events):

    state = initial_state.copy()

    semantic_trace = []
    observable_trace = []

    for event in events:

        enabled = [

            r for r in rules

            if r.event == event
            and r.condition(state)
        ]

        if not enabled:

            semantic_trace.append(
                (
                    event,
                    "⊥",
                    "τ"
                )
            )

            observable_trace.append(
                (
                    event,
                    "τ",
                    tuple(sorted(state.items()))
                )
            )

            continue

        max_priority = max(
            r.priority for r in enabled
        )

        maximal = [

            r for r in enabled

            if r.priority == max_priority
        ]

        maximal.sort(key=lambda r: r.name)

        rule = maximal[0]

        next_state = delta(
            state,
            rule.action
        )

        semantic_trace.append(
            (
                event,
                rule.name,
                rule.action
            )
        )

        observable_trace.append(
            (
                event,
                rule.action,
                tuple(sorted(next_state.items()))
            )
        )

        state = next_state

    return semantic_trace, observable_trace
