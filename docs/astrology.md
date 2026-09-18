---
tags:
  - memory/astrology
---

# Deterministic Astrology — Stages 6–7

Related: [[02_ARCHITECTURE]], [[05_DECISIONS]], [[06_API_CONTRACTS]], [[07_TEST_STRATEGY]].

## Engine and installation

Runtime dependency: `pyswisseph==2.10.3.2`; bundled Swiss Ephemeris version `2.10.03`.
The response reports both versions. Planet calculations explicitly request `FLG_MOSEPH | FLG_SPEED`;
returned flags are checked. Moshier is the selected Swiss Ephemeris backend, not a silent fallback.
No external ephemeris files are installed. Results are reproducible for the same inputs and pinned
runtime; engine upgrades require regression review. Native calls are serialized by a process-local lock.
Each worker call explicitly runs `set_ephe_path` with a private empty directory, then resets automatic
tidal acceleration and Delta-T. Nonempty `SE_EPHE_PATH` is rejected to prevent external files from
overriding this configuration. See [[astrology-verification]] for initialization tests and provenance.

Windows: the pinned release publishes Python 3.11 wheels. Python 3.12 requires a working C++ build
toolchain; the existing local Python 3.12 environment could not compile the package. Stage 6 was
verified in `backend/.venv-stage6` using Python 3.11.9. For a durable development installation,
install Python 3.11 and create a new virtual environment, then install `requirements-dev.txt`.
The temporary verification runtime must not be treated as a production deployment.

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Use a new environment directory if `.venv` already belongs to another Python version.

## Input and ownership

`POST /api/v1/astrology/calculate` accepts `utc_datetime`, `latitude`, `longitude` and optional
`house_system` (only `placidus`; default `placidus`). UTC must be timezone-aware with zero offset
(`Z` or `+00:00`). Naive times, nonzero offsets, numeric timestamps, nonfinite coordinates and
coordinates outside latitude [-90, 90] / longitude [-180, 180] are rejected.
East longitude and north latitude are positive. Gregorian calendar is used.

Use the resolved UTC from the timezone layer. This service does no geocoding, timezone resolution,
interpretation or AI processing. `utc_to_jd` converts UTC to TT and UT1: planets use `calc(TT)`,
houses use `houses_ex(UT1)`. Fractional seconds are preserved. This astronomical timescale conversion
is distinct from resolving a local civil timezone. Python datetime does not represent leap-second 60.

## Canonical conventions

- Tropical zodiac; geocentric apparent ecliptic longitudes of date, in degrees.
- Placidus houses (`P`), ASC and MC. No automatic alternative house system.
- True North Node (`TRUE_NODE`). South Node is `(north + 180) % 360`, with the same longitude speed.
- Lilith means **Mean Black Moon Lilith**, the mean lunar apogee (`MEAN_APOG`); not asteroid Lilith
  and not osculating/true apogee.
- Bodies: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto,
  True North Node, South Node and Lilith. Chiron is omitted because its asteroid ephemeris data
  are not supplied in this configuration.

`longitude` is [0, 360); `degree_in_sign` is [0, 30). Sign names are lowercase English identifiers
from `aries` to `pisces`. `speed_longitude` is degrees/day; `retrograde = speed_longitude < 0`.
There are no body-specific overrides: even True Node can be direct. Zero speed is not retrograde.

## Houses and angles

`ascendant` and `mc` contain longitude, sign and degree-in-sign. `houses` is an ordered array of
12 objects, each with `house` (1–12) and the same position fields. Each body includes its house.
Placement uses Swiss `house_pos` with ecliptic longitude **and latitude**, true obliquity and ARMC.
Stage 7 replaced the Stage 6 cusp-longitude projection after finding seven different placements
across six fixtures. Latitude remains internal; metadata reports `swiss_house_pos_longitude_latitude`.
The returned fractional house position is floored. At zero latitude an exact cusp belongs to its
starting house (1e-10-degree numerical equality tolerance). 360-degree wrap and house 12 → 1 are
tested. Full comparison and decision: [[astrology-verification]] and ADR-010 in [[05_DECISIONS]].

At polar/high latitudes Placidus can be undefined. Native house failures return
`house_calculation_error`, with no chart or fallback result (including no Porphyry or Whole Sign).

## Aspects

All unordered body pairs, including nodes and Lilith, are considered once. Node opposition is
therefore present by definition. Angles are not included as aspect bodies in this version.
Circular separation is the shortest angle in [0, 180]. Orb is absolute distance from the exact angle.

| Aspect | Exact angle | Maximum orb |
| --- | --- | --- |
| Conjunction | 0 | 8 if either body is Sun/Moon, otherwise 6 |
| Sextile | 60 | 4 for every pair |
| Square | 90 | 8 if either body is Sun/Moon, otherwise 6 |
| Trine | 120 | 8 if either body is Sun/Moon, otherwise 6 |
| Opposition | 180 | 8 if either body is Sun/Moon, otherwise 6 |

Boundary orbs are included. `ORB_POLICY` in the service is the single policy source.
Each aspect contains body1, body2, type, exact_angle, separation, orb and `applying: null`.
Applying/separating is intentionally unimplemented, never guessed.

## Errors and limitations

The existing API envelope is retained: `{"detail":{"code":"...","message":"..."}}`.
HTTP 422: `invalid_utc_datetime`, `invalid_coordinates`, `unsupported_house_system`,
`house_calculation_error`, `invalid_request`. HTTP 503: `ephemeris_error`.
Raw native exceptions are never returned. Malformed/nonobject JSON and extra fields use
`invalid_request`, not an unrelated datetime error.

Moshier has a finite date range (approximately 3000 BCE–3000 CE); unsupported dates fail rather
than switch data sources. It is less precise than file-based JPL/Swiss ephemerides, especially for
the Moon. UTC/TT/UT1 uses the pinned library's leap-second/Delta-T model; future or historical time
model changes require review before deployment. External Swiss data paths are not supported in this mode.
Stage 7 verification passed for nine modern-date fixtures: JPL DE441 for Sun/Moon/Mercury/Jupiter,
external Astrodienst swetest for angles, cusps, body placement and speeds. The latter shares Swiss
algorithms and is an integration check, not independent algorithm verification. Scope, measured
deviations and limitations: [[astrology-verification]].

## Fixtures and licensing

Tests read UTC and coordinates from `backend/tests/fixtures/birth_cases.json`, using synthetic case IDs; no real-person birth data is permitted.
Boundary tests mutate these inputs for invalid/high-latitude requests. Synthetic angular inputs
test mathematical helpers; they are not astronomical reference observations.
`astrology_references.json` contains nine externally sourced records with raw artifact hashes,
query URLs, retrieval dates, conventions and field-level source maps. Its null template is preserved.
No engine-generated expected positions are stored. Reference regression tests run offline.

AGPL-3.0 is the chosen project/Swiss Ephemeris licensing route. No Professional License is used.
Upstream copyright and license notices were checked against the pinned source distribution;
see [THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES.md) and [LICENSE](../LICENSE).

Primary references (checked 2026-09-17):

- [pyswisseph 2.10.3.2 and source distribution](https://pypi.org/project/pyswisseph/2.10.3.2/)
- [Swiss Ephemeris programming interface](https://www.astro.com/swisseph/swephprg.htm)
- [Swiss Ephemeris general documentation and Moshier backend](https://www.astro.com/swisseph/swisseph.htm)
