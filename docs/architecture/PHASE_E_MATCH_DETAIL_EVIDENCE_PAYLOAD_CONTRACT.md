Phase E Match Detail Evidence Payload Contract

Mini-EPIC: 33.13

Purpose

This document defines the backend-owned evidence payload boundary for Match Detail.

Evidence Payload Requirements

Evidence payload must be:

backend-owned
structured
display-safe
linked to match_id
stable enough for product-facing UI display
free from frontend-generated calculations
Frontend Constraint

The frontend may display evidence but must not generate, calculate, merge, reinterpret, or invent evidence.
