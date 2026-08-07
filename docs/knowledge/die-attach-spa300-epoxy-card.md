# Die Attach SPA-300 Epoxy Knowledge Card

## Card Status

| Field | Value |
| --- | --- |
| `process_id` | `die_attach_spa300_epoxy` |
| `process_name` | SPA-300 epoxy die attach / die bonding |
| `process_family` | Semiconductor package assembly |
| `card_status` | Project-ready draft |
| `last_updated` | 2026-08-03 |
| `intended_use` | First DOE design, DOE result interpretation, next DOE recommendation |

This card defines the process knowledge that the AI DOE Planner should use
before designing or interpreting an epoxy die attach DOE. It is not a recipe.
Actual low/high levels, hard specs, and unsafe zones must be confirmed with the
engineer before a real experiment.

## Source Map

| Source | Evidence Used |
| --- | --- |
| `docs/die-attach-spa300-epoxy-doe-brief.md` | SPA-300 scope, Ag epoxy assumption, equipment capability, epoxy dispense and die attach process notes |
| `docs/die-bonding-0625-transcript-review.md` | Lab process family, epoxy paste rather than DAF, pickup/release cautions, cure and epoxy handling cautions |
| `docs/die-bond-solder-ball-theory-review.md` | Die attach theory, candidate X/Y, defect mechanism mapping |
| `docs/260625-die-attach-wire-bonding-practice-doe-review.md` | SPA-300 screen values, first DOE posture, response candidates, interaction hypotheses |
| `docs/260629-shear-pull-test-measurement-review.md` | Die shear and failure-mode measurement interpretation |
| `docs/four-process-doe-summary.md` | Multi-Y decision direction for die attach DOE |
| `docs/process-knowledge-schema.md` | Reusable process knowledge schema and DOE design rules |

## Process Scope

Included scope:

- Epoxy paste die attach on an SPA-300 style die bonder.
- Conductive Ag epoxy style bonding is the working project assumption.
- Die is picked up after sawing and bonded onto a lead frame or substrate.
- DOE focuses on dispense and bonding conditions, not on upstream sawing.

Excluded or deferred scope:

- DAF die attach, flip-chip attach, and solder ball attach.
- Cure profile optimization, unless a separate DOE is explicitly planned.
- Pickup/ejector optimization, unless pickup miss, chip damage, or no-die
  defects become the observed bottleneck.

Fixed or recorded preconditions:

- Substrate or lead frame type.
- Die size and die thickness.
- Epoxy material, lot, storage condition, thaw/aging time, and pot life.
- UV tape release condition and ejector/pickup setup.
- Collet type and condition.
- Cure profile, unless cure is intentionally selected as a DOE factor.
- Operator and measurement method.

Main process question:

> Which dispense and bonding settings can satisfy BLT and die shear quality
> while avoiding bleed, void, placement, crack, and pickup-related guardrail
> failures, and then improve epoxy usage or cycle time only after quality is
> stable?

## Public Process Facts

| Item | Current Knowledge | DOE Use |
| --- | --- | --- |
| Equipment | SPA-300 style die bonder | Treat as the target tool family |
| Bonding method | Epoxy bonding is available; DAF is also possible but not the current scope | Do not mix epoxy and DAF knowledge in one DOE |
| Bonding force capability | Source notes include about `0.2~15.0 N`, or `20~1,500 gf` | Capability range is not the same as DOE low/high |
| Epoxy dispense unit | Dots Ag epoxy on the lead frame or substrate | Epoxy amount/pattern is a primary process lever |
| Die pickup | Ejector pin pushes die up; collet picks die and bonds it | Pickup issues should be fixed/monitored unless selected as factors |
| Ejector risk | Wrong ejector pin array can cause chipping | Keep ejector/pickup stable for bonding DOE |
| Example screen values | Prior screen evidence included bonding force around `500 gf`, bonding time around `500 ms`, touchdown speed around `9.75 mm/s` | Use as reference context only, not fixed universal recipe |
| Cure example | Practice notes referenced cure around `180 C`, `30 min` | Fix cure in first DOE unless cure is the project objective |

## Confirmed Knowledge

