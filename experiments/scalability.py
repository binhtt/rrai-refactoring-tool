import time
import random

from rules import build_rules
from equivalence import check_equivalence


def generate_rule_specs(n):

    specs = []

    for i in range(n):

        specs.append({

            "name": f"r{i}",

            "event":
                random.choice([
                    "sensor",
                    "timer",
                    "watchdog"
                ]),

            "condition":
                "True",

            "action":
                random.choice([
                    "moveForward",
                    "turnLeft",
                    "evade",
                    "dock"
                ]),

            "priority":
                random.randint(1, 100)
        })

    return specs


def scalability_test():

    print("\n================================================")
    print("SCALABILITY EVALUATION")
    print("================================================")

    rule_sizes = [
        10,
        50,
        100,
        500,
        1000
    ]

    for size in rule_sizes:

        original_specs = generate_rule_specs(size)

        refactored_specs = list(original_specs)

        original_rules = build_rules(
            original_specs
        )

        refactored_rules = build_rules(
            refactored_specs
        )

        start = time.time()

        result = check_equivalence(
            original_rules,
            refactored_rules,
            iterations=1000
        )

        elapsed = time.time() - start

        print(f"\nRules: {size}")

        print(
            f"Observable equivalence: "
            f"{result}"
        )

        print(
            f"Execution time: "
            f"{elapsed:.4f} seconds"
        )


if __name__ == "__main__":

    scalability_test()
