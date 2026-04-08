from __future__ import annotations

from invomatch.services.ingestion_run_integration.models import (
    IdempotencyDecision,
    IdempotencyDecisionType,
)


class RunCreationIdempotencyPolicy:
    def evaluate(
        self,
        *,
        existing_run_id: str | None,
        same_batch_identity: bool,
        same_normalized_fingerprint: bool,
    ) -> IdempotencyDecision:
        if existing_run_id is None:
            return IdempotencyDecision(
                decision=IdempotencyDecisionType.CREATE_NEW,
                existing_run_id=None,
                reason_code="no_existing_run",
            )

        if same_batch_identity and same_normalized_fingerprint:
            return IdempotencyDecision(
                decision=IdempotencyDecisionType.REUSE_EXISTING,
                existing_run_id=existing_run_id,
                reason_code="existing_run_reused",
            )

        if same_batch_identity and not same_normalized_fingerprint:
            return IdempotencyDecision(
                decision=IdempotencyDecisionType.CONFLICT,
                existing_run_id=existing_run_id,
                reason_code="batch_identity_conflict",
            )

        return IdempotencyDecision(
            decision=IdempotencyDecisionType.CREATE_NEW,
            existing_run_id=None,
            reason_code="new_batch",
        )