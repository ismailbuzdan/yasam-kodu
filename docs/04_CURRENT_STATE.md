---
tags:
  - memory/core
---

# Current State

**Last updated:** 2026-09-18
**Current stage:** Stage 7 completed (nine-case verification scope)
**Next stage:** Stage 8 — Numerology
**License:** AGPL-3.0
**Development environment:** Docker Compose available and preferred; host workflows remain a fallback.

## AI Handoff

Before coding:

- Read `AGENTS.md`, this file, [[03_ROADMAP]], [[07_TEST_STRATEGY]] and task-specific docs.

After coding:

- Update this file, decisions and changelog when applicable; run relevant tests.

## Completed

Stages 1, 2, 3, 3.5, 4, 5, 6 and 7. Backend: 467 tests passed and `pip check` successful
in the Docker Compose Python 3.11 backend after the synthetic-fixture migration. See [[astrology]] for installation and conventions.
Frontend: unchanged; last recorded lint, typecheck, 8/8 tests and production build pass.

Git: public sanitized baseline. This repository contains no prior private Git history.

**Current blockers:** None.
Tracked fixtures are synthetic and must remain synthetic.

**Astrology:** Moshier retained. Nine synthetic external reference records; JPL astronomy and external swetest
integration verified. Native house_pos now uses latitude, initialization is explicit, and unexpected
request fields have a correct domain code. See [[astrology-verification]] for evidence and limits.
The existing Python 3.12 `.venv` lacks pyswisseph: use Python 3.11 or install a C++ build toolchain.

**Known non-blocking warnings:** FastAPI/Starlette test dependencies emit deprecation warnings;
pytest cache can warn under OneDrive file permissions. See [[10_KNOWN_ISSUES]].

Project history: [[CHANGELOG]].

**Next task:** Stage 8 — Numerology (not started). Continue to require external provenance for references.
AI interpretation, Human Design and PDF remain future stages.
