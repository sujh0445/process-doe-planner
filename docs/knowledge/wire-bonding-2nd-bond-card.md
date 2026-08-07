# Wire Bonding 2nd Bond Knowledge Card

## Card Status

| Field | Value |
| --- | --- |
| process_id | `wire_bonding_2nd_bond` |
| process_name | Thermosonic wire bonding, 2nd bond / stitch bond focus |
| card_status | Project-ready draft |
| last_updated | 2026-06-29 |
| intended use | First DOE design, DOE result interpretation, next DOE recommendation |

This card consolidates the wire-bonding information already captured in the
project documents. It is not a universal wire-bonding rulebook. It is the
current project knowledge base for a 2nd-bond-centered DOE.

## Source Map

| Source document | Information used |
| --- | --- |
| `docs/wire-bonding-theory-doe-review.md` | thermosonic mechanism, X/Y candidates, ball shear details, defect-cause map, interaction hypotheses |
| `docs/260625-die-attach-wire-bonding-practice-doe-review.md` | practice recipe screen values, instructor discussion, pull failure code logic, 2nd-bond project recommendation |
| `docs/260629-shear-pull-test-measurement-review.md` | pull/shear measurement interpretation, fixed measurement conditions, failure-mode guardrail logic |
| `docs/wire-bonding-2nd-bond-scoring-rules.md` | concrete scoring rules for pull force, failure code, ball shear, condition state |
| `docs/wire-bonding-2nd-bond-report-template.md` | reporting surface for analysis and next DOE explanation |

## Process Scope

| Item | Decision |
| --- | --- |
| Included | 2nd bond / stitch bond / lead or substrate-side recipe optimization |
| Fixed or monitored | 1st bond recipe, capillary, wire material/diameter, pad/lead geometry, sample type |
| Main process question | Can the 2nd bond recipe satisfy pull force while avoiding risky break codes? |
| Why 2nd bond focus | Instructor discussion indicated lead/second-bond side often dominates bondability evaluation because lead finish, plating thickness, oxidation, storage, and plasma state vary more than chip pad side |
| Main caution | Do not mix 1st and 2nd bond recipe effects unless the DOE explicitly separates them |

## Equipment / Recipe Evidence

Practice photos show separate recipe fields for 1st and 2nd bond.

| Target | Search level | Search speed | US time | US power | Bond force | Force time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1st Bond | 150.0 um | 3.0 mm/s | 12.0 ms | 250 | 40.0 gf | 7.0 ms |
| 2nd Bond | 100.0 um | 5.0 mm/s | 15.0 ms | 300 | 60.0 gf | 5.0 ms |

Interpretation:

- `US time`, `US power`, `bond force`, `force time`, `search level`, and
  `search speed` exist as recipe parameters.
- For the first project DOE, search level and search speed should normally be
  fixed or recorded to avoid too many active X values.
- DOE low/high levels are screening levels or engineer-safe levels, not
  equipment hard minimum/maximum values.

## Confirmed Knowledge

| Knowledge | Project use |
| --- | --- |
| Main bonding mechanism is thermosonic bonding | Heat, ultrasonic energy, force, and time are coupled physical levers |
| 1st bond is ball bonding, 2nd bond is stitch bonding | Do not interpret ball-shear changes as direct 2nd-bond effects without checking first-bond controls |
| Pull force must be paired with break position / failure code | Force alone can hide interface or metallization risk |
| Pull force project spec is `>= 7 g` | Primary numeric lower-bound Y |
| Pull failure codes 1-3 are acceptable if force passes | Candidate/pass region |
| Pull failure codes 4-7 are risky | Guardrail / engineering review / possible block |
| Ball shear checks 1st bond ball-pad quality | Secondary guardrail when optimizing 2nd bond |
| Ball shear measurement depends on tool height and speed | Measurement method must be fixed |
| Capillary, wire diameter, pad/lead geometry should be fixed | Otherwise they become hidden X values |

## Inferred / Working Knowledge

| Inference | Confidence | Use |
| --- | --- | --- |
| `US power x US time` controls ultrasonic energy dose | high | key interaction hypothesis |
| `Bond force x Force time` controls mechanical contact/hold stability | medium-high | key interaction hypothesis |
| High power/time may improve pull force but create neck damage, cratering, or metal lift | high | guardrail interpretation |
| Low power/time may create weak bond, no bond, pad open, or wedge failure | high | baseline search direction |
| High force can improve contact but can also cause spread, short, cratering, or metal lift | high | range and guardrail control |
| Ball shear abnormality during 2nd-bond DOE may indicate first-bond drift or measurement issue | high | prevents false attribution |

## Missing / Must Confirm Before Real DOE

