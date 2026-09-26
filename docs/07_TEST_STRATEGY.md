---
tags:
  - memory/quality
---

# Test Strategy

## Stage 11B Gemini adapter/runtime

`test_gemini_interpretation.py`: **77 offline tests** using synthetic symbolic cases, an injected
SDK client and the real pinned google-genai SDK over httpx.MockTransport. No live credentials/network
are needed. Request shape/model/native JSON, empty/unsupported configuration, all depth sections,
canonical Kamerî IDs, missing-system references/timeline, privacy/injection admission, static errors,
refusal, invalid JSON/schema, one repair, shared retry budget, Retry-After/deadline/cancellation and
client cleanup are covered. The unchanged 11A suite now exercises 70 cases because its error taxonomy
parameterization includes two new static codes. Combined targeted result: **147 passed**.

Docker 2026-09-26: **full backend 1685 passed / 1 existing Starlette/httpx warning**;
pip check clean; HD read-only evidence audit **68/68**; Kamerî references **12/12** separately rerun.
The prior AnyIO alias warning did not recur in the rebuilt dependency environment. No frontend changes,
so frontend tests were not rerun. No live API smoke was run; model acceptance/quality/prose safety
remain UNVERIFIED. These tests prove structural/failure behavior, not semantic safety of arbitrary prose.
Original evidence/provenance/goldens remain unchanged. See [[08_AI_INTERPRETATION]] for the 11C delivery gate.

## Stage 11A interpretation contracts

`test_interpretation_contracts.py`: 68 new synthetic tests qualify the detached symbolic allowlist,
private-field exclusion, metadata/instruction rejection, frozen snapshots, exact copied values,
repeatability/no engine or network calls, explicit personal-year opt-in/nulls, all depth contracts,
required Premium sections, missing data, unsupported timeline, reference binding, cross-system kinds,
Kamerî canonical claims/citations/abstention, static errors and closed JSON schemas.
No real provider or mock provider; no AI quality claims. Future 11B must test semantic factuality,
unsafe prose, prompt injection, SDK JSON dialects, refusals and bounded retry/deadline behavior.
Docker 2026-09-26: targeted 68; full backend **1606 passed / 2 existing warnings**; pip check clean;
read-only HD audit **68/68**. Use the existing K2B temporary research-ledger setup for full pytest.
Original engine/fixture/API/frontend/dependency files remain unchanged.

## Stage K2B qualified KB

`test_kameri_knowledge_base.py` and `test_kameri_knowledge_selector.py`: **83 tests** enforce exact
four-claim admission, unchanged qualified-ledger metadata/boundaries, source resolution/locators,
restricted AI policy, rights structure, invalid-data rejection and typed explicit lookup errors.
All 12 months have exact contextual coverage or abstention; abjad 66 cannot select the Asma reference.
Tests cover nested immutability, repeatability, concurrent 9/12/1/reference lookup and a fresh process
with network/research access and calculation imports blocked. No expected astronomy is generated.
The ledger comparison fails if its source is absent; Docker's backend-only mount requires a temporary
ledger copy and test-only `KAMERI_RESEARCH_LEDGER` path as documented in [[kameri-knowledge-base]].

Docker results: K2B 83; K1A 464; K1B 67; full backend **1538 passed, 2 existing warnings**;
pip check clean; read-only HD audit **68/68**; Kamerî evidence **12/12**. No frontend changes/tests.
The K2A section below records historical research qualification; its planned K2B gates are now covered.

## Stage K2A research qualification

This stage changes only docs and a non-runtime provenance ledger. Validate JSON syntax, unique
source/claim/method IDs, source resolution, required nonempty locators and exact count summaries.
Check that every qualified claim has a complete bounded proposition, identified tradition/method,
acceptable inspected source, limitations, religious boundary and factual reuse/AI policy. Catalogs,
abstracts and Tier D discoveries must never be mistaken for complete verified mapping rules.
Assert unqualified/research/deferred claims have forbidden AI usage and the mansion bridge and
mother-name flags remain false. Check local document links, docs-only diff, unchanged ADR-017/018
and original provenance, and git diff --check. No runtime tests are required for this docs-only
stage; the prior 1455/two-warning baseline must not be reported as re-run.

