from rules import build_rules, original_specs, safe_specs
from equivalence import check_equivalence

original = build_rules(original_specs)

safe = build_rules(safe_specs)

print(check_equivalence(original, safe))
