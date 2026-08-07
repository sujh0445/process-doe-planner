# Contributing

AI DOE Planner is an engineering decision-support project. Contributions
should preserve the separation between reproducible statistical evidence and
project-specific engineering judgment.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -q
python scripts/run_mvp_smoke.py
python scripts/check_public_release.py
```

## Contribution Rules

1. Add or update tests when changing a decision rule, response policy, risk
   gate, DOE generator, or report contract.
2. Keep equipment limits separate from engineer-approved DOE ranges and the
   actual levels used in one experiment round.
3. Do not turn exploratory p-values, capability estimates, or model rankings
   into automatic production approval.
4. Document the response type, spec direction, DOE stage, measurement method,
   and mechanism assumption behind a new reference example.
5. Do not commit raw production data, lecture material, transcripts,
   credentials, personal paths, or generated local outputs.

## Pull Requests

Keep changes focused and explain:

- the engineering decision being improved;
- the statistical or process evidence used;
- any rejected alternative;
- the tests and CLI workflows executed;
- remaining claim boundaries or known risks.
