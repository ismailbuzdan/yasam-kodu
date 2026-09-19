---
tags:
  - memory/history
---

# Changelog

Current delivery state: [[04_CURRENT_STATE]]. Milestone sequence: [[03_ROADMAP]].

## 2026-09-19 — Stage 9A.1 official reference research (incomplete)

- Preserved all local continuation work and 50 original raw artifacts; added 14 public official
  Jovian synthetic chart captures, pinned-PyHD diagnostics and collection provenance (68 artifacts).
- Recorded 364/364 activation matches; True Node matches 56/56 N/S observations, with 46
  discriminating against Mean. Version/settings remain undisclosed; node status PARTIALLY VERIFIED.
- Bracketed Gate 41 transition using 00:53/00:55 UTC official observations. Approximately 302°
  supported; exact equality ownership UNRESOLVED. No invented second-precision evidence.
- Verified previously missing rare category examples and four missing profile pairs. Added
  field-level research graph comparison and updated acceptance matrix, without golden promotion.
- Made audit read-only, retaining original checks. Docker: 8 integrity / 592 total tests pass,
  two existing warnings; pip check clean. ADR-015 Proposed; Stage 9A incomplete / 9B not ready.
- No production HD engine, endpoint, schemas, solver, frontend or other production change.

## 2026-09-19 — Stage 9A Human Design convention research continuation

- Diagnosed all 19 stored Gate/Line disagreements as one fixed 2.5-arcminute mapper offset: 17
  line-only and two gate+line differences; no candidate was promoted.
- Confirmed that True versus Mean Node materially changes 19 of 24 north-node activations in the
  synthetic set; retained the node convention as unresolved.
- Recorded continuous motor-to-Throat graph semantics, connected-component Definition probes,
  Authority branch requirements, Profile rule and current coverage gaps.
- Added the missing [[human-design-verification]] evidence/quality record and Proposed ADR-015.
- Kept `accepted_expectations` empty, Stage 9A incomplete and Stage 9B not ready. No production
  Human Design engine, endpoint, frontend change or dependency was added.

## 2026-09-18 — Stage 8 deterministic numerology

- Added pure Pythagorean numerology service, request/response models and `/api/v1/numerology/calculate`.
- Defined Turkish normalization, AEIOU/Y policy, master reductions and explicit nullable target year.
- Shared the existing future-birth-date validation rule; numerology API uses an injectable admission clock.
- Added 117 synthetic unit/API tests; all 584 Docker backend tests pass, pip check clean.
- Documented formulas, privacy and limitations in [[numerology]] and ADR-014.
- Frontend, astrology/timezone algorithms and reference fixtures unchanged; no new dependencies.
- Stage 9 — Human Design is next and has not started. Sanitized-baseline fixture policy is preserved.

## 2026-09-18 — Synthetic fixture privacy migration

- Replaced nine historical birth cases with synthetic calendar/season examples and coarse coordinates.
- Refreshed four JPL DE441 and nine external swetest outputs, hashes, query provenance and reference records.
- Sanitized the named backend profile sample, provider mocks and timezone documentation example.
- Independently checked timezone expectations against pinned IANA data; Docker: 467 tests pass, pip check clean.
- Added synthetic-only fixture policy and ADR-013. Production/frontend code and Stage 8 are unchanged.
- Public baseline contains synthetic fixtures only and no prior private Git history.

## 2026-09-18 — Docker development environment

- Added Compose development services for Python 3.11 backend and Node 22 frontend with bind mounts,
  frontend dependency/build volumes and healthchecks.
- Made Docker Compose the preferred reproducible local workflow; host Python/Node steps remain fallback.
- Documented Docker commands, environment ownership, cold-reset caution and OneDrive bind-mount advice.

## 2026-09-17 — Stage 7 astrology verification

- Added nine externally sourced JPL/swetest reference records, raw evidence, hashes and provenance.
- Verified Moshier Sun/Moon/Mercury/Jupiter, ASC/MC, twelve cusps, speeds and body placement.
- Corrected projected house placement to native longitude+latitude house_pos; seven changes across six cases.
- Made native initialization explicit and serialized; fixed extra-field/malformed-body error codes.
- Added 340 tests; 467 tests pass and pip check is clean. Reference tests are offline.
- Recorded bounded verification scope and shared Swiss algorithm limitation in [[astrology-verification]].
- Stage 8 remains unstarted; frontend and production dependency versions unchanged.

## 2026-09-17 — Stage 6 deterministic astrology engine

- Added Swiss Ephemeris/pyswisseph service, schemas and calculation endpoint; canonical Tropical,
  Placidus, True Node and Mean Black Moon Lilith conventions, explicit Moshier mode.
- Added body positions, angles, cusp-based house placement, retrograde and major aspects.
- Added 76 tests; all 127 backend tests and pip check pass in Python 3.11.9 `.venv-stage6`.
- Preserved independent reference fixtures; Stage 7 verification has not started.
- Verified upstream licenses/notices and documented Windows Python 3.12 compiler limitation.
- Frontend unchanged.

## 2026-09-16 — AGPL-3.0 licensing

- Added the standard GNU Affero General Public License v3.0 text at the repository root.
- Documented the accepted license decision, dependency-compatibility rule and Stage 6 Swiss
  Ephemeris AGPL path.

## 2026-09-16 — Project Memory / Obsidian setup

- Added root `AGENTS.md`, project-memory index documents and Obsidian-compatible docs structure.
- Added Mermaid architecture and roadmap diagrams, current-state handoff and decisions log.
- Added source maps for existing documentation; application behavior did not change.

## 2026-09-16 — Stage 6 regression fixture preparation

- Centralized anonymous birth cases for historical timezone and future astrology regression.
- Added an empty, provenance-first astrology reference record schema.
- Documented independent-reference and circular-testing rules.

## Milestones

- **Stage 1:** project foundation.
- **Stage 2:** frontend design system and birth form.
- **Stage 3:** frontend to FastAPI birth-profile validation.
- **Stage 3.5:** Yaklaşım content page.
- **Stage 4:** backend geocoding service.
- **Stage 5:** offline IANA timezone and historical UTC conversion.
