---
tags:
  - memory/core
---

# Current State

**Last updated:** 2026-09-19
**Current stage:** Stage 8 completed; Stage 9A Human Design convention research in progress
**Next stage:** Complete Stage 9A evidence; Stage 9B is not ready
**License:** AGPL-3.0
**Development environment:** Docker Compose available and preferred; host workflows remain a fallback.

## AI Handoff

Before coding:

- Read `AGENTS.md`, this file, [[03_ROADMAP]], [[07_TEST_STRATEGY]] and task-specific docs.

After coding:

- Update this file, decisions and changelog when applicable; run relevant tests.

## Completed

Stages 1, 2, 3, 3.5, 4, 5, 6, 7 and 8. Backend: 589 tests passed (584 Stage 8 baseline
+ 5 Stage 9A research-integrity tests) and `pip check` successful in the Docker Compose Python 3.11 backend.
See [[astrology]] and [[numerology]] for installation and conventions.
Frontend: unchanged; last recorded lint, typecheck, 8/8 tests and production build pass.

Git: public sanitized baseline. This repository contains no prior private Git history.

**Current blockers:** Stage 9A lacks public original-system precision for the exact gate-wheel anchor
and True/Mean Node convention, a second trusted complete chart export, and rare branch coverage.
Tracked fixtures are synthetic and must remain synthetic.

**Astrology:** Moshier retained. Nine synthetic external reference records; JPL astronomy and external swetest
integration verified. Native house_pos now uses latitude, initialization is explicit, and unexpected
request fields have a correct domain code. See [[astrology-verification]] for evidence and limits.
The existing Python 3.12 `.venv` lacks pyswisseph: use Python 3.11 or install a C++ build toolchain.

**Known non-blocking warnings:** FastAPI/Starlette test dependencies emit deprecation warnings;
pytest cache can warn under OneDrive file permissions. See [[10_KNOWN_ISSUES]].

Project history: [[CHANGELOG]].

**Numerology:** Pure Pythagorean calculation endpoint, Turkish normalization, explicit nullable target
year and hand-calculated synthetic golden vectors. Future-date validation is outside the service,
using a shared BirthProfile rule and injectable API clock. Names are not echoed, logged or stored.

**Human Design:** Stage 9A research-only fixtures/tools exist; no production engine or endpoint.
Stored candidates remain `candidate_not_approved`, `accepted_expectations` is empty, ADR-015 is
Proposed, Stage 9A is incomplete and Stage 9B is not ready. The 19 mapper differences are explained
by a fixed 2.5-arcminute offset, while True/Mean Node remains materially unresolved. See
[[human-design]] and [[human-design-verification]].

**Next task:** Obtain trusted convention evidence and missing synthetic reference coverage without
promoting engine output by vote. AI interpretation, production Human Design and PDF remain future work.
