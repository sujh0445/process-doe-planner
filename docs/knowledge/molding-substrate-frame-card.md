# Molding Substrate Frame Knowledge Card

## Card Status

| Field | Value |
| --- | --- |
| process_id | `molding_substrate_frame` |
| process_name | Transfer molding / substrate-frame molding focus |
| card_status | Draft, practice + lecture-PDF + equipment-spec evidence reviewed |
| last_updated | 2026-07-02 |
| intended use | Molding DOE feasibility judgment, first DOE design, next DOE routing |

This card consolidates molding information already captured in the project
documents. It is intentionally more cautious than the wire-bonding 2nd-bond
card because molding quality Y values are less certain in the current lab
setting.

## Source Map

| Source document | Information used |
| --- | --- |
| `docs/260626-molding-practice-doe-review.md` | engineer statements, HMI observations, practical X/Y feasibility |
| `docs/260626-packaging-practice-photo-evidence-index.md` | photo-by-photo equipment and parameter evidence |
| `docs/molding-practice-doe-prep-checklist.md` | pre-practice question list, generic X/Y candidates |
| `docs/molding-substrate-frame-v1-engine-review.md` | virtual DOE lessons and engine behavior for molding |
| `docs/260630-molding-theory-doe-review.md` | 2026-06-30 molding lecture PDF extraction: process flow, work conditions, defect cause map |
| `docs/260702-molding-practice-transcript-doe-review.md` | 2026-07-02 molding practice transcript review: lead-frame run structure, sweep/sagging separation, measurement validity rules |
| `docs/package-process-material-index.md` | process-level source map and current project interpretation |
| `docs/icloud-file-organization-log.md` | iCloud file organization and 2026-06-30 retry success status |
| `assets/260701_molding_equipment/manual_press_spec_slide.png` | manual press equipment specification |
| `assets/260701_molding_equipment/mold_top_bottom_pcb_tqfp_slide.png` | mold set evidence: TQFP-1414 and PCB TOP/BTM |
| `assets/260701_molding_equipment/molded_pcb_front_back_slide.png` | after-molding PCB/substrate visual evidence |

## Current Lecture Extraction Status

The 2026-06-30 iCloud access retry succeeded. The molding lecture PDFs were
organized under iCloud and extracted into local text assets:

- `2-3-6-1. Moldding 공정.pdf`
- `260630_MoldDispensing이론_KDT.pdf`
- `assets/260630_molding_theory/text/moldding_process.txt`
- `assets/260630_molding_theory/text/mold_dispensing_theory.txt`

This card now combines practice transcript/photo evidence with lecture-PDF
evidence. The newly organized 2026-06-30 molding photos are still unclassified
visually and should be reviewed separately if the project uses photo evidence
for equipment screens or measurement methods.

## Process Scope

| Item | Decision |
| --- | --- |
| Included | Molding recipe effect on molded substrate/frame quality |
| Likely method | Manual-press transfer molding equipment |
| Current likely sample | Lead-frame molding for current practice; earlier slides also show PCB/substrate mold evidence |
| Fixed or monitored | EMC material/lot/storage, package type, mold chase/cavity, vent/cleaning state, upstream wire loop/sample state, post mold cure |
| Main process question | Can molding conditions reduce wire sweep / void / fill defects while preserving acceptable cycle time? |
| Main caution | Molding DOE is only useful if a measurable quality Y exists; injection time alone is not enough |
| Current confidence | High for equipment/process framing, medium-high for X candidates, medium for real measurable Y |

## 2026-07-02 Lead-Frame Practice Correction

The 2026-07-02 transcript changed the molding interpretation in two important
ways.

| Correction | Project impact |
| --- | --- |
| The current practice sample is lead-frame-like, not one continuous substrate panel | One molding condition can create multiple unit/wire observations, but those are nested under the same shot. They are not independent DOE runs. |
| Wire sweep and wire sagging must be separated | Sweep is lateral EMC-flow deformation. Sagging is vertical loop droop/collapse or pre-existing/handling deformation. They need different measurement and decision rules. |

Default molding response structure after this correction:

```text
Primary Y: wire sweep percent / sweep fail count
Separate guardrail: sagging or loop-height collapse
Validity flags: pre-mold abnormality, handling damage, visibility confidence
Production monitor: injection time
```

