Phase E Match ID Retrieval Contract

Mini-EPIC: 33.13

Purpose

This document defines the stable retrieval path from Review Queue to Match Detail.

Required Retrieval Path

Review Queue
-> stable match_id
-> product-facing Match Detail retrieval
-> backend-owned evidence payload
-> backend-owned traceability payload
-> explicit failure semantics

Contract Rule

The Match Detail endpoint must accept the same stable match_id exposed by the Review Queue.

Forbidden Fallbacks

The frontend must not reconstruct detail state from invoice_id.
The frontend must not reconstruct detail state from payment_id.
The frontend must not infer match identity from row position, display labels, or local UI state.
