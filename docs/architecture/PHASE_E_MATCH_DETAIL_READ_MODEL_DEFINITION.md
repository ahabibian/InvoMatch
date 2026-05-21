Phase E Match Detail Read Model Definition

Mini-EPIC: 33.13

Purpose

This document defines the expected Match Detail read model / DTO boundary.

Required Fields

The product-facing Match Detail read model must be backend-owned and may include:

match_id
invoice summary
payment summary
match status or posture
confidence or score if backend-owned
explanation if backend-owned
evidence items
traceability fields
source references
audit-safe identifiers
Frontend Constraint

The frontend must not construct match truth from invoice fragments, payment fragments, evidence signals, or local assumptions.

Non-Actions

No Base44 binding is authorized here.
No frontend truth synthesis is authorized here.
