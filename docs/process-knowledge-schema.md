# Process Knowledge Schema

## Purpose

The DOE planner needs process knowledge in a reusable format.

"Manual input dependent" means the planner can only reason correctly when the
user explains process mechanisms in the chat every time. That is not scalable.

The fix is to store process knowledge as structured records:

```text
process
-> equipment
-> controllable X
-> measurable Y
-> project-specific decision criteria
-> X-Y mechanism
-> defect/failure rules
-> interaction hypotheses
-> production burdens
```

Then the planner can check statistical results against known mechanisms
instead of relying only on free-form conversation.

Use `docs/process-knowledge-card-template.md` as the fillable template for
each process, and use `docs/x-candidate-scoring.md` to decide which X values
become active in the next DOE.

## Knowledge Layers

| Layer | Purpose |
| --- | --- |
| Process card | Defines process scope and fixed assumptions |
| Equipment card | Defines actual machine, controllable knobs, practical ranges |
| X catalog | Defines each factor and whether it is quality, production, or mixed |
| Y catalog | Defines response type, spec, direction, guardrail role |
| Decision criteria card | Defines how this project judges pass/watch/fail, margin, risk, and next DOE direction |
| X selection record | Documents why each candidate X is active, fixed, blocked, deferred, or excluded |
| Mechanism map | Defines expected X -> Y direction and risks |
| Interaction map | Defines suspected X * X interactions |
| Defect map | Links failure/defect modes to likely causes |
| Production map | Links X values to time/material/tool burden |

## Process Card

| Field | Description |
| --- | --- |
| process_id | Stable identifier, e.g. `die_attach_epoxy` |
| process_name | Human-readable process name |
| process_scope | What is included and excluded |
| upstream_dependencies | Upstream conditions that can confound results |
| fixed_conditions | Materials, tool, substrate, die size, cure profile, etc. |
| measurement_constraints | What can and cannot be measured in the project |
| experiment_constraints | Expected run limit, repeat limit, safety limits |

Example:

| Field | Value |
| --- | --- |
| process_id | `die_attach_epoxy_spa300` |
| process_scope | Epoxy die attach on SPA-300-style bonder |
| fixed_conditions | die/substrate/epoxy/cure fixed |
| measurement_constraints | BLT and die shear measurable; void/bleed may be grade-based |
| experiment_constraints | low run count, limited repeat |

## Equipment Card

| Field | Description |
| --- | --- |
| equipment_id | Machine identifier |
| equipment_name | Tool name |
| recipe_knobs | Adjustable parameters |
| logged_values | Values captured every run |
| practical_notes | Engineer comments, physical limitations, startup/calibration notes |
| excluded_knobs | Parameters not adjustable or not safe for DOE |

Important rule:

```text
DOE low/high levels are not necessarily equipment min/max values.
```

The planner must store:

- engineer-safe DOE range,
- known practical range,
- absolute equipment range only if known.

## X Catalog

Each controllable X should have this structure.

| Field | Description |
| --- | --- |
| x_id | `A`, `B`, or stable name |
| x_name | Parameter name |
| unit | Unit |
| role_tag | quality_primary, quality_production_mixed, production_secondary, guardrail_stabilizer |
| doe_low | planned low level |
| doe_high | planned high level |
| safe_range | engineer-approved safe range, if known |
| hard_limit | equipment hard limit, if known |
| expected_direction | brief mechanism summary |
| production_burden | time/material/energy/tool impact |
| risk_notes | possible failure mechanism |
| first_doe_priority | high, medium, low, or unknown |
| selection_status | active, fixed, blocked, deferred, excluded |
| selection_reason | why this X is or is not used in the current DOE |

Example:

| x_id | x_name | role_tag | first_doe_priority | selection_status | expected_direction | risk_notes |
| --- | --- | --- | --- | --- | --- | --- |
| A | Epoxy amount | quality_primary | high | active | increases BLT and may improve coverage/shear | too high may cause bleed |
| B | Bond force | quality_primary | high | active | compresses BLT and improves contact | too high may squeeze out epoxy |
| C | Bond time | quality_production_mixed | medium | active or fixed | improves contact/wetting/shear | longer cycle time |
| D | Wetting time | quality_production_mixed | medium | deferred or active | reduces void risk by allowing spread/settling | longer cycle time |

