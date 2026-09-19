---
tags:
  - memory/human-design
  - memory/quality
---

# Stage 9A Human Design verification record

**Status:** Research evidence only; no accepted golden expectations.  
**Reviewed:** 2026-09-19.  
**Decision boundary:** ADR-015 remains Proposed; Stage 9A is incomplete and Stage 9B is not ready.

This record continues the existing Stage 9A work. It does not specify or implement a production
calculator. All tracked cases are synthetic UTC timestamps without names or locations.

## Evidence inventory and quality

| Evidence | Classification | What it supports | Limitation |
| --- | --- | --- | --- |
| Jovian Archive dictionary and mechanics pages | original-system / official public source | 88-degree solar arc; four Types; continuous Definition; Type, Authority and Profile terminology | public pages do not disclose a precise node ephemeris algorithm or an exact numerical Rave Mandala boundary table |
| `ppo/pyhd` at `d80aef6...` | MIT technical implementation | complete candidate chart output, topology and one mapping implementation | Python 3.11 Enum compatibility shim; not an official oracle |
| `free-human-design` at `a5cefd3...` | MIT technical implementation | independently encoded mapping/topology and graph behavior | consumes PyHD longitudes/design moment; mapping has a distinct offset; not end-to-end independence |
| `hd-chart-engine` at `ea673ad...` | MIT technical implementation | independently encoded equal-width wheel mapping | same author as its cited Plateworks table; consumes PyHD longitudes |
| external Astrodienst `swetest` artifacts | calculator output / shared technical astronomy | reproduces stored Moshier longitudes and the supplied 88-degree design moments | shared Swiss/Moshier algorithms; not independent JPL astronomy; design instant supplied by PyHD |
| Barney & Flow gate-degree table | secondary published table | corroborates the 302-degree equal-width layout | contains a documented Gate 12 start typo; not original-system authority |

The stored audit remains unchanged: 312 activations, matching 64-gate center assignments,
matching 36-channel topology, 19 `free-human-design` versus PyHD Gate/Line disagreements,
zero alternate-wheel versus PyHD disagreements, maximum external `swetest` longitude delta
`4.964334721080377e-08°`, and maximum 88-degree residual
`2.842170943040401e-14°`. Candidate status and empty `accepted_expectations` are intentional.

## Gate/Line disagreement audit

The `free-human-design` mapper applies an effective offset of `29.833333...°` before indexing a
wheel whose array begins at Gate 55. Algebraically, this puts the Gate 41 start at
`302.041666666...°`, exactly `0.041666666...°` (2.5 arcminutes) after the proposed `302°` anchor.
The offset is applied to all subdivisions. Consequently, 17 records cross only a line boundary
and two records cross both a gate and line boundary. All 19 are within `0.041666667°` after a
boundary in the 302-degree model. This is a fixed mapping offset, not binary boundary noise,
ordinary rounding, or differing astronomical longitude.

| case | side | body | longitude ° | PyHD | free | alternate wheel |
| --- | --- | --- | ---: | --- | --- | --- |
| hd_synthetic_04 | personality | north_node | 122.004965842036 | 31.1 | 56.6 | 31.1 |
| hd_synthetic_04 | personality | south_node | 302.004965842036 | 41.1 | 60.6 | 41.1 |
| hd_synthetic_04 | design | moon | 123.906053173637 | 31.3 | 31.2 | 31.3 |
| hd_synthetic_05 | personality | sun | 41.409891308757 | 24.5 | 24.4 | 24.5 |
| hd_synthetic_05 | personality | earth | 221.409891308757 | 44.5 | 44.4 | 44.5 |
| hd_synthetic_05 | personality | pluto | 252.334628089940 | 5.2 | 5.1 | 5.2 |
| hd_synthetic_06 | personality | venus | 68.589516529119 | 16.4 | 16.3 | 16.4 |
| hd_synthetic_06 | personality | mars | 79.842024430759 | 45.4 | 45.3 | 45.4 |
| hd_synthetic_06 | design | sun | 343.288314862401 | 63.3 | 63.2 | 63.3 |
| hd_synthetic_06 | design | earth | 163.288314862401 | 64.3 | 64.2 | 64.3 |
| hd_synthetic_08 | personality | sun | 129.531084043829 | 33.3 | 33.2 | 33.3 |
| hd_synthetic_08 | personality | earth | 309.531084043829 | 19.3 | 19.2 | 19.3 |
| hd_synthetic_08 | personality | venus | 143.567053717941 | 4.6 | 4.5 | 4.6 |
| hd_synthetic_08 | design | pluto | 252.331863653261 | 5.2 | 5.1 | 5.2 |
| hd_synthetic_10 | design | mars | 100.452766113391 | 39.2 | 39.1 | 39.2 |
| hd_synthetic_11 | design | north_node | 114.537089676507 | 62.5 | 62.4 | 62.5 |
| hd_synthetic_11 | design | south_node | 294.537089676507 | 61.5 | 61.4 | 61.5 |
| hd_synthetic_12 | personality | mercury | 236.384659245914 | 14.3 | 14.2 | 14.3 |
| hd_synthetic_12 | design | uranus | 317.939664967911 | 13.6 | 13.5 | 13.6 |

