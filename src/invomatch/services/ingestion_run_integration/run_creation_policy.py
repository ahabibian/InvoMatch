from __future__ import annotations

from invomatch.services.ingestion_run_integration.models import RunCreationPolicyDecision


class RunCreationPolicy:
    def evaluate(
        self,
        *,
        ingestion_succeeded: bool,
        accepted_invoice_count: int,
        accepted_payment_count: int,
        rejected_count: int,
        conflict_count: int,
        blocking_conflict: bool,
    ) -> RunCreationPolicyDecision:
        if not ingestion_succeeded:
            return RunCreationPolicyDecision(
                creatable=False,
                reason_code="ingestion_failed",
                partial_ingestion=False,
                blocking_conflict=False,
            )

        if accepted_invoice_count <= 0:
            return RunCreationPolicyDecision(
                creatable=False,
                reason_code="no_accepted_invoices",
                partial_ingestion=False,
                blocking_conflict=False,
            )

        if accepted_payment_count <= 0:
            return RunCreationPolicyDecision(
                creatable=False,
                reason_code="no_accepted_payments",
                partial_ingestion=False,
                blocking_conflict=False,
            )

        if blocking_conflict or conflict_count > 0:
            return RunCreationPolicyDecision(
                creatable=False,
                reason_code="blocking_conflict",
                partial_ingestion=False,
                blocking_conflict=True,
            )

        partial_ingestion = rejected_count > 0

        return RunCreationPolicyDecision(
            creatable=True,
            reason_code="creatable",
            partial_ingestion=partial_ingestion,
            blocking_conflict=False,
        )