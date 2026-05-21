Phase E Match Detail Failure Semantics Contract

Mini-EPIC: 33.13

Purpose

This document defines failure semantics required for product-facing Match Detail / Evidence retrieval.

Required Failure States

The backend must distinguish:

match not found
missing evidence
unavailable evidence
malformed or incomplete payload
backend error
UI Responsibility

The UI may display backend failure state.
The UI must not synthesize failure semantics from generic errors or missing fields.

Contract Principle

Failure semantics are backend-owned product truth.
