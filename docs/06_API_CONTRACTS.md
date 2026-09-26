---
tags:
  - memory/architecture
---

# API Contracts

This is a summary; code schemas are the contract source. Planned endpoints are not implemented.
Related boundaries and ownership: [[02_ARCHITECTURE]] and [[05_DECISIONS]].

Stage 11A adds internal interpretation schemas/projection only, documented in [[08_AI_INTERPRETATION]].
There is no interpretation endpoint; existing Life Code/Kamerî responses and routes are unchanged.

## `POST /api/v1/kameri/calculate`

Required JSON fields are strict `local_date` (`YYYY-MM-DD`, 1800–2100), aware zero-offset
`utc_datetime` (`Z` or `+00:00`, 1800–2100), finite inclusive-range `latitude`/`longitude`,
nonempty IANA `timezone_id`, 1–200 character `arabic_name`, and literal `true`
`arabic_name_confirmed`. Extra fields are rejected. Local-date admission uses its own injectable
calendar clock; UTC future admission uses an injectable instant clock. The two input dates may differ.

Success returns `kameri-code-v1` metadata and Hijri, lunar (including numeric mansion), abjad and
planetary-hour layers. `interpretation_present` is always false. The response never echoes Arabic
input and excludes raw solar events/JDs, exact Fraction bounds, native flags and search diagnostics.
All four calculations must succeed; no partial response exists.

Validation errors use 422 and static codes/messages. Stable priority is malformed/extra request,
local date, UTC instant, coordinates, timezone, confirmation/name schema, then K1A character rules.
`ephemeris_error` and `invalid_astronomical_result` use 503; `solar_event_unavailable` and an
unresolved/unsupported supplied timezone use 422. Submitted values and native diagnostics are never
serialized. ADR-018 freezes this boundary; Life Code v1 is unchanged.

## `POST /api/v1/numerology/calculate`

**Purpose:** deterministic Pythagorean numerology under [[numerology]] conventions.
**Input:** `full_name` (strict string, 1–200 characters), `birth_date` (YYYY-MM-DD, not future),
optional `target_year` (strict integer 1–9999 or null; no implicit current year).
**Output:** metadata plus `life_path`, `birthday`, `expression`, nullable `soul_urge` and `personality`,
`maturity`, nullable `personal_year`. Each number has `raw_sum`, `value`, `is_master`.
Name/normalized name and date are never echoed. Missing target year gives null personal year.
**Important errors:** HTTP 422 `invalid_name`, `unsupported_name_characters`, `invalid_birth_date`,
`invalid_target_year`, `invalid_request`; envelope `detail.code/message`, with no submitted input.

## `GET /health`

**Purpose:** service health check.
**Input:** none.
**Output:** `{ "status": "ok", "service": "yasam-kodu-api" }`.
**Important errors:** standard HTTP transport errors only.

## `POST /api/v1/birth-profiles/validate`

**Purpose:** validate and normalize a birth profile without persistence.
**Input:** `first_name`, `last_name`, `birth_date`, `country`, `city`, `district`, `time_accuracy`,
and the exact or approximate time fields required by `time_accuracy`.
**Output:** `{ "valid": true, "profile": { ... } }`.
**Important errors:** `422` field errors for future dates, malformed times and incompatible exact /
approximate / unknown time combinations.

## `POST /api/v1/locations/resolve`

**Purpose:** resolve country, city and optional district through the backend geocoding service.
**Input:** `{ "country": string, "city": string, "district": string | null }`.
**Output:** `{ "resolved": true, "location": { "display_name", "latitude", "longitude",
"country", "city", "district", "provider" } }`.
**Important errors:** `404 location_not_found`, `409 location_ambiguous`, `502` malformed provider
response, `503` unavailable provider, `504` timeout.

## `POST /api/v1/timezones/resolve`

**Purpose:** resolve IANA timezone and historical UTC for exact local birth time.
**Input:** `{ "latitude": number, "longitude": number, "birth_date": "YYYY-MM-DD",
"birth_time": "HH:MM" }`.
**Output:** `resolved`, `status`, `timezone`, timezone-aware `local_datetime` and `utc_datetime`,
`utc_offset_minutes`, `dst`, `fold`.
**Important errors:** `422 invalid_coordinates` / `invalid_datetime` / `nonexistent_local_time`,
`404 timezone_not_found`, `409 ambiguous_local_time` with candidates, `503 timezone_data_unavailable`.

## `POST /api/v1/astrology/calculate`