If a wire is already abnormal before molding or is damaged while moving the
sample, it must be excluded or flagged before sweep-rate calculation. If
sagging appears after molding, it is a separate loop-stability warning and
should not be hidden inside the sweep average.

## Transfer Molding Mechanism For DOE

This project should treat molding as transfer molding unless later lecture
material says otherwise.

| Step | Mechanism | DOE meaning |
| --- | --- | --- |
| EMC heating / softening | EMC becomes flowable under mold temperature and preheat history | mold temperature and material condition change viscosity and flow behavior |
| Transfer / plunger motion | plunger pushes softened EMC from pot through runner/gate into cavity | transfer down slow / transfer speed controls fill rate and injection time |
| Cavity filling | EMC flow front fills package area around die, wire, and substrate/leadframe | too slow can risk poor fill; too fast can disturb wires or trap air |
| Packing / pressure holding | transfer pressure helps fill and pack the cavity | pressure can reduce incomplete fill but may increase wire sweep, flash, or overflow |
| Air escape / venting | air must leave through vent path while EMC fills | poor venting plus aggressive fill can increase void or short shot |
| Cure in mold | resin cures under heat and time | cure time matters only if cure completeness or reliability is measurable |
| Demold / inspection | molded package is released and inspected | flash, short shot, wire sweep, void, dimension, and damage become Y candidates |
| Post Mold Cure | molded package is additionally cured after molding | PMC should be fixed unless it becomes a reliability/cure-completion study |

Mental model:

```text
Transfer molding DOE is a flow-control problem.
Temperature changes how easily EMC flows.
Transfer speed changes how violently and quickly EMC enters the cavity.
Transfer pressure changes how strongly EMC is packed.
Venting/sample geometry decide whether that flow becomes a good fill,
wire sweep, void, short shot, or flash.
```

## Equipment / HMI Evidence

Practice photos show molding HMI and manual pages with recipe and monitor
fields.

| Evidence | Observed value / field | DOE meaning |
| --- | --- | --- |
| Equipment specification slide | manual press; AC 380 V 3-phase; pump motor 3.75 kW x 6P; heater 6 kW | equipment identity/capability evidence, not recipe low/high |
| Clamp capability | force max `40 ton`, stroke `200 mm`, fast up `71 mm/sec`, slow up `0-6 mm/sec`, down speed `53 mm/sec` | clamp is normally fixed/monitored; do not treat capability range as DOE range |
| Transfer capability | force max `3.5 ton`, stroke `200 mm`, fast down `63 mm/sec`, slow down `0-63 mm/sec`, up speed `125 mm/sec` | transfer capability is much wider than safe recipe range; actual DOE levels must be engineer-approved |
| Mold set slide | `TQFP-1414 TOP/BTM` and `PCB TOP/BTM` positions | PCB/substrate sample type is likely project-relevant and must be recorded as a fixed block |
| Molded PCB slide | front/back molded PCB/substrate image | measurement planning should focus on actual PCB geometry and molded region |
| Speed table | transfer down slow observed around `0.8`; transfer down high around `3.0` | Transfer down slow is a practical filling-speed X |
| Pressure table | transfer pressure observed around `1.6-1.7 ton`; clamp around `40 ton` | Transfer pressure is real but should use narrow engineer-approved levels |
| Heater monitor | top/bottom heater zones around `174-175 degC` | Mold temperature is multi-zone and should be monitored as actual values |
| Cure time | setting shown around `150 sec`; actual monitor examples also shown | Cure time is settable but weak for first DOE unless cure/reliability Y exists |
| System monitor | cure time, injection time, clamp pressure, transfer pressure | These can be logged as run monitors |
| Manual capability | transfer force max `3.5 ton`, clamp max `40 ton`, speed capability listed | Machine limits are not DOE low/high values |
| Lecture work condition | mold die temp `175 degC`, transfer time `22.2 sec`, transfer pressure `1.0 ton`, transfer speed `1.1 mm/s`, cure time `80 sec` | Use as nominal-center references, not automatic low/high values |

Lecture work-condition references:

