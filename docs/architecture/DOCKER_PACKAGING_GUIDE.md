# Docker Packaging Guide

## 1. Purpose

This document defines the Docker packaging boundary for InvoMatch.

The goal is deterministic packaging, not advanced orchestration.

---

## 2. Packaging Principles

Docker packaging must provide:

- deterministic dependency installation
- explicit runtime working directory
- explicit environment selection
- explicit runtime startup command
- support for mounted persistence volumes
- production-safe defaults

---

## 3. Required Files

Required packaging files:

- Dockerfile
- .dockerignore
- .env.example

Optional later:

- docker-compose.local.yml
- docker-compose.staging.yml

Those optional files are convenience layers, not the primary architecture boundary.

---

## 4. Image Responsibilities

The Docker image must:

- install application dependencies reproducibly
- copy only required application files
- expose runtime through a deterministic startup command
- allow environment selection via environment variables
- avoid hidden dependence on host-specific paths

---

## 5. Runtime Directories

Expected container runtime directories:

- /app/data
- /app/storage
- /app/logs
- /app/tmp

These directories must map to configuration values, not hardcoded assumptions buried inside services.

---

## 6. Startup Command

The startup command must be environment-aware and deterministic.

Example target:

- uvicorn invomatch.main:app --host 0.0.0.0 --port 8000

Any environment-specific behavior must come from configuration, not different code branches.

---

## 7. Persistence Expectations

Docker containers are ephemeral.

Therefore durable state must not rely on container lifetime.

Durable data must be stored in mounted directories for:

- sqlite databases
- artifact storage
- upload storage
- logs if required

---

## 8. Production Safety

Docker production defaults must ensure:

- debug disabled
- environment explicitly set
- deterministic writable paths
- no accidental local development paths
- explicit startup validation
- stable dependency installation

---

## 9. Non-Goals

This guide does not include:

- Kubernetes
- autoscaling
- distributed workers
- secrets platform integration
- cloud vendor deployment recipes

Those are outside EPIC 24.

---

## 10. Design Rule

Docker is a deployment packaging boundary.

It must reflect the configuration architecture, not bypass it.