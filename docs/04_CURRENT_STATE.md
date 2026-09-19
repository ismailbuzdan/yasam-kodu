---
tags:
  - memory/core
---

# Current State

**Last updated:** 2026-09-19
**Current stage:** Stage 9B.1A complete — HD astronomy, 88° solver and Gate/Line mapper
**Next stage:** Stage 9B.1B ready, not started; API not implemented
**License:** AGPL-3.0
**Development environment:** Docker Compose available and preferred; host workflows remain a fallback.

## AI Handoff

Before coding:

- Read `AGENTS.md`, this file, [[03_ROADMAP]], [[07_TEST_STRATEGY]] and task-specific docs.

After coding:

- Update this file, decisions and changelog when applicable; run relevant tests.

## Completed

Stages 1, 2, 3, 3.5, 4, 5, 6, 7, 8 and 9A (specification/reference qualification only).
Backend: 641 tests passed (584 Stage 8 baseline + 11 Stage 9A integrity + 46 HD core tests),
two existing warnings, and `pip check` successful in Docker.
See [[astrology]] and [[numerology]] for installation and conventions.
Frontend: unchanged; last recorded lint, typecheck, 8/8 tests and production build pass.

Git: public sanitized baseline. This repository contains no prior private Git history.

**Current blockers:** None for Stage 9B semantic readiness. Unknown proprietary internals are
non-blocking for scoped behavioral references. Official exact equality remains unobserved;
the project explicitly owns its deterministic tie-break. Graph/classification and API remain future work.
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

**Human Design:** Stage 9B.1A production astronomy core exists: immutable activations, UTC/UT1
conversion, True Node/oppositions, exact 88° solver and rational Gate/Line mapping. It reuses the
existing Astrology native lock/initialization without changing Astrology code. No graph,
Type/Authority/Definition/Profile or API/frontend implementation. Stage 9B.1B not started.
Raw candidates remain byte-preserved. Schema-2 `accepted_expectations` separately promotes 14
official behavioral snapshots (364 Gate/Line values plus Type/Authority/Definition/Profile), not
longitude or Design timestamps. ADR-015 unchanged; all 364 accepted activation values match core output.
True Node and 302° wheel are RESOLVED project choices based on official behavior, not claims of a
published precise official algorithm. `[start,end)` is a project tie-break. All 68 raw artifacts
and original audit checks are unchanged. Tests cover 384 boundary neighborhoods and 18 graph probes.
Official splenic and 3/5 examples remain absent; structural coverage is sufficient for readiness. See
[[human-design]] and [[human-design-verification]].

**Next task:** Separately authorize Stage 9B.1B graph/classification work. The API, frontend,
AI interpretation and PDF are not implemented by Stage 9B.1A.