| Knowledge | Confidence | How It Should Affect DOE |
| --- | --- | --- |
| Current project is epoxy paste die attach, not DAF | High | Keep material/process family fixed |
| Epoxy amount and bond force strongly affect bond line thickness and epoxy spread | High | Protect `A x B` interpretation if possible |
| Die shear is meaningful only after cure | High | Record cure condition and keep it stable |
| Void and bleed can be important but may be hard to quantify in the education setting | High | Use as guardrail or ordinal/count Y unless image/area measurement is available |
| Epoxy amount is both a quality factor and a material-usage production concern | High | Do not optimize epoxy reduction before quality pass |
| Pickup/release condition can dominate defects if unstable | Medium-high | Monitor no-die, chip damage, placement, and pickup miss |
| Cure profile has quality and productivity trade-off | Medium-high | Fix first; optimize later only if time permits |

## Inferred / Working Knowledge

These are process-mechanism hypotheses, not measured facts.

| Hypothesis | Confidence | Expected Direction |
| --- | --- | --- |
| Higher epoxy amount tends to increase BLT, improve coverage, and increase bleed risk | Medium-high | Quality may improve then fail by overflow |
| Higher bond force tends to reduce BLT and improve contact, but excessive force may squeeze epoxy or damage die/substrate | Medium-high | Useful for BLT control, with damage guardrail |
| Longer bond time may improve wetting/contact, but increases cycle time | Medium | Quality benefit may saturate |
| Wait/wetting time after dispense may affect void and wetting | Medium | Useful only if controllable and time budget allows |
| Epoxy age/viscosity can confound epoxy amount effects | Medium | Record as hidden noise or block condition |
| Pickup/eject instability can mimic poor bonding results | Medium | If no-die/chipping appears, stop bonding optimization first |

## Missing Inputs Before Real DOE

The planner should ask for these before generating a real DOE:

- Actual substrate or lead frame type.
- Actual die size and die thickness.
- Actual epoxy material and storage/aging state.
- Engineer-approved DOE low/high levels for each active X.
- Numeric BLT spec or target range.
- Numeric die shear spec.
- Whether BLT can be measured repeatedly and how.
- Whether void can be quantified, graded, counted, or only observed visually.
- Whether bleed/overflow has a binary fail rule or an ordinal severity rule.
- Number of repeats or samples per run.
- Whether cure condition is fixed or adjustable.
- Whether wait time, touchdown speed, level, or overtravel are safe recipe knobs.
- Unsafe combinations that should be blocked before DOE generation.

## Y Catalog

| Y | Type | Role | Direction / Rule | Measurement Note |
| --- | --- | --- | --- | --- |
| Bond line thickness (`BLT`) | Continuous | Primary quality / hard constraint | Must be within spec; within spec, thinner may be preferred if shear margin remains | Requires defined thickness method |
| Die shear strength | Continuous | Primary quality | Higher is better after meeting lower-bound spec | Measured after cure |
| Die shear failure mode | Categorical | Guardrail | Bad interface, die crack, substrate damage, or abnormal mode can reject a high-force condition | Do not judge by force value alone |
| Epoxy bleed / overflow | Binary, ordinal, or count | Guardrail | Lower is better; severe pad contamination rejects the condition | Visual or microscope inspection |
| Void | Binary, ordinal, count, or continuous area | Guardrail or primary if quantifiable | Lower is better | Use image-derived area/count only if measurement is reliable |
| Die placement shift | Continuous or binary | Guardrail | Must stay within placement tolerance | Vision/microscope |
| No die / pickup miss | Count or binary | Hard guardrail | Any repeated occurrence can block bonding DOE interpretation | Indicates pickup/release problem |
| Chip crack / chipping | Count or binary | Hard guardrail | Reject or hold depending on severity | Often pickup/ejector related |
| Process time | Continuous | Secondary production | Lower is better only among quality-pass candidates | Do not outrank quality |
| Epoxy usage | Continuous | Secondary production | Lower is better only among quality-pass candidates | Avoid direct optimization before BLT/shear pass |

## X Candidate Catalog