## X Selection Record

The planner must preserve the reasoning used to compress candidate X values
before DOE design. This prevents the system from silently choosing factors by
habit.

The numeric rubric is maintained in `docs/x-candidate-scoring.md`; this schema
stores the resulting record so the decision can be audited later.

| Field | Description |
| --- | --- |
| x_id | Candidate factor |
| mechanism_relevance | low, medium, high |
| engineer_priority | low, medium, high, unknown |
| controllability | easy, limited, difficult, unsafe |
| measurement_linkage | whether current Y can reveal this X effect |
| interaction_risk | key interactions involving this X |
| production_relevance | whether changing this X affects time/material/tool burden |
| range_confidence | whether DOE-safe low/high or local levels are credible |
| selection_status | active, fixed, blocked, deferred, excluded |
| fixed_value | value used when status is fixed |
| decision_reason | concise explanation for the DOE report |

Example:

| X | Status | Reason |
| --- | --- | --- |
| Epoxy amount | active | directly affects BLT, shear, material use, and A*B interaction |
| Bond force | active | directly affects BLT/shear and can compensate or worsen epoxy spread |
| Bond time | active | likely affects wetting/shear but costs cycle time |
| Wetting time | fixed | important for void risk, but void is not measurable in this project round |

Rule:

```text
If process knowledge identifies only 2-3 credible active X values, do not add
a weak fourth X just to make a fractional screening design look complete.
```

## Y Catalog

Each response Y should have this structure.

| Field | Description |
| --- | --- |
| y_id | Stable response ID |
| y_name | Response name |
| y_type | continuous, binary, categorical, ordinal, count, proportion, image_derived |
| role | primary, guardrail, secondary, monitor |
| decision_role | hard_constraint, quality_objective, guardrail, production_objective, monitor |
| spec_rule | Pass/fail rule |
| preference | higher, lower, target, within_range |
| margin_formula | How margin is calculated |
| fail_rule | Immediate rejection rule |
| borderline_rule | Warning rule |
| measurement_method | How it is measured |
| repeat_rule | Required repeat/pass pattern |

Example:

| y_id | y_name | y_type | role | decision_role | spec_rule | preference |
| --- | --- | --- | --- | --- | --- | --- |
| Y1 | BLT | continuous | primary | hard_constraint | 35-55 um | lower within range |
| Y2 | Die shear | continuous | primary | quality_objective | >= 22 MPa | higher |
| Y3 | Void grade | ordinal | guardrail | guardrail | 0-1 pass, 2-3 fail | lower |
| Y4 | Bleed grade | ordinal | guardrail | guardrail | 0-1 pass, 2-3 fail | lower |
| Y5 | Process time | continuous | secondary | production_objective | no hard spec | lower |

Y role rule:

```text
Define hard constraints and guardrails before production objectives. Production
metrics rank only candidates that remain quality-safe.
```

## Decision Criteria Card

Decision criteria are not universal. They must be created for each DOE project
from the current process, measurable Y values, specs, measurement method, and
production goal.

Each criterion should have this structure.

| Field | Description |
| --- | --- |
| criterion_id | Stable identifier |
| criterion_name | Human-readable name |
| criterion_type | hard_gate, quality_margin, tail_risk, tradeoff, production_objective, measurement_confidence, mechanism_consistency, next_doe_readiness |
| applies_to_y | Y values or Y group affected by this criterion |
| source | spec, engineer, lecture, project_goal, measurement_constraint, assumption |
| rule | How the criterion is calculated or judged |
| pass_condition | Condition judged acceptable |
| watch_condition | Borderline or weak-evidence condition |
| fail_condition | Condition judged unacceptable |
| priority | critical, high, medium, low |
| next_doe_routing_effect | How this criterion changes the next DOE direction |
| notes | Context, caveats, or unresolved assumptions |

Example:

| criterion_id | criterion_name | criterion_type | rule | next_doe_routing_effect |
| --- | --- | --- | --- | --- |
| C1 | chipping hard gate | hard_gate | reject when any measured chipping exceeds the project reject limit | avoid or reduce risky feed/RPM region |
| C2 | tail risk | tail_risk | compare max and over-spec count, not only mean | add confirmation or sampling DOE when mean is good but worst case is weak |
| C3 | productivity trade-off | production_objective | feed speed increase is useful only inside quality-safe region | allow higher feed only after quality margin is acceptable |

