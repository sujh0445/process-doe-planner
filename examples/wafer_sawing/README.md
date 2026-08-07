# Wafer Sawing Example

This example demonstrates the first executable AI DOE Planner MVP.

It is a small, synthetic wafer-sawing scenario based on the project logic:

- quality gate first
- productivity improvement second
- statistics as evidence
- process criteria as the main decision layer

## Files

- `request.yaml`: process objective, controllable X factors, Y response, spec, and decision criteria.
- `results.csv`: example measured data for a 2-factor DOE.

## Scenario

The example asks:

> Can feed speed be increased while keeping max chipping size under control?

The planner evaluates `max_chipping_size_um` by condition, checks the upper spec
and warning zone, compares tail risk, then recommends a next DOE focused on
productivity refinement only after the quality gate is passed.

The sample values are demonstration data, not production data.
