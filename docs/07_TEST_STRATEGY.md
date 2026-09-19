---
tags:
  - memory/quality
---

# Test Strategy

## Backend

592 tests (584 Stage 8 baseline plus 8 Stage 9A research-integrity tests) cover health, birth-profile validation, location resolution, historical timezone behavior,
fixture-integrity boundaries and Stages 6–7 astrology. Original tests remain; the old empty-reference
guard now checks provenance. Astrology includes invariants, error boundaries, threaded repeatability,
real Swiss smoke tests and offline external-reference regression; see [[astrology-verification]].
Run `pytest` and `pip check` for backend changes.

Stage 9A has research-only Human Design integrity tests. They verify synthetic UTC identity,
artifact hashes, candidate/non-golden status, 64-gate/9-center and 36-channel structural agreement,
and preservation of known mapper disagreements. They do not assert candidate chart output as correct.
Stage 9A.1 additionally checks 14 official visible-DOM captures, UTC confirmation, numeric completeness,
North/South oppositions, recorded comparison counts, rare-category observations and reproducible
offline graph probes. These are evidence-consistency tests, NOT production accuracy/golden tests.
The audit is read-only and must reject hash/inventory mismatch instead of rewriting references.
Network candidate search is explicit, pinned, hash-checked and outside the offline test suite.
See [[human-design-verification]].

Stage 8 tests in `tests/test_numerology.py` use hand-calculated synthetic golden vectors, normalization
and reducer boundaries, API validation/privacy, expression partition invariants and exact repeatability.
The API validation clock is overridden explicitly; no current-year default is permitted. See [[numerology]].

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
independent end-to-end references. Promote a field only with raw hashed provenance, exact tool/version,
classified independence, resolved convention semantics and no disagreement affecting that field.
