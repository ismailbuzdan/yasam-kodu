---
tags:
  - memory/human-design
  - memory/quality
---

# Stage 9A Human Design verification record

**Status:** Stage 9A.2 accepted project conventions and scoped behavioral golden references.
**Reviewed:** 2026-09-19.  
**Decision boundary:** ADR-015 Accepted; Stage 9A complete, Stage 9B ready but not started.

This record continues the existing Stage 9A work. It does not implement a production calculator.
The original cases are synthetic UTC timestamps without names or locations. New official form
captures disclose the generic UTC-transport city, not a person's birthplace.
Sections before "Stage 9A.2 final qualification" preserve historical assessments at their recorded
stage. Their Proposed/empty/unresolved statements are superseded by the final qualification section;
raw evidence and recorded empirical limitations are not superseded or rewritten.

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

## Stage 9A.1 continuation — 2026-09-19

This section supersedes the earlier baseline coverage/blocker statements, not its immutable evidence.
Continuation began on `stage9a-wip`, HEAD and origin both
`4777b17b66fe72523d836f29a9e3fb064bbe2fb2`. At the latest continuation request,
17 untracked research/evidence files already existed; all were retained. No tracked diff existed.
The original 50 evidence files and original 12 timestamp fixture remain byte-identical.

### Source search and collection qualification