**Purpose:** deterministic tropical astrology calculations from already resolved UTC and coordinates.
**Input:** timezone-aware zero-offset `utc_datetime`, `latitude`, `longitude`; optional
`house_system` (only `placidus`).
**Output:** `metadata`, keyed `bodies`, `ascendant`, `mc`, twelve `houses`, and `aspects`.
**Important errors:** `422 invalid_utc_datetime`, `invalid_coordinates`, `unsupported_house_system`,
`house_calculation_error`, `invalid_request` (extra fields/malformed bodies); `503 ephemeris_error`.
Envelope: `detail.code` and `detail.message`. Stage 7 placement metadata is
`swiss_house_pos_longitude_latitude`; body latitude stays internal.
Full conventions and precision limits: [[astrology]].

## `POST /api/v1/human-design/calculate`

**Status:** Stage 9B.2 implemented. Explicit strict Pydantic models in
`backend/app/schemas/human_design.py`; no interpretation, persistence or location processing.
The adapter calls the unchanged `calculate_human_design_core(utc_datetime)` once.

**Request:** only `utc_datetime`, an ISO 8601 calendar datetime with explicit zero offset.
`Z` and `+00:00` are equivalent (`+0000` also accepted). Extended calendar date/time,
minute or second precision and up to six fractional-second digits are supported; no epoch
coercion, date-only, naive/nonzero-offset, leap-second or sub-microsecond truncation.
Years 1800–2100 inclusive. Extra fields (including name/location/coordinates) are forbidden.
Missing/invalid `utc_datetime` uses `invalid_utc_datetime`; malformed/non-object/empty bodies
and extra fields use `invalid_request`. Extra-field errors take precedence over field errors.

```json
{"utc_datetime":"2000-02-24T12:00:00Z"}
```

**Admission:** `validation_now()` supplies an aware UTC clock, overridable in tests. Shared
BirthProfile future-date validation is applied, then exact UTC instant comparison rejects even
a later instant on the same day. Equality with now is accepted. No clock enters the core;
testing the 2100 support edge requires overriding admission time beyond that input.

**Response:** birth/design UTC serialize canonically with `Z`. Both activation arrays contain
13 bodies in the frozen order: sun, earth, moon, north_node, south_node, mercury, venus, mars,
jupiter, saturn, uranus, neptune, pluto. Longitude floats pass through without added rounding.
Active gates, channels, centers and components preserve the core's sorted deterministic order.
Definition is a kind identifier, with separate `component_count` and `definition_components`;
it is not channel count. Profile contains both Sun lines and the allowed pair label.
All identifiers use the core's Literal vocabulary. No service dataclass is the public schema.

Metadata includes convention/version and fixed solver settings required by [[human-design]].
Actual iterations, residual, final bracket width and internal Julian days are NOT exposed.
The following complete synthetic response is a transport example, NOT a new independent golden
or a promotion of its longitude/Design timestamp into the official behavioral evidence:

