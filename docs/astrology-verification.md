---
tags:
  - memory/astrology
---

# Stage 7 — Astrology engine independent verification

Synthetic references refreshed and verified 2026-09-18. Related: [[astrology]], [[07_TEST_STRATEGY]], [[05_DECISIONS]], [[04_CURRENT_STATE]].
Stage 7 acceptance is limited to the evidence and conventions below; it is not universal accuracy
certification over every date or latitude. Stage 8 has not started.

## Sources and provenance

1. **NASA/JPL Horizons**, API 1.2, **DE441**: independently implemented astronomical reference,
   not a Swiss Ephemeris result. Geocenter `500@399`, observer quantity **31**, AIRLESS, UT/UTC,
   apparent IAU76/80 ecliptic-of-date longitude/latitude. Light-time, gravitational light deflection
   and aberration are included. No J2000, heliocentric, geometric or topocentric values are mixed
   into the comparisons. Targets: Sun 10, Moon 301, Mercury 199, Jupiter system barycenter 5.
   Jupiter's barycenter matches the Swiss default planetary-system position convention.
2. **Astrodienst public swetest**, reported version **2.10.03**, `-emos`, Tropical, `-house...,P`,
   `-hsyP`, explicit `-utcHH:MM:SS`, `-geopos`, `-fPlbsj`. Provides angles, twelve cusps,
   longitude/latitude, speed and fractional house position. This is an **external execution and
   integration reference using the same Swiss algorithm**, NOT an independent implementation.
   It catches parameter/wiring and placement errors but cannot expose a shared Swiss algorithm bug.

All regression birth cases are synthetic and are not sourced
from real users or identifiable persons. All nine cases use UTC and coordinates only from
`backend/tests/fixtures/birth_cases.json`. No names are sent. Collection tools do not import
the application or pyswisseph. Results are fetched first, then parsed from external files.
JPL sorts output dates; parsing joins by UTC rather than assuming input/output row order.
All sample dates are after 1962, when Horizons observer UT labels mean UTC.

`backend/tests/fixtures/astrology_sources/` contains JPL raw JSON and extracted swetest PRE
numerical output (HTML scripts, tracking and page chrome are excluded). Each has a provenance
sidecar: full query URL, retrieval timestamp and SHA-256 of the saved data. Swetest also retains
the original HTTP-body hash and extraction description. `astrology_references.json` retains its
schema version and null template and adds nine records with field-to-source maps and artifacts.
Reference fields were parsed from those artifacts, never from the production motor. Tests verify
hashes and reparse the evidence to check fixture integrity. No network is needed for pytest.
Git attributes preserve evidence bytes (including provider whitespace) across Windows/Linux checkouts.

## Coordinate alignment and tolerance

Both planet paths are geocentric, apparent, tropical/ecliptic-of-date, in degrees at the same UTC.
Horizons uses IAU76/80 and Swiss uses its pinned modern precession/nutation models; these are
different realizations of the same requested coordinate convention. No rotation from J2000 is
needed because quantity 31 already returns of-date ecliptic coordinates. The comparison reports
the combined ephemeris + model discrepancy, not a pure numerical integrator error.

- **JPL longitude acceptance: 0.01 degrees (36 arcseconds).** This is the requested application
  accuracy budget. Moshier's documented planetary/sub-few-arcsecond lunar precision and small
  model differences are below it for these modern dates. JPL prints seven decimal degrees,
  contributing at most 0.00018 arcseconds of rounding. Tolerance was not widened after results.
- **External ASC/MC/cusps: 0.05 degrees (180 arcseconds)** as the requested angle budget;
  actual differences round to at most 0.000180 arcseconds. That close agreement is expected from a shared
  native algorithm and seven-decimal output; it is not independent sky-angle accuracy evidence.
- Additional swetest body longitude and speed checks: **0.00001 degrees / degrees per day**,
  respectively, allowing printed rounding without hiding material integration errors.
- House integers must match exactly. No tolerance can move a body to another house to pass.

## Measured absolute deviations

All values below are **arcseconds**, using circular separation. Reproduce with
`docker compose run --rm backend python tools/report_astrology_verification.py` from the repo root.

