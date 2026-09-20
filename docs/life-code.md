---
tags:
  - memory/life-code
---

# Unified Life Code — internal aggregation and public transport

**Status:** Stage 10A complete; Stage 10B complete; Stage 10 complete. Unified Life Code API complete.
Stage 11 AI and Stage 12 PDF not started. Unified result frontend UI is not implemented.
See [[02_ARCHITECTURE]], ADR-016 in [[05_DECISIONS]] and [[07_TEST_STRATEGY]].

## Ownership and scope

`calculate_life_code(input: LifeCodeInput) -> LifeCodeResult` in
`backend/app/services/life_code_service.py` orchestrates existing Python engines sequentially:
Astrology → Numerology → Human Design. It is not a fourth calculation system.
The internal service has no HTTP request/response model, endpoint, geocoding, timezone resolution,
interpretation, database, network call, new dependency or added native lock. Existing engine conventions and
reference fixtures remain unchanged. Calculation-layer results remain the sole mechanical input
for a future interpretation layer; Stage 10 does not implement that interpretation layer.

| Input | Owner | Rule |
| --- | --- | --- |
| `full_name: str` | Numerology | Input only; no name or normalized name in result/logs |
| `birth_date: date` | Numerology | Supplied LOCAL/CALENDAR date, never derived from UTC |
| `utc_datetime: datetime` | Astrology + Human Design | Same resolved aware zero-offset instant |
| `latitude: float`, `longitude: float` | Astrology | Resolved numeric coordinates only; Placidus fixed |
| `target_year: int \| None = None` | Numerology | Explicit year only; None preserves null personal year |

Calendar date and UTC date may differ. Their geographic/timezone consistency belongs to the
upstream resolver; the aggregation service neither invents a zone nor imposes date equality.
Changing name/target year must not change Astrology/HD. Changing coordinates must not change
Numerology/HD. Only Astrology receives coordinates. Name does not enter astrology or HD requests.

## Internal models and immutability boundary

`backend/app/services/life_code_models.py` contains frozen dataclasses:

- `LifeCodeInput`: six resolved fields above; name is excluded from its generated repr.
- `LifeCodeMetadata`: `schema_version="life-code-v1"`,
  `calculation_layers=("astrology", "numerology", "human_design")`,
  `interpretation_present=False`. These fixed aggregation fields cannot be constructor-overridden.
- `LifeCodeResult`: `metadata`, original typed `AstrologyResponse`, `NumerologyResponse` and
  `HumanDesignResult` objects. No full name, retained input object or normalized name.

**User-selected boundary: frozen outer model, NOT deep immutability.** Existing Astrology and
Numerology Pydantic children (including lists/dicts) remain mutable; consumers must treat them
as read-only. Human Design already uses frozen internal values. Tests explicitly exercise this
boundary rather than claiming recursive immutability. No frozen copies or parallel engine result
schemas are introduced. Each successful call produces fresh engine results; no result caching.

The original child objects are retained by identity. All fields, order, precision, nulls and
engine-owned metadata are preserved; no fields are dropped/renamed/recomputed/rounded.
This internal result also retains HD's internal astronomy diagnostics: unlike the HD HTTP
response, this is lossless aggregation, not a public transport contract. Stage 10B projects HD through
the same explicit helper as the standalone endpoint. Unified metadata does not duplicate engine conventions.

## Validation, errors and clock ownership

`LifeCodeInput` enforces resolved Python types (not wire-format strings), including exact `date`
rather than `datetime` for calendar birth date and non-boolean numeric coordinates.
`calculate_life_code` first builds existing `AstrologyRequest` and `NumerologyRequest` values,
reusing their UTC/coordinate/name-length/year validation before invoking any engine.
The HD core continues to own its 1800–2100 range check; no duplicate HD convention check is added.
Numerology continues to own name normalization/character acceptance. No engine schema is changed.

Pydantic validation failures cannot propagate raw input/context because they may contain names.
They become `LifeCodeInputError(code="invalid_input", field=<known field>)` with static field-only
text and suppressed validation exception display. There is no HTTP status mapping in the internal service.

Engine domain errors preserve their original class, code and safe domain message. Only native
cause display is suppressed (`raise error from None`); errors are not replaced with generic
exceptions, swallowed or logged. Known exception objects may retain traceback/context internally;
future API/logging layers must never serialize exceptions or traceback locals. Unexpected programming
exceptions are not caught. Fail-fast behavior means later engines are not called after an earlier
failure; no partial result, retry or fallback is returned. Exactly one call per engine on success.

No current time/random/default target year or future-date admission check is added. A supported
future UTC instant is calculable internally; Stage 10B owns injectable admission-clock policy.
Swiss state remains owned by the existing shared Astrology/HD native lock and initialization.

## Stage 10B public API

`POST /api/v1/life-code/calculate` is a thin transport around this unchanged service:
strict resolved request → LifeCodeInput → one service call → explicit LifeCodeResponse.
The response composes existing AstrologyResponse/NumerologyResponse/HumanDesignResponse plus
typed aggregation metadata. `api/human_design_projection.py` extracts the existing HD mapping
without changing its schema or values, and both routers use it. Internal HD Julian days and
per-calculation solver diagnostics cannot enter the public response. Fixed solver settings remain
public exactly as before. No deep-freeze, result caching or service/model change is introduced.

UTC instant admission uses injectable aware `validation_now()`. Calendar admission reuses standalone
Numerology's injectable `validation_today()` SERVER-local date policy, not a birthplace timezone.
The clocks can differ at day boundaries; no calendar-date/UTC-date equality or new timezone
consistency rule is imposed. This preserves the existing calendar-admission limitation explicitly.
No clock enters the core. Full request/response shape, privacy and errors: [[06_API_CONTRACTS]].

Known engine errors use stable public codes and static safe messages: input/admission and Placidus
house failures are 422; ephemeris/design/classification failures are 503. LifeCodeInputError maps
by field; unknown fields use invalid_request. Programming errors are not generically caught.
No full/normalized name, input coordinates or calendar date is newly echoed, logged or stored.
Existing HD birth/design UTC values remain public. No provider/AI/frontend/PDF/database work.

## Verification

46 targeted tests use only synthetic names/timestamps/coarse coordinates. They cover original
object identity, direct-output equality, routing/call order/count, local-calendar/UTC-date separation,
name/year/coordinate metamorphic invariants, input errors, private exception text, fail-fast engine
error ownership, suppressed native causes, network guards, null target year, no clock and the chosen
shallow frozen boundary. Repeated and parallel complete calculations verify native-state isolation.
These are aggregation/invariant tests, not newly generated engine accuracy references.

Existing Astrology, Numerology and HD regression suites and the full backend suite remain required,
as do `pip check` and the read-only 68-artifact HD audit. No accepted expectation may be regenerated
to accommodate an orchestration discrepancy.

Stage 10B qualification (Docker, 2026-09-20): 89 new API tests pass, including standalone equality,
shared HD projection/non-mutation, diagnostics/name exclusion, cross-date/metamorphic ownership,
strict input/error contracts, injectable clocks, canonical repeats and small parallel requests.
Stage 10A regression: 46; standalone API-containing suites: 246; full backend: 924 with two existing
warnings. `pip check` clean; read-only evidence audit 68/68. The earlier Docker startup blocker is
resolved; preserved WIP passed without calculation or adapter fixes. Frontend lint/typecheck/8 tests/
production build also pass; generated dev paths returned to production paths through the build,
leaving no frontend diff. No reset/restore or reference changes.
