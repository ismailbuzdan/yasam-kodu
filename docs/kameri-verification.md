---
tags:
  - memory/kameri
  - quality/verification
---

# Kamerî Kod — K1A qualification

2026-09-20. Conventions: [[kameri-code]], ADR-017 unchanged. Start commit
`d4e62c0f4ed0cfeefd1227d81b6b5f14abe32354`; branch `stage-k1a-kameri-core`.
K0 complete; K1A deterministic core complete. K1B API NOT STARTED. Stage 11 NOT STARTED.

## Preserved WIP and implementation boundary

Resume found ten untracked files: seven under `backend/app/services/traditional/`
(`__init__`, `_astronomy`, `models`, `hijri`, `abjad`, `lunar`, `planetary_hours`) and
three suites (`test_traditional_hijri`, `test_traditional_abjad`, `test_traditional_lunar`).
No reset, restore, stash, deletion or reconstruction of that WIP. Initial Hijri/abjad rerun:
156 passed. Added missing hour/concurrency/reference tests, qualified adapters, expanded error
coverage, fixed the repeated-event search bug and completed this documentation.

Core uses frozen nested dataclasses/tuples and exact rational boundaries; no mutable engine
outputs are embedded. Input script is only a local function argument. Confirmation is per exact
text/policy and must be renewed by callers on changes. It is not a historical-spelling certification.
No API/Pydantic response, router, frontend, clock, network, geocoding, persistence or interpretation.
No new dependency or third-party source code. Existing Astrology, Numerology, HD and Life Code
code, contracts, goldens and all HD artifacts remain unchanged.

Native ownership remains Astrology's existing RLock and initializer, shared with HD. TT feeds
`calc` and `pheno`; UT1 feeds rise/set and exact interval membership. Existing engines inline
UTC-to-JD conversion, so a small Kamerî-only wrapper uses the same native call, with no shared
refactor. `load_zone` supplies pinned tzdata without coordinate lookup. R0's local date, not t's
date, owns the weekday. The civil-date projection floors subsecond values so a pre-midnight value
cannot round into tomorrow; this projection never feeds interval membership. ZoneInfo transitions
and offsets are whole-second. No microsecond display serialization is provided in K1A.

Domain codes distinguish invalid calendar/UTC/coordinates/zone, unsupported range, invalid or
unsupported abjad, native ephemeris failure, invalid astronomical result and unavailable events.
Native diagnostics are suppressed, not echoed. Programming errors are not broadly swallowed.

## External evidence and acceptance limits

Ten evidence artifacts plus ten provenance receipts are in
`backend/tests/fixtures/kameri_sources/`. Receipt SHA256 covers the captured artifact bytes.
HTTP body hashes additionally exist for network captures; extracted swetest PRE output retains
numeric text. The calendar file is explicitly a manually transcribed short excerpt, not a saved
whole PDF/HTTP response. Git attributes preserve evidence bytes across Windows checkouts.
Raw output is not rewritten to fit tests. Tests parse external numbers directly and verify hashes.