| Symbol | Factor | Status | Why It Matters | Caution |
| --- | --- | --- | --- | --- |
| A | Epoxy dispense amount or dispense time | Active candidate | Controls coverage, BLT, void, bleed, and material usage | Too low can reduce shear; too high can bleed |
| B | Bond force | Active candidate | Controls contact pressure, BLT, wetting, and squeeze-out | Excess can damage or over-squeeze |
| C | Bond time | Active candidate | Controls wetting/contact time | Longer time reduces throughput |
| D | Wait/wetting time after dispense or time-to-bond | Active/deferred candidate | May affect void and wetting stability | Only use if controllable and not too costly |
| D-alt | Touchdown speed, level, gap, or overtravel | Deferred candidate | Can affect contact event and final thickness | Use only after confirming it is a true recipe knob |
| Fixed | Pickup force/time/speed, ejector pin/plunge | Fixed/recorded first | Can cause no-die, crack, or placement noise | Optimize separately if pickup defects appear |
| Fixed/deferred | Cure temperature/time | Fixed first, deferred later | Affects final strength and productivity | Major confound if varied unintentionally |
| Fixed | Epoxy lot/aging | Fixed/recorded | Viscosity changes can distort A effects | Treat as block or risk item |

## Current Project X Selection Guidance

Planning score is qualitative. It ranks usefulness for an education-lab DOE,
not real equipment importance.

| Factor | Score | Default Decision |
| --- | ---: | --- |
| Epoxy amount / dispense time | 34 | Include |
| Bond force | 32 | Include |
| Bond time | 28 | Include |
| Wait/wetting time | 25 | Include if controllable; otherwise defer |
| Touchdown speed / level / overtravel | 20 | Defer unless engineer confirms |
| Pickup/ejector settings | 19 | Fix and monitor |
| Cure condition | 22 | Fix first; possible later DOE |
| Epoxy lot/aging | N/A | Fixed/blocking variable |

## Recommended First DOE Posture

If the project has 8 experimental conditions:

1. Prefer a 3-factor, 2-level full factorial DOE with `A/B/C` when only three
   credible active factors are confirmed.
2. Use a 4-factor, 2-level fractional DOE only when `D` is a credible,
   controllable factor and the team accepts aliasing.
3. If using a 4-factor fractional DOE, protect the `A x B` interpretation as
   much as possible because epoxy amount and bond force are the most likely
   BLT/spread interaction.

Recommended first response set:

- Primary Y: BLT and die shear strength.
- Guardrail Y: bleed/overflow, void grade or count, die placement, no-die,
  chip crack, and chipping.
- Production monitor: epoxy usage and process time.

## Interaction Hypotheses

| Interaction | Priority | Mechanism Hypothesis | DOE Handling |
| --- | --- | --- | --- |
| `A x B` | High | Epoxy amount and bond force jointly determine spread, BLT, bleed, and contact | Avoid aliasing with key main effects when possible |
| `A x D` | Medium | Amount and wait/wetting time can affect void and wetting | Examine if void is a measurable Y |
| `B x C` | Medium | Force and time jointly determine contact/wetting energy | Useful if shear is weak |
| `A x cure` | Medium | Epoxy amount and cure may affect final strength and void | Fix cure first |
| `epoxy age x A` | Hidden | Viscosity shift changes dispense amount behavior | Record or block |

## Decision Criteria For Next DOE

The next DOE should be selected by criteria state first, then supported by
statistics. Do not let a single strong statistical effect override a hard
quality guardrail.

| Criteria State | Recommended Next DOE |
| --- | --- |
| Die shear fails | Rescue DOE around epoxy amount, force, and/or bond time; do not optimize production |
| BLT out of spec high | Reduce epoxy amount or increase force within safe limits; check bleed/overflow |
| BLT out of spec low | Increase epoxy amount or reduce force; check shear margin |
| Bleed/overflow severe | Reduce epoxy amount, reduce squeeze, or check viscosity/dispense pattern |
| Void high | Review dispense amount/pattern, wait/wetting, material condition, and cure; use image/grade if possible |
| Placement/no-die/pickup defect appears | Hold bonding DOE interpretation and stabilize pickup/eject/vision first |
| Quality pass but small margin | Run confirmation or narrow stabilization DOE |
| Quality pass with enough margin | Consider cautious epoxy reduction or cycle-time reduction DOE |
| Production improvement causes shear/BLT margin loss | Stop aggressive improvement and select conservative baseline |

