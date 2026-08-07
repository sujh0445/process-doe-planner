# Process Knowledge Card: Wafer Sawing / DISCO D3241 Blade Saw

Status: practice-informed draft
Primary source dates: 2026-06-30 wafer sawing practice, 2026-07-06 wafer sawing practice transcript
Equipment focus: DISCO D3241 automatic dicing saw

## 1. DOE Scope

The practical project scope should be blade saw wafer dicing, not laser or plasma dicing.

Goal:
- Find a wafer sawing condition that satisfies chipping quality.
- If quality margin exists, improve productivity by increasing feed speed or reducing process time.

## 2. Public Process Facts

Observed equipment:
- DISCO D3241 automatic dicing saw.
- HMI screens include device data, alignment, auto/manual cut, spindle speed, feed speed, blade height, wafer thickness, tape thickness, and cutting sequence.

Observed measurement:
- Microscope/image software can inspect die edge and cut line.
- Current project correction: chipping size should be treated as a saw-line-boundary based damage measurement, not a generic edge peak-to-valley roughness value.
- Practically, draw/identify a horizontal saw-line boundary reference, then draw a horizontal line through the deepest recessed/chipped point. The chipping size is the y-direction gap between those two lines.
- Do not mix this with scribe-line margin, kerf width, or generic peak-to-valley roughness.
- High-scope images may support wider-area image analysis, but the saw line must be used as the reference line.
- If hairline/alignment is properly set, saw-line margin is a setup guardrail rather than the main optimization response.

Practice update from 2026-07-06:
- Feed/stage speed was discussed with practical values such as 100, 150, and 200.
- Spindle RPM values such as 30k, 40k, and 50k were discussed; typical use was described around 40k-50k.
- One wafer can be split by channel/line range to reduce wafer use, but condition boundaries and measurement locations must be recorded.

## 3. Recommended X Candidates

| Priority | X | Role | Recommendation |
| --- | --- | --- | --- |
| 1 | Feed speed / cutting speed | Main quality-productivity lever | Include in first DOE |
| 2 | Spindle RPM | Cutting mechanics lever | Include in first DOE |
| 3 | Blade type/spec | Material/tool factor | Include only if blade change time is acceptable |
| 4 | Cut depth / blade height | Setup/depth factor | Usually fixed for UV tape; reconsider for DAF |
| 5 | DI water flow | Cooling/debris/static support | Usually fixed/monitored in short practice |
| 6 | UV/tape condition | Holding/support factor | Fixed control unless multiple tape/UV conditions are available |

Note:
- Cutting method, step cut, dual-pass cut, and laser grooving can matter for chipping, but they are too broad for the first project DOE unless explicitly selected as the project scope.

## 4. Recommended Y Candidates

| Priority | Y | Type | Direction |
| --- | --- | --- | --- |
| 1 | Observed local max chipping size | continuous | lower is better |
| 2 | Chipping pass/fail by spec | binary | pass required |
| 3 | Chipping spread/range/stdev | continuous | lower is more stable |
| 4 | Mean chipping size | continuous | lower is better |
| 5 | Edge contour / sidewall roughness image score | continuous or image-derived score | lower is better |
| 6 | Cutting time or feed-speed-derived throughput | production metric | faster is better after quality pass |
| Guardrail | blade break, chip fly-off, severe misalignment | categorical | abnormal / invalidate or separate |

## 5. Measurement Rules

Before DOE:
- Define the project quality target using baseline comparison if no official chipping spec is available.
- Because the current chipping measurement is tied to the saw line boundary, scribe-line geometry should be used only as a physical guardrail/background margin. Do not invent a hard customer spec unless it is approved by the instructor/engineer.
- Define fixed measurement points, preferably 5-point or 9-point if time permits.
- Record worst visible chipping as an observed local maximum, not as a true wafer-level maximum.
- Save measurement photos.
- If multiple conditions are made on one wafer, record channel, line range, direction, and condition boundary.

Current project measurement definition:

```text
Chipping size = y-direction distance between the saw-line boundary reference
and the horizontal line passing through the deepest recessed/chipped point.
```