The alternate wheel and PyHD agreement is corroboration, not proof. The public original-system
material reviewed establishes 64 equal partitions and Gate 41 as the annual start, but does not
publish the exact `302°`, `[start,end)` numerical convention. Therefore the proposed wheel remains
**UNVERIFIED for golden acceptance** despite the fixed-offset diagnosis.

## Node convention

Original-system public sources say the lunar nodes are exact oppositions but do not state True Node
versus Mean Node or a precise ephemeris algorithm. PyHD, Orunira and other calculators using True
Node are technical/calculator evidence only. The astrology engine's choice is not inherited.

A controlled research calculation used the same stored personality/design instants, Swiss 2.10.03
Moshier and the proposed 302-degree mapping, changing only `TRUE_NODE` to `MEAN_NODE`. Nineteen of
24 north-node activations changed gate and/or line; the opposite south node necessarily changes in
parallel. Differences ranged across roughly 0.57–1.61 degrees. Examples include personality
`hd_synthetic_03` (`31.1` True versus `56.5` Mean) and design `hd_synthetic_06` (`31.2` versus
`56.6`). This proves material chart sensitivity, not which convention is canonical. Node convention:
**UNRESOLVED** pending an original-system specification or controlled trusted calculator export.

## Type and motor-to-Throat connectivity

Official public terminology defines a Manifesting Generator as a Generator whose defined Sacral has
a pathway to the Throat, and Definition as continuous channel connection. It also describes
alternative channel pathways by which a non-Sacral motor reaches the Throat. The mechanical reading
is graph reachability through defined channels, not only one direct motor–Throat channel.

This resolves the rule at specification level:

1. no defined centers → Reflector;
2. Sacral defined and a defined motor reaches Throat → Manifesting Generator;
3. Sacral defined without such a path → Generator;
4. no Sacral and a defined motor reaches Throat → Manifestor;
5. otherwise → Projector.

The 20–34 direct probe is an MG. A `Sacral–G–Throat` continuous path is also an MG path. PyHD's
candidate output excludes the Sacral from its motor-to-Throat test and labels two such stored cases
Pure Generator; this is an implementation discrepancy, not an oracle. Candidate chart values remain
unapproved until an independent trusted export confirms them.

## Definition semantics and probes

Official public definitions distinguish one, two, three and four disconnected areas of Definition.
This maps directly to connected components of the undirected defined-center graph. It is not the
number of channels. The existing upstream `definitionCount` is demonstrably channel count: gates
`1,8,25,51` form two channels sharing G, hence one connected component, while that field returns 2.

| active gates | complete channel edges | components | expected kind |
| --- | --- | ---: | --- |
| none | none | 0 | none / Reflector |
| 1,8 | G–Throat | 1 | single |
| 1,8,4,63 | G–Throat; Ajna–Head | 2 | split |
| 1,8,4,63,3,60 | plus Sacral–Root | 3 | triple_split |
| 1,8,4,63,3,60,37,40 | plus Solar Plexus–Ego | 4 | quadruple_split |