| Source | Artifact/count | Qualified field and tolerance | Limitation |
| --- | --- | --- | --- |
| K1-JPL: [Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html), DE441, API version in raw JSON | Sun/Moon JSON, 2 artifacts, 4 synthetic instants (2000-01-01/08/15/22 12:00 UTC) | Apparent geocentric longitude: 0.001°; Moon disk fraction: 0.0001 after percent conversion | Independent numerical comparison, not bitwise equality; IAU76/80 ecliptic-of-date and model differences. No full 1800–2100 accuracy claim |
| K1-SWETEST: [Astrodienst](https://www.astro.com/cgi/swetest.cgi), separately reported 2.10.03 | 3 rise/set captures, 1 separate version capture | R0/S0/R1 UT1, 0.2 seconds for output printed to 0.1 second | SHARED Swiss/Moshier integration, not independent astronomy. Rise output has no version header; exact deployed build identity UNVERIFIED |
| K1-USNO: [API](https://aa.usno.navy.mil/data/api), returned 4.0.1 | 3 daily JSON captures | Sunrise/sunset UT1, 120 seconds as a coarse cross-model check | INDEPENDENT APPROXIMATE; [fixed 50-arcminute center depression](https://aa.usno.navy.mil/faq/RST_defs), minute output, no selectable 1013.25 hPa/15°C. Not exact atmospheric field matching |
| CAL-02: [Richards 2012 §15.6.3, p.607](https://aa.usno.navy.mil/downloads/c15_usb_online.pdf); K1-CAL: [Dershowitz/Reingold 1990 p.901](https://reingold.co/cc-paper.pdf) | 1 short excerpt artifact, 2 published correspondences | AH1/1/1 ↔ JDN1948440; Gregorian1945-11-12 ↔ AH1364/12/6, exact integers | Epoch is a private-helper test outside public range. One in-range published date pair is narrow coverage; whole-range properties are not independent references |

Solar captures use three synthetic calendar dates (2000-01-01, 2000-06-15, 2020-12-15), coarse
40°N/30°E and no personal identity. swetest's explicit command selects Sun/Moshier, upper limb,
refraction, height0, pressure1013.25 and temperature15. Its rise_trans parameter routing was
checked in upstream v2.10.03 swetest source; no source code was incorporated. USNO uses tz0/DSTfalse
solely to request UT1 event labels, not to resolve a person's timezone.
Horizons query records target301/10, center500@399, quantities10/31, airless and UT calendar labels;
these post-1962 labels are UTC. Quantity23 (unsigned angular separation) is not treated as directed
longitude elongation. No external producer qualifies project phase-bin or sector tie-break policy.

Tolerances are field-specific acceptance limits, not measured accuracy promises. Evidence tests
all pass without relaxing those limits. `tools/collect_kameri_references.py` is an explicit network
collector, does not import production or Swiss, and refuses to overwrite existing captures.

Abjad expectations are independently encoded factual K0 table values and hand-derived synthetic
glyph sums, not external calculator goldens. Sources ABJ-01/02 and TXT-01 remain in the K0
bibliography. No copyrighted table graphic, paper or interpretive prose is redistributed.
Mansion correctness is the exact project partition of a represented float, not historical
calculator majority agreement. Arabic labels, stellar reconstruction and all interpretations remain
UNVERIFIED/UNQUALIFIED as recorded in K0; they are not necessary for this limited core delivery.

## Executed Docker gates

| Suite | Passed |
| --- | ---: |
| Hicri | 41 |
| Abjad | 116 |
| Lunar/phase/mansion | 77 |
| Planetary hours | 217 |
| Mixed native concurrency | 1 |
| External references/integrity | 12 |
| New K1A total | 464 |
| Existing Astrology/HD/Life Code regression | 756 |
| Full backend (924 baseline + 464) | 1388 |

Targeted suites were run separately. Full suite emits only the two pre-existing Starlette/httpx
and anyio deprecations. `python -m pip check`: No broken requirements found.
Read-only HD audit: 68/68 unchanged evidence artifacts. Shared helpers were not changed;
Astrology's stage7 audit tests are included in the regression/full suite. Frontend unchanged;
lint/typecheck/test/build not rerun for this backend-only stage.

Tests traverse all 109,938 supported calendar dates, all cycle/month edges, eight phase boundaries,
all 28 rational sector boundaries and adjacent floats, all24 hours × seven weekdays, exact R0/S0/R1
ownership, nonrepresentable subdivision points, polar absence, historical/DST date ownership,
typed failures, fixed observing flags, all eight ligatures, all other Arabic presentation codepoints,
confirmation, privacy, sequential repeats and interleaved native calls on eight worker threads.

No outstanding blocker for K1A's scoped core. K1B is ready for separately authorized API design,
not implemented and not covered by this qualification. No main merge or Stage11 work.
