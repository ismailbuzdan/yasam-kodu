---
tags:
  - memory/core
---

# Current State

**Last updated:** 2026-09-20
**Current stage:** Stage K1A Kamerî deterministic core complete on stage-k1a-kameri-core; K0 complete
**Next step:** Separately authorize K1B API; Stage 11 AI NOT STARTED, PDF NOT STARTED
**License:** AGPL-3.0
**Development environment:** Docker Compose available and preferred; host workflows remain a fallback.

## AI Handoff

Before coding:

- Read `AGENTS.md`, this file, [[03_ROADMAP]], [[07_TEST_STRATEGY]] and task-specific docs.

After coding:

- Update this file, decisions and changelog when applicable; run relevant tests.

## Completed

**Stage K1A (2026-09-20):** Preserved/resumed dirty WIP at `d4e62c0f4ed0cfeefd1227d81b6b5f14abe32354`
on `stage-k1a-kameri-core`. Added five mechanical methods in an isolated `traditional` service package,
frozen results, fixed private domain errors, exact rational phase/sector/hour boundary tests,
confirmed-script normalization/privacy, existing-lock native callers and pinned-zone reuse.
No existing engine, schema, API, frontend, dependency or original evidence changes. ADR-017 unchanged.
Docker targeted: Hijri 41, abjad 116, lunar 77, planetary hours 217, concurrency 1, references 12:
**464 passed**. Existing Astrology/HD/Life Code regression **756 passed**. Full backend **1388 passed**,
only the **2 existing dependency warnings**; pip check clean; HD read-only evidence audit **68/68**.
Ten new evidence artifacts with receipts/hashes: 2 JPL, 3 shared swetest rise/set, 1 separate remote
version capture, 3 approximate USNO rise/set, 1 short published-calendar excerpt file. Scope is narrow:
two calendar correspondences, four JPL instants and three solar dates, not full-range external accuracy.
See [[kameri-verification]]. K1A complete; K1B API ready for separate scoping, NOT STARTED.
Stage 11 NOT STARTED. No main merge; no automatic script rendering, mansion names or interpretation.

**Stage K0 (docs/research only, 2026-09-20):** [[kameri-code]] and
[[kameri-source-qualification]] define five scoped methods, 19 source records (A:9/B:8/C:2),
claim-to-source limits, normalization, boundary ownership and deferred traditions. ADR-017 accepted
for these project boundaries. K1 methodological readiness is limited to tabular date, Moon,
numeric equal-sector mansion index, confirmed-Arabic abjad and seasonal planetary hour.
Arabic mansion labels are proposed/unverified against an Arabic edition; automatic transcription,
stellar reconstruction and interpretations remain unqualified/deferred. No K1 code, API, frontend,
dependency, AI or Life Code v1 modification. Stage 10 main start verified at
`6250d347af39da04291af7412521664532a03363`; work is on `stage-k0-kameri-methodology`.
K0 validation passed: JSON metadata/unique IDs/tier counts/claim references, local wiki links,
28 sequential proposed labels and docs-only changed-path checks; `git diff --check` clean.
These are document checks, not new runtime accuracy measurements.
The 924 backend / 8 frontend baseline below is prior Stage 10 qualification, not a K0 rerun.

Stages 1, 2, 3, 3.5, 4, 5, 6, 7, 8, 9A and 9B (Human Design mechanical core + API).
Stage 10A internal aggregation and Stage 10B API are complete.
Backend: 924 tests passed (789 Stage 9 baseline + 46 Life Code service + 89 Life Code API tests),
two existing warnings, and `pip check` successful in Docker.
See [[astrology]] and [[numerology]] for installation and conventions.
Frontend: unchanged; Docker lint, typecheck, 8/8 tests and production build rerun successfully
during Stage 10B qualification. Next.js regenerated its dev import paths on startup; the normal
production build regenerated the tracked production paths. Final frontend diff is empty.

Git: public sanitized baseline. This repository contains no prior private Git history.

**Current blockers:** None for Stage 9B semantic readiness. Unknown proprietary internals are
non-blocking for scoped behavioral references. Official exact equality remains unobserved;
the project explicitly owns its deterministic tie-break. Human Design frontend remains future work.
Tracked fixtures are synthetic and must remain synthetic.

**Stage 10B verification:** Docker availability restored by the user; preserved WIP resumed without
reset/restore/stash/deletion. Targeted API 89, Stage 10A 46, standalone API-containing suites 246,
full backend 924 tests pass, with only the two existing warnings. `pip check` clean; read-only
HD audit verifies 68/68 artifacts and unchanged comparison metrics. No remaining Stage 10 blocker.

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
request validation, while engine domain type/code/message remain intact. The service has no HTTP endpoint, clock,
network, provider, interpretation or persistence. ADR-016 accepted; [[life-code]] documents boundaries.
Docker: 46 new tests, 416 Astrology, 117 Numerology, 205 HD and full 835 pass; pip check/audit clean.

Stage 10B completes strict resolved-input transport and composed public engine responses at
`POST /api/v1/life-code/calculate`, with shared standalone-HD public projection and static errors.
UTC admission and the existing Numerology server-calendar policy are separately injectable; calendar
date is never derived from UTC. Engine/service/internal-model code and existing schemas are unchanged.
All 89 API tests pass, covering privacy, diagnostics exclusion, standalone equivalence, dates,
errors and concurrency. See [[life-code]] and [[06_API_CONTRACTS]]. Unified result frontend UI is not implemented.

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

**Next step:** Separately scope and authorize K1B's public contract for the completed five-method core.
Automatic name suggestions, mansion name publication and interpretation require additional qualification.
Stage 10A, Stage 10B and Stage 10 complete;
Unified Life Code API complete. Stage 11 AI NOT STARTED; Stage 12 PDF NOT STARTED.
No frontend/database work. Engine conventions, original goldens and all 68 HD artifacts are unchanged.