Interpretation:
- Treat chipping size as the main quality Y for local damage depth from the saw-line boundary.
- Use mean, max/worst-case, and spread together.
- A large observed local max value matters even when the mean is acceptable because a single severe local chip-out can make the condition risky.
- If the remaining safe region to the product area is consumed or the chip/product area is invaded, that condition is a guardrail failure regardless of mean value.

Measurement reliability limitation:

The current project data are not based on full-wafer inspection. The measured
`Max chipping size` should therefore be interpreted as:

```text
Observed local max chipping size
  = the largest chipping value found within the limited inspected chips/edges
    under the project's manual observation procedure.
```

This is not the true maximum chipping value of the entire wafer or condition.
It can be affected by where the operator starts looking, how many adjacent chips
are inspected, and whether the worst defect happens to be found. Therefore:
- Use it mainly for relative comparison between conditions measured with the same procedure.
- Do not claim it as a full population maximum or final outgoing-quality guarantee.
- Report mean, spread, and sample count together so the decision is not based on one observed max alone.
- Kerf/effective-width guardrail was considered during method design, but it is not used in the current Wafer1-Wafer5 DOE decision. The current project decision is intentionally based on max chipping size only, because kerf width and alignment margin were not measured consistently across all wafer runs.

Geometry reference for the current wafer:

```text
Scribe line width = 60 um
Nominal blade width = 23 um
Nominal one-side kerf clearance = 1/2 * Scribe line width - 1/2 * Kerf width
```

Use this geometry as a safety margin reference, but evaluate the practical
guardrail with chipping and alignment included:

```text
Margin =
1/2 * Scribe Line Width
- (
    1/2 * Kerf Width
    + Max Chipping Size
    + Alignment Error
  )
```

For the current 60 um scribe-line case:

```text
Margin =
30 um
- (
    1/2 * Kerf Width
    + Max Chipping Size
    + Alignment Error
  )
```

Acceptance guardrail:

```text
Margin > 0
```

This is a possible physical safety check for a future expanded analysis. It is not part of the current Wafer1-Wafer5 DOE acceptance decision.

Optional kerf-width diagnostic:

```text
Kerf width = scribe line width - upper remaining margin - lower remaining margin
```

For the current 60 um scribe-line case:

```text
Kerf width = 60 um - upper margin - lower margin
```

Use kerf width only as a secondary diagnostic Y if it is measured consistently. It can help determine whether a feed/RPM condition is widening the actual cut width, but it is not part of the current Wafer1-Wafer5 DOE decision logic.

Important separation:
- Kerf width should use the representative/normal saw-line boundary, excluding local chipping pits.
- Chipping size should use the y-direction distance from the saw-line boundary reference to the horizontal line through the deepest local chipped point.
- Mixing the deepest chipping point into kerf width double-counts damage and makes the two responses ambiguous.

Deprecated / future-only guardrail metric:

The following conservative effective-width guardrail was discussed during method
development, but it is not used in the current Wafer1-Wafer5 DOE report. It
should only be revived if kerf width and alignment/margin data are measured
consistently for every condition.

```text
Alignment allowance = 2.5 um

Effective damage width
  = Kerf width + 2 * Observed local max chipping size + 2 * Alignment allowance
  = Kerf width + 2 * Observed local max chipping size + 5 um

Remaining margin
  = Scribe line width - Effective damage width
  = 60 um - Effective damage width
```

Interpretation if revived later:
- `Alignment allowance = 2.5 um` is a fixed conservative project constant, based on the practice discussion that a properly aligned saw line can still move around roughly 1-2 um, with additional measurement/setup uncertainty.
- Do not add alignment allowance to the raw chipping Y. Keep chipping as the measured saw-line-boundary damage depth.
- Use the allowance only in a future guardrail calculation, not in the current raw chipping analysis.
- If this future guardrail is revived and `Effective damage width` approaches or exceeds 60 um, reject or treat the condition as high risk even if the average chipping value looks acceptable.
- If a clear align miss is observed, mark the run abnormal instead of trying to correct it with this allowance.

After DOE:
- Report mean, max, min, range, stdev, and pass count.
- Do not claim full Cpk unless enough same-condition data exist.
- Use Cpk only as a provisional final-condition check if the run count is limited.

