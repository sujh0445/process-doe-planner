# Wire Bonding Mixed-Y Example

This synthetic example verifies that AI DOE Planner is not hard-coded to the
wafer-sawing case.

- `Pull force` is a lower-spec continuous Y. Its decision evidence uses the
  minimum, p05, lower margin, under-spec count, and Cpl eligibility.
- `Failure code` is a categorical guardrail Y. Codes 5-7 reject a condition,
  while code 4 marks it for confirmation.
- The best condition must satisfy both response types. A high pull-force mean
  does not override a risky fracture-mode code.

The values are demonstration data, not production data.
