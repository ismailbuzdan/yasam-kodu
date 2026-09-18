---
tags:
  - memory/architecture
---

# Architecture

Güncel sınırlar ve kaynak haritası için [[04_CURRENT_STATE]]; kararlar için [[05_DECISIONS]];
gerçek HTTP sınırları için [[06_API_CONTRACTS]]. Tarihsel başlangıç notu için
[architecture.md](architecture.md); timezone ayrıntıları için [[timezone]] ([GitHub link](timezone.md));
tasarım ayrıntıları için [[frontend-design]] ([GitHub link](frontend-design.md)).

```mermaid
flowchart LR
  A[User Birth Data] --> B[COMPLETED: BirthProfile Validation]
  B --> C[COMPLETED: Geocoding]
  C --> D[COMPLETED: Historical Timezone]
  D --> E[COMPLETED: Astrology Engine and Stage 7 verification]
  D --> F[PLANNED: Numerology Engine]
  D --> G[PLANNED: Human Design Engine]
  E --> H[PLANNED: Unified Life Code]
  F --> H
  G --> H
  H --> I[PLANNED: AI Interpretation]
  I --> J[PLANNED: Web Report / PDF]
```

| Layer | Technology | Status |
| --- | --- | --- |
| Frontend | Next.js, TypeScript, App Router, Tailwind | completed foundation |
| Backend | FastAPI, Python, Pydantic | completed foundation |
| Geocoding | Nominatim through backend service | completed |
| Timezone | timezonefinder, zoneinfo, tzdata | completed |
| Astrology | Swiss Ephemeris 2.10.03 / pyswisseph 2.10.3.2 | Stages 6–7 completed; scope: [[astrology-verification]] |
| Database | PostgreSQL | planned |
| AI | provider abstraction, Gemini/OpenAI candidates | planned |
| PDF | shared report JSON source | planned |

Frontend never calls a geocoding provider directly. The timezone layer takes resolved coordinates
and exact local time; the astrology service receives its UTC result and must not repeat
timezone resolution.

## Stage 6 Swiss Ephemeris licensing

Stage 6 uses the AGPL route; the Professional License is not used. Copyright and license notices
were verified against the pinned source distribution and preserved in
[THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES.md). Calculation conventions: [[astrology]].