| Missing item | Why it matters |
| --- | --- |
| Actual engineer-approved low/high levels for the lab tool | Must not use simulator or old discussion values as equipment limits |
| Whether students can independently change 1st and 2nd bond settings | Determines whether 2nd-bond-only DOE is valid |
| Pull test repetitions available per condition | Controls confidence grade and analysis depth |
| Whether failure code is exported or manually selected | Determines categorical Y reliability |
| Ball shear spec for the actual wire/sample | Current project rule uses >=20 g as guardrail, while practice discussion mentioned roughly 25-35 g level |
| Wire material and diameter | Pull and shear spec depend on wire size/material |
| Fixed capillary and tool condition | Tool variation can dominate recipe effect |
| Lead/substrate surface condition and plasma/oxidation state | 2nd bond is sensitive to lead-side surface state |

## Y Definition

| Y | Type | Decision role | Spec / rule | Preference | Measurement method | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Pull Test Force | continuous | hard_constraint / quality_objective | `>= 7 g` | higher only after guardrail pass | wire pull tester | use min/pass count before average with small n |
| Pull Spec Pass/Fail | binary | hard_constraint | force >= 7 g | pass | derived from pull force | useful for small sample DOE |
| Pull Failure Code | multiclass categorical | guardrail | codes 1-3 acceptable, 4-7 risky | acceptable codes | break position classification | do not collapse into force |
| Pull Risk Group | categorical derived | guardrail summary | acceptable / risky | acceptable | derived from failure code | presentation-friendly |
| Ball Shear Force | continuous | 1st-bond guardrail | project default >=20 g; real spec must be confirmed | pass check | ball shear tester | primary Y only if DOE switches to 1st bond |
| Ball Shear Case | categorical | 1st-bond guardrail | normal preferred | normal/pass | shear fracture position | force alone is insufficient |
| Stitch Quality Grade | ordinal | visual/supporting guardrail | 0-1 preferred | lower | microscope/visual | useful when force is high but failure code is risky |
| Pad/metal damage | categorical/count | hard guardrail | no cratering/lift | none | visual/failure mode | critical high-energy/force risk |

## Pull Failure Code Interpretation

| Code | Position / name | Process meaning | DOE decision |
| ---: | --- | --- | --- |
| 1 | Wire Break | wire/loop breaks away from bond interface | acceptable if pull force passes |
| 2 | Neck / HAZ Break | break near ball neck or heat-affected zone | acceptable if pull passes; monitor if concentrated at high energy |
| 3 | Wedge / Heel Break | break near 2nd bond heel/stitch neck | acceptable/watch if pull passes; monitor 2nd-bond stress |
| 4 | Ball Bond Failure | ball separates from pad | risky/fail; check 1st bond assumption |
| 5 | Ball Metal Lift | ball and pad metal lift together | critical risk; pad/interface damage |
| 6 | Wedge Bond Failure | 2nd bond separates from lead/substrate | critical for 2nd-bond DOE |
| 7 | Wedge Metal Lift | lead-side metal lift | critical over-stress/metallization risk |

Decision rule:

```text
Optimal condition = pull force >= 7 g
                  + no repeated codes 4-7
                  + no concentration of damage-like break modes
                  + first-bond guardrail remains healthy.
```

Codes 4-7 are not always automatic physical scrap if pull force exceeds spec,
but they prevent confirmed-baseline adoption until confirmed or stabilized.

## Ball Shear / First-Bond Check

Ball shear evaluates 1st bond ball-pad adhesion. For a 2nd-bond DOE, it is a
guardrail, not the main optimization response.

Measurement conditions to fix:

| Condition | Project rule |
| --- | --- |
| Tool height | keep constant; theory material mentions 3-5 um above pad surface |
| Tool speed | keep constant; theory material mentions 200 um/sec |
| Tool / vibration | same tool, isolated from vibration |
| Ball/wire/pad geometry | fixed across DOE |

Ball shear case interpretation:

| Category / mode | Interpretation | Decision |
| --- | --- | --- |
| Ball shear / ball residue remains | normal fracture-like result | pass with force |
| IMC failure or clean lift-off | weak interface | fail / check first bond |
| Pad lift / metal lift | pad damage | critical fail |
| Oxide or silicon damage | device damage | critical fail |
| Test error / abnormal | invalid or review | repeat or block interpretation |

## X Candidate Table