Rule:

```text
The planner should recommend the next DOE from criteria state first, then use
statistics, mechanism checks, and production evidence to defend that route.
```

## Mechanism Map

Mechanism records explain why an X should affect a Y.

| Field | Description |
| --- | --- |
| process_id | Process |
| x_id | Factor |
| y_id | Response |
| expected_effect_direction | increase, decrease, U-shaped, threshold, unknown |
| confidence | low, medium, high |
| mechanism | Physical/process explanation |
| risk | What can go wrong |
| source | lecture, engineer, experiment, assumption |

Example:

| X | Y | Direction | Mechanism | Risk |
| --- | --- | --- | --- | --- |
| Epoxy amount | BLT | increase | more adhesive volume makes thicker bond line | bleed |
| Epoxy amount | Die shear | increase up to coverage limit | coverage improves contact area | too much can bleed |
| Bond force | BLT | decrease | compression spreads adhesive | too thin, squeeze-out |
| Wetting time | Void grade | decrease | more time for epoxy spread/settling | longer cycle |

## Interaction Map

Interactions should be predicted before fractional DOE design when possible.

| Field | Description |
| --- | --- |
| x1 | First factor |
| x2 | Second factor |
| affected_y | Response likely affected |
| expected_pattern | What interaction means |
| priority | high, medium, low |
| design_implication | Avoid aliasing with key main effect, or resolve in next DOE |

Examples:

| Interaction | Affected Y | Why it matters |
| --- | --- | --- |
| Epoxy amount * Bond force | BLT, bleed, shear | thickness is formed by volume and compression together |
| US power * US time | pull force, failure code | ultrasonic energy dose is power-time coupled |
| Mold temperature * EMC viscosity | void, flow, warpage | flow/cure behavior depends on thermal-viscosity interaction |
| Spindle speed * feed speed | chipping | cutting energy and brittle fracture depend on both |

## Defect Map

Defect/failure records connect observed bad modes to possible causes.

| Field | Description |
| --- | --- |
| defect_id | Stable defect name/code |
| y_id | Related Y |
| pass_fail_role | critical, major, minor, monitor |
| possible_causes | X or fixed factors |
| immediate_action | reject, stabilize, inspect upstream, ask engineer |
| notes | Context |

Example:

| Defect | Possible causes | Immediate action |
| --- | --- | --- |
| Void grade high | low wetting time, low coverage, contamination, poor dispense | guardrail stabilization |
| Bleed grade high | high epoxy amount, high force, poor viscosity | reduce material/force or check material |
| Low die shear | low epoxy, low force, short time, poor wetting | rescue DOE |

## Production Map

Production records define what each X costs.

| X | Production burden | Good direction | Quality risk if moved |
| --- | --- | --- | --- |
| Epoxy amount | material cost, bleed contamination | lower | low shear/coverage |
| Bond force | tool/mechanical stress | lower | low contact/shear |
| Bond time | cycle time | lower | low shear/contact |
| Wetting time | cycle time | lower | void/shear risk |

Rule:

```text
Production burden is evaluated after quality guardrails pass.
```

## Recommended File Layout

The eventual implementation can store knowledge as YAML or JSON.

```text
knowledge/
  die_attach_epoxy_spa300.yaml
  wire_bonding_second_bond.yaml
  wafer_sawing_disco_blade_saw.yaml
  molding_transfer.yaml
```

Each file should contain:

```yaml
process:
equipment:
x_catalog:
x_selection_record:
y_catalog:
mechanism_map:
interaction_map:
defect_map:
production_map:
sources:
```

## Minimum Knowledge Required Before First DOE

Before the planner proposes a first DOE, it needs:

| Required item | Why |
| --- | --- |
| Candidate X list | DOE factors |
| X selection status and reason | focused DOE factor compression |
| DOE-safe low/high or allowed levels | design levels |
| Measurable Y list | output variables |
| Y type and spec/decision rule | analysis selection |
| Hard guardrails | prevents unsafe recommendation |
| Fixed conditions | avoids false factor attribution |
| Expected key interactions | fractional DOE aliasing decision |
| Run/repeat limit | feasible DOE size |

If these are missing, the planner should not pretend to optimize. It should
ask for or infer a minimum DOE-ready brief.
