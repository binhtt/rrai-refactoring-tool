from rules import build_rules, original_specs, unsafe_specs
from equivalence import check_equivalence

original = build_rules(original_specs)

unsafe = build_rules(unsafe_specs)

print(check_equivalence(original, unsafe))
