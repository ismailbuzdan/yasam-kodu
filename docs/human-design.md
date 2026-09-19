---
tags:
  - memory/human-design
---

# Stage 9A — Human Design mechanical calculation specification

**Status: Proposed; reference acceptance blocked. Stage 9A is NOT complete.**
Research date: 2026-09-19. See [[human-design-verification]], [[05_DECISIONS]],
[[07_TEST_STRATEGY]] and [[04_CURRENT_STATE]]. No production service or endpoint exists.

## 1. Scope and system boundary

Only Personality/Design activations, gate/line, active gates, channels, centers,
Type, Strategy, Authority, Profile and Definition are proposed. Astronomical positions
are measurable; Human Design is a symbolic self-knowledge framework, not a scientifically
validated personality measurement. No interpretation text is included.

Excluded: Color/Tone/Base, Variable, PHS, Environment, Motivation, Perspective,
Transference, DreamRave, composite/transit charts, gate/line descriptions and Cross names.
The Sun/Earth quartet can later be read from existing activations; no naming system here.

## 2. Input proposal — not an implemented contract

Future `POST /api/v1/human-design/calculate`:

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

## 4. Proposed solver specification

Engineering choices below are project proposals, not quotations from Human Design sources.

- Convert UTC using `utc_to_jd`; use UT1 with `calc_ut` consistently. Convert the root
  back with `jdut1_to_utc`. Do not confuse UTC, UT1 and TT.
- Bracket `[birth_jd - 100, birth_jd - 80]` days. Define residual
  `((sun(t) - target + 180) mod 360) - 180`. Verify finite values, increasing Sun,
  opposite endpoint signs and no residual discontinuity inside this short bracket.
- Bisection, maximum 64 iterations. Require BOTH bracket width <= 0.01 seconds
  and absolute residual <= 1e-7 degrees. These are numerical convergence limits,
  not a claim of astronomical accuracy. Detect floating-point stagnation.
- Return only a converged past root. No convergence/bracket failure => proposed
  `design_moment_error`; native failure => `ephemeris_error`; no 88-day fallback.
- Initially propose birth years 1800–2100, with the entire earlier bracket in the
  supported astronomical range. Confirm this product range before 9B implementation.

## 5. Astronomy and reuse boundary

Propose the already pinned pyswisseph 2.10.3.2 / Swiss 2.10.03, explicit Moshier,
tropical, geocentric, apparent ecliptic-of-date longitude. No SIDEREAL, HELCTR,
BARYCTR, TOPOCTR, TRUEPOS or J2000 flags. Retain speed if needed by diagnostics.
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

**True Node is proposed independently for HD and remains UNRESOLVED**, not inherited from astrology.
[Orunira's own method](https://orunira.com/en/human-design/method), pinned PyHD and
free-human-design all explicitly use true nodes. The original-system public pages
reviewed do not specify the precise lunar-node ephemeris algorithm. A controlled
official-calculator comparison remains an acceptance requirement; do not call this
an official Jovian precision guarantee. Raw sources/settings are in the evidence register.
A controlled True/Mean comparison changed 19 of 24 north-node Gate/Line activations in the
12 synthetic cases, so this is a material acceptance blocker; see [[human-design-verification]].

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
and obtain an original-system boundary export before accepting references.
The engine and Plateworks site have the same author and do NOT count as independent sources.
The 19 stored mapper disagreements are fully explained by `free-human-design` using an effective
Gate 41 start of `302.041666666...°`: 17 line-only and two gate+line differences. This diagnoses a
fixed 2.5-arcminute offset but does not by itself prove the 302-degree proposal; golden acceptance
remains **UNVERIFIED**. Full rows are in [[human-design-verification]].

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

## 12. Authority proposal with explicit ordering

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
Engine disagreement on ego variants remains a reference-acceptance blocker, not an excuse
to silently reduce both to a generic `ego` field. The hierarchy is mechanically supported by
official public descriptions but rare branches still lack controlled trusted chart exports; it is
therefore unapproved as golden chart evidence.

## 13. Profile

Personality Sun line / Design Sun line. Proposed representation:
`{"personality_line":1,"design_line":3,"label":"1/3"}`.
Allowed pairs: 1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6, 4/1, 5/1, 5/2, 6/2, 6/3.
Source: [original-system profile guide](https://jovianarchive.com/pages/understanding-profile-in-human-design).
Impossible pair => verification failure, never force-fit. No descriptions.

## 14. Proposed response, privacy and errors

Metadata should declare spec revision, ephemeris/version, tropical/geocentric/apparent,
node type and solver settings. Include birth/design UTC, per-side 13 ordered
`{body, longitude, gate, line}` records, sorted active gates, channels, defined/undefined
centers, Type/Strategy/Authority/Profile and `{kind, component_count, components}`.
No person names, coordinates, logs or storage in the future calculation service.
Research fixtures contain synthetic timestamps only.

Proposed domain envelope: `detail.code/message`; `invalid_utc_datetime`, `invalid_request`,
`ephemeris_error`, `design_moment_error`, `classification_error`. Do not expose native exceptions.
None of these proposed HD contracts is registered in FastAPI in Stage 9A.

## 15. Verification and Stage 9B entry gate

See [[human-design-verification]] for actual evidence, hashes, rejected candidates,
coverage gaps, copyright audit and reproduction commands. No candidate is an accepted
expected result. Two independent mapping implementations over the same longitudes do
not equal two independently calculated charts.

Before 9B: obtain a second complete trusted chart export for selected synthetic cases,
resolve documented disagreements, cover the missing types/authorities, and promote
references field-by-field with provenance. Then accept ADR-015 and finalize date range.

Only after a separate 9B task: design a shared astronomy adapter without altering existing
outputs; implement UTC schema, 88° solver, exact gate/line mapping, graph classification
and endpoint; add boundary, graph, concurrency, API and independent-reference regression.
No Stage 10 or AI work is authorized by this specification.
