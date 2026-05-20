Phase E Backend Truth Ownership Preservation Rules
Purpose

This document preserves the central EPIC 33 doctrine that backend systems remain the sole source of product truth during Phase E.

Core Rule

Phase E backend binding must reveal backend-governed truth.

It must never relocate truth ownership into the frontend.

Backend Owns

The backend remains the authority for:

review state
evidence state
correction acceptance state
finalized truth
export readiness
permission enforcement
trust-relevant operational decisions
Frontend May

The Pilot UI may:

render backend-returned facts
route between views
display loading, unavailable, empty, and error states
present bounded operator actions
communicate contract-backed operational posture
Frontend May Not

The Pilot UI may not:

manufacture truth
synthesize readiness verdicts
infer permission decisions
invent trust outcomes
convert placeholders into product states
present fallback content as backend fact
compute finalized truth semantics locally
redefine correction or export semantics
Traceability Requirement

Each backend-bound UI state must be traceable to:

a backend contract or endpoint
one or more returned fields
a defined unavailable pathway
a defined error pathway
No Frontend Truth Rewrite

Phase E is not permission to reinterpret the product model in Base44.

It is permission to expose backend truth through controlled Pilot UI surfaces.

Governing Statement

Frontend must never manufacture truth. Phase E does not weaken this rule; it applies this rule under real backend binding pressure.
