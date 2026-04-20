# Startup Validation Policy

## 1. Purpose

This document defines the startup validation rules for InvoMatch.

The goal is to ensure the application fails early and clearly when critical runtime dependencies are unavailable or invalid.

---

## 2. Principle

Startup must not partially succeed.

If critical configuration or storage dependencies are invalid, the application must fail before becoming available.

---

## 3. Validation Scope

Startup validation must verify:

- environment value is valid
- persistence backends are valid
- persistence directories are valid
- sqlite directories are writable when sqlite is enabled
- storage root exists or can be created
- artifact storage is writable
- temp directory is valid
- log directory is valid
- scheduler configuration is valid
- lease and retry settings are valid
- startup repair configuration is valid
- feature flags are dependency-compatible

---

## 4. Validation Categories

### Configuration Validation

Checks:

- required settings present
- enum values valid
- numeric values bounded
- incompatible combinations rejected

### Path Validation

Checks:

- directory paths resolvable
- parent directories creatable
- writable filesystem access available where required
- forbidden shared paths rejected

### Dependency Validation

Checks:

- enabled backends supported by runtime
- startup repair compatible with configured persistence
- scheduler dependencies constructible
- storage dependencies constructible

---

## 5. Failure Behavior

If validation fails:

- startup must fail
- a clear exception must be raised
- the failure reason must identify the invalid subsystem
- partial app wiring is not acceptable

---

## 6. Validation Result Model

A validation result model may include:

- is_valid
- errors
- warnings
- selected_environment
- resolved_paths
- enabled_features

Warnings may be logged, but errors must block startup.

---

## 7. Production Rules

Production must apply stricter validation than local execution.

Production-specific enforcement includes:

- no relative persistence roots
- no debug defaults
- no unbounded retry budgets
- no disabled startup validation
- no unsafe temp directory usage

---

## 8. Test Rules

Tests may override startup validation only in explicitly controlled cases.

Disabling validation in tests must not change production startup rules.

---

## 9. Startup Order

Recommended startup order:

1. load raw settings
2. resolve environment profile defaults
3. build final settings object
4. validate settings
5. validate paths
6. validate dependency compatibility
7. build dependencies
8. create app
9. attach routes
10. start scheduler if enabled

Validation must occur before dependency graph activation.

---

## 10. Operational Consequence

A deployable system must fail clearly when invalid.

Silent fallback startup behavior is forbidden for critical deployment dependencies.