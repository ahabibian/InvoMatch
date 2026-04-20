# EPIC 24 Test Strategy

## 1. Purpose

This document defines the validation strategy for EPIC 24.

The focus is environment safety, startup correctness, deterministic configuration loading, and regression protection.

---

## 2. Test Categories

### Configuration Tests

Validate:

- valid settings load correctly
- invalid enum values fail
- invalid numeric values fail
- missing required values fail where appropriate
- environment defaults resolve deterministically

### Environment Tests

Validate:

- local profile behavior
- development profile behavior
- test profile behavior
- staging profile behavior
- production profile behavior
- isolation between environments

### Validation Tests

Validate:

- invalid paths fail startup validation
- unwritable sqlite directory fails validation
- invalid scheduler config fails validation
- invalid feature flag combinations fail validation
- production unsafe defaults are rejected

### Bootstrap Tests

Validate:

- persistence factory selects correct backends
- storage factory resolves correct paths
- runtime factory builds expected dependencies
- app factory wiring remains deterministic

### Startup Tests

Validate:

- startup succeeds with valid config
- startup fails with invalid config
- startup fails clearly on invalid path setup
- startup behavior changes only through config inputs

---

## 3. Suggested Test Files

Suggested additions:

- tests/config/test_settings_loading.py
- tests/config/test_environment_profiles.py
- tests/config/test_validation.py
- tests/bootstrap/test_persistence_factory.py
- tests/bootstrap/test_storage_factory.py
- tests/bootstrap/test_runtime_factory.py
- tests/test_app_startup_validation.py
- tests/test_app_environment_isolation.py
- tests/test_production_safe_defaults.py

---

## 4. Required Scenario Re-Runs

The following system scenarios are mandatory before closure:

- Scenario 1 — Happy Path Full Flow
- Scenario 4 — Runtime Failure Terminalization
- Scenario 6 — Restart Recovery Consistency
- Scenario 7 — Startup Repair Visibility & Recovery Alignment

These scenario reruns are required because EPIC 24 changes startup and runtime wiring.

---

## 5. Acceptance Standard

EPIC 24 test validation is sufficient only if:

- new configuration coverage exists
- startup validation is explicitly tested
- environment isolation is explicitly tested
- required permanent scenarios stay green