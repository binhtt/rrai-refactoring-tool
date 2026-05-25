from semantics import (
    enabled_rules,
    select_rule,
    delta
)


def execute_trace(
    rules,
    initial_state,
    events
):

    state = initial_state.copy()

    semantic_trace = []
    observable_trace = []

    for event in events:

        enabled = enabled_rules(
            rules,
            state,
            event
        )

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

        rule = select_rule(enabled)

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
