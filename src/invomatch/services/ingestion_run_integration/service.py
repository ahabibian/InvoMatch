from __future__ import annotations

from invomatch.services.ingestion_run_integration.idempotency_policy import (
    RunCreationIdempotencyPolicy,
)
from invomatch.services.ingestion_run_integration.mapper import IngestionToRunMapper
from invomatch.services.ingestion_run_integration.models import (
    IdempotencyDecisionType,
    IngestionRunResult,
    IngestionRunStatus,
)
from invomatch.services.ingestion_run_integration.run_creation_policy import (
    RunCreationPolicy,
)


class IngestionRunIntegrationService:
    def __init__(
        self,
        *,
        mapper: IngestionToRunMapper | None = None,
        run_creation_policy: RunCreationPolicy | None = None,
        idempotency_policy: RunCreationIdempotencyPolicy | None = None,
    ) -> None:
        self._mapper = mapper or IngestionToRunMapper()
        self._run_creation_policy = run_creation_policy or RunCreationPolicy()
        self._idempotency_policy = idempotency_policy or RunCreationIdempotencyPolicy()

    def create_run_from_ingestion(
        self,
        *,
        ingestion_batch_id: str,
        ingestion_succeeded: bool,
        accepted_invoices: list[object],
        accepted_payments: list[object],
        rejected_count: int,
        conflict_count: int,
        blocking_conflict: bool,
        existing_run_id: str | None,
        same_batch_identity: bool,
        same_normalized_fingerprint: bool,
        create_run,
    ) -> IngestionRunResult:
        policy_decision = self._run_creation_policy.evaluate(
            ingestion_succeeded=ingestion_succeeded,
            accepted_invoice_count=len(accepted_invoices),
            accepted_payment_count=len(accepted_payments),
            rejected_count=rejected_count,
            conflict_count=conflict_count,
            blocking_conflict=blocking_conflict,
        )

        if not policy_decision.creatable:
            status = (
                IngestionRunStatus.RUN_FAILED
                if policy_decision.reason_code == "ingestion_failed"
                else IngestionRunStatus.RUN_REJECTED
            )
            return IngestionRunResult(
                status=status,
                run_id=None,
                reason_code=policy_decision.reason_code,
                ingestion_batch_id=ingestion_batch_id,
                accepted_invoice_count=len(accepted_invoices),
                accepted_payment_count=len(accepted_payments),
                rejected_count=rejected_count,
                conflict_count=conflict_count,
                partial_ingestion=policy_decision.partial_ingestion,
            )

        idempotency_decision = self._idempotency_policy.evaluate(
            existing_run_id=existing_run_id,
            same_batch_identity=same_batch_identity,
            same_normalized_fingerprint=same_normalized_fingerprint,
        )

        if idempotency_decision.decision == IdempotencyDecisionType.REUSE_EXISTING:
            return IngestionRunResult(
                status=IngestionRunStatus.RUN_REUSED,
                run_id=idempotency_decision.existing_run_id,
                reason_code=idempotency_decision.reason_code,
                ingestion_batch_id=ingestion_batch_id,
                accepted_invoice_count=len(accepted_invoices),
                accepted_payment_count=len(accepted_payments),
                rejected_count=rejected_count,
                conflict_count=conflict_count,
                partial_ingestion=policy_decision.partial_ingestion,
            )

        if idempotency_decision.decision == IdempotencyDecisionType.CONFLICT:
            return IngestionRunResult(
                status=IngestionRunStatus.RUN_FAILED,
                run_id=None,
                reason_code=idempotency_decision.reason_code,
                ingestion_batch_id=ingestion_batch_id,
                accepted_invoice_count=len(accepted_invoices),
                accepted_payment_count=len(accepted_payments),
                rejected_count=rejected_count,
                conflict_count=conflict_count,
                partial_ingestion=policy_decision.partial_ingestion,
            )

        run_input = self._mapper.map(
            accepted_invoices=accepted_invoices,
            accepted_payments=accepted_payments,
        )

        run_id = create_run(
            run_input=run_input,
            traceability={
                "ingestion_batch_id": ingestion_batch_id,
                "accepted_invoice_count": len(accepted_invoices),
                "accepted_payment_count": len(accepted_payments),
                "rejected_count": rejected_count,
                "conflict_count": conflict_count,
                "partial_ingestion": policy_decision.partial_ingestion,
                "idempotency_decision": idempotency_decision.reason_code,
            },
        )

        return IngestionRunResult(
            status=IngestionRunStatus.RUN_CREATED,
            run_id=run_id,
            reason_code="run_created",
            ingestion_batch_id=ingestion_batch_id,
            accepted_invoice_count=len(accepted_invoices),
            accepted_payment_count=len(accepted_payments),
            rejected_count=rejected_count,
            conflict_count=conflict_count,
            partial_ingestion=policy_decision.partial_ingestion,
        )