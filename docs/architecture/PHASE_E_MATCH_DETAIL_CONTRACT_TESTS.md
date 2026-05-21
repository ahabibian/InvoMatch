Phase E Match Detail Contract Tests

Mini-EPIC: 33.13

Purpose

This document defines contract-test expectations for Match Detail / Evidence backend readiness.

Required Test Coverage

Contract tests must prove:

detail retrieval by match_id works
payload includes backend-owned evidence
payload includes backend-owned traceability
match not found is distinguishable
missing evidence is distinguishable
unavailable evidence is distinguishable
malformed or incomplete payload is distinguishable
backend error is distinguishable
response shape is stable
frontend truth synthesis is not required
Closure Constraint

Mini-EPIC 33.13 cannot close unless contract-test expectations are documented and implementation evidence is available or explicitly bounded.
