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

## ADR-016 — Unified Life Code Aggregation Contract

**Status:** Accepted (Stage 10A, 2026-09-19)
**Context:** The three verified calculation systems require one typed internal result without
duplicating calculations, mixing local calendar dates with UTC or retaining names in output.
**Decision:** Sequentially call the existing AstrologyService, NumerologyService and HD core once
per successful request. Retain their original typed outputs without field loss, renaming or
recalculation. Numerology owns supplied calendar birth date, name and explicit nullable target year;
Astrology/HD consume the same resolved UTC; only Astrology consumes coordinates (Placidus).
Geocoding/timezone resolution remains upstream. No name in output, logs or error text; no clock,
network, interpretation or persistence in aggregation. Metadata describes only `life-code-v1`
aggregation, not duplicate engine conventions. Validation reuses existing typed request models;
private input-validation errors and original engine domain error types/codes remain distinguishable.
**Immutability:** The user explicitly selected a frozen outer result retaining original typed engine
objects. Astrology/Numerology child objects remain mutable and must be treated as read-only.
No claim of deep immutability; no existing engine/model mutation to enforce it.
**Reason:** Preserve one source of truth per engine, deterministic field ownership and a narrow
Stage 10 boundary. A local midnight may map to a different UTC date without changing Numerology's date.
**Consequences:** Stage 10A is internal orchestration only; API/admission mapping belongs to Stage 10B.
No partial-success result, generic exception swallowing, fallback or implicit target year.
Tests cover lossless identity/equality, data routing/privacy and shared native-state repeatability.
ADR-001 and engine conventions remain unchanged. Details: [[life-code]].

## ADR-017 — Kamerî Kod Methodology and Provenance Boundary

**Status:** Accepted (Stage K0, 2026-09-20; scoped project conventions `kameri-k0-v1`).
**Context:** A future Kamerî Kod module must distinguish computed astronomy/calendar values,
symbolic arithmetic and source-specific historical interpretation before production work begins.
**Decision:** Keep Kamerî Kod separate from the unchanged Stage 10 Life Code v1 contract.
Freeze only the five mechanical methods specified in [[kameri-code]]: Friday-epoch tabular Hijri
date with explicit local civil-date semantics; Swiss/Moshier apparent geocentric Moon and illuminated
fraction with separately identified project phase bins; 28 equal tropical sectors at 0° with rational
half-open boundaries; Eastern additive abjad with explicit Unicode/letter policy and user-confirmed
Arabic input; and sunrise-owned seasonal planetary hours with fixed observing assumptions and no
polar substitution. These are project choices, not universal historical or religious rules.
**Provenance:** Source IDs, claim locators, method/version, classification and limitations are mandatory.
Historical traditions and modern popular claims must be separately labeled; every interpretation
requires its own qualified source. Unsupported traditions/characters are not silently normalized.
No religious-authority, unseen-knowledge, destiny, scientific-personality or personal divine-name
claim; no devotional count recommendation. Calculation and interpretation remain separate.
AI never calculates, selects a mansion/Asma, sums letters or invents missing historical meaning.
ADR-013 synthetic-only tracked personal fixtures applies; mother's name is not collected.
**Name boundary:** Choose user-confirmed Arabic-script input for ebced. Later automatic suggestions
must be transparent and versioned; `tr_ar_v1` is only a proposal until its dictionary and complete
transcription policy are qualified. Confirmation does not certify historical or religious truth.
**Scope of acceptance:** Mansion numeric-sector calculation is frozen; proposed Arabic/name labels
are not edition-collated and are not accepted for production. Stellar reconstruction, lunar-age solver,
automatic name rendering, huruf/Asma/zodiac–Asma/dhikr/yildizname/mother-name methods remain excluded
at their explicit research/deferred/unqualified statuses. Unresolved conventions must be qualified
and frozen before their own implementation; this ADR does not promote them by implication.
**Reason:** Reproducible modest calculations can be specified without asserting one canonical tradition
or importing unverifiable formulas. [[kameri-source-qualification]] records 19 bounded source records.
**Consequences:** K0 methodology complete; K1 methodologically ready only for the five scoped methods
(numeric mansion index and confirmed-script ebced), and separately requires authorization, reference
qualification and runtime tests. No production implementation, endpoint, frontend, database, AI,
PDF, dependency or existing engine/API change is part of K0. Stage 11 remains not started.

## ADR-018 — Kamerî Kod Public API Boundary