## 6. Process Mechanism Rules

| Observation | Process interpretation | DOE action |
| --- | --- | --- |
| Feed speed high and chipping increases | Higher mechanical load / less gentle cutting, possible vibration/debris effect | Reduce feed or find RPM/blade condition that recovers margin |
| Feed speed high but chipping still within spec | Quality margin exists | Consider production-improvement DOE |
| Feed speed high and chipping increases but kerf width stays similar | Local chip-out/intrusion worsened without major cut-width expansion | Treat feed as the likely quality-productivity trade-off lever |
| Feed speed high and kerf width also increases | Actual cut width may be widening due to blade load, runout, vibration, or blade condition | Treat as higher risk; check blade/kerf/alignment before accepting feed increase |
| RPM effect unclear | RPM may interact with feed, blade state, and wafer condition | Do not overinterpret one run; use repeat/interaction check |
| Severe misalignment | Setup failure rather than normal recipe effect | Mark abnormal; do not use as normal chipping response |
| Tape mount poor / chip fly-off | Holding/support issue | Treat as abnormal setup or fixed-control failure |
| Edge/center difference | Wafer location/upstream wheel mark may be nuisance factor | Record measurement location or block if possible |
| Saw-line offset is small after correct alignment | Normal equipment repeatability rather than process response | Treat as setup guardrail; do not make it a primary Y |
| Feed speed high but chipping stays within spec | Quality margin can be converted into productivity | Consider margin-budget DOE to raise feed while monitoring max chipping |

## 7. First DOE Templates

### Template A: Minimum practical focused DOE

Use when project time is tight.

| Factor | Low | High |
| --- | --- | --- |
| A: Feed speed | instructor-approved low, likely around 100 | instructor-approved high, likely around 150 or 200 |
| B: Spindle RPM | instructor-approved low, likely around 40k | instructor-approved high, likely around 50k |

Design:
- 2^2 full factorial.
- Repeat if possible.
- Use one extra confirmation condition if time remains.
- If one wafer is split into conditions, treat channel/line segment as a nuisance/block note rather than a perfect independent replicate.

### Template B: Blade-comparison DOE

Use only if blade change is feasible.

| Factor | Low | High |
| --- | --- | --- |
| A: Feed speed | low | high |
| B: Spindle RPM | low | high |
| C: Blade type | blade 1 | blade 2 |

Design:
- Prefer 2^3 full factorial if time allows.
- If time is tight, block by blade and run feed/RPM DOE on one blade first.

## 8. Next-DOE Decision Engine

```text
IF no official chipping spec exists:
  define a baseline condition and compare candidate conditions against it.
  use mean chipping, observed local max chipping, spread, and productivity improvement.
  treat obvious chip-area invasion, blade damage, or clear align miss as abnormal-run flags.

IF no condition passes chipping spec:
  lower feed speed and/or adjust RPM; check blade/tape/alignment.

IF one condition barely passes:
  run confirmation/repeatability near that condition.

IF one condition passes with comfortable chipping margin:
  run margin-budget DOE: increase feed speed while monitoring max chipping and spread.

IF multiple conditions pass:
  choose candidate by quality margin first, then productivity.

IF categorical abnormal events occur:
  separate them from continuous chipping analysis and treat as guardrail failures.
```

Current wafer-sawing project framing:

```text
Baseline:
  RPM 50k / Feed 50

Goal:
  Keep saw-line-boundary chipping size close to baseline while increasing feed speed
  to reduce cutting time.

Decision:
  Prefer the highest feed condition whose mean, observed local max/worst-case, and spread do not
  worsen beyond the project-accepted quality margin.
```

## 9. What To Ask Before Actual Project

- What feed speed values are safe and instructor-approved?
- What RPM values are safe and meaningful on the actual recipe?
- Is blade type fixed or can two blades be compared?
- What blade spec is installed?
- What is wafer thickness and tape thickness?
- Is the tape UV only, or is DAF involved?
- What chipping spec should be used: 5 um, 10 um, or another value?
- How many measurement points and repeated measurements are realistically possible?
