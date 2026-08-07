# DOE Request Templates

This folder contains copy-and-edit YAML request templates for the AI DOE Planner.

Use these templates when starting a new DOE project:

1. Copy one request YAML into a new project folder.
2. Replace project name, equipment, response specs, factor levels, and measurement methods.
3. Keep `levels` as the actual DOE experiment levels, not the machine minimum/maximum values.
4. Put measured result data in a CSV/XLSX file with the same factor and response column names.
5. Run `ai-doe design` before the experiment and `ai-doe analyze` after measurement.

Example:

```bash
cd ai-doe-planner

.venv/bin/ai-doe design \
  --request templates/process_requests/wafer_sawing_request.yaml \
  --out outputs/example_design.csv

.venv/bin/ai-doe analyze \
  --request templates/process_requests/wafer_sawing_request.yaml \
  --data path/to/results.csv \
  --out outputs/example_report.md \
  --next-doe-out outputs/example_next_doe.csv \
  --plots-out outputs/example_plots
```

## Core Concepts

Response roles:

- `primary_quality_y`: main quality response used for pass/fail and next DOE routing.
- `secondary_quality_y`: quality response that matters, but does not dominate the whole decision alone.
- `guardrail_y`: safety or validity check. If it fails, the condition should be held or rejected.
- `production_y`: cycle time, material usage, throughput, or cost metric. Optimize only after quality is acceptable.
- `monitor_y`: recorded context that helps interpretation but is not a hard decision gate.

Factor roles:

- `quality_factor`: process setting expected to affect quality.
- `productivity_factor`: factor that can improve throughput, cost, or cycle time.
- `throughput_factor`: factor related to process time or speed.
- `guardrail_factor`: setting that must be fixed or monitored because it can invalidate the DOE.

Important distinction:

```text
practical_doe_range = engineer-approved safe range worth considering
levels              = actual low/high or multi-level settings for this DOE round
machine capability = equipment limit, not automatically safe DOE range
```

Design generation:

- If the requested levels fit inside `constraints.max_runs`, `ai-doe design` creates a full factorial table.
- If a 4- or 5-factor two-level request would exceed `max_runs`, but a half-fraction fits, it creates a fractional screening table.
- Fractional tables include `design_type` and `alias_structure` columns so the report can explain what effects are confounded.
- `ai-doe design --explain` prints the design-selection rationale, including full-factorial run count, selected run count, rejected alternatives, and alias warnings.

The planner is criteria-first:

```text
project goal + response type + spec/guardrail + process mechanism
-> statistical evidence
-> process and production interpretation
-> multi-mode next DOE recommendation
```