| Parameter | Lecture allowable / reference | Lecture work value | DOE interpretation |
| --- | --- | --- | --- |
| Plasma power | `400 +/- 50 W` | `400 W` | upstream surface-condition fixed factor |
| Plasma time | `30 +/- 120 sec`, four repeats noted | `50 sec` | upstream adhesion/void guardrail |
| Argon gas | `300 +/- 50 sccm` | `300 sccm` | upstream plasma fixed factor |
| Mold die temperature | `175 +/- 10 degC` | `175 degC` | active X candidate if stabilization time allows |
| Clamp pressure | `40 +/- 25 ton` | `24 ton` | normally fixed/monitored |
| Transfer time | `5-30 sec` | `22.2 sec` | secondary process monitor; affected by speed |
| Transfer pressure | `0.8-1.8 ton` | `1.0 ton` | active X candidate, use narrow engineer-approved range |
| Transfer speed | not specified | `1.1 mm/s` | maps to transfer-down-slow / injection speed concept |
| Cure time | `100 +/- 50 sec` | `80 sec` | defer/fix unless cure quality is measured |
| PMC temperature/time | `175 +/- 5 degC`, `4+1 hr` | `4 hr` | fixed downstream cure condition |

Transfer down slow reference table from practice material:

| Transfer down slow setting | Injection time |
| ---: | ---: |
| 0.2 | 37.6 |
| 0.3 | 25.6 |
| 0.4 | 19.7 |
| 0.5 | 16.0 |
| 0.6 | 13.5 |
| 0.7 | 11.7 |
| 0.8 | 10.1 |
| 0.9 | 9.1 |
| 1.0 | 8.5 |
| 1.1 | 7.6 |
| 1.2 | 6.9 |

Interpretation:

- Higher transfer down slow setting appears to reduce injection time.
- Injection time is a useful production / process-monitor Y.
- Faster injection cannot be accepted unless quality Y values remain inside
  guardrails.
- The manual specification range is not a DOE range. It only tells what the
  equipment can physically do; project low/high values must come from the
  engineer's safe working recipe window.

## Confirmed Knowledge

| Knowledge | Project use |
| --- | --- |
| The selected molding type is transfer molding | Interpret X through plunger transfer, cavity filling, venting, and in-mold cure |
| The equipment is a manual press style molding press with clamp and transfer units | Separate clamp, transfer, heater, and monitor variables in the DOE brief |
| The mold has PCB TOP/BTM positions and a molded PCB/substrate sample is shown | Treat PCB/substrate as the current project sample until the actual run uses TQFP |
| Transfer down slow was emphasized by the engineer as the key adjustable speed parameter | Use as first-priority molding X |
| Mold temperature affects EMC melting, viscosity, flow, and cure behavior | Use as X if changeover/stabilization is feasible |
| Transfer pressure affects filling but excessive pressure can push material out or create meaningless overflow/flash-like behavior | Use narrow range only |
| Cure time is settable but may mostly change wait time after sufficient cure in the mold | Fix first unless under-cure/reliability Y exists |
| Injection time changes with transfer down slow | Use as secondary production Y and equipment stability monitor |
| Wire loop height affects how visible wire sweep sensitivity becomes | Treat as upstream block/stress factor, not normal molding recipe knob |
| Molding defects cannot be interpreted without upstream wire/sample condition | Record upstream wire bonding and loop condition |
| Wire sweep and wire sagging are not the same response | Analyze sweep as EMC-flow lateral displacement; analyze sagging as loop/vertical stability or handling/pre-mold abnormality |
| Plasma cleaning removes contaminants, improves adhesion, and suppresses EMC void | Keep plasma condition fixed or record as upstream block |
| EMC handling matters: low-temperature storage, aging, and use-time window affect material state | Treat EMC lot/storage/moisture as hidden material block |
| Transfer molding has known risks of nonuniform fill, incomplete mold, void/porosity, and wire sweep | Use these as guardrail categories even if only one is selected as primary Y |
| Compression molding exists as an alternative to reduce transfer-flow issues | Do not mix compression-mold conclusions into transfer-mold DOE unless equipment changes |

## Inferred / Working Knowledge

| Inference | Confidence | Use |
| --- | --- | --- |
| Faster transfer can reduce injection time but may increase wire sweep, void, or fill instability | high | quality-margin budget rule |
| Higher mold temperature can lower viscosity and help flow/void, but may affect cure timing or thermal stress | medium-high | interaction hypothesis |
| Higher transfer pressure can improve fill but may worsen wire sweep or flash | high | interaction hypothesis and range caution |
| Wire loop height can expose molding sensitivity; high loop is a stress condition | high | block/stress-factor interpretation |
| Free-standing lead-frame wires can show more sagging risk than substrate-supported structures | medium-high | pre-mold inspection and sagging flag required |
| Void may be the bottleneck when transfer speed is increased for productivity | medium | learned from virtual DOE; must validate with real inspection |
| Higher EMC viscosity can worsen wire sweep and void by increasing flow resistance around wires/cavity | medium-high | mechanism check for temperature/material-state conclusions |
| Incomplete mold can occur from temperature, EMC amount/density, or transfer-pressure insufficiency | medium-high | avoid declaring speed-only root cause from short-shot data |