| X | Unit | Role tag | Expected Y impact | Production impact | Risk | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 2nd US Power | equipment unit | quality_primary | increases bonding energy and pull force up to a safe region | energy/tool load | over-energy, neck damage, cratering, metal lift | active |
| 2nd Bond Force | gf | quality_primary | improves contact/deformation and stitch formation | tool/mechanical stress | over-compression, spread, short, lift/cratering | active |
| 2nd US Time | ms | quality_primary / production_mixed | increases energy exposure duration | cycle time | over-energy if too long; weak bond if too short | active |
| 2nd Force Time | ms | quality_primary / production_mixed | increases contact/hold stability | cycle time | over-stress or throughput burden | active |
| Stage / bond temperature | degC | quality_primary | supports thermosonic bonding and lowers needed energy | thermal load | thermal damage or material sensitivity | deferred unless controllable |
| Search level | um | guardrail_stabilizer | affects touchdown/contact consistency | setup/motion | hidden contact change | fixed/recorded |
| Search speed | mm/s | guardrail_stabilizer | affects contact/touchdown dynamics | cycle time | hidden contact variation | fixed/recorded |
| Capillary type | categorical | fixed context | affects ball/stitch geometry | tool wear/cost | confounds all results | fixed |
| Wire material/diameter | categorical/um | fixed context | affects strength/spec/failure code | material cost | changes spec and mechanism | fixed |
| Pad/lead surface condition | categorical | block/noise factor | affects bondability, especially 2nd bond | cleaning/plasma burden | oxidation/contamination | block/record |

## X Selection Scoring For Current Project

Using the project scoring rubric, the default 2nd-bond first DOE keeps four
active recipe X values if run budget allows an 8-run fractional DOE. If the
project budget is tighter or engineer knowledge is strong, reduce to the
highest-priority 2-3 factors.

| X | Mechanism | Engineer | Control | Measure | Interaction | Production | Range | Risk | Bottleneck adj. | Final | Status | Reason |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 2nd US Power | 5 | 5 | 5 | 5 | 5 | 3 | 4 | -3 | +4 | 33 | active | direct energy lever for pull force and failure code |
| 2nd Bond Force | 5 | 5 | 5 | 5 | 4 | 3 | 4 | -4 | +4 | 31 | active | direct contact/stress lever; also risk driver |
| 2nd US Time | 5 | 5 | 5 | 5 | 5 | 4 | 4 | -3 | +4 | 34 | active | energy-dose and cycle-time lever |
| 2nd Force Time | 4 | 4 | 5 | 4 | 4 | 4 | 4 | -3 | +4 | 30 | active | contact stability and cycle-time lever |
| Stage temperature | 4 | 3 | 2 | 4 | 4 | 3 | 2 | -3 | +2 | 21 | deferred | important but controllability/range uncertain |
| Search level/speed | 3 | 2 | 3 | 3 | 2 | 2 | 3 | -3 | 0 | 15 | fixed/recorded | can confound contact but too many X for first DOE |
| Capillary / wire / pad geometry | 5 | 5 | 1 | 5 | 4 | 3 | 1 | -5 | 0 | 19 | fixed | critical context, not project DOE knob |

Note:

```text
The scores are planning scores, not measured effects. They should be revised
after engineer confirmation and real DOE data.
```

## Recommended First DOE Posture

Preferred if 8 conditions are feasible:

```text
4-factor 2-level fractional DOE, 8 runs
Active X: 2nd US Power, 2nd Bond Force, 2nd US Time, 2nd Force Time
Main Y: Pull Test Force, Pull Failure Code
Guardrail Y: Ball Shear Force/Case, Stitch Quality Grade
```

Alternative if the instructor says one factor is weak or time is too limited:

```text
3-factor full factorial, 8 runs
Active X: US Power, Bond Force, US Time
Fixed X: Force Time at safe/default or engineer-recommended value
```

Alternative if failure code, not force, is the bottleneck after round 1:

```text
Focused guardrail stabilization DOE
Active X: US Time and Force Time, plus one of Power/Force depending on code pattern
Purpose: reduce codes 4-7 while maintaining pull >= 7 g
```

## Interaction Hypotheses

| Interaction | Affected Y | Expected pattern | Priority | DOE implication |
| --- | --- | --- | --- | --- |
| US Power x US Time | pull force, failure code, neck damage | total ultrasonic dose; low-low underbonds, high-high can over-stress | high | avoid overclaiming separated effects in 8-run fractional DOE |
| US Power x Bond Force | pull force, cratering/lift/short | energy coupling depends on contact deformation | high | confirm if force/power both look important |
| Bond Force x Force Time | pull force, wedge failure, metal lift | contact pressure duration affects stitch formation and stress | high | important if failure code is bottleneck |
| Temperature x US Power | pull force, damage risk | higher temperature may lower required ultrasonic energy | medium | defer unless temperature is adjustable |
| Force x pad/capillary geometry | short, spread, cratering | physical geometry changes safe force window | medium-high | fix geometry; do not compare across tool changes |