## Mechanism Map

| Observation | Likely Mechanism | Planner Response |
| --- | --- | --- |
| Higher epoxy improves shear but increases BLT | Coverage/contact improved but bond line thickens | Search lower epoxy with force/time support |
| Higher force reduces BLT but creates bleed or damage | Squeeze-out or mechanical stress | Reduce force or epoxy; inspect failure mode |
| Longer time improves shear but not BLT | Wetting/contact improved without geometry change | Consider fixing time if cycle-time cost is acceptable |
| Void appears despite high epoxy | Entrapped air, poor wetting, contamination, or dispense pattern issue | Do not solve by amount alone |
| High shear with bad failure mode | Measured force does not equal good interface quality | Keep as risky candidate or reject |
| No-die or pickup miss | Pickup/release process is unstable | Stop DOE optimization and stabilize handling |

## Defect Map

| Defect | Possible Causes | DOE Treatment |
| --- | --- | --- |
| Epoxy on die or collet contamination | Off-center collet, weak vacuum, too much epoxy, excessive press | Guardrail; inspect pickup and dispense |
| Epoxy on lead/pad overflow | Too much epoxy, dotter issue, tailing, squeeze-out | Guardrail; reduce amount or adjust dispense |
| Placement shift / orientation issue | Index, camera, pin, head, vacuum, release issue | Guardrail; not solved by bond force alone |
| No die | Pickup miss, release failure, vacuum issue | Hard hold/block |
| Epoxy void | Amount variation, contamination, leveling, wrong collet, wetting issue | Guardrail or primary if quantified |
| Chip crack/chipping | Ejector pin array, pickup force, excessive bonding force | Hard guardrail |

## Production Map

| Production Metric | Optimization Rule |
| --- | --- |
| Epoxy usage | Reduce only after BLT and die shear pass with stable margin |
| Bond time | Reduce only if shear and failure mode remain acceptable |
| Wait/wetting time | Treat as quality lever first, production penalty second |
| Cure time | Major productivity lever, but defer unless cure DOE is planned |
| Rework/scrap risk | Any no-die, crack, severe bleed, or bad failure mode can dominate nominal productivity gain |

## Analysis Guidance By Y Type

Continuous Y such as BLT and die shear:

- Report mean, standard deviation, min, max, and worst-case.
- Calculate factor effects and contribution when design structure permits.
- Use ANOVA/regression only with clear model assumptions and enough degrees of
  freedom.
- If a spec exists, report margin and capability-style indices only as
  supporting evidence.

Categorical or ordinal Y such as failure mode, void grade, bleed grade, or
pickup miss:

- Report pass/fail count, worst observed grade, and risky-code frequency.
- Use proportion or chi-square style tests only when counts are sufficient.
- With small counts, prioritize engineering guardrail logic over p-value claims.

Repeated measurements:

- Do not show only averages.
- Always show min/max or worst-case for hard quality risks.
- If repeats disagree, recommend confirmation before narrowing the DOE.

## DOE-Ready Checklist

Before generating the first real DOE, the planner should confirm:

- What is the exact process family: epoxy, DAF, flip-chip, or other?
- What are the engineer-approved active X factors?
- Are the proposed low/high values DOE levels, not equipment min/max?
- What are the hard specs for BLT and die shear?
- What Y values can actually be measured in the available lab time?
- How many samples or repeats are possible per run?
- Which guardrail failures immediately reject a condition?
- Is cure fixed?
- Are epoxy storage, thaw, aging, and lot controlled?
- Is pickup/release stable enough to interpret bonding DOE results?

## Use Rule For AI DOE Planner

When the structured request declares `process_id = die_attach_spa300_epoxy`,
the planner should:

1. Load this card before selecting factors or levels.
2. Ask for missing specs, safe factor ranges, and measurement availability.
3. Prefer focused 2- or 3-factor DOE if process knowledge already identifies
   credible active factors.
4. Avoid adding a weak fourth factor just to create a fractional DOE.
5. If 4 factors are used, explicitly disclose aliasing and the interaction that
   will be resolved in the next DOE.
6. Recommend the next DOE from criteria state first, then support it with
   statistical analysis.
7. Never treat example screen values or past education-lab levels as equipment
   limits.
