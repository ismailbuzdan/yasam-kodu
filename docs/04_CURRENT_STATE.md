---
tags:
  - memory/core
---

# Current State

**Last updated:** 2026-09-19
**Current stage:** Stage 10A complete — Unified deterministic Life Code internal model/service complete
**Next stage:** Stage 10B API ready for separate scoping/authorization; not implemented
**License:** AGPL-3.0
**Development environment:** Docker Compose available and preferred; host workflows remain a fallback.

## AI Handoff

Before coding:

- Read `AGENTS.md`, this file, [[03_ROADMAP]], [[07_TEST_STRATEGY]] and task-specific docs.

After coding:

- Update this file, decisions and changelog when applicable; run relevant tests.

## Completed

Stages 1, 2, 3, 3.5, 4, 5, 6, 7, 8, 9A and 9B (Human Design mechanical core + API).
Stage 10A internal aggregation is also complete (Stage 10B API remains unimplemented).
Backend: 835 tests passed (789 Stage 9 baseline + 46 Life Code service tests),
two existing warnings, and `pip check` successful in Docker.
See [[astrology]] and [[numerology]] for installation and conventions.
Frontend: unchanged; last recorded lint, typecheck, 8/8 tests and production build pass.

Git: public sanitized baseline. This repository contains no prior private Git history.

**Current blockers:** None for Stage 9B semantic readiness. Unknown proprietary internals are
non-blocking for scoped behavioral references. Official exact equality remains unobserved;
the project explicitly owns its deterministic tie-break. Human Design frontend remains future work.
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

**Unified Life Code:** Stage 10A adds frozen internal input/metadata/result and sequential one-call
orchestration of existing Astrology, Numerology and Human Design engines. Original typed outputs
are retained without field loss or recalculation. User-selected immutability is shallow: the frozen
envelope retains mutable Astrology/Numerology children; consumers must treat them as read-only.
Calendar birth date/name/target year belong to Numerology; the same resolved UTC goes to Astrology
and HD, and coordinates only to Astrology. No name in output/logs/errors; safe input errors reuse
request validation, while engine domain type/code/message remain intact. No HTTP endpoint, clock,
network, provider, interpretation or persistence. ADR-016 accepted; [[life-code]] documents boundaries.
Docker: 46 new tests, 416 Astrology, 117 Numerology, 205 HD and full 835 pass; pip check/audit clean.

**Human Design:** Stage 9B.1A production astronomy core exists: immutable activations, UTC/UT1
conversion, True Node/oppositions, exact 88° solver and rational Gate/Line mapping. It reuses the
existing Astrology native lock/initialization without changing Astrology code. Stage 9B.1B adds
active-gate union, channels, centers/components, Type/Strategy/Authority/Definition/Profile and
immutable complete result/metadata. `calculate_human_design_core(birth_utc)` computes astronomy once.
All 18 structural vectors and all 14 official classifications match. Stage 9B.2 exposes
`POST /api/v1/human-design/calculate` with strict UTC-only request, typed mechanical response,
injectable future-instant admission and private 422/503 errors. Seven official API representatives
cover all five Types and rare Authorities. No core/convention/Astrology/Numerology changes.
Frontend not implemented. OpenAPI/CORS unchanged; no new dependency, logs or persistence.
Raw candidates remain byte-preserved. Schema-2 `accepted_expectations` separately promotes 14
official behavioral snapshots (364 Gate/Line values plus Type/Authority/Definition/Profile), not
longitude or Design timestamps. ADR-015 unchanged; all 364 accepted activation values match core output.
True Node and 302° wheel are RESOLVED project choices based on official behavior, not claims of a
published precise official algorithm. `[start,end)` is a project tie-break. All 68 raw artifacts
and original audit checks are unchanged. Tests cover 384 boundary neighborhoods and 18 graph probes.
Official splenic and 3/5 examples remain absent; structural coverage is sufficient for readiness. See
[[human-design]] and [[human-design-verification]].

**Next task:** Separately scope and authorize Stage 10B API/admission contract. Stage 10A internal
aggregation is complete; Stage 10B API not implemented, Stage 11 AI and Stage 12 PDF not started.
No frontend/database work. Engine conventions, original goldens and all 68 HD artifacts are unchanged.
