---
tags:
  - memory/life-code
---

# Stage 10A — Unified Life Code internal aggregation

**Status:** Stage 10A complete. Unified deterministic Life Code internal model/service complete.
Stage 10B API not implemented; Stage 11 AI and Stage 12 PDF not started.
See [[02_ARCHITECTURE]], ADR-016 in [[05_DECISIONS]] and [[07_TEST_STRATEGY]].

## Ownership and scope

`calculate_life_code(input: LifeCodeInput) -> LifeCodeResult` in
`backend/app/services/life_code_service.py` orchestrates existing Python engines sequentially:
Astrology → Numerology → Human Design. It is not a fourth calculation system.
There is no HTTP request/response model, endpoint, geocoding, timezone resolution, interpretation,
database, network call, new dependency or added native lock. Existing engine conventions and
reference fixtures remain unchanged. Calculation-layer results remain the sole mechanical input
for a future interpretation layer; this stage does not implement that layer or its public API.

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
response, this is lossless aggregation, not a public transport contract. Stage 10B must explicitly
decide its API-safe projection. Unified metadata does not duplicate any engine convention/version.

## Validation, errors and clock ownership

`LifeCodeInput` enforces resolved Python types (not wire-format strings), including exact `date`
rather than `datetime` for calendar birth date and non-boolean numeric coordinates.
`calculate_life_code` first builds existing `AstrologyRequest` and `NumerologyRequest` values,
reusing their UTC/coordinate/name-length/year validation before invoking any engine.
The HD core continues to own its 1800–2100 range check; no duplicate HD convention check is added.
Numerology continues to own name normalization/character acceptance. No engine schema is changed.

Pydantic validation failures cannot propagate raw input/context because they may contain names.
They become `LifeCodeInputError(code="invalid_input", field=<known field>)` with static field-only
text and suppressed validation exception display. There is no HTTP status mapping in this stage.

Engine domain errors preserve their original class, code and safe domain message. Only native
cause display is suppressed (`raise error from None`); errors are not replaced with generic
exceptions, swallowed or logged. Known exception objects may retain traceback/context internally;
future API/logging layers must never serialize exceptions or traceback locals. Unexpected programming
exceptions are not caught. Fail-fast behavior means later engines are not called after an earlier
failure; no partial result, retry or fallback is returned. Exactly one call per engine on success.

No current time/random/default target year or future-date admission check is added. A supported
future UTC instant is calculable internally; Stage 10B owns injectable admission-clock policy.
Swiss state remains owned by the existing shared Astrology/HD native lock and initialization.

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