## Missing / Must Confirm Before Real DOE

| Missing item | Why it matters |
| --- | --- |
| Exact equipment model name beyond manual-press/spec label | Needed for parameter names, limits, and HMI fields if the manual is cited formally |
| Actual engineer-approved low/high for transfer down slow | Must not use full capability range as DOE range |
| Actual engineer-approved low/high for mold temperature | Temperature changeover/stabilization may limit DOE design |
| Actual engineer-approved low/high for transfer pressure | Pressure is risky if varied too widely |
| Which Y values can actually be measured | Determines whether molding is suitable as main DOE process |
| Wire sweep measurement method | Need visual grade, image length/displacement, or pass/fail rule |
| Sagging measurement method | Need pre/post side/profile image, loop-height drop, or at least a categorical sagging flag |
| Void measurement method | X-ray, CSAM, cross-section, visual proxy, or unavailable |
| Flash / short-shot / incomplete-fill inspection rule | Needed if these become categorical/count Y |
| Final package/sample type: PCB/substrate vs TQFP | Current slide evidence points to PCB/substrate, but the actual DOE sample must be confirmed |
| Number of shots/samples per condition | Determines whether 2-factor, 3-factor, or confirmation DOE is possible |
| One-condition cycle time including stabilization/cleaning/inspection | Determines practical run budget |
| EMC material lot/storage/moisture/preheat | Hidden material X for void/fill defects |
| Mold cavity/chase/vent/cleaning state | Hidden equipment X |
| Upstream wire loop height and bonding condition | Hidden upstream X for wire sweep |

## Lecture Material Update Queue

Lecture extraction has been completed for the currently available PDFs. Still
pending:

| Priority | Remaining item | Why |
| ---: | --- | --- |
| 1 | Visual classification of 2026-06-30 molding photos | may contain equipment screens, actual parameter names, or measurement setup |
| 2 | Real lab measurement method/spec for wire sweep | defines whether Y is continuous, ordinal, count, or pass/fail |
| 3 | Real lab measurement method/spec for void | determines whether void can be primary Y or only a visual guardrail |
| 4 | Engineer-approved DOE low/high ranges | lecture ranges and equipment capability are not automatically DOE low/high |
| 5 | Actual run budget and samples per condition | decides 2-factor focused DOE vs 3-factor full factorial vs 4-factor screening |

## Lecture Defect Cause Map

| Defect / symptom | Lecture cause candidates | DOE use |
| --- | --- | --- |
| Incomplete Mold / short shot | mold temperature too high/low, EMC amount or density issue, transfer pressure insufficient | guardrail Y; check pressure/temp/material state before blaming speed |
| Void | mold die cleaning bad, air exhaust blocked, EMC state bad | primary or guardrail Y if measurable; requires vent/clean/material controls |
| Blister | EMC moisture high, molding temperature too high, preheating temperature too low | material and temperature guardrail |
| Wire exposure | wire bonding loop-height defect, mold thickness design miss, foreign material on bottom mold | upstream/sample guardrail, not pure molding recipe effect |
| Wire sweeping | transfer pressure too strong, EMC viscosity too high, bonded frame caught by foreign material | primary quality Y candidate; pressure/speed/temp/loop interaction likely |
| Delamination | inaccurate plasma cleaning, PCB issue, air/moisture inside EMC | adhesion/void guardrail; plasma and material condition must be fixed |
| Package contamination | oil from equipment/mold, bad mold cleaning | equipment-cleaning block |
| Frame/substrate/package damage | misalignment, index jam, foreign material, residual EMC | hard exclusion / abnormal-run flag |

## Y Definition

