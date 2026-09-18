---
tags:
  - memory/quality
---

# Known Issues

## OneDrive Docker bind mounts

**Severity:** low
**Status:** documented recommendation
**Impact:** Docker isolates dependencies, but OneDrive synchronization of bind-mounted source files can
still cause file locks, watcher misses or slower reloads on Windows.
**Next action:** if this disrupts development, use a non-synced location such as `C:\Projects\yasam-kodu`.
This is a recommendation, not a requirement.

## Windows Python 3.12 pyswisseph installation

**Severity:** medium
**Status:** local environment limitation; validated alternative available
**Impact:** pyswisseph 2.10.3.2 has no Python 3.12 Windows wheel; source compilation requires C++ tools
absent from the current machine. The original `.venv` cannot run the new endpoint yet.
**Next action:** use Python 3.11 with the published wheel, as verified in `.venv-stage6`, or provision
a compatible C++ build toolchain. See [[astrology]].

## Third-party test warnings

**Severity:** low
**Status:** known, non-blocking
**Impact:** FastAPI/Starlette test dependencies produce deprecation warnings.
**Next action:** review when their compatible releases change.

## OneDrive test cache permissions

**Severity:** low
**Status:** known, non-blocking
**Impact:** pytest cache can report a file-permission warning under OneDrive.
**Next action:** use a non-synced workspace if locks become disruptive.

## Geocoding provider network dependency

**Severity:** medium
**Status:** known
**Impact:** Nominatim availability, network access and its policy affect live location resolution.
**Next action:** preserve backend abstraction and provider mocks; assess production provider policy.

## Timezone polygon scope

**Severity:** low
**Status:** documented limitation
**Impact:** timezonefinder polygons do not recreate historical political-boundary changes.
**Next action:** evaluate boundary-sensitive or historical cases separately.