Future K2B tests must enforce fail-closed claim selection, citation/version retention, no implicit
personal-name/Asma or sector/mansion bridge, no devotional instructions, no private input leakage,
and abstention where coverage is absent. This was the K2A plan; the K2B suite above now implements it.

## Stage K1B API qualification

The public contract suite compares its allowlist response to direct K1A typed results, proves each
entry point is called once and in order, and covers strict/missing/extra/malformed input, two independent
clocks, cross-date ownership, literal Arabic confirmation, fail-closed character handling and static
422/503 envelopes. It also checks submitted-text/log privacy, forbidden JD/Fraction/native fields,
all-or-nothing failure, `Z`/`+00:00` equivalence, determinism, metamorphic ownership and concurrent
repeatability. K1A's 464-test evidence/reference suite, existing APIs, full backend, pip check and HD
68-artifact audit remain mandatory regressions. Frontend checks apply only if frontend changes.

## Stage K1A qualification

Six offline `test_traditional_*` suites add **464 tests**: Hijri 41, abjad 116, lunar 77,
planetary hours 217, concurrency 1, external references 12. Full Docker suite **1388 passed**
(924 prior baseline + 464), only two existing warnings. Existing Astrology/HD/Life Code
regression separately passes 756 tests. Pip check and the 68-artifact HD audit remain clean.

Calendar tests traverse all 109,938 supported Gregorian dates for inverse and consecutive-day
properties, all 30 leap positions/month ends, epoch and century boundaries. Two published date
correspondences are independent references; round trips alone are not independent accuracy proof.
Phase tests inspect all eight equality/adjacent boundaries; mansion tests compare all 28 exact
rational boundaries to adjacent binary64 values. All 24 hour offsets across seven weekdays,
nonrepresentable subdivision points, R0/S0/R1 ownership, historical/DST/local-date conversion,
polar absence, bounded search and native error/flag tests are included. Native search alternates
event types to avoid re-discovering the same root; it does not shift classification boundaries.
Abjad covers all values/extensions, eight ligatures, NFC equivalence, exact ignore allowlists,
all other presentation-form codepoints, invalid input/confirmation and no result/error/log echo.
Mixed sequential/concurrent Moon/hour/Astrology/HD tests check deterministic state isolation.

New artifacts live only in `kameri_sources/`, with byte-preserving Git attributes and hash/inventory
checks. JPL, shared swetest and approximate USNO scopes/tolerances are separate; see
[[kameri-verification]]. Collector is explicit network tooling, never imported by production.
No expectations are derived from the implementation under test or regenerated to match it.

## Stage K0 documentation qualification

K0 changes only methodology/provenance documents, with bibliography JSON under docs.
Validate JSON structure, unique source IDs, required fields, tier counts, claim references,
local document links, `git diff --check` and a docs-only changed-path allowlist.
No new runtime feature test or backend/frontend rerun is required for this docs-only stage.
The 924/8 runtime baselines below remain prior verified results, not new K0 runs.
Before a future K1 delivery, execute the calendar/Moon/sector/Unicode/hour boundary matrix in
[[kameri-code]], independent-reference checks and shared native-state/privacy regressions.
Methodology READY must never be reported as runtime accuracy verified.

## Backend

924 tests (789 Stage 9 baseline plus 46 Life Code service and 89 Life Code API tests) cover health, birth-profile validation, location resolution, historical timezone behavior,
fixture-integrity boundaries and Stages 6–7 astrology. Original tests remain; the old empty-reference
guard now checks provenance. Astrology includes invariants, error boundaries, threaded repeatability,
real Swiss smoke tests and offline external-reference regression; see [[astrology-verification]].
Run `pytest` and `pip check` for backend changes.