| Y | Type | Decision role | Spec / rule | Preference | Measurement method | Current status |
| --- | --- | --- | --- | --- | --- | --- |
| Wire Sweep | continuous / ordinal / binary | primary quality Y | needs lab rule | lower / pass | image measurement, scope grade, or pass/fail | likely best real Y if visible |
| Wire Sagging | binary / ordinal / continuous if height measured | separate quality guardrail or secondary Y | no collapse / no excessive droop | lower / pass | pre/post side/profile check, loop-height drop, or visual flag | must not be merged with sweep |
| Void | count / proportion / ordinal / binary | primary or guardrail Y | needs inspection rule | lower / pass | X-ray image, CSAM, cross-section, image grade | feasible only if raw image capture is consistent enough for AI/image quantification |
| Short shot / incomplete fill | categorical or count | guardrail | no incomplete fill | none | visual inspection | possible |
| Flash / overflow | ordinal / categorical / count | guardrail | no or low flash | lower | visual grade | possible, especially with pressure |
| Open/short after molding | binary | hard quality guardrail | pass | pass | electrical test | unknown |
| PCB/substrate warpage | continuous / ordinal | quality or auxiliary Y | needs tool/spec | lower / within spec | warpage measurement, flatness proxy, before/after photo fixture | possible but only if method is repeatable |
| Package dimension/thickness | continuous | backup Y | within spec | within spec | caliper/microscope | possible backup |
| Injection time | continuous | secondary production Y / monitor | lower only if quality passes | lower | HMI monitor | strong evidence |
| Actual mold temperature | continuous | block/monitor | stable at target | stable | HMI monitor | record every run |
| Actual transfer pressure | continuous | block/monitor | stable at target | stable | HMI monitor | record every run |

## X Candidate Table

| X | Unit | Role tag | Expected Y impact | Production impact | Risk | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Transfer down slow | setting value | quality_production_mixed | affects flow front, wire sweep, void/fill; strongly affects injection time | faster setting reduces injection time | too fast can increase void/sweep/fill risk | active primary |
| Mold temperature | degC | quality_primary / whole-plot | affects EMC viscosity, flow, cure, void, warpage | may reduce flow/cure burden but has stabilization cost | too low poor fill/void; too high cure/stress risk | active if feasible |
| Transfer pressure | ton | quality_primary | affects fill, packing, void, flash, wire sweep | may help fill | too high may flash, overflow, sweep wires | active narrow range only |
| Wire loop height | um or categorical | upstream block/stress | affects wire-sweep sensitivity and sagging risk | none as molding recipe; upstream design burden | high/free-standing loop exposes sweep and sagging risk | block/stress factor |
| Cure time | sec | production_mixed | affects cure completeness only if under-cure is present | longer cycle time | too short under-cure; too long no benefit | fixed first |
| Clamp pressure | ton | guardrail/fixed | affects flash, seal, package shape | equipment/mechanical burden | usually fixed around 40 ton | fixed/record |
| Vacuum / vent condition | categorical | guardrail/fixed | affects trapped air, void, short shot | setup burden | poor venting confounds speed effect | fixed/record |
| EMC preheat / storage / moisture | categorical | material block | affects flow and void | handling burden | hidden material variation | fixed/record |
| Shot size / resin amount | amount | material/fill factor | affects short shot, flash, void | material usage | too much flash, too little incomplete fill | defer unless adjustable |

## X Selection Scoring For Current Project

These are planning scores, not measured effects.

| X | Mechanism | Engineer | Control | Measure | Interaction | Production | Range | Risk | Bottleneck adj. | Final | Status | Reason |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Transfer down slow | 5 | 5 | 5 | 5 | 5 | 5 | 4 | -4 | +4 | 34 | active | best evidence chain: engineer focus, HMI setting, injection-time table |
| Mold temperature | 5 | 4 | 3 | 5 | 5 | 3 | 3 | -3 | +3 | 28 | active if feasible | strong mechanism but slow/stabilization issue |
| Transfer pressure | 5 | 4 | 4 | 5 | 5 | 3 | 2 | -5 | +3 | 26 | active narrow | important but risky if wide |
| Wire loop height | 5 | 4 | 2 | 4 | 4 | 1 | 2 | -4 | +4 | 22 | block/stress | upstream condition, not normal molding recipe knob |
| Cure time | 3 | 2 | 5 | 4 | 3 | 5 | 4 | -2 | 0 | 24 | fixed/defer | settable but weak without cure/reliability Y |
| Clamp pressure | 3 | 2 | 2 | 4 | 3 | 2 | 1 | -4 | 0 | 13 | fixed | visible but not emphasized; likely fixed |
| Vacuum/vent | 5 | 3 | 1 | 3 | 4 | 2 | 1 | -4 | +2 | 17 | fixed/record | high mechanism importance but not easy DOE knob |

