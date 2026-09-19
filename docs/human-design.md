---
tags:
  - memory/human-design
---

# Stage 9A — Human Design mechanical calculation specification

**Status: Accepted project convention (ADR-015, stage9a2-v1). Stage 9B.2 and Stage 9B complete; Human Design backend/API complete.**
Research date: 2026-09-19. See [[human-design-verification]], [[05_DECISIONS]],
[[07_TEST_STRATEGY]] and [[04_CURRENT_STATE]]. Complete mechanical core and typed API exist.

Implementation scope: `human_design_astronomy.py` owns orchestration/native primitives/88° solver,
`human_design_mapping.py` owns the pure mapper and wheel, `human_design_models.py` immutable internal
values and domain errors. The native adapter imports the existing Astrology state owner (same
`_LOCK` and `initialize_ephemeris`), with no behavior-changing refactor. All native calls, including
UTC conversions, occur under that lock. No fixture/research tool or external HD engine is imported.
The existing astronomy/mapper code is unchanged by Stage 9B.1B. `human_design_core.py` consumes
AstronomyResult for pure graph/classification and exposes `calculate_human_design_core(birth_utc)`.
It calls astronomy exactly once. Complete immutable results preserve the original astronomy object
(including both activation lists and Design moment), plus sorted mechanical fields, Profile
lines/label and metadata. Components are sorted tuples, not channel counts. No interpretation text,
person identifiers, coordinates or logs. Internal errors include classification_error.
46 astronomy and 95 classification tests pass: all 18 structural vectors, 364 official activations
and 14/14 Type/Authority/Definition/Profile matches. Stage 9B.2 adds 53 API tests without core changes.
Frontend/AI/PDF remain unimplemented.

## 1. Scope and system boundary

Only Personality/Design activations, gate/line, active gates, channels, centers,
Type, Strategy, Authority, Profile and Definition are specified. Astronomical positions
are measurable; Human Design is a symbolic self-knowledge framework, not a scientifically
validated personality measurement. No interpretation text is included.

Excluded: Color/Tone/Base, Variable, PHS, Environment, Motivation, Perspective,
Transference, DreamRave, composite/transit charts, gate/line descriptions and Cross names.
The Sun/Earth quartet can later be read from existing activations; no naming system here.

## 2. Frozen input contract — implemented in Stage 9B.2

`POST /api/v1/human-design/calculate`:

```json
{"utc_datetime":"2000-01-01T12:00:00Z"}
```

