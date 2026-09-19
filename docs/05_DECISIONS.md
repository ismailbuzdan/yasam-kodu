---
tags:
  - memory/decision
---

# Decisions

## ADR-001 — Calculation and interpretation are separate

**Status:** Accepted
**Context:** Symbolic calculations and explanatory prose have different reliability requirements.
**Decision:** Deterministic engines calculate; AI only interprets verified output.
**Reason:** Prevents invented calculation values.
**Consequences:** A verified unified JSON contract precedes any AI layer.

## ADR-002 — Geocoding is backend-only

**Status:** Accepted
**Context:** Provider policy, User-Agent and errors must be controlled.
**Decision:** Frontend does not call the provider; FastAPI service does.
**Reason:** Keeps provider control and normalization server-side.
**Consequences:** Provider changes remain isolated in the backend service.

## ADR-003 — IANA timezone plus zoneinfo plus tzdata

**Status:** Accepted
**Context:** Birth-time conversion must use historical rules on Windows too.
**Decision:** Resolve an IANA zone from coordinates, then read pinned tzdata through zoneinfo.
**Reason:** Current UTC offset is not a valid historical substitute.
**Consequences:** DST ambiguity and nonexistent local time are explicit domain outcomes.

## ADR-004 — Unknown birth time is not invented

**Status:** Accepted
**Context:** A missing time cannot safely become noon or another default.
**Decision:** Keep it unknown; exact timezone conversion requires an exact time.
**Reason:** Avoids fabricated UTC and later chart data.
**Consequences:** Approximate and unknown processing need their own future paths.

## ADR-005 — Frontend secrets are forbidden

**Status:** Accepted
**Context:** Browser environment variables are public to users.
**Decision:** Provider keys remain backend-only if introduced.
**Reason:** Prevents client-side credential exposure.
**Consequences:** `.env.example` may document non-secret values only.

## ADR-006 — Astrology consumes timezone-layer UTC

**Status:** Accepted
**Context:** Timezone logic must have one owner.
**Decision:** Future astrology service uses UTC produced by the timezone layer.
**Reason:** Avoids duplicate, inconsistent historical conversion.
**Consequences:** Stage 6 does not redo timezone lookup.

## ADR-007 — Open Source Licensing

**Status:** Accepted
**Context:** The project needs a clear open-source license before the planned Swiss Ephemeris integration.
**Decision:** Yaşam Kodu AGPL-3.0 altında açık kaynak olarak geliştirilecektir.
**Reason:** Swiss Ephemeris'in AGPL lisans yolu kullanılacaktır. Projenin kaynak kodunun açık olması
ürün stratejisi açısından kabul edilmiştir. Yaşam Kodu ücretli hosted service, premium analysis,
AI interpretation, PDF ve diğer ticari hizmetleri sunabilir; lisans yükümlülükleri korunacaktır.
**Consequences:** Stage 6 Swiss Ephemeris entegrasyonu AGPL yolu üzerinden geliştirilecek;
Professional License kullanılmayacak. Swiss Ephemeris copyright/license notice korunacak ve gerekli
attribution ile notice'lar Stage 6 sırasında doğrulanacaktır. Yeni dependency'lerin AGPL-3.0
uyumluluğu kontrol edilmelidir.

## ADR-008 — Canonical Stage 6 astrology conventions

**Status:** Accepted
**Context:** Stage 6 requires explicit deterministic conventions; the user has selected the canonical defaults.
**Decision:** Tropical zodiac, Placidus houses, True North Node, South Node derived by adding 180 degrees,
and Mean Black Moon Lilith (`MEAN_APOG`). Stage 6 placement used ecliptic longitude cusp intervals;
the placement part is superseded by ADR-010 after Stage 7 verification.
**Reason:** A single documented convention avoids ambiguous or silently changing chart results.
**Consequences:** No house-system fallback. Retrograde follows longitude speed. Orb limits are 8 degrees
for Sun/Moon pairs, 6 otherwise, with 4 for all sextiles. Applying remains null. See [[astrology]].

## ADR-009 — Explicit Moshier backend and independent verification boundary

**Status:** Accepted
**Context:** Stage 6 must run deterministically without untracked external ephemeris files.
**Decision:** Pin pyswisseph 2.10.3.2 / Swiss Ephemeris 2.10.03, explicitly select Moshier with speed,
and reject unexpected returned flags. Include mean apogee Lilith; omit Chiron without asteroid data.
**Reason:** Explicit calculation mode avoids silent fallback and environment-dependent body availability.
**Consequences:** Moshier precision/date limits apply. No claim of Stage 7 accuracy verification;
reference fixtures remain untouched. Python 3.11 wheels support Windows without a C++ compiler.

## ADR-010 — Native Placidus house placement and explicit initialization

**Status:** Accepted
**Context:** Stage 7 comparison found seven different placements across six cases when latitude
was discarded. The official native API uses longitude and latitude; public swetest confirms the changes.
**Decision:** Use `house_pos` with ecliptic longitude/latitude, ARMC and true obliquity. Keep latitude
internal, change placement metadata, floor fractional house position, and preserve exact zero-latitude
cusp ownership. Initialize each worker under the lock with an empty private path and automatic
time-model defaults; reject nonempty SE_EPHE_PATH. Moshier and other canonical choices stay unchanged.
**Reason:** Use the documented 3D Placidus placement and remove implicit native initialization state.
**Consequences:** House integers can differ from Stage 6 (including 12↔1). No house fallback.
Boundary and thread-repeatability tests added. Full audit: [[astrology-verification]].

## ADR-011 — External evidence provenance and validation error ownership