**Status:** Accepted (Stage K1B, 2026-09-21)
**Context:** K1A implements the five ADR-017 mechanical methods, but public admission and serialization
must not expose private Arabic text or internal astronomical diagnostics.
**Decision:** Expose `POST /api/v1/kameri/calculate` with required resolved local date, UTC instant,
coordinates, IANA timezone, Arabic text and literal-true confirmation. Field ownership follows K1A;
local and UTC calendar dates need not match. Invoke Hijri, lunar, abjad and planetary-hour entry points
once in sequence and return no partial success. The response is an explicit `kameri-code-v1` allowlist,
has `interpretation_present=false`, never echoes Arabic, and excludes raw solar events/JDs, Fraction
boundaries, flags and search diagnostics. Validation and TraditionalError codes map to static private
422/503 envelopes; supplied invalid/unresolved timezone is a 422 admission failure. Programming errors
are not swallowed.
**Reason:** Preserve deterministic calculation ownership and privacy while providing a narrow stable
transport independent of interpretation.
**Consequences:** K1B and the scoped Kamerî mechanical API are complete without changing ADR-017
calculations or Life Code v1. Automatic rendering, historical mansion
labels, Hurûf/Esmâ/zodiac–Esmâ/dhikr/yıldıznâme, frontend, persistence and AI remain outside this API.
Stage 11 remains not started.

## ADR-019 — Traditional Interpretation Knowledge Boundary

**Status:** Accepted (Stage K2A, 2026-09-21; knowledge-policy boundary only).
**Context:** Completed Kamerî mechanical calculations do not authenticate historical symbolic
interpretations. [[kameri-interpretation-qualification]] distinguishes four bounded qualified
arithmetic/cultural facts from incomplete, disputed or unsupported mappings.
**Decision:** Future interpretation requires individually qualified, versioned claim records with
exact source locators, explicit method/tradition, original context, applicability, limitations,
religious boundary, rights review and AI usage policy. No source-free additions or unverified
mappings in production KB; research records and free source prose are not runtime inputs.
Multiple traditions remain separate; copying or majority agreement does not establish authority.
Historical attribution is neither religious truth nor scientific validation. AI only narrates
applicable qualified fragments with citations and abstains on gaps; it never calculates or fills
tables. Keep attributed tradition separate from modern explanatory wording, which cannot create
new correspondences. Use associated_asma only for a separately sourced association; personal/true/
your Asma claims, devotional prescriptions and deterministic future claims are excluded.
Mother's name remains uncollected absent a complete qualified method, separate approval and privacy
review. No K1 numeric-sector-to-historical-mansion bridge is approved; a future bridge requires
explicit PROJECT INTERPRETATION BRIDGE labeling and a separate evidence-backed decision.
Retain short independent factual normalization and citations, not bulk copyrighted prose/scans;
edition rights are separate from underlying historical work rights. No blanket reuse license inferred.
**Consequences:** K2A complete as a bounded source decision. K2B source-ready only for four limited
fragments, not full-feature mappings; no production KB built. Stage 11 knowledge readiness YES,
LIMITED to descriptive narration, not personalized Kamerî interpretation. K2B/Stage 11 NOT STARTED.
ADR-017/018, mechanical conventions, public API and Life Code v1 are unchanged.

## ADR-020 — Kamerî Qualified Knowledge Base v1

**Status:** Accepted (Stage K2B, 2026-09-21).
**Context:** K2A qualified four bounded facts, not personal correspondences or complete historical
tables. Production admission and contextual selection must enforce these limits independently of AI.
**Decision:** `schema_version=kameri-kb-v1`; production contains exactly the qualified K2A set
ASMA_NUM_001, HIJRI_CTX_001/002/003 with only KI-A03/B05/B07/B08 source records. All research-only,
unqualified and deferred records are excluded. Runtime loads separate immutable/versioned data,
never the research ledger or network. Mandatory source locators, original context, limitations,
religious boundary and `ai_usage=restricted` remain attached to every claim. Short independent facts
and citation metadata only; no source prose, translations, scans or tables.

Only typed Hijri month cultural context is automatically applicable: month 9 selects HIJRI_CTX_001
and HIJRI_CTX_002, month 12 selects HIJRI_CTX_003, all other months explicitly abstain with no fallback.
ASMA_NUM_001 is `reference_only`; explicit non-personal lookup is allowed, but abjad 66 creates no
associated/personal Asma and the automatic selection model excludes reference-only records.
No mansion bridge, planetary-hour interpretation, Hurûf, zodiac–Asma, dhikr prescription, yıldıznâme,
mother-name collection, calculation calls, API change or AI implementation is admitted.
**Reason:** Fail-closed, source-aware limited context is reproducible without inventing missing
knowledge or implying that arithmetic establishes personal or religious associations.
**Consequences:** K2B LIMITED PRODUCTION KB COMPLETE; K2A and mechanical API COMPLETE. Stage 11
readiness YES, LIMITED to the three cultural fragments, not a deep personalized reading; Stage 11
NOT STARTED. ADR-017/018/019 remain unchanged. Tests freeze ledger admission, all-month selection,
the abjad-66 firewall, provenance, immutability, parallel/offline use and calculation independence.
Details: [[kameri-knowledge-base]].