```json
{
  "metadata": {
    "spec_revision": "stage9a2-v1",
    "pyswisseph_version": "2.10.3.2",
    "swiss_ephemeris_version": "2.10.03",
    "ephemeris": "moshier",
    "zodiac": "tropical",
    "observer": "geocentric",
    "longitude_frame": "apparent_ecliptic_of_date",
    "node_algorithm": "true_node",
    "design_arc_degrees": 88.0,
    "solver_bracket_days": [100, 80],
    "solver_max_iterations": 64,
    "solver_max_bracket_seconds": 0.01,
    "solver_max_residual_degrees": 1e-7
  },
  "birth_utc": "2000-02-24T12:00:00Z",
  "design_utc": "1999-11-29T20:47:19.479281Z",
  "personality": [
    {"body":"sun","longitude":335.18020366745594,"gate":55,"line":6},
    {"body":"earth","longitude":155.180203667456,"gate":59,"line":6},
    {"body":"moon","longitude":215.30304553391198,"gate":28,"line":4},
    {"body":"north_node","longitude":123.23378730154295,"gate":31,"line":2},
    {"body":"south_node","longitude":303.233787301543,"gate":41,"line":2},
    {"body":"mercury","longitude":346.44728509946594,"gate":63,"line":6},
    {"body":"venus","longitude":307.7804063928942,"gate":19,"line":1},
    {"body":"mars","longitude":9.454196315851844,"gate":17,"line":6},
    {"body":"jupiter","longitude":31.651650375061166,"gate":3,"line":6},
    {"body":"saturn","longitude":41.975522237274326,"gate":24,"line":5},
    {"body":"uranus","longitude":317.84511186110524,"gate":13,"line":5},
    {"body":"neptune","longitude":305.1839211487368,"gate":41,"line":4},
    {"body":"pluto","longitude":252.78773361404362,"gate":5,"line":2}
  ],
  "design": [
    {"body":"sun","longitude":247.18020364973475,"gate":9,"line":2},
    {"body":"earth","longitude":67.18020364973472,"gate":16,"line":2},
    {"body":"moon","longitude":155.89654200023665,"gate":40,"line":1},
    {"body":"north_node","longitude":125.62825671988702,"gate":31,"line":4},
    {"body":"south_node","longitude":305.628256719887,"gate":41,"line":4},
    {"body":"mercury","longitude":227.40380166130169,"gate":1,"line":5},
    {"body":"venus","longitude":202.98058080211334,"gate":32,"line":3},
    {"body":"mars","longitude":302.738707041327,"gate":41,"line":1},
    {"body":"jupiter","longitude":25.752512622609157,"gate":42,"line":6},
    {"body":"saturn","longitude":41.91294623593258,"gate":24,"line":5},
    {"body":"uranus","longitude":313.45645664545646,"gate":13,"line":1},
    {"body":"neptune","longitude":302.1875003139082,"gate":41,"line":1},
    {"body":"pluto","longitude":250.22015295303407,"gate":9,"line":5}
  ],
  "active_gates": [1,3,5,9,13,16,17,19,24,28,31,32,40,41,42,55,59,63],
  "channels": [],
  "defined_centers": [],
  "undefined_centers": ["ajna","ego","g","head","root","sacral","solar_plexus","spleen","throat"],
  "type": "reflector",
  "strategy": "wait_lunar_cycle",
  "authority": "lunar",
  "profile": {"personality_line":6,"design_line":2,"label":"6/2"},
  "definition": "none",
  "component_count": 0,
  "definition_components": []
}
```

**Errors:** route-local validation handling; existing routers and global handlers are unchanged.

| HTTP | Code | Meaning |
| --- | --- | --- |
| 422 | `invalid_request` | Extra fields or malformed/non-object/empty body |
| 422 | `invalid_utc_datetime` | Missing/invalid UTC or future instant |
| 422 | `unsupported_date_range` | Birth year outside 1800–2100 |
| 503 | `ephemeris_error` | Native/astronomical calculation unavailable |
| 503 | `design_moment_error` | Safe 88-degree convergence unavailable |
| 503 | `classification_error` | Mechanical result could not be classified |

Calculation-domain failures use 503, consistent with astrology's unavailable ephemeris outcome;
they do not imply bad input or promise that retry will succeed. No fallback chart is fabricated.
Messages are static and never reuse exception text, native details, paths, input or Pydantic ctx.

```json
{"detail":{"code":"invalid_request","message":"İstek gövdesini ve alanlarını kontrol edin."}}
```

```json
{"detail":{"code":"ephemeris_error","message":"Astronomik hesaplama tamamlanamadı."}}
```

No submitted data is logged or persisted by this adapter. Success intentionally returns birth UTC;
errors do not echo it. No name, location or coordinates occur in the response. Existing CORS and
disabled `/docs`, `/redoc`, `/openapi.json` policy remain unchanged.

## `POST /api/v1/life-code/calculate`

**Qualification:** Stage 10B complete; 89 targeted API tests and full 924 backend tests pass in Docker.

**Purpose:** deterministic public aggregation of the three verified calculation systems.
Input must already be resolved. This endpoint does NOT perform geocoding or historical timezone
resolution and does not generate interpretation. Schemas: `backend/app/schemas/life_code.py`.
Internal orchestration/ownership: [[life-code]] and ADR-016.

**Synthetic request:**

```json
{
  "full_name": "Synthetic Example",
  "birth_date": "2000-01-02",
  "utc_datetime": "2000-01-01T21:30:00Z",
  "latitude": 41.0,
  "longitude": 29.0,
  "target_year": null
}
```

- `full_name`: strict string, 1–200 characters; existing Numerology character rules apply.
- `birth_date`: strict `YYYY-MM-DD` calendar date (the LOCAL date supplied to Numerology).
- `utc_datetime`: existing HD ISO 8601 zero-offset grammar, supported UTC years 1800–2100.
  Z/+00:00 are equivalent; naive, nonzero offset, epoch, date-only and leap-second input rejected.
  The HD microsecond precision limit is preserved, without silent truncation.