**Status:** Accepted
**Context:** Stage 7 needs both independent astronomy and correct integration evidence; Stage 6
also mislabeled extra request fields as invalid UTC.
**Decision:** Store JPL DE441 and external Astrodienst swetest artifacts with hashes and field provenance.
Label swetest as shared-algorithm evidence. Preserve the null template; never use null in assertions.
Use `invalid_request` for extra fields/malformed bodies in the existing error envelope.
**Reason:** Prevent circular validation and misleading reference/error claims.
**Consequences:** Offline reference tests; explicit nine-case accuracy scope. Aspects continue to include
nodes and Lilith as already documented; this policy was not changed in Stage 7.

## ADR-012 — Docker Compose development environment

**Status:** Accepted
**Context:** The project is used across development computers, while Windows Python/pyswisseph builds
can vary by interpreter and compiler availability.
**Decision:** Docker Compose is the primary reproducible local workflow: a Python 3.11 backend
container and Node 22 frontend container. Bind mounts provide reload; Linux frontend dependencies
and build output use named volumes. The existing non-Docker workflow remains supported as fallback.
**Reason:** Reproducibility and dependency isolation without requiring host Python or Node.
**Consequences:** This is development infrastructure, not a production deployment architecture.
Browser-facing API URL remains `http://localhost:8000`; CORS policy is unchanged.

## ADR-013 — Synthetic Personal-Data Fixtures

**Status:** Accepted
**Context:** Removing names does not anonymize a real person's birth date/time/location combination.
**Decision:** Tracked regression fixtures may contain only synthetic personal data.
**Reason:** Preserve privacy while retaining reproducible historical-timezone and astronomy coverage.
**Consequences:** Choose dates/times for coverage and coarse generic locations; omit districts unless
needed for fictional provider mocks. Refresh external JPL/swetest evidence with provenance rather
than copying engine outputs. Public baselines must include only the synthetic tracked tree and no
prior private Git history.

## ADR-014 — Deterministic Pythagorean Numerology Convention

**Status:** Accepted
**Context:** Symbolic numerology has multiple conventions; Stage 8 needs reproducible explicit rules.
**Decision:** Use the A–Z Pythagorean table in [[numerology]], Turkish letter normalization and AEIOU
vowels; Y is consonant. Life Path sums every date digit without component reduction. Birthday starts
from day-of-month. Expression sums all letters; Soul Urge vowels; Personality consonants (empty
partitions are null). Maturity sums reduced Life Path and Expression values. Core reduction preserves
11/22/33 at every step. Personal Year sums month/day/explicit target-year digits and reduces to 1–9
without masters. Null target year means null personal year; no implicit current year.
**Reason:** Keep results deterministic and auditable without inference, AI or interpretation.
**Consequences:** Pure service has no clock/I/O; shared future-birth-date rule is applied at API admission
with an injectable clock. Unsupported alphabets are rejected. Names never appear in responses/logs
or persistence. Only synthetic golden vectors; no dependency additions or Stage 9 work.

## ADR-015 — Human Design Mechanical Calculation Convention

**Status:** Accepted (Stage 9A.2, 2026-09-19; revision `stage9a2-v1`)
**Context:** Stage 9 requires deterministic conventions for the 88-degree Design moment, Rave wheel,
lunar node, graph classification, Type, Authority, Profile and Definition before implementation.
**Decision:** Use the exact previous 88.0-degree solar arc; equal 5.625-degree gates and
0.9375-degree lines anchored with Gate 41 at 302 degrees and `[start,end)` ownership;
derive channels/centers and connected components from the documented 36-channel graph; use continuous
defined-channel reachability for motor-to-Throat Type classification. Profile is Personality Sun line
then Design Sun line. Freeze True Node, the eight-branch Authority hierarchy, 13 bodies, opposition
rules, tables, identifiers, solver limits and 1800–2100 birth-year support as specified in [[human-design]].
**Evidence classes:** Publicly specified system rules: 88-degree arc, continuous Definition/Type
mechanics and Sun-line Profile. Official behavioral inference: 302-degree wheel and True Node,
supported by 364/364 discrete activation matches and 46 discriminating N/S observations.
Project engineering/tie-break decisions: exact `[start,end)` ownership, rational binary64 mapping,
no epsilon, pinned Swiss/Moshier/time handling, solver tolerance, support range and serialization.
None of the latter is claimed to be a published official precision algorithm.
**Acceptance policy:** The 14 hashed timestamped official chart captures are golden mechanical
behavior references only for observed Gate/Line, Type, Authority, Definition and Profile. Node
behavior is included in Gate/Line; official internal algorithm, longitude and Design timestamp are
not promoted. Unknown official version/settings prevent independent astronomical qualification,
not discrete behavioral snapshot acceptance. This intentionally supersedes the earlier single-tier
policy requiring a published exact version for every kind of reference.
**Reason:** Material discrepancies are explained (fixed wheel offset, omitted Sacral motor,
channel-count field and label aliases). Eighteen structural probes and all 384 boundary neighborhoods
make remaining project choices explicit. Missing official splenic/3/5 snapshots are non-blocking:
structural coverage exists; exhaustive combinations and proprietary internals are not necessary
to implement deterministic semantics. No rule is selected by implementation majority vote.
**Consequences:** Stage 9A complete; Stage 9B ready but not started or authorized in this task.
Raw evidence remains byte-preserved with historical candidate labels. Future implementation must
pass behavioral and project-contract regressions; discrepancies require investigation and an explicit
decision, not regenerated goldens. See [[human-design-verification]] and [[07_TEST_STRATEGY]].