Require an explicit zero UTC offset; reject naive datetimes, unknown/approximate birth
times and extra fields. No name, latitude or longitude: geocentric longitude has Earth’s
center as observer and needs time, not birthplace. Coordinates belong to the existing
geocoding/timezone pipeline. No houses, ASC, MC or aspects. [Swiss API](https://www.astro.com/swisseph/swephprg.htm)
documents geocentric defaults and the separate topocentric flag.

## 3. Two moments

Personality uses the exact birth instant. Design solves the previous **88.0° solar arc**,
not 88 calendar days: `target = normalize(birth_sun_longitude - 88)`.
This distinction comes from the [original-system introduction](https://jovianarchive.com/blogs/human-design-basics/introduction-to-the-human-design-system).
Both moments use the same body set and astronomical convention.

## 4. Frozen project solver specification

Engineering choices below are project decisions, not quotations from Human Design sources.

- Convert UTC using `utc_to_jd`; use UT1 with `calc_ut` consistently. Convert the root
  back with `jdut1_to_utc`. Do not confuse UTC, UT1 and TT.
- Bracket `[birth_jd - 100, birth_jd - 80]` days. Define residual
  `((sun(t) - target + 180) mod 360) - 180`. Verify finite values, increasing Sun,
  opposite endpoint signs and no residual discontinuity inside this short bracket.
- Bisection, maximum 64 iterations. Require BOTH bracket width <= 0.01 seconds
  and absolute residual <= 1e-7 degrees. These are numerical convergence limits,
  not a claim of astronomical accuracy. Detect floating-point stagnation.
- Return the final bracket midpoint only after both limits pass; evaluate residual at that midpoint.
  Use the unrounded UT1 Julian day for Design activations, not the serialized UTC timestamp.
  Serialize UTC to microseconds, round half-even; serialization must not feed back into astronomy.
  Return only a converged past root. No convergence/bracket failure =>
  `design_moment_error`; native failure => `ephemeris_error`; no 88-day fallback.
- Freeze supported birth years 1800–2100 inclusive (Gregorian UTC); the earlier Design bracket
  may precede 1800. Reject out-of-range input. This is a project support boundary, not an accuracy
  guarantee for the entire range. API future-date validation uses the existing shared injectable
  BirthProfile policy; the pure calculation layer has no clock. Reject leap-second :60 inputs.

## 5. Astronomy and reuse boundary

Use the already pinned pyswisseph 2.10.3.2 / Swiss 2.10.03, explicit Moshier,
tropical, geocentric, apparent ecliptic-of-date longitude. No SIDEREAL, HELCTR,
BARYCTR, TOPOCTR, TRUEPOS or J2000 flags. Request FLG_MOSEPH | FLG_SPEED consistently.
Use ADR-010 automatic time-model defaults, empty private ephemeris path and no external time files.
Moshier range/accuracy limits remain; inspect returned flags and fail on unexpected mode.
The future adapter must share safe native-state locking/initialization across engines;
do not introduce a second independent lock around Swiss global state. This stage does
not refactor astrology. House/aspect service output is not the HD astronomy interface.

## 6. Bodies and nodes

Exactly 13 entries on each side (26 total): `sun`, `earth`, `moon`, `north_node`,
`south_node`, `mercury`, `venus`, `mars`, `jupiter`, `saturn`, `uranus`, `neptune`, `pluto`.
No Chiron or Lilith. Earth = normalized Sun + 180°, not a geocentric Earth-body call.
South Node = normalized North Node + 180°. Original-system opposition terminology:
[Jovian dictionary](https://jovianarchive.com/pages/human-design-dictionary).

**True Node is RESOLVED as the adopted HD project convention**, not inherited from astrology.
[Orunira's own method](https://orunira.com/en/human-design/method), pinned PyHD and
free-human-design all explicitly use true nodes. The original-system public pages
reviewed do not specify the precise lunar-node ephemeris algorithm. Stage 9A.1 collected 14 official
Jovian charts: all 56 North/South Node observations match True Node, with 46 discriminating against
Mean Node. This is observed calculator behavior, not a published algorithm/precision guarantee;
the official version, settings and exact Design instant are undisclosed. Raw sources/settings are
in the evidence register. The 56 observed node Gate/Line values are accepted behavioral expectations;
the claim that Jovian publishes or internally uses our exact algorithm remains UNVERIFIED.
A controlled True/Mean comparison changed 19 of 24 north-node Gate/Line activations in the
12 synthetic cases. This motivated the controlled test; it is no longer an unresolved project choice.

## 7. Gate wheel and line mapping

Gate 41 begins at **302° = 2° Aquarius**. Gate width = **45/8° = 5.625°**;
line width = **15/16° = 0.9375°**. Prograde gate sequence starting at 302°:

```text
41 19 13 49 30 55 37 63 22 36 25 17 21 51 42 3
27 24 2 23 8 20 16 35 45 12 15 52 39 53 62 56
31 33 7 4 29 59 40 64 47 6 46 18 48 57 32 50
28 44 1 43 14 34 9 5 26 11 10 58 38 54 61 60
```

Source comparison: [published gate-degree table](https://www.barneyandflow.com/gate-zodiac-degrees)
and [pinned wheel implementation](https://github.com/domalhambra/hd-chart-engine/blob/ea673ad2614b7968ddf1c93670b6cbf20ab26eed/src/wheel.ts).
The published table contains a Gate 12 start typo (22°37′30″ Gemini versus the preceding
Gate 45 end 22°27′30″); use the consistent equal-width structure, document the discrepancy,
without treating that secondary table as an original-system specification.
The engine and Plateworks site have the same author and do NOT count as independent sources.
The 19 stored mapper disagreements are fully explained by `free-human-design` using an effective
Gate 41 start of `302.041666666...°`: 17 line-only and two gate+line differences. This diagnoses a
fixed 2.5-arcminute offset. Acceptance is based on the combined official behavioral and technical
evidence, not mapper voting. Full rows are in [[human-design-verification]].
Stage 9A.1 official minute probes bracket the transition between 301.99922119558215° and
302.0006347126726° under local Swiss/Moshier astronomy. Anchor and transition are PARTIALLY
VERIFIED as official-system facts. The project adopts exactly 302 degrees and `[start,end)`:
both are RESOLVED project decisions. Official behavior supports the boundary location; exact
equality ownership is a project-defined deterministic tie-break rule. The public form exposes
HH:mm, not seconds. A minute bracket must not be presented as an exact official mathematical boundary.

For a finite longitude, treat its binary64 value as an exact rational number:
`r = (longitude - 302) mod 360`, `i = floor(r / (45/8))`,
`gate = sequence[i]`, `line = 1 + floor((r - i*(45/8)) / (15/16))`.
Use stdlib exact rational arithmetic at this small mapping boundary if necessary.
Intervals are `[start,end)`; exact endpoints belong to the next interval. Normalize
360 to 0. No snapping epsilon and no rounding before mapping. An ephemeris uncertainty
interval crossing a boundary must be flagged during verification, not silently snapped.

Hand-derived structural vectors (not chart-engine snapshots):

| Longitude | Gate.Line |
| --- | --- |
| 302 | 41.1 |
| 302.000001 | 41.1 |
| 307.624999 | 41.6 |
| 307.625 | 19.1 |
| 302.9375 | 41.2 |
| 359.999999, 0, 360 | 25.2 |
| 30 | 3.4 |
| 90 | 15.2 |
| 180 | 46.2 |
| 270 | 10.2 |

## 8. Gate → Center structural table

Internal center identifiers are fixed below. Each gate belongs to exactly one center.
Independently encoded identifiers; matched against PyHD and free-human-design snapshots
after `heart→ego`, `splenic→spleen`, `solarplexus→solar_plexus` alias normalization.

| Center | Gates |
| --- | --- |
| head | 61, 63, 64 |
| ajna | 4, 11, 17, 24, 43, 47 |
| throat | 8, 12, 16, 20, 23, 31, 33, 35, 45, 56, 62 |
| g | 1, 2, 7, 10, 13, 15, 25, 46 |
| ego | 21, 26, 40, 51 |
| sacral | 3, 5, 9, 14, 27, 29, 34, 42, 59 |
| solar_plexus | 6, 22, 30, 36, 37, 49, 55 |
| spleen | 18, 28, 32, 44, 48, 50, 57 |
| root | 19, 38, 39, 41, 52, 53, 54, 58, 60 |

## 9. Channel topology

The original system identifies [36 channels](https://jovianarchive.com/pages/channels-in-human-design-the-life-force).
The full pairs agree between the two source snapshots; no interpretive channel names are copied.

| gate_a | gate_b | center_a | center_b |
| --- | --- | --- | --- |
| 1 | 8 | g | throat |
| 2 | 14 | g | sacral |
| 3 | 60 | sacral | root |
| 4 | 63 | ajna | head |
| 5 | 15 | sacral | g |
| 6 | 59 | solar_plexus | sacral |
| 7 | 31 | g | throat |
| 9 | 52 | sacral | root |
| 10 | 20 | g | throat |
| 10 | 34 | g | sacral |
| 10 | 57 | g | spleen |
| 11 | 56 | ajna | throat |
| 12 | 22 | throat | solar_plexus |
| 13 | 33 | g | throat |
| 16 | 48 | throat | spleen |
| 17 | 62 | ajna | throat |
| 18 | 58 | spleen | root |
| 19 | 49 | root | solar_plexus |
| 20 | 34 | throat | sacral |
| 20 | 57 | throat | spleen |
| 21 | 45 | ego | throat |
| 23 | 43 | throat | ajna |
| 24 | 61 | ajna | head |
| 25 | 51 | g | ego |
| 26 | 44 | ego | spleen |
| 27 | 50 | sacral | spleen |
| 28 | 38 | spleen | root |
| 29 | 46 | sacral | g |
| 30 | 41 | solar_plexus | root |
| 32 | 54 | spleen | root |
| 34 | 57 | sacral | spleen |
| 35 | 36 | throat | solar_plexus |
| 37 | 40 | solar_plexus | ego |
| 39 | 55 | root | solar_plexus |
| 42 | 53 | sacral | root |
| 47 | 64 | ajna | head |

## 10. Activation and definition mechanics

Union gates across both imprints. A channel exists when both endpoint gates are present,
even on different sides; duplicates remain in planetary lists but collapse in the topology.
A center is defined only if incident to a complete channel; a lone gate cannot define it.
Use `undefined`, not `open`, for all remaining centers: no activated gates is a distinct
case from undefined-with-activations. Sources: the original-system
[black/red distinction](https://jovianarchive.com/pages/the-black-and-red-in-human-design)
and the independently reviewed channel implementations.

Create an undirected graph of defined centers with defined channels as edges.
DFS/BFS counts connected components, not channels. `0:none`, `1:single`, `2:split`,
`3:triple_split`, `4:quadruple_split`. Reflector: zero components, empty component list.
Sort centers/components and channel gate pairs for reproducible JSON.
[Original-system definition guide](https://jovianarchive.com/pages/understanding-definition-in-human-design)
supports the connected-group interpretation. Ignore wide/simple split subtypes for this scope.

## 11. Type and Strategy

Motors: `sacral, ego, solar_plexus, root`. Connection means any continuous path through defined
channels, not only a direct motor–throat edge. Source: Jovian dictionary's continuous
definition rule and [Type/Strategy](https://jovianarchive.com/pages/type-and-strategy-in-human-design).

```text
if no defined centers: reflector
else if sacral defined:
    if any motor reaches throat: manifesting_generator
    else: generator
else if any motor reaches throat: manifestor
else: projector
```

Strategy identifiers: generator/manifesting_generator → `wait_to_respond`;
manifestor → `inform`; projector → `wait_for_invitation`; reflector → `wait_lunar_cycle`.
These are system labels, not advice generated by the application. Do not impose an
additional MG strategy of informing as a replacement for response.

## 12. Frozen Authority hierarchy with explicit ordering

```text
if type == reflector: lunar
else if solar_plexus defined: emotional
else if sacral defined: sacral
else if spleen defined: splenic
else if ego defined and connected(ego, throat): ego_manifested
else if ego defined and channel(25,51) and type == projector: ego_projected
else if connected(g, throat) and type == projector: self_projected
else if type == projector and defined_centers subset {head,ajna,throat}: mental_environmental
else: classification_error  # never guess
```

The priority prevents lower authorities overriding emotional/sacral/splenic definition.
Ego manifested can run through G, not just 21–45. Sources:
[ego manifested](https://jovianarchive.com/pages/ego-manifested-authority-in-human-design-the-will-that-speaks),
[ego projected](https://jovianarchive.com/pages/ego-projected-authority-in-human-design-willpower-and-invitations),
[self projected](https://jovianarchive.com/pages/self-projected-authority-in-human-design-the-projectors-voice).
Mental/environmental and lunar identifiers do not imply a defined inner authority center.
Engine labels collapsing ego variants are not accepted; never reduce both to generic `ego`.
The hierarchy is mechanically supported by
official public descriptions. Stage 9A.1 adds controlled official examples for all previously
missing authority labels; 14 chart graph probes agree. Stage 9A.2 adds structural tests for splenic
Projector/Manifestor, emotional/sacral priority and indirect Ego paths. Authority rules are RESOLVED
as project mechanics. Lack of an official splenic chart is a disclosed non-blocking coverage limit,
not a hidden choice. Official Authority labels in the 14 captures are accepted behavioral references.

## 13. Profile

Personality Sun line / Design Sun line. Representation:
`{"personality_line":1,"design_line":3,"label":"1/3"}`.
Allowed pairs: 1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6, 4/1, 5/1, 5/2, 6/2, 6/3.
Source: [original-system profile guide](https://jovianarchive.com/pages/understanding-profile-in-human-design).
Impossible pair => verification failure, never force-fit. No descriptions.

## 14. Frozen response semantics, privacy and errors

Metadata must declare spec revision, ephemeris/version, tropical/geocentric/apparent,
node type and fixed solver settings (not actual residual/bracket width/iterations or Julian days).
Include birth/design UTC, per-side 13 ordered
`{body, longitude, gate, line}` records, sorted active gates, channels, defined/undefined
centers, Type/Strategy/Authority/Profile and Definition kind/count/components. Transport fields are
`definition`, `component_count` and `definition_components`, preserving these semantics.
No person names, coordinates, logs or storage in the calculation service or API adapter.
Research fixtures contain synthetic timestamps only.

Domain envelope: `detail.code/message`; `invalid_utc_datetime`, `invalid_request`, `unsupported_date_range`,
`ephemeris_error`, `design_moment_error`, `classification_error`. Do not expose native exceptions.
Stage 9B.2 registers strict Pydantic request/response/error models and a thin FastAPI adapter.
Request/admission errors use 422; ephemeris/design/classification failures use 503 with static safe
messages. `validation_now()` is UTC and injectable; shared birth-date policy plus exact instant
comparison rejects future inputs without a core clock. Z/+00:00 are equivalent; response uses Z.
Calendar date/time supports minute/second precision and up to six fractional-second digits;
sub-microsecond inputs are rejected rather than silently truncated. See [[06_API_CONTRACTS]]
for full synthetic examples and error precedence. No float rounding or serialization feedback.

## 15. Verification and Stage 9B entry gate

See [[human-design-verification]] for actual evidence, hashes, rejected candidates,
coverage gaps, copyright audit and reproduction commands. Raw candidate labels remain historical;
only field-level rows in `human_design_references.json/accepted_expectations` are accepted.
Two independent mapping implementations over the same longitudes do
not equal two independently calculated charts.

Stage 9A.1 now has a second trusted complete chart source: 14 Jovian public UI numeric captures,
364 matching activations and official examples of the missing rare categories. Independent internal
astronomy is UNKNOWN; official tool version/settings are undisclosed. Stage 9A.2 accepts those
discrete outputs as golden mechanical behavior, NOT version-pinned independent astronomy.
All project semantic choices are frozen; ADR-015 is unchanged. Stage 9B.1A astronomy and Stage 9B.1B
graph/classification are complete. Stage 9B.2 API is complete; the Stage 9B delivery matrix passes.
Every official regression must pass in 9B; a mismatch blocks release and requires diagnosis, never
automatic fixture replacement or tolerance added to Gate/Line labels. Further original-system
evidence may require a new versioned decision, not silent drift of this convention.

The Stage 9B.2 adapter preserves the completed core and its behavioral, boundary, graph and
concurrency regressions. Seven representative official API cases cover all five Types and rare
Authorities; the complete 14-case golden matrix remains in the core tests. All raw evidence is unchanged.
No Stage 10 or AI work is authorized by this specification.
