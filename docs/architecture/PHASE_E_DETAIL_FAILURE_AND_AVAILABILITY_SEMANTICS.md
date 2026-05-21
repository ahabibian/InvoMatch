
Phase E Detail Failure and Availability Semantics
Purpose

This document defines failure and availability semantics for Match Detail / Evidence.

Required States

The Match Detail / Evidence product-facing contract must distinguish the following states:

found
not found
missing evidence
unavailable evidence
malformed or incomplete detail payload
backend error
Not Found

Not found means the requested match_id does not resolve to a product-facing match detail record.

Frontend posture:

show a bounded not-found state
do not reconstruct detail from Review Queue
do not display stale detail
do not claim evidence exists
Missing Evidence

Missing evidence means the match detail exists, but expected evidence is not present in the product-facing payload.

Frontend posture:

show match detail with an explicit missing-evidence warning only if the backend marks the detail as displayable
do not invent evidence
do not hide the missing-evidence state
do not use explanation as a substitute for evidence
Unavailable Evidence

Unavailable evidence means evidence exists conceptually or historically but is not currently retrievable or not exposed through the product-facing contract.

Frontend posture:

show unavailable-evidence state
preserve backend wording or status
do not treat unavailable evidence as missing proof
do not treat unavailable evidence as successful evidence
Malformed or Incomplete Detail Payload

Malformed or incomplete detail payload means the backend response cannot safely support Match Detail display.

Frontend posture:

show bounded technical failure state
do not partially reconstruct the detail page
do not combine Review Queue data with partial detail data to create a complete-looking page
Backend Error

Backend error means the read path failed.

Frontend posture:

show backend-error state
provide retry affordance only if allowed by the UI design boundary
do not cache or invent successful detail state
do not continue into correction or finalization workflows
Availability Rule

Availability is backend-owned.

The frontend may display availability states but must not decide whether evidence is complete, sufficient, authoritative, or final.