## Recommended First DOE Posture

Preferred current posture after equipment/spec/sample review:

```text
Do not force a 4-factor screening DOE.
Use PCB/substrate transfer molding as the working frame.
First lock measurable Y and actual shot budget.
```

If wire sweep or another quality Y is measurable and 8 runs are feasible:

```text
3-factor 2-level full factorial, 8 runs
Active X:
  A = Transfer down slow
  B = Mold temperature
  C = Transfer pressure, narrow range
Main Y:
  Wire sweep if X-ray/image measurement is available
Secondary Y:
  Injection time
Guardrail Y:
  Void-by-X-ray, flash, short shot, PCB/substrate warpage if measurable
```

If only 4-6 conditions are feasible:

```text
2-factor focused DOE with confirmation
Active X:
  A = Transfer down slow
  B = Mold temperature or transfer pressure
Keep:
  cure time, clamp pressure, EMC, loop/sample condition fixed
Use remaining runs for baseline repeat and one boundary check.
```

If X-ray images can be saved:

```text
Promote void from guardrail to candidate primary Y only after a measurement
protocol exists:
  same X-ray magnification
  same contrast/exposure
  same PCB region of interest
  same threshold or manual review rule
  run ID embedded in file name
Without this lock, void remains visual/ordinal evidence, not a clean DOE Y.
```

If wire loop height can be intentionally prepared:

```text
Use loop height as block/stress factor, not as a normal recipe X.
Purpose:
  test whether the molding recipe remains robust under a more sweep-sensitive
  upstream wire-loop condition.
```

### Candidate Strategy: Wire Loop Height Handling

Status: not fixed. This is a planning option to revisit after confirming
whether two loop-height levels can actually be prepared.

Reason:

```text
Wire sweep is strongly affected by wire loop height.
However, loop height is not a molding equipment parameter.
It is an upstream wire-bonding/sample condition that changes how sensitive
the sample is to molding flow.
```

Two viable DOE strategies are kept:

| Strategy | How to run it | When it is useful | Risk |
| --- | --- | --- | --- |
| Keep height as a 2-level block/stress factor | Run molding X combinations at low/high loop height, at least for key conditions | Best for proving robustness across loop variation | Sample count increases quickly |
| Optimize at one height, then validate at the other height | Find A/B recipe at one representative or high-risk height, then apply the selected recipe to the other height | Best when run count is tight and the goal is practical recipe selection | May miss an interaction if the untested height behaves differently |

Preferred tentative logic:

```text
If high loop height is realistic and available:
  Use high loop as the stress condition for first recipe search.
  Optimize main molding factors there, especially transfer down slow and
  mold temperature.
  Then validate the selected recipe on low loop height.

If both heights are easy to prepare and run count allows:
  Include loop height as a 2-level block/stress factor in the early DOE.

If height preparation is difficult:
  Fix height, record it, and treat loop-height robustness as a later
  confirmation question.
```

Presentation wording:

```text
Loop height is not treated as a normal molding knob.
It is used to test whether the molding recipe is robust to upstream wire-loop
variation, especially because high loop conditions can reveal wire sweep more
clearly than low loop conditions.
```

## Interaction Hypotheses

| Interaction | Affected Y | Expected pattern | Priority | DOE implication |
| --- | --- | --- | --- | --- |
| Transfer down slow x Transfer pressure | wire sweep, flash, void, short shot | high speed/pressure may improve fill but increase sweep/flash | high | avoid aliasing if both active |
| Mold temperature x Transfer down slow | void, fill, sweep, injection behavior | temperature changes viscosity, so same speed may behave differently | high | strong reason for 3-factor full factorial if possible |
| Mold temperature x Transfer pressure | void, flash, fill | lower viscosity may reduce needed pressure | medium-high | useful for pressure range selection |
| Wire loop height x Transfer down slow | wire sweep | high loop amplifies sweep under aggressive transfer | high if loop varied | treat loop as block/stress factor |
| Vacuum/vent x Transfer down slow | void, short shot | poor venting plus fast fill traps air | medium | record vent/cleaning condition |
| Cure time x Mold temperature | cure completeness, warpage, productivity | temperature and time jointly affect cure | medium | defer unless cure/warpage Y exists |

