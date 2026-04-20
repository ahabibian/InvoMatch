# EPIC 24 Implementation Plan

## 1. Phase Order

EPIC 24 should be implemented in the following order:

1. document the architecture
2. introduce centralized config models
3. introduce environment selection
4. introduce config validation
5. extract dependency factories
6. refactor main.py into a thin startup boundary
7. introduce Docker packaging files
8. add startup validation tests
9. rerun required permanent scenarios
10. write closure documentation

---

## 2. Phase A — Configuration Layer

Create:

- src/invomatch/config/__init__.py
- src/invomatch/config/models.py
- src/invomatch/config/defaults.py
- src/invomatch/config/environment.py
- src/invomatch/config/loaders.py
- src/invomatch/config/settings.py
- src/invomatch/config/validation.py

Goal:

- move runtime-critical defaults out of scattered services

---

## 3. Phase B — Bootstrap Layer

Create:

- src/invomatch/bootstrap/app_factory.py
- src/invomatch/bootstrap/persistence_factory.py
- src/invomatch/bootstrap/storage_factory.py
- src/invomatch/bootstrap/runtime_factory.py
- src/invomatch/bootstrap/validation_factory.py

Goal:

- centralize dependency construction
- reduce direct construction inside main.py

---

## 4. Phase C — main.py Refactor

Refactor main.py so that it:

- loads settings
- validates startup state
- builds dependencies via factories
- creates the app
- wires routes
- optionally starts scheduler behavior

Goal:

- make startup deterministic and inspectable

---

## 5. Phase D — Packaging Boundary

Create:

- Dockerfile
- .dockerignore
- update .env.example

Goal:

- introduce deterministic packaging
- align runtime directories with config model

---

## 6. Phase E — Tests

Add tests for:

- settings loading
- environment profile selection
- startup validation
- path isolation
- factory behavior
- production-safe defaults

Goal:

- prevent config drift and startup regressions

---

## 7. Phase F — Scenario Re-Runs

Re-run:

- Scenario 1
- Scenario 4
- Scenario 6
- Scenario 7

Goal:

- verify startup and runtime refactor did not break product behavior

---

## 8. Completion Rule

Do not mark EPIC 24 complete before:

- config is centralized
- startup is fail-fast
- Docker packaging exists
- required scenarios remain green
- closure doc matches actual repo state