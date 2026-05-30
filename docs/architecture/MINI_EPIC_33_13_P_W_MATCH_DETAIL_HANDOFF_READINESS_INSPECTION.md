
Mini-EPIC 33.13.P-W — Match Detail Handoff Readiness Inspection
Status

Inspection complete.

Mini-EPIC 33.13.P-W is an inspection-only readiness boundary after P-V closure.

This document defines the next safe Match Detail handoff boundary. It does not implement Match Detail loading. It does not change backend contracts. It does not change ReviewQueuePage.tsx. It does not claim Scenario 15 completion. It preserves the rule that Review Queue passes only match_id.

Objective

Inspect and define the next safe Match Detail handoff boundary after P-V closure.

The inspection verifies:

how the App shell currently captures the match_id handed off from Review Queue,
how Review Queue currently passes the handoff identifier,
whether a frontend Match Detail surface/client already exists,
what backend API dependency the later controlled implementation must use,
what minimum safe path is authorized for the next mini-epic.
Hard Boundaries

P-W did not perform implementation.

P-W did not modify ReviewQueuePage.tsx.

P-W did not change backend contracts.

P-W did not introduce Match Detail loading.

P-W did not introduce a frontend Match Detail page.

P-W did not introduce a frontend Match Detail service function.

P-W did not synthesize Match Detail data in the frontend.

P-W did not pass full Review Queue row payloads.

P-W did not bind Base44 to new behavior.

P-W did not claim Scenario 15 completion.

Review Queue passes only match_id.

Evidence Summary
Repository state

The inspection was performed from a clean working tree.

The final inspection confirmed that the working tree remained clean after the read-only evidence inspection.

App shell handoff capture

The App shell imports ReviewQueuePage and keeps a selectedReviewMatchId state value.

Observed App shell evidence:

App.tsx imports ReviewQueuePage.
App.tsx defines selectedReviewMatchId.
App.tsx defines openMatchFromReviewQueue(matchId: string).
openMatchFromReviewQueue stores only the incoming matchId.
ReviewQueuePage is rendered with onOpenMatch={openMatchFromReviewQueue}.
The App shell currently displays a readiness message that the selected Review Queue match_id has been captured and that Match Detail loading is not validated.

Conclusion:

The App shell currently captures the Review Queue handoff as a match_id-only state boundary. It does not yet load Match Detail.

Review Queue handoff behavior

ReviewQueuePage accepts an onOpenMatch callback with a matchId string.

Observed Review Queue evidence:

ReviewQueuePage imports listReviewQueue and ReviewQueueRow.
ReviewQueuePage loads rows through listReviewQueue().
ReviewQueuePage renders rows keyed by row.match_id.
ReviewQueuePage passes onOpenMatch(row.match_id).
The UI title states that only match_id is passed across the Review Queue to Match Detail handoff boundary.
The page text states that only match_id is passed and Match Detail loading is not validated.

Conclusion:

ReviewQueuePage preserves the P-V boundary. It passes only backend-provided row.match_id. It does not pass full row payloads, does not synthesize Match Detail data, and does not validate Match Detail loading.

Frontend API client expectation

The frontend api.ts currently defines ReviewQueueRow, ReviewQueueResponse, and listReviewQueue().

Observed frontend service evidence:

ReviewQueueRow includes match_id: string.
ReviewQueueResponse includes items: ReviewQueueRow[].
listReviewQueue() calls /api/review/queue.
No ProductMatchDetail frontend type was observed.
No Match Detail frontend client function was observed.
No /api/review/matches/{match_id}/detail frontend client binding was observed.

Conclusion:

The frontend API client does not yet expose a Match Detail loading function. A later implementation must add a controlled client function without changing the Review Queue row contract.

Frontend Match Detail surface

No dedicated frontend Match Detail page/component/service file was found under the frontend src pages/components/services areas.

Conclusion:

The current frontend has a handoff capture boundary but not a real Match Detail surface. A later mini-epic must create or bind the Match Detail surface in a controlled step.

Backend API dependency

The backend route dependency exists.

Observed backend evidence:

src/invomatch/api/review_cases.py defines /api/review/matches/{match_id}/detail.
The route returns ProductMatchDetailResponse.
The route calls read_match_detail_by_id().
The route passes matches=query_service.list_match_detail_candidates().
tests/contracts/test_match_detail_evidence_api.py contains contract coverage for retrieval, not-found behavior, malformed payload behavior, and review-store-bound match_id continuity.

Conclusion:

The later frontend loading step must consume the existing backend-owned Match Detail route:

GET /api/review/matches/{match_id}/detail

The frontend must treat this route as the source of Match Detail truth. The frontend must not reconstruct Match Detail from Review Queue rows.

Minimum Safe Next Path

The next mini-epic may implement only a controlled Match Detail loading boundary if it follows these constraints:

Preserve ReviewQueuePage.tsx handoff behavior.
Preserve the rule that Review Queue passes only match_id.
Do not pass full Review Queue row payloads.
Add a frontend API client function for GET /api/review/matches/{match_id}/detail.
Use selectedReviewMatchId from the App shell as the only handoff input.
Create or bind a Match Detail surface that loads backend-owned data only.
Render loading, unavailable, not-found, malformed, and backend failure states explicitly.
Do not synthesize confidence, evidence, traceability, invoice data, payment data, or failure semantics in the frontend.
Do not change backend contracts.
Do not claim Scenario 15 completion until the full Review Queue -> match_id -> Match Detail loading -> evidence/trust/error rendering path is validated.
Authorization Decision

P-W authorizes the next mini-epic to define and implement a controlled frontend Match Detail loading boundary.

The authorization is narrow.

It authorizes using the existing App shell selectedReviewMatchId handoff and the existing backend route GET /api/review/matches/{match_id}/detail.

It does not authorize changes to ReviewQueuePage.tsx.

It does not authorize backend contract changes.

It does not authorize frontend truth synthesis.

It does not authorize Scenario 15 completion.

Recommended Next Mini-EPIC

Mini-EPIC 33.13.P-X — Controlled Match Detail Loading Boundary Implementation

Recommended description:

Implement the minimum controlled frontend Match Detail loading boundary authorized by P-W. Add a frontend API client function for GET /api/review/matches/{match_id}/detail, consume only the App shell selectedReviewMatchId captured from Review Queue, and create or bind a Match Detail surface that renders backend-owned Match Detail response states. Do not change ReviewQueuePage.tsx, do not change backend contracts, do not pass full Review Queue row payloads, do not synthesize Match Detail data in the frontend, and do not claim Scenario 15 completion until the full Review Queue to Match Detail path is validated.

P-W Closure Statement

Mini-EPIC 33.13.P-W is complete as a handoff-readiness inspection.

The current handoff boundary is understood:

ReviewQueuePage passes only row.match_id.

The App shell captures only selectedReviewMatchId.

The frontend does not yet expose a Match Detail client function.

The frontend does not yet contain a dedicated Match Detail surface.

The backend Match Detail dependency is GET /api/review/matches/{match_id}/detail.

The next step is authorized only as a controlled Match Detail loading boundary implementation.