## Defect / Failure Map

| Defect / failure | Likely cause | DOE interpretation |
| --- | --- | --- |
| Wire sweep | high transfer speed/pressure, high loop height, low viscosity flow force | central Y if wire-bonded sample is available |
| Void | air entrapment, poor venting, fast fill, material/preheat/moisture condition | strong guardrail if measurable |
| Short shot / incomplete fill | low pressure, slow/poor flow, low temperature, insufficient material | guardrail, especially at conservative fill conditions |
| Flash / overflow | excessive pressure, clamp/seal issue, too much material, low viscosity | guardrail against over-aggressive pressure/temperature |
| Warpage | cure/thermal stress, package geometry, material mismatch | useful only if measurement tool exists |
| Delamination | adhesion/moisture/cure issue | likely unavailable without CSAM/reliability inspection |
| Package crack/damage | excessive stress or handling | rare but hard guardrail |
| Electrical open/short | wire movement, sweep, breakage, package stress | strong final Y if testable |

## Production Burden Map

| X / condition | Production burden | Good direction | Quality risk if moved |
| --- | --- | --- | --- |
| Transfer down slow | injection time / cycle time | higher setting if quality margin remains | faster fill may increase void/sweep/flash |
| Mold temperature | stabilization time / thermal load | use only if quality benefit justifies change | thermal/cure/stress risk |
| Transfer pressure | mechanical/material stress | avoid unnecessarily high pressure | flash/sweep/overflow |
| Cure time | cycle time | shorter if cure quality is proven | under-cure/reliability risk |
| EMC handling/preheat | preparation burden | stable and repeatable | material variation/void |

Production improvement rule:

```text
Injection-time reduction is valuable only inside the quality-safe region.
Quality margin is the budget that allows a faster transfer condition.
```

## Measurement Method Lock

| Measurement | Conditions to fix |
| --- | --- |
| Wire sweep | image angle, magnification, before/after reference, displacement or grade rule |
| Void | X-ray/CSAM/cross-section setting, area/count threshold, inspected PCB region, raw image preservation |
| PCB/substrate warpage | measurement fixture, point layout, before/after rule, unit or grade |
| Short shot / flash | visual grade scale, inspector rule, inspected location |
| Injection time | HMI field name, actual vs reference table, run order |
| Temperature | top/bottom heater zones, stabilization time before run |
| Pressure | commanded setting and actual monitor value |
| Sample context | package type, loop height, wire material, EMC lot, cavity position |

If measurement method changes between runs, it becomes a hidden X.

## First DOE Success / Reject Criteria

| Criterion | Success | Warning | Reject / block |
| --- | --- | --- | --- |
| Measurable quality Y exists | at least one repeatable quality Y | only rough visual pass/fail | only injection time is measurable |
| Wire sweep | below spec/grade limit | pass but thin margin | repeated excessive sweep |
| Void | below spec/grade limit | uncertain or thin margin | repeated high void / unmeasurable if claimed |
| Flash/short shot | no critical defect | minor grade | repeated or critical defect |
| Injection time | improves while quality passes | improves but margin thin | improves by consuming quality margin |
| Actual settings | stable and match command | small drift | drift dominates result |
| Upstream loop/sample | fixed or intentionally blocked | unclear variation | uncontrolled sample state |

## Next DOE Routing

| Result pattern | Next DOE |
| --- | --- |
| No measurable quality Y exists | do not run molding as main DOE; use as process-knowledge example |
| Quality fails broadly | baseline search DOE: reduce aggressive transfer/pressure or adjust temperature |
| Quality passes but injection time is slow | mixed confirmation / production-improvement DOE focused on transfer down slow |
| Faster transfer improves time but weakens void/sweep margin | margin-budget DOE with baseline repeat and small speed steps |
| Wire sweep appears only at high loop height | loop robustness DOE or upstream wire-loop control review |
| Flash appears at high pressure | pressure guardrail stabilization or fix pressure lower |
| Void appears under fast transfer | transfer speed/temperature/vent-focused guardrail DOE |

## Presentation Summary

The molding module should be presented as:

```text
Molding DOE is not driven by injection time alone.
The planner first checks whether a measurable quality response exists, then
protects wire sweep, void, short-shot, and flash guardrails. Only after a
quality-safe baseline exists does it use transfer down slow or related settings
to reduce injection time.
```