## Defect / Failure Map

| Defect / failure | Likely cause from source | DOE interpretation |
| --- | --- | --- |
| Pad Open | capillary setting miss, wire contamination, bond parameter miss, pad contamination | check 1st bond/tool/pad before blaming 2nd bond X |
| No Bond | coordinate miss, wire feed detection, equipment operation miss | setup special cause unless repeated by low-energy condition |
| Bond Short | excessive bond force, wire too thick, ball spread, offset | high force/power cannot be accepted only because pull is high |
| Wire Short | clamp setting, index vibration, capillary contamination, external contact | likely setup/handling/tool issue |
| Broken Wire | impact, external contact, inappropriate bond parameters, neck damage | high power/force/time concentration suggests over-bonding |
| Missing Wire | capillary setting, wire feed detection, pad/lead contamination | equipment/feed/surface issue |
| Sagging Wire | index impact, magazine contact, thin/ductile wire, molding EMC pressure | downstream/handling guardrail, not first DOE recipe target |
| Tail Bond | clamp, feed guide, capillary, wire contamination | tool/feed issue; lowers recipe interpretation confidence |
| Bond Cratering | power too strong, force too strong, thin pad metal, chip contamination/corrosion | critical high-energy/force guardrail |
| Wedge Bond Failure | weak 2nd bond on lead/substrate | central failure mode for 2nd-bond DOE |
| Wedge Metal Lift | lead-side metal/metallization damage | critical 2nd-bond over-stress or surface issue |

Rule:

```text
Map every bad failure code to recipe effect vs surface/material/tool issue vs
handling special cause before selecting the next DOE.
```

## Production Burden Map

| X / condition | Production burden | Good direction | Quality risk if moved |
| --- | --- | --- | --- |
| US Power | energy/tool load | lower if pull/code stable | low power weak bond; high power damage |
| Bond Force | tool/mechanical stress | lower if contact remains stable | low force weak contact; high force cratering/lift/short |
| US Time | cycle time and energy exposure | lower if pull/code stable | low time weak bond; high time over-energy |
| Force Time | cycle time and mechanical hold | lower if failure code remains stable | low time weak contact; high time stress/time burden |
| Stage temperature | thermal load | lower if bonding remains stable | too low weak bond; too high thermal/material risk |

Production metrics should not drive the first DOE unless quality already
passes. They become important after a provisional baseline exists.

## Measurement Method Lock

Before analyzing DOE data, lock the following measurement conditions.

| Measurement | Conditions to fix |
| --- | --- |
| Wire pull | hook position, pull speed, loop engagement, failure-code classification rule |
| Ball shear | tool height, tool speed, tool condition, vibration environment |
| Visual stitch grade | microscope/scope setting, inspector criterion |
| Sample context | wire diameter, capillary, pad/lead, first-bond recipe, operator/setup notes |

Rule:

```text
If the measurement method changes between DOE runs, the measurement method
becomes a hidden X and the result cannot be interpreted as pure recipe effect.
```

## First DOE Success / Reject Criteria

| Criterion | Success | Warning | Reject / block |
| --- | --- | --- | --- |
| Pull force | 3/3 pass, min >= 7 g | pass but thin margin | repeated fail or min < 7 g |
| Pull failure code | codes 1-3 only | one code 4-7 with force pass | repeated codes 4-7 |
| Ball shear | force passes and case normal | force passes but case watch | force fails or critical case |
| Stitch quality | grade 0-1 | one grade 2 | repeated grade 2 or any grade >=3 |
| Process plausibility | trend matches mechanism | plausible but risky | contradicts mechanism or special cause likely |

## Next DOE Routing

| Result pattern | Next DOE |
| --- | --- |
| No condition passes pull force | baseline search DOE: widen/shift energy-contact window |
| Pull force passes but codes 4-7 appear | guardrail stabilization DOE: diagnose 1st vs 2nd bond, underbond vs over-stress |
| One provisional baseline appears | mixed confirmation DOE with baseline repeats and nearby alternatives |
| Baseline confirmed and production burden high | production-improvement DOE, usually reducing unnecessary power/time/force time |
| Ball shear fails while 2nd-bond X changed | pause 2nd-bond interpretation; check first-bond or measurement method |
| Highest pull condition has risky code | do not select it directly; use as boundary or risk evidence |

## Presentation Summary

The wire-bonding 2nd-bond module should be presented as:

```text
The planner does not maximize pull force alone.
It seeks a recipe that passes pull force, avoids risky failure codes, keeps
the first-bond ball-shear guardrail healthy, and only then considers production
burden such as excessive power, force, or time.
```