Stage 9A has research-only Human Design integrity/contract tests. They verify synthetic UTC identity,
artifact hashes, field-scoped acceptance vs raw candidate status, 64-gate/9-center and 36-channel structural agreement,
and preservation of known mapper disagreements. They do not assert candidate chart output as correct.
Stage 9A.1 additionally checks 14 official visible-DOM captures, UTC confirmation, numeric completeness,
North/South oppositions, recorded comparison counts, rare-category observations and reproducible
offline graph probes. These are evidence-consistency tests, NOT production accuracy/golden tests.
Stage 9A.2 accepts 14 official behavioral snapshots with source-linked fields, mutation rejection,
384 exact/adjacent binary64 boundary neighborhoods, 18 hand-specified graph vectors (including
splenic/priority/indirect paths) and all 12 Profile pairs. Test-only arithmetic/graph probes are
not a production engine. Raw source artifacts and their historical labels remain unchanged.
The audit is read-only and must reject hash/inventory mismatch instead of rewriting references.
Network candidate search is explicit, pinned, hash-checked and outside the offline test suite.
See [[human-design-verification]].

Stage 8 tests in `tests/test_numerology.py` use hand-calculated synthetic golden vectors, normalization
and reducer boundaries, API validation/privacy, expression partition invariants and exact repeatability.
The API validation clock is overridden explicitly; no current-year default is permitted. See [[numerology]].

## Human Design core

Stage 9B.1A is complete. `test_human_design_core.py` tests production mapping at all 384 exact
and adjacent binary64 boundaries, all 364 official Gate/Line observations, native body/flag/node
rules, opposition/normalization, 1800/2100 range edges, input/domain errors, solver residual AND
bracket limits, failure/iteration/stagnation paths, exact half-even ties and no UTC serialization
feedback. Repeated calculations and mixed HD/Astrology threads verify determinism/state isolation.
No research tool is imported by production or these core tests. Stage 9B.1B is complete:
`test_human_design_classification.py` adds 95 production tests covering all 18 structural vectors,
all 36 channels crossing imprints, 64-gate/9-center integrity, lone/duplicate gates, component counts,
all five Types/Strategies, eight Authorities with priority/path collisions and error handling,
all 12 Profiles (Sun located by body), immutable metadata/result, single astronomy call,
determinism and parallel complete calculations. All 14 official Type/Authority/Definition/Profile
fields and 364 activation observations match. Stage 9B.2 is complete: `test_human_design_api.py`
adds 53 tests for all five Types through seven source-owned official synthetic representatives,
including rare ego/self/environmental/lunar authorities. Exact field-by-field core/API consistency
covers all activations (unrounded longitudes included), metadata, graph and classification fields.
Other tests verify strict UTC/body validation, zero-offset equivalents, 1800/2100 support edges,
injectable same-day future-microsecond admission, private 422/503 domain errors, no submitted-body
logging, explicit response field inventory, fixed ordering, byte-identical repeats and unchanged
disabled docs policy. The full 14-case official matrix stays in the core suite; no golden regeneration.

Stage 9B.2 Docker verification: targeted API 53; astronomy/classification 141 (46 + 95);
integrity 11; full backend 789 with two pre-existing dependency deprecations; `pip check` clean.
Read-only audit verifies all 68 raw artifacts and unchanged original comparison metrics.
No production core or reference files changed. Response examples are transport documentation,
not independently sourced astronomy expectations. Frontend was unchanged and not retested this stage.

## Unified Life Code internal aggregation

Stage 10A `test_life_code_service.py` has 46 synthetic tests for original typed object identity,
field-lossless direct-output equality, once-only sequential calls, shared UTC routing and the
different local calendar date for Numerology. Metamorphic tests vary name, target year and
coordinates independently. Coverage includes immutable outer models with explicitly mutable
Astrology/Numerology children, no shared result reuse, null target year, future input without
service clock, private input/domain failures, fail-fast behavior and suppressed native causes.
Network connections are forbidden during a real calculation; DEBUG-level logs are checked for
absence. Parallel/repeated three-engine calculations and subsequent direct calls verify existing
Swiss native-state isolation. No existing engine, schema, golden or evidence changes.

Docker Stage 10A qualification: 46 targeted; 416 Astrology, 117 Numerology, 205 Human Design;
full 835 passed with two existing warnings. `pip check` clean and read-only HD audit 68/68.
Frontend unchanged; last qualification on the Stage 9 main merge remains lint/typecheck/8 tests/build.
These new assertions qualify orchestration, not independent astronomical accuracy.
Details and the user-selected immutability boundary: [[life-code]].