| Case ID | Sun (JPL) | Moon (JPL) | Mercury (JPL) | Jupiter (JPL) | ASC (swetest) | MC (swetest) | Max cusp (swetest) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| synthetic_tr_dst_01 | 0.068236 | 0.327240 | 0.061591 | 0.038886 | 0.000008 | 0.000180 | 0.000180 |
| synthetic_tr_dst_02 | 0.001852 | 0.412549 | 0.012309 | 0.020933 | 0.000005 | 0.000002 | 0.000146 |
| synthetic_tr_dst_03 | 0.038532 | 0.587830 | 0.034390 | 0.251861 | 0.000150 | 0.000175 | 0.000175 |
| synthetic_tr_standard_01 | 0.007594 | 0.038545 | 0.023667 | 0.257599 | 0.000120 | 0.000067 | 0.000177 |
| synthetic_tr_standard_02 | 0.036551 | 0.454548 | 0.012963 | 0.096027 | 0.000023 | 0.000012 | 0.000169 |
| synthetic_leap_date_01 | 0.058820 | 1.046542 | 0.062069 | 0.038813 | 0.000100 | 0.000021 | 0.000161 |
| synthetic_tr_permanent_utc3_01 | 0.096211 | 0.289927 | 0.090114 | 0.013829 | 0.000059 | 0.000029 | 0.000179 |
| synthetic_leap_date_02 | 0.029777 | 0.659421 | 0.036267 | 0.206055 | 0.000123 | 0.000114 | 0.000177 |
| synthetic_us_winter_01 | 0.076587 | 0.151767 | 0.055897 | 0.015818 | 0.000090 | 0.000028 | 0.000132 |

Maximum observed JPL longitude discrepancy: Moon, 1.046542 arcseconds (approximately 0.000291 degrees).
Moshier satisfies the 0.01-degree application budget on these representative modern cases.
There is no evidence here requiring a production mode change; Moshier remains explicit.
All twelve cusps and all twelve directly calculated bodies' houses/speeds match external swetest.

## House-position audit and correction

Stage 6 discarded ecliptic latitude and assigned houses by cusp longitude intervals.
Swiss `house_pos(armc, geolat, eps, (longitude, latitude), b'P')` instead uses the body's actual
ecliptic latitude. The official documentation describes 3D house placement; a nonzero-latitude
body need not change houses at the same longitude as an ecliptic cusp.

The original Stage 7 audit motivated the existing correction. Personal-case tables have been
removed. Re-running the diagnostic on the nine synthetic cases finds **four differences across
three cases**, all one adjacent house apart. Diagnostic script:
`docker compose run --rm backend python tools/audit_house_placement.py`.
These are diagnostic comparisons, not generated reference expectations.

| Case | Body | Old interval | Native house_pos | Fractional native position |
| --- | --- | ---: | ---: | ---: |
| synthetic_tr_dst_01 | Pluto | 4 | 5 | 5.1717635 |
| synthetic_tr_standard_01 | Jupiter | 6 | 7 | 7.0026373 |
| synthetic_tr_standard_01 | Pluto | 8 | 9 | 9.0170513 |
| synthetic_tr_permanent_utc3_01 | Venus | 11 | 12 | 12.0077121 |

Production now preserves latitude internally, obtains true obliquity from `ECL_NUT` at TT and ARMC
from `houses_ex` at UT1, and calls `house_pos`. The public body schema is unchanged; metadata now
reports `swiss_house_pos_longitude_latitude`. Fractional position is floored to house 1–12.
Invalid/undefined house results are rejected. At exactly zero ecliptic latitude, a cusp belongs
to its starting house; 1e-10-degree comparison tolerance handles floating-point roundoff only.
Nonzero-latitude bodies are never forced onto a cusp by longitude alone. Tests cover each cusp,
0/360 equivalence, and both sides of the 12→1 boundary. Placidus polar failure still has no fallback.

## Initialization and other audit findings

The official programmer manual recommends `set_ephe_path` even for Moshier. Installed binding
documentation confirms `swe.set_ephe_path(path)` and `None` support. The wrapper already initializes
at import, so missing an explicit call was not established as a current numeric error. It was an
implicit state dependency. Production now explicitly initializes on **every worker call under
the existing lock**, using a private empty directory to exclude external leap-second/Delta-T files.
Nonempty `SE_EPHE_PATH` is rejected because Swiss would override the supplied path. Automatic
tidal acceleration and Delta-T are restored. Threaded repeatability and hostile prior model-state
tests pass. Moshier flags are still explicit and returned flags checked; no file/JPL fallback.