- [Official Jovian calculator](https://jovianarchive.com/pages/get-your-human-design-chart):
  14 complete synthetic charts, retrieved 2026-09-19; each includes 13 Personality and 13 Design
  Gate/Line values, displayed UTC, Type, Authority, Definition and Profile.
- [Official 2026 Rave New Year announcement](https://jovianarchive.com/products/2026-rave-new-year-forecast):
  Gate 41 ingress is published at January 22, 2026, 00:54 UTC, minute precision.
- [IHDS](https://www.ihdschool.com/) public chart form inspected; no additional chart collected.
  Jovian/IHDS/MyBodyGraph documentation searches did not locate a precise public node algorithm.
  Searches for Maia Mechanics technical/archived documentation returned no qualifying primary
  algorithm specification. This is a search limitation, not proof none exists.
- [RoxyAPI](https://roxyapi.com/products/human-design-api) technical vendor material was considered,
  not treated as original-system specification. Secondary assertions about Maia/True Node were
  not accepted as proof; no real-person chart examples were copied.
- Existing pinned MIT implementation evidence retained. No new dependency or third-party source
  was vendored; source fetched temporarily by the adapter is hash-checked against the old manifest.
- [Jovian terms](https://jovianarchive.com/pages/terms-and-conditions) reviewed. Only mechanical
  numeric facts and short classification labels recorded. No interpretive descriptions, graphics,
  chart image, private endpoint, login or paywall bypass used.

Browser skill was used for public UI interaction and read-only rendered DOM extraction. These are
structured captures of visible textContent, NOT raw HTML/API response bytes and NOT manual numeric
transcription. The left/right column ordering was checked against visible planetary glyphs:
Sun, Earth, Moon, North Node, South Node, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto.
Header strings and spaces inside numeric labels are preserved. Each capture has its own source URL,
retrieval timestamp, input and collection metadata; SHA256 is in `human_design_references.json`.
Version, ephemeris and node setting are explicitly null/UNVERIFIED, not guessed.

The public form requires a city. Reykjavik was a UI-only UTC transport selection, not a person's
birthplace; every output's displayed UTC was checked against the intended synthetic instant.
Synthetic labels only; email omitted. No real-user data. UI inspection found `HH:mm`,
`maxLength=5`; no seconds interface was exposed. No attempt was made to evade that limitation.

**Second complete chart: RESOLVED as source availability.** This is a trusted official separate
calculation pipeline: we supplied no PyHD longitudes or Design moment. Its internal astronomy
independence is UNKNOWN; it may share Swiss algorithms. Opaque versions/settings prevent
fully reproducible version-pinned golden qualification.

### Official synthetic coverage

All entries below remain `candidate_not_approved`, not golden expectations.

| case_id | synthetic UTC | official Type | official Authority | official Definition | Profile |
| --- | --- | --- | --- | --- | --- |
| hd_boundary_0053 | 2026-01-22 00:53:00 | Projector | Solar Plexus | Split | 6/3 |
| hd_boundary_0055 | 2026-01-22 00:55:00 | Projector | Solar Plexus | Split | 1/3 |
| hd_rare_ego_manifested | 2002-06-14 12:00:00 | Manifestor | Ego Manifested | Single | 1/3 |
| hd_rare_ego_projected | 2000-04-08 12:00:00 | Projector | Ego Projected | Split | 5/1 |
| hd_rare_environmental | 2000-04-10 12:00:00 | Projector | Sounding Board | Single | 1/3 |
| hd_rare_manifestor | 2000-03-11 12:00:00 | Manifestor | Solar Plexus | Single | 5/1 |
| hd_rare_profile25 | 2000-01-13 12:00:00 | Generator | Solar Plexus | Triple Split | 2/5 |
| hd_rare_profile36 | 2000-02-05 12:00:00 | Manifesting Generator | Sacral | Single | 3/6 |
| hd_rare_profile41 | 2000-02-17 12:00:00 | Manifesting Generator | Solar Plexus | Single | 4/1 |
| hd_rare_profile52 | 2000-02-18 12:00:00 | Manifesting Generator | Solar Plexus | Single | 5/2 |
| hd_rare_quadruple | 2000-01-12 12:00:00 | Generator | Solar Plexus | Quadruple Split | 1/4 |
| hd_rare_reflector | 2000-02-24 12:00:00 | Reflector | Lunar Cycle | None | 6/2 |
| hd_rare_self | 2000-03-16 12:00:00 | Projector | Self Projected | Single | 4/6 |
| hd_synthetic_03 | 2000-03-20 00:00:00 | Generator | Sacral | Single | 2/4 |

The bounded pinned-PyHD search inspected 896 daily 12:00 UTC moments, found all requested discovery
labels in 11 cases and reported no errors. Its original stdout is retained as `pyhd_rare_search.jsonl`.
Its exact capture timestamp/historical adapter hash were not in stdout and remain UNVERIFIED;
the provenance envelope discloses this. It is discovery evidence only. Subsequent exact-case
comparisons have timestamp, upstream commit/version, adapter SHA256 and checked source hashes.

Official new-set coverage: all five Types and five Definition kinds; seven Authority labels
(emotional, sacral, ego manifested, ego projected, self projected, environmental, lunar).
Splenic remains covered only by the original provisional set, not this official subset.
All four previously missing profiles (2/5, 3/6, 4/1, 5/2) now have official observations;
union with the original provisional set covers all 12, NOT 12 golden-verified profiles.
Rare category presence is verified; exhaustive priority/path combinations and near-boundary
cases are not. Thus rare mechanics coverage overall is PARTIALLY VERIFIED.

### Field-level comparison

`human_design_official_comparison.json` contains each official chart versus pinned PyHD and
the separately encoded project-proposal graph probe. For EACH of the 14 rows above:

| field | Official vs PyHD | Official vs proposed mechanics |
| --- | --- | --- |
| Personality Gate/Line | MATCH (182/182) | NOT AVAILABLE: no project astronomical/mapping engine |
| Design Gate/Line | MATCH (182/182) | NOT AVAILABLE: no project astronomical/mapping engine |
| Type | MATCH after declared subtype normalization | MATCH (14/14 graph probes on official gates) |
| Authority | MATCH after declared label normalization | MATCH (14/14 graph probes on official gates) |
| Definition | MATCH (component-count label) | MATCH (14/14 graph probes on official gates) |
| Profile | MATCH | MATCH (14/14 Sun-line probes) |

Raw labels are never replaced: Pure Generator → Generator, Energy/Classic/Mental Projector →
Projector are comparison-only subtype normalization; Lunar → Lunar Cycle and Outer Authority →
Sounding Board are explicitly declared label aliases. Sounding Board is the official observed label,
mapped in our proposal to mental/environmental with no inner authority. Without this normalization
some strings differ; this is not concealed mechanical agreement. There are zero new semantic
mismatches in the collected subset. The original Sacral-exclusion Type discrepancy and channel-count
`definitionCount` issue remain; this subset does not validate every problematic original case.
Graph probes derive channels from official gates using corroborated structural tables, not from
official graph exports, and are not an independent astronomical chart pipeline.

### Anchor and exact boundary

Official observations on 2026-01-22:

| synthetic UTC | official Personality Sun | Swiss/Moshier Sun longitude |
| --- | --- | ---: |
| 00:53 | 60.6 | 301.99922119558215° |
| 00:55 | 41.1 | 302.0006347126726° |

This is an approximately 0.001414° bracket under the stated local astronomy, consistent with 302°
and inconsistent with the competing 302.0416667° anchor at these inputs. The official ephemeris
itself is undisclosed; this is controlled behavioral inference, not an official longitude table.
The published 00:54 minute event reinforces the bracket, not exact sub-minute precision.

Gate 41 anchor: **PARTIALLY VERIFIED**. Exact boundary: **PARTIALLY VERIFIED** for transition
bracketing; equality ownership `[start,end)` is **UNRESOLVED**. No exact equality observation or
complete original-system numerical table was found. Neither constant rounding tolerance nor all
384 line boundaries can be inferred from two minute inputs. The original 19-offset diagnosis
remains intact (17 line-only, two gate+line); no implementation-voting acceptance.

### Controlled True/Mean comparison

The same Swiss 2.10.03 Moshier flags, same instant and same pinned proposed wheel are used,
changing only node algorithm; South Node is the corresponding +180° point.
Personality instants are exact supplied UTC. Design instants are the pinned PyHD 88° solver output:
the official calculator does NOT expose its exact Design instant, an explicit limitation.
The adapter discloses both Enum compatibility shim and controlled longitude/angle override before
calling the upstream mapper. No astrology production code is involved.

| case_id | side | body | official | TRUE_NODE | MEAN_NODE | official_match |
| --- | --- | --- | --- | --- | --- | --- |
| hd_boundary_0053 | personality | north_node | 37.4 | 37.4 | 37.6 | TRUE_ONLY |
| hd_boundary_0053 | personality | south_node | 40.4 | 40.4 | 40.6 | TRUE_ONLY |
| hd_boundary_0053 | design | north_node | 22.1 | 22.1 | 63.5 | TRUE_ONLY |
| hd_boundary_0053 | design | south_node | 47.1 | 47.1 | 64.5 | TRUE_ONLY |
| hd_boundary_0055 | personality | north_node | 37.4 | 37.4 | 37.6 | TRUE_ONLY |
| hd_boundary_0055 | personality | south_node | 40.4 | 40.4 | 40.6 | TRUE_ONLY |
| hd_boundary_0055 | design | north_node | 22.1 | 22.1 | 63.5 | TRUE_ONLY |
| hd_boundary_0055 | design | south_node | 47.1 | 47.1 | 64.5 | TRUE_ONLY |
| hd_rare_ego_manifested | personality | north_node | 45.1 | 45.1 | 45.1 | BOTH |
| hd_rare_ego_manifested | personality | south_node | 26.1 | 26.1 | 26.1 | BOTH |
| hd_rare_ego_manifested | design | north_node | 45.6 | 45.6 | 45.6 | BOTH |
| hd_rare_ego_manifested | design | south_node | 26.6 | 26.6 | 26.6 | BOTH |
| hd_rare_ego_projected | personality | north_node | 56.4 | 56.4 | 56.4 | BOTH |
| hd_rare_ego_projected | personality | south_node | 60.4 | 60.4 | 60.4 | BOTH |
| hd_rare_ego_projected | design | north_node | 31.2 | 31.2 | 31.3 | TRUE_ONLY |
| hd_rare_ego_projected | design | south_node | 41.2 | 41.2 | 41.3 | TRUE_ONLY |
| hd_rare_environmental | personality | north_node | 56.4 | 56.4 | 56.4 | BOTH |
| hd_rare_environmental | personality | south_node | 60.4 | 60.4 | 60.4 | BOTH |
| hd_rare_environmental | design | north_node | 31.2 | 31.2 | 31.3 | TRUE_ONLY |
| hd_rare_environmental | design | south_node | 41.2 | 41.2 | 41.3 | TRUE_ONLY |
| hd_rare_manifestor | personality | north_node | 31.1 | 31.1 | 56.6 | TRUE_ONLY |
| hd_rare_manifestor | personality | south_node | 41.1 | 41.1 | 60.6 | TRUE_ONLY |
| hd_rare_manifestor | design | north_node | 31.3 | 31.3 | 31.5 | TRUE_ONLY |
| hd_rare_manifestor | design | south_node | 41.3 | 41.3 | 41.5 | TRUE_ONLY |
| hd_rare_profile25 | personality | north_node | 31.2 | 31.2 | 31.3 | TRUE_ONLY |
| hd_rare_profile25 | personality | south_node | 41.2 | 41.2 | 41.3 | TRUE_ONLY |
| hd_rare_profile25 | design | north_node | 33.3 | 33.3 | 33.2 | TRUE_ONLY |
| hd_rare_profile25 | design | south_node | 19.3 | 19.3 | 19.2 | TRUE_ONLY |
| hd_rare_profile36 | personality | north_node | 31.2 | 31.2 | 31.2 | BOTH |
| hd_rare_profile36 | personality | south_node | 41.2 | 41.2 | 41.2 | BOTH |
| hd_rare_profile36 | design | north_node | 31.6 | 31.6 | 33.1 | TRUE_ONLY |
| hd_rare_profile36 | design | south_node | 41.6 | 41.6 | 19.1 | TRUE_ONLY |
| hd_rare_profile41 | personality | north_node | 31.2 | 31.2 | 31.1 | TRUE_ONLY |
| hd_rare_profile41 | personality | south_node | 41.2 | 41.2 | 41.1 | TRUE_ONLY |
| hd_rare_profile41 | design | north_node | 31.5 | 31.5 | 31.6 | TRUE_ONLY |
| hd_rare_profile41 | design | south_node | 41.5 | 41.5 | 41.6 | TRUE_ONLY |
| hd_rare_profile52 | personality | north_node | 31.2 | 31.2 | 31.1 | TRUE_ONLY |
| hd_rare_profile52 | personality | south_node | 41.2 | 41.2 | 41.1 | TRUE_ONLY |
| hd_rare_profile52 | design | north_node | 31.5 | 31.5 | 31.6 | TRUE_ONLY |
| hd_rare_profile52 | design | south_node | 41.5 | 41.5 | 41.6 | TRUE_ONLY |
| hd_rare_quadruple | personality | north_node | 31.2 | 31.2 | 31.3 | TRUE_ONLY |
| hd_rare_quadruple | personality | south_node | 41.2 | 41.2 | 41.3 | TRUE_ONLY |
| hd_rare_quadruple | design | north_node | 33.3 | 33.3 | 33.2 | TRUE_ONLY |
| hd_rare_quadruple | design | south_node | 19.3 | 19.3 | 19.2 | TRUE_ONLY |
| hd_rare_reflector | personality | north_node | 31.2 | 31.2 | 31.1 | TRUE_ONLY |
| hd_rare_reflector | personality | south_node | 41.2 | 41.2 | 41.1 | TRUE_ONLY |
| hd_rare_reflector | design | north_node | 31.4 | 31.4 | 31.6 | TRUE_ONLY |
| hd_rare_reflector | design | south_node | 41.4 | 41.4 | 41.6 | TRUE_ONLY |
| hd_rare_self | personality | north_node | 31.1 | 31.1 | 56.6 | TRUE_ONLY |
| hd_rare_self | personality | south_node | 41.1 | 41.1 | 60.6 | TRUE_ONLY |
| hd_rare_self | design | north_node | 31.3 | 31.3 | 31.4 | TRUE_ONLY |
| hd_rare_self | design | south_node | 41.3 | 41.3 | 41.4 | TRUE_ONLY |
| hd_synthetic_03 | personality | north_node | 31.1 | 31.1 | 56.5 | TRUE_ONLY |
| hd_synthetic_03 | personality | south_node | 41.1 | 41.1 | 60.5 | TRUE_ONLY |
| hd_synthetic_03 | design | north_node | 31.3 | 31.3 | 31.4 | TRUE_ONLY |
| hd_synthetic_03 | design | south_node | 41.3 | 41.3 | 41.4 | TRUE_ONLY |

North: True matches 28/28, Mean matches 5/28; 23 discriminating activations.
South: True matches 28/28, Mean matches 5/28; 23 discriminating activations.
All 46 discriminating node records favor True; 10 match both. Opposite pairs and the two
nearby boundary charts are correlated, NOT 56 statistically independent experiments.
The 14 charts include 13 distinct calendar dates. This is strong observed official True-Node
behavior. It does not disclose osculating-node algorithm details, ephemeris flags/version,
rounding or the official Design solver. **Node convention: PARTIALLY VERIFIED**.
Published precise official specification remains UNVERIFIED; golden promotion remains blocked.

### Updated acceptance matrix

RESOLVED means the stated specification/source-availability question is settled, not that
every chart is a golden. Independent refers to computation provenance, not number of votes.

| Convention | Evidence | Independent? | Official? | Status | Remaining blocker |
| --- | --- | --- | --- | --- | --- |
| 88° Design moment | prior original-system text + stored residual | shared astronomy | yes, conceptual rule | RESOLVED | solver precision/date-range acceptance later |
| Gate sequence | prior technical tables + 364 sampled official activations | separate official pipeline, partial sampling | behavior only | PARTIALLY VERIFIED | full numerical original-system table |
| Gate anchor | two minute probes + annual ingress | separate opaque pipeline | yes | PARTIALLY VERIFIED | exact numerical anchor specification |
| Gate exact boundary | 60.6 → 41.1 bracket | separate opaque pipeline | yes | PARTIALLY VERIFIED | equality ownership UNRESOLVED; all line boundaries |
| Node algorithm | 46 discriminating N/S matches favor True | separate official pipeline; shared local Swiss probes | behavior only | PARTIALLY VERIFIED | precise public algorithm/version/settings |
| Gate→Center | original two complete technical tables | separately encoded tables | no complete official table captured | PARTIALLY VERIFIED | table-level golden qualification |
| Channels | original 36-edge agreement + official graph probes | separate technical tables, shared probe topology | chart labels only | PARTIALLY VERIFIED | full topology reference qualification |
| Motor→Throat | prior official continuous-path rule | source plus graph reasoning | yes | RESOLVED | problematic original charts not newly exported |
| Type | prior decision tree + 14 matching graph probes | official pipeline vs research graph | yes | RESOLVED | full golden per-chart coverage |
| Definition | official component semantics + 0–4 observations | official pipeline vs graph components | yes | RESOLVED | golden promotion policy |
| Authority | prior branch hierarchy + rare official examples | official pipeline vs graph probes | yes | PARTIALLY VERIFIED | exhaustive priority/path branches; official splenic sample |
| Profile | prior Sun-line rule + missing-pair observations | official pipeline vs direct Sun-line extraction | yes | RESOLVED | all 12 official/golden cases not collected |
| Second trusted complete chart | 14 complete public UI captures | separate pipeline; independent astronomy UNKNOWN | yes | RESOLVED | exact tool/version/astronomy unavailable |
| Rare coverage | 11 official rare candidates | separate pipeline vs discovery engine | yes | PARTIALLY VERIFIED | category presence ≠ exhaustive mechanics |

### Acceptance and reproduction

No values promoted: `accepted_expectations=[]`, ADR-015 Proposed,
`stage_9a_complete=false`, `stage_9b_ready=false`.
Critical residual blockers are exact wheel/equality semantics, precise node algorithm qualification,
opaque official tool/settings provenance and incomplete exhaustive mechanics/reference coverage.
Second-chart absence and missing rare-category examples are no longer accurate blockers.

The audit is now deliberately READ-ONLY. It validates recorded hashes and original checks instead
of rewriting the manifest to fit current files. New artifacts were registered only after all
50 prior hashes were independently checked unchanged. The original audit remains 312 activations;
the new 364 comparison activations are reported separately, not silently merged into its dataset.

```text
docker compose exec backend python -m pytest tests/test_human_design_reference_integrity.py -q
docker compose exec backend python -m pytest -q
docker compose exec backend python -m pip check
docker compose exec backend python tools/audit_human_design_references.py
docker compose exec backend python tools/inspect_human_design_official.py
```

The last command re-derives the offline comparison; it writes no evidence.
The explicit network diagnostic `tools/search_human_design_candidates.py --compare-official`
prints a fresh candidate run; never redirect it over preserved raw artifacts.

## Stage 9A.2 final qualification — 2026-09-19

Repository gate: clean `stage9a-wip`, HEAD = origin =
`61c1e3c37db523b9ef99b3305a0b7a7de01c7a3c`. This is an acceptance review of existing
evidence, not a new web search or chart collection. All 68 raw artifacts, their manifest hashes,
the original 12 candidates, and the 9A.1 comparison outputs remain unchanged.

**Decision: Stage 9A complete; Stage 9B ready, not started. ADR-015 Accepted.**
The question is whether a developer has deterministic, defensible rules, not whether proprietary
official implementation details can be reproduced. Unknown official internals remain UNVERIFIED.
They are not necessary for the explicitly bounded reference class adopted here.

### Frozen rules and evidence status

In this table RESOLVED refers to the PROJECT implementation decision. Empirical claims remain
limited to their stated precision. No undocumented choice is relabeled an official-system fact.

| Choice | Project status | Basis / residual empirical limitation |
| --- | --- | --- |
| Previous 88.0° solar arc | RESOLVED | original-system public rule; shared Swiss residual check, not independent astronomy |
| Gate 41 anchor = 302° | RESOLVED | official minute bracket/annual ingress plus consistent technical layout; exact official numerical specification PARTIALLY VERIFIED |
| Gate width = 45/8° | RESOLVED | equal 64-part project wheel, corroborated layout and sampled official behavior |
| Line width = 15/16° | RESOLVED | six equal subdivisions per gate; sampled official behavior, not all official endpoints observed |
| 64-gate sequence | RESOLVED | freeze the complete sequence in human-design.md and convention fixture; technical corroboration, not votes |
| Equality [start,end) | RESOLVED | project deterministic tie-break; exact official equality ownership UNRESOLVED, no observed contradiction |
| True Node | RESOLVED | all 46 discriminating N/S observations favor Swiss TRUE_NODE; proprietary algorithm/version UNVERIFIED |
| Gate→Center / 36 channels | RESOLVED | freeze documented complete tables, two-source agreement plus graph/official behavioral checks |
| Motor→Throat / Type | RESOLVED | continuous defined-channel path; Sacral is a motor; all five Types represented |
| Authority | RESOLVED | explicit priority and path rules, rare official charts plus structural splenic and priority probes |
| Definition | RESOLVED | connected components 0–4, never channel count |
| Profile | RESOLVED | Personality Sun line / Design Sun line; exactly 12 allowed pairs |
| Astronomy / solver / range | RESOLVED | pinned Swiss/Moshier, UTC→UT1, 80–100 day bracket, midpoint/both tolerances; 1800–2100 birth years |
| Second chart / rare coverage | RESOLVED | separate official behavioral pipeline plus sufficient focused structural coverage |

Official behavior supports the boundary location; exact equality ownership is a project-defined
deterministic tie-break rule. True Node is adopted on official calculator behavioral evidence,
NOT because Jovian publishes a True Node algorithm or because the astrology engine uses it.

Project support years do not assert full-range observational accuracy. Solver tolerances are
numerical limits, not ephemeris accuracy. The final unrounded midpoint drives Design activations;
UTC serialization never feeds back into the calculation. All concrete choices are in
[[human-design]], including clock-free calculation and separate API future-date validation.

### Two reference classes and field promotion

A **golden mechanical behavior reference** is a preserved dated official visible output for
specified synthetic input and discrete fields. Its exact unknown software version is disclosed.
An **independent astronomical reference** requires appropriate independent astronomical provenance;
the official calculator does not qualify for that class. PyHD-fed mappers and Swiss/swetest
agreement also do not constitute independent end-to-end astronomy.

| Field | Evidence / acceptance | Independence | Risk / exclusion |
| --- | --- | --- | --- |
| Personality/Design Gate.Line | accept 364 official observations in 14 snapshots | separate official pipeline, internals unknown | unobserved sub-minute behavior; mapping/astronomy mismatch must fail regression |
| Type | accept 14 displayed labels with explicit normalization | official pipeline vs research graph probe | no claim of every topology sampled |
| Authority | accept 14 displayed labels, preserving ego variants | official pipeline vs hierarchy probe | no official splenic chart in this subset |
| Definition | accept 14 displayed kinds, covering 0–4 | official output; graph corroboration shares structural table | component membership itself was derived, not exported; not promoted as official |
| Profile | accept 14 displayed pairs | official output and Sun-line corroboration | 11/12 official pairs, not 12 |
| Node behavior | accept 56 N/S Gate.Line observations as part of activations | official output vs controlled Swiss True/Mean comparison | not an official algorithm declaration; N/S and nearby charts correlated |
| Longitude | NOT accepted | official output absent | local/PyHD values are not official astronomy |
| Exact Design timestamp | NOT accepted | official output absent | local solver timestamp is not an official timestamp |
| Official version/ephemeris/algorithm | NOT accepted | unknown | remain null / UNVERIFIED |

`human_design_references.json` schema 2 contains 14 `accepted_behavioral_reference` rows,
each linked to original artifact path/SHA256/retrieval instant, with only the allowed discrete
fields. No promotion is sourced from PyHD or the derived graph comparison.
Original raw `candidate_not_approved` labels reflect collection-time state and remain untouched;
promotion is a separate field-scoped decision. The old 12 engine candidates stay unapproved.

This explicitly revises the earlier all-purpose exact-version requirement. It is not a claim
that new empirical evidence appeared in 9A.2, or that unknown internals became verified.
Snapshot correctness is independently checked against the stored visible source, and malformed
promoted values are rejected by the audit. The audit remains read-only; only its acceptance-schema
validation changed to support the authorized decision.

### Coverage sufficient for implementation

| Dimension | Official behavioral set | Additional coverage / limitation |
| --- | --- | --- |
| Type | all 5 | direct/indirect MG, disconnected and separate motor probes |
| Authority | 7 of 8 | Splenic absent officially; original provisional charts plus structural Projector [18,58] and Manifestor [18,58,16,48] probes |
| Definition | none, single, split, triple, quadruple | focused graph probes; components distinct from channel count |
| Profile | 11 of 12; missing 3/5 | all 12 in combined official+candidate pool; all 12 pairs explicitly tested structurally |

The 18 hand-specified graph probes cover all eight authorities, direct/indirect Ego paths,
emotional-over-sacral/spleen priority, sacral-over-spleen priority, direct/indirect Sacral paths,
a disconnected motor, a separate Ego-to-Throat motor with defined Sacral, and 0–4 components.
These are PROJECT contract vectors, not invented external charts. The existing research graph
probe is used to check their consistency, not as a production oracle.
All 384 line starts (thus all 64 gate starts), exact equality and adjacent representable binary64
values are checked with test-only exact rational arithmetic. Normalization and anchor vectors
are separate fixed expectations. These are project tie-break tests, not official precision proof.

The original 19 differences remain explained by +2.5 arcminutes (17 line-only, two gate+line).
Sacral-excluding Type and channel-count Definition fields are rejected where they conflict with
the frozen semantics; additional Projector subtype strings are explicit aliases, not hidden
mechanical agreement. No unexplained material semantic choice remains.

**True blockers: none for starting 9B.** Non-blocking limitations: proprietary version/settings,
official equality observation, independent HD-specific astronomy, official splenic and 3/5
snapshots, untested exhaustive graph combinations and full-date-range accuracy.
Implementation correctness is NOT established by this decision. Failure of any mandatory 9B
regression blocks delivery and must be diagnosed; never overwrite goldens or snap longitudes
to conceal it. Later contrary evidence requires a versioned decision and reviewed migration.

### Mandatory Stage 9B verification matrix

| Area | Required implementation tests |
| --- | --- |
| Wheel | 302°, full 64-gate order, six lines each, all 384 exact/nextafter boundaries, 0/360 and negative normalization, nonfinite rejection, no epsilon |
| Bodies/nodes | exactly 13 per side; True Node discriminating cases; Earth=Sun+180 and South=North+180; circular normalization |
| Design | previous exact 88° arc; both convergence limits, unrounded midpoint, no 88-day shortcut, bracket failure/stagnation/errors, UTC/UT1 conversion |
| Structure | all 36 channel pairs and 9 centers; hanging gates, cross-side endpoints, duplicates, components vs channel counts, 0–4 kinds |
| Classification | all 5 Types, all 8 Authorities and priority/path probes; all 12 Profiles; invalid pairs/classification error |
| Behavioral regression | every accepted discrete field of all 14 charts; exact labels, no Gate/Line tolerance; failed comparisons diagnosed before release |
| Runtime | pinned flags, initialization/shared native lock, concurrent HD+astrology isolation, repeat determinism, no untracked ephemeris files |
| API/privacy | UTC-only exact time, extras/malformed/nonfinite/out-of-range rejection, future-date injectable clock, support endpoints, no person name/location/logging/storage |
| Regression boundary | unchanged astrology/numerology outputs; no network in tests; provenance/hash mutation rejection |

Passing 9A tests verifies evidence, specification arithmetic and structural consistency, not a
production implementation. The mandatory matrix is a Stage 9B delivery gate, not completed work.