## Unified Life Code API — Stage 10B complete

Stage 10B adds 89 tests in `test_life_code_api.py` for typed response/core equality, standalone endpoint equality,
shared HD safe projection and diagnostics exclusion, cross-date ownership, name/year/coordinate
metamorphic invariants, strict validation, static domain errors, private 422/503 responses, exact
UTC admission and separate Numerology calendar-clock behavior. Also covers repeated canonical
Z/+00:00 output, null default target year, small parallel requests and visible programming errors.

After user-restored Docker availability, the preserved WIP passed without adapter/test fixes:
89 targeted API tests, 46 Stage 10A service tests and 246 standalone API-containing regressions
(`test_astrology.py`: 76, `test_numerology.py`: 117, `test_human_design_api.py`: 53).
Full backend: 924 passed with only two existing dependency warnings. `pip check` clean;
read-only HD audit verifies 68/68 artifacts and unchanged comparison metrics.
Frontend lint/typecheck/8 tests/production build also pass in Docker. Startup regenerated
`next-env.d.ts` dev paths; the normal production build regenerated production paths, leaving no
frontend diff without restore/reset. No engine/service/model/golden changes.

## Frontend

8 Node tests cover profile validation and API request conversion. For frontend changes run lint,
typecheck, tests and production build.

## Regression fixtures

`backend/tests/fixtures/birth_cases.json` holds synthetic historical timezone cases and fixed UTC
expectations. Regression fixtures must not contain real-person birth data. Omission of names alone
is insufficient. Dates/times are chosen for coverage; locations use coarse generic test points with
null districts. Verify hand-selected UTC expectations using `tools/verify_synthetic_timezones.py`,
which loads pinned IANA data without importing production services.

## External provider mocks

Geocoding tests mock HTTP/provider behavior. Tests must not depend on a live provider.

## Historical timezone regression

Fixtures test dates with distinct historical offsets and DST edge cases. They prevent current
offset from becoming an accidental expectation.

## Astrology regression

Use independent reliable references for expected ephemeris values. Do not use the engine under test
to generate its own expected values.

## Astrology Independent References

`backend/tests/fixtures/astrology_references.json` contains nine Stage 7 records sourced from JPL
DE441 and external Astrodienst swetest. The latter shares Swiss algorithms and must not be labeled
independent astronomy. Raw artifacts, query URLs, timestamps and hashes are preserved in
`astrology_sources/`. Its null template is not an expectation; null values must never be asserted.
`test_astrology_reference_regression.py` checks provenance and numerical comparisons offline.

- The Stage 6 code path must not generate its own expected values.
- Validate at least Sun, Moon, ASC and MC against an independent reference.
- Preserve source name, version/settings and retrieval date with each record.
- Preserve tropical/sidereal, house-system and node-type conventions.
- Read UTC and coordinates from `birth_cases.json`; do not duplicate them in reference records.
- Add an expected value only when its provenance is documented.

## Circular testing prevention

An engine output cannot become its own fixture reference. Document each expected source and preserve
the input, convention and expected result independently.

For Human Design, two mappers consuming the same upstream longitude and Design moment are not two
independent end-to-end references. ADR-015 distinguishes discrete behavioral snapshots from independent
astronomy: official unknown-version output can be accepted with input, retrieval time, raw hash,
explicit unknown internals and field-scoped semantics. It cannot supply unexposed longitude/Design
timestamps or be labeled version-pinned independent astronomy. PyHD output is not promoted by agreement.

## Mandatory Stage 9B delivery gate

Implement every row of the mandatory matrix in [[human-design-verification]]: all 384 exact and
adjacent boundaries, 302-degree anchor/order/widths, normalization, True Node discrimination,
Earth/South oppositions, exact 88-degree solver and errors, all channel/center/component rules,
all Types/Authorities/Definitions/Profiles, and all 14 accepted official behavioral regressions.
Also require shared native-state/concurrency isolation, determinism, flags/time-model initialization,
API validation/date range/future-date clock, privacy and unchanged astrology/numerology regression.
Exact discrete golden mismatch blocks delivery: investigate it rather than rounding, snapping,
relaxing label assertions or regenerating reference values. 9A passing is not 9B implementation success.