UTC → `utc_to_jd` → TT for planets and UT1 for houses is correct. There is no new timezone lookup.
Longitude, speed and retrograde agree with external swetest. Mapping remains TRUE_NODE=11,
MEAN_APOG=12; South Node is North+180 normalized with identical speed and zero ecliptic latitude.
South Node is a derived identity, not a separately observed JPL body.

Aspects retain the documented decision to include nodes and Lilith: all unordered body pairs,
including the unavoidable nodal opposition. Tests check all five aspect types at and just outside
their orb limits, Sun and Moon special limits, universal sextile limit, and circular wrap.
Applying stays null. No aspect policy or Lilith convention changed.

Unexpected JSON fields/malformed bodies incorrectly mapped to `invalid_utc_datetime` in Stage 6.
They now return **422 `invalid_request`**, preserving the `detail.code/message` envelope.
Valid UTC, explicit +00:00, nonzero offset, naive time, bad coordinates and unsupported house
systems are covered. Coordinate/time/house-specific errors retain their appropriate codes.

## Synthetic input selection and timezone verification

Nine synthetic dates span 1988–2024, selected by calendar/season rather than from user data.
Three cases exercise Turkish summer DST; three exercise historical UTC+2 (including a leap day);
two exercise permanent UTC+3 (including another leap day); one exercises New York winter EST.
Times vary across the day and all nine are away from DST transitions. Existing gap/overlap tests remain.
Coordinates are generic points rounded to one decimal near Ankara, Kayseri, Konya and New York;
none are residential addresses. Every regression district is null. Geocoding mocks use fictional
Turkish place labels; the separate profile-validation sample uses a fictional Unicode name.

Expected UTC values were written by subtracting the selected historical offset, then checked with
stdlib ZoneInfo loading pinned IANA tzdata 2026.4 directly. No production timezone output was copied.
Reproduce: `docker compose run --rm backend python tools/verify_synthetic_timezones.py`.
The check verifies UTC, offset, DST, unambiguous local times and round trips for all nine cases.
Production timezone regression separately checks coordinate-to-IANA resolution.

## Privacy boundary

This public baseline contains synthetic fixtures only and includes no prior private Git history.
Tracked fixtures must remain synthetic. No old reference artifact is retained in this repository;
all four JPL and nine swetest outputs and their sidecars were refreshed.

## Tests, scope and remaining limitations

**467 passed**, **pip check: no broken requirements** in the Docker Compose Python 3.11 backend.
Two existing FastAPI/Starlette deprecation warnings remain. All existing tests remain; the
fixture-integrity test now validates provenance rather than requiring the Stage 6 empty list,
and the native wiring mock now supplies ARMC required by house_pos.

This is nine synthetic modern-date evidence points (1988–2024), not a proof across the full Moshier date
range. Independent JPL longitude checks cover Sun/Moon/Mercury/Jupiter; the other bodies are
verified against external Swiss execution. Angles/houses do not have a second independently
implemented algorithm reference. Future ancient dates, near-polar behavior and engine/time-model
updates merit further references. Python's datetime still cannot encode leap-second second 60.
The existing Windows Python 3.12 compiler limitation is unchanged. No production dependencies,
frontend code, numerology, Human Design, interpretation or Stage 8 work were added.

To refresh evidence deliberately, run the collector with network access, inspect the raw responses,
then run `build_astrology_references.py`; cached files are not silently replaced. Never generate
expected values using the service. Source reads in routine pytest remain entirely offline.

Primary sources:

- [Horizons quantity 31 and UTC conventions](https://ssd.jpl.nasa.gov/horizons/manual.html)
- [Horizons API parameters](https://ssd-api.jpl.nasa.gov/doc/horizons.html)
- [Astrodienst swetest command reference](https://www.astro.com/cgi/swetest.cgi?arg=-h)
- [Swiss initialization and house_pos documentation](https://www.astro.com/swisseph/swephprg.htm)
