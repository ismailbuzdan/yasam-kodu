---
tags:
  - memory/architecture
---

# API Contracts

This is a summary; code schemas are the contract source. Planned endpoints are not implemented.
Related boundaries and ownership: [[02_ARCHITECTURE]] and [[05_DECISIONS]].

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