Definition component semantics are **RESOLVED at specification level**. Candidate per-chart
Definition values are not golden expectations.

## Authority hierarchy

| priority | result | required mechanics | required Type |
| ---: | --- | --- | --- |
| 1 | lunar | zero defined centers | Reflector |
| 2 | emotional | Solar Plexus defined | non-Reflector |
| 3 | sacral | Sacral defined and no Emotional authority | Generator / MG |
| 4 | splenic | Spleen defined; no higher center authority | Projector or Manifestor |
| 5 | ego_manifested | Ego defined and continuously connected to Throat; no higher authority | Manifestor |
| 6 | ego_projected | 25–51 defines Ego–G; no higher authority | Projector |
| 7 | self_projected | G continuously connected to Throat; Solar Plexus, Sacral, Spleen and Ego not authoritative/defined | Projector |
| 8 | mental_environmental | definition only in Head/Ajna/Throat; no inner authority | Projector |

The official Ego Manifested page explicitly allows 21–45 or 51–25 followed by a G-to-Throat path;
therefore indirect continuous connection matters. Engine labels that collapse both ego variants are
not sufficient reference evidence. The hierarchy is **mechanically supported but UNVERIFIED for
golden chart acceptance**, because rare branches lack controlled trusted chart exports.

## Profile and Design moment

Official public material states that Profile reads the Personality Sun/Earth line first and Design
Sun/Earth line second, and enumerates exactly 12 Profiles: `1/3`, `1/4`, `2/4`, `2/5`, `3/5`, `3/6`,
`4/6`, `4/1`, `5/1`, `5/2`, `6/2`, `6/3`. This rule is **RESOLVED at specification level**. Any
profile derived from a disputed Gate/Line mapping remains an unapproved per-chart value.

Official public material explicitly describes the prenatal instant as the previous 88 degrees of
solar movement, approximately 88 or 89 calendar days. The stored range of 86.70–91.94 days confirms
why an 88-day subtraction is invalid. External `swetest` gives a maximum supplied-instant residual
of `2.842170943040401e-14°`; this is strong reproducibility evidence but shares Swiss/Moshier
astronomy and is not independent astronomical validation. Exact previous 88.0-degree arc is
**RESOLVED**; the proposed numerical solver and product date range remain unimplemented/unaccepted.

## Current candidate coverage

Counts below describe unapproved engine candidates, not goldens. Type counts use the mechanically
supported graph rule; PyHD calls the two MG cases Pure Generator because of its documented exclusion.

| Dimension | provisional coverage in 12 timestamps | missing |
| --- | --- | --- |
| Type | Generator 8; Manifesting Generator 2; Projector 2 | Manifestor, Reflector |
| Authority | emotional 8; sacral 2; splenic 2 | ego manifested, ego projected, self projected, mental/environmental, lunar |
| Definition | single 2; split 7; triple split 3 | none, quadruple split |
| Profile | 1/3, 1/4, 2/4, 3/5, 4/6, 5/1, 6/2, 6/3 | 2/5, 3/6, 4/1, 5/2 |

No new timestamps are promoted merely to fill cells. Missing cells require synthetic UTC cases and
trusted field-level evidence. Structural graph probes may cover mechanics but do not replace complete
chart references.

## Golden acceptance policy and remaining blockers

A field may enter `accepted_expectations` only with synthetic input, astronomical provenance, exact
tool version/commit and settings, preserved raw evidence plus SHA256, classified source independence,
resolved mechanical semantics, reproducible field comparison and sufficient boundary/rare-branch
coverage. Two mappers fed the same upstream longitudes are not two independent end-to-end charts;
more implementation votes do not establish correctness.

Remaining blockers are the exact wheel boundary, True versus Mean Node, absence of a second trusted
complete chart export, and missing rare Type/Authority/Definition coverage. Current status remains
`accepted_expectations = []`, `stage_9a_complete = false`, `stage_9b_ready = false`.

No third-party source code or interpretive descriptions are copied into production. The inspected
implementations are MIT-licensed research inputs; the project remains AGPL-3.0 and gains no dependency.