- Coordinates: finite numeric latitude −90..90, longitude −180..180, inclusive; no string/bool coercion.
- `target_year`: omitted/null or strict integer 1..9999; no implicit current year.
- Extra fields forbidden, including `house_system`, country/city/district/local-time fields.
  Placidus remains fixed internally. Calendar date and UTC date need NOT be equal.

**Two admission clocks, no timezone inference:** UTC instant must be `<= validation_now()` (aware
UTC); equality is accepted, even a future microsecond is rejected. Calendar birth date uses the
same `validation_today()` dependency and `validate_birth_date` rule as standalone Numerology:
`birth_date <= date.today()` in the SERVER's local calendar. Both dependencies are independently
overridable in tests. This preserves existing behavior; it does not interpret the user's birthplace
timezone or substitute UTC date for the calendar date. Near a day boundary a valid local date may
still fail the existing server-day admission rule; no unapproved timezone policy is introduced.
Calendar admission runs before instant admission. No clock enters the Stage 10A service.

**Response shape** (type placeholders, not a literal full payload):

```text
{
  "metadata": {
    "schema_version": "life-code-v1",
    "calculation_layers": ["astrology", "numerology", "human_design"],
    "interpretation_present": false
  },
  "astrology": <existing AstrologyResponse>,
  "numerology": <existing NumerologyResponse>,
  "human_design": <existing HumanDesignResponse>
}
```

The three section models are composed, not copied or recalculated. Astrology/Numerology fields
and metadata are unchanged. The shared `api/human_design_projection.py` helper is used by BOTH
standalone HD and Life Code; HD core objects are never serialized wholesale. Actual Julian days,
residual, bracket width, iterations and internal astronomy containers are absent. Fixed solver
SETTINGS already exposed by standalone HD remain unchanged. No float rounding, ordering changes
or serialization feedback. The HTTP bytes are a snapshot; internal shallow immutability is unchanged.

**Privacy:** full/normalized name never appears in any response section or metadata. Calendar
birth date is not newly echoed; existing HD `birth_utc`/`design_utc` remain public. No input coordinates
are newly echoed (activation longitude remains astronomical longitude). No request logging,
persistence, cache, network/provider or AI call is introduced. Errors never echo submitted values,
Pydantic input/ctx/raw repr, native exception text, file paths or traceback.

| HTTP | Code | Condition |
| --- | --- | --- |
| 422 | `invalid_request` | Extra fields, malformed/non-object/empty body, unknown internal input field |
| 422 | `invalid_name` | Missing/invalid name or Numerology name rejection |
| 422 | `unsupported_name_characters` | Existing Numerology alphabet restriction |
| 422 | `invalid_birth_date` | Missing/malformed calendar date or future server-calendar date |
| 422 | `invalid_target_year` | Noninteger/bool or out-of-range target year |
| 422 | `invalid_utc_datetime` | Missing/malformed/nonzero-offset or future instant |
| 422 | `invalid_coordinates` | Missing/nonfinite/non-numeric/out-of-range coordinates |
| 422 | `unsupported_date_range` | UTC birth year outside HD's 1800–2100 support |
| 422 | `house_calculation_error` | Placidus domain failure; same status as standalone Astrology |
| 503 | `ephemeris_error` | Astrology/HD astronomical failure |
| 503 | `design_moment_error` | HD safe Design convergence failure |
| 503 | `classification_error` | HD classification failure |

Request validation is route-local. Extra/malformed-body errors take precedence; otherwise first
invalid field in this fixed order wins: full_name, birth_date, utc_datetime, latitude, longitude,
target_year. An empty object therefore uses `invalid_name`. A recognized HD range failure uses
`unsupported_date_range`. `LifeCodeInputError.field` maps to these same public field codes;
unknown fields map to `invalid_request`. Known engine domain errors retain code/status semantics
but use static safe messages, never exception text. No generic `except Exception`: programming
errors still fail instead of becoming fabricated successful charts or input errors.

```json
{"detail":{"code":"invalid_birth_date","message":"Geçerli ve gelecekte olmayan bir doğum tarihi girin."}}
```

```json
{"detail":{"code":"ephemeris_error","message":"Astronomik hesaplama tamamlanamadı."}}
```

CORS and disabled OpenAPI/docs policy are unchanged. Stage 11 AI and Stage 12 PDF remain separate,
unimplemented stages; no unified frontend result UI is added here.
