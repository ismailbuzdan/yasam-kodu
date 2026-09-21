---
tags:
  - memory/architecture
---

# Kamerî qualified knowledge base — Stage K2B

2026-09-21: **K2A COMPLETE; K2B LIMITED PRODUCTION KB COMPLETE; Kamerî mechanical API COMPLETE;
Stage 11 NOT STARTED.** ADR-020 in [[05_DECISIONS]] freezes this delivery.

## Data and policy boundary

`backend/app/knowledge/kameri/` is independent of `app.services.traditional`:

- `models.py`: strict frozen Pydantic models; nested collections are tuples, unknown fields rejected.
- `data/kameri_kb_v1.json`: separately curated, versioned production snapshot, exactly four claims
  and four source records (KI-A03, KI-B05, KI-B07, KI-B08).
- `repository.py`: validates the bundled file once during module initialization; shared read-only
  snapshot, explicit `get_claim`, static `ClaimNotFoundError` for missing records.
- `selector.py`: accepts only `HijriMonthContext(hijri_month=...)`, a strict integer in 1–12.
  Caller supplies an already calculated month; no date conversion occurs here.

Schema and each claim use `kameri-kb-v1`. Source references retain precise claim locators; source
records retain title, URL, locator, tier and verified scope. The four statements are short independent
factual normalizations from the qualified ledger, not copied source paragraphs, translations, scans
or tables. All claims retain method/tradition, original context, limitations, excluded inferences,
religious boundary and `ai_usage=restricted`. This policy metadata is not an AI implementation.

| Claim | Application | Meaning and limit |
| --- | --- | --- |
| ASMA_NUM_001 | `reference_only`, key null | Specified spelling الله has additive value 66. Explicit non-personal lookup only; no automatic association from a person's abjad total. |
| HIJRI_CTX_001 | `hijri_month_context`, key 9 | Ramadan fasting/Quran context; not personal virtue or a religious ruling. |
| HIJRI_CTX_002 | `hijri_month_context`, key 9 | Ramadaniyye literary context; not a person's artistic trait. |
| HIJRI_CTX_003 | `hijri_month_context`, key 12 | Dhulhijja pilgrimage/festival context; not a personality or ritual instruction. |

Model validation enforces the claim-specific modes, keys and classifications. The selector filters
month-context records and orders them by claim ID. It never accepts names, Arabic text, AbjadResult,
UTC, coordinates or prompts. `raw_sum=66` cannot enter selection and never selects ASMA_NUM_001.
The typed selection model also rejects reference-only claims.

For months 1–8, 10 and 11, the immutable result has `claims=()`, `abstained=True`,
`reason="no_qualified_claims_for_context"`. For months 9 and 12, `abstained=False`, `reason=None`.
There is no nearest-month or generic personality fallback. Finding a contextual fragment does not
mean a personal interpretation has been qualified. Tabular month context does not certify actual
religious observance dates.

## Provenance and operational limits

The [K2A ledger](references/kameri_interpretation_sources.json) remains research/audit evidence,
unchanged and never loaded at runtime. Tests require exact equality of its `QUALIFIED_FOR_KB` IDs
and the four production IDs, compare provenance/boundaries, and exclude its other 14 assessments.
See [[kameri-interpretation-qualification]] for the original qualification and rights limits.
No new source research or expanded claims were introduced.

Loading is local and fail-closed: invalid bundled data raises validation errors, not a partial KB.
No network calls, calculation calls, database, logs, provider clients or prompts. Python module
initialization publishes one validated snapshot per process; tuple/frozen children prevent ordinary
caller mutation, and exported dictionaries do not alias it. Code using Pydantic's deliberately
unchecked construction/copy APIs is outside the validated input boundary; do not use them to admit data.

The mechanical `POST /api/v1/kameri/calculate` contract is unchanged, including
`interpretation_present=false`. No public KB endpoint or Life Code v1 integration is introduced.
Frontend remains unchanged and stopped during K2B; no dependency change or image rebuild was needed.

## Validation

Docker: K2B **83**, K1A **464**, K1B **67**, full backend **1538 passed / 2 existing warnings**;
pip check clean; HD audit **68/68**; Kamerî evidence **12/12**. Tests cover all months, explicit
abstention, invalid data/admission, the abjad-66 firewall, locators, rights structure, nested
immutability, repeated/parallel calls and a fresh offline repository load without calculation imports.
The existing warnings concern Starlette/httpx and anyio BlockingPortal deprecations.

Compose mounts only `backend/`. For ledger comparison, copy the unchanged research file into the
container's temporary filesystem and provide a **test-only** path (no skip if missing):

```sh
docker compose cp docs/references/kameri_interpretation_sources.json backend:/tmp/k2b-research-ledger.json
docker compose exec -e KAMERI_RESEARCH_LEDGER=/tmp/k2b-research-ledger.json backend python -m pytest -q tests/test_kameri_knowledge_base.py tests/test_kameri_knowledge_selector.py
docker compose exec -e KAMERI_RESEARCH_LEDGER=/tmp/k2b-research-ledger.json backend python -m pytest -q
```

On the host the test defaults to the repository ledger path. Recopy after any separately authorized
ledger edit; the temporary copy is not a second source of truth or a runtime configuration.

## Stage 11 readiness

**YES, LIMITED**: only the three cited Ramadan, Ramadaniyye and Dhulhijja cultural fragments can
be automatically selected for a future narrator. ASMA_NUM_001 is not automatic personal context.
Deep personalized Kamerî reading, personal Asma, mansion/hour interpretation, Hurûf personality,
zodiac–Asma, yıldıznâme, dhikr recommendation and mother's-name collection remain excluded.
Stage 11 requires separate authorization and has **NOT STARTED**.

Related: [[kameri-code]], [[02_ARCHITECTURE]], [[04_CURRENT_STATE]], [[07_TEST_STRATEGY]].
