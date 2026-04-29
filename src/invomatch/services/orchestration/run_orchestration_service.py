from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from invomatch.domain.models import ReconciliationRun
from invomatch.domain.tenant import TenantContext
from invomatch.services.orchestration.review_case_generation_service import (
    ReviewCaseGenerationService,
)
from invomatch.services.orchestration.review_integration_service import (
    ReviewIntegrationService,
)
from invomatch.services.orchestration.review_requirement_evaluator import (
    ReviewRequirementEvaluator,
)
from invomatch.services.orchestration.run_finalization_evaluator import (
    RunFinalizationEvaluator,
)
from invomatch.services.export.finalized_projection_store import FinalizedProjectionStore
from invomatch.services.completed_run_projection_service import CompletedRunProjectionService
from invomatch.services.reconciliation_runs import update_reconciliation_run
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import RunStore


@dataclass
class RunOrchestrationResult:
    run_status: str
    review_cases: List[Dict[str, Any]]


class RunOrchestrationService:
    def __init__(
        self,
        review_store: Optional[InMemoryReviewStore] = None,
        review_service: Optional[ReviewService] = None,
        projection_store: FinalizedProjectionStore | None = None,
    ) -> None:
        self._review_store = review_store or InMemoryReviewStore()
        self._projection_store = projection_store
        self._review_requirement_evaluator = ReviewRequirementEvaluator()
        self._review_case_generation_service = ReviewCaseGenerationService()
        self._run_finalization_evaluator = RunFinalizationEvaluator()
        self._review_integration_service = ReviewIntegrationService(
            review_service=review_service or ReviewService(),
            review_store=self._review_store,
        )

    def orchestrate_post_matching(
        self,
        *,
        run_id: str,
        reconciliation_outcomes: List[Dict[str, Any]],
        tenant_id: str | None = None,
        tenant_context: TenantContext | None = None,
    ) -> RunOrchestrationResult:
        review_requirement = self._review_requirement_evaluator.evaluate(
            reconciliation_outcomes
        )

        if review_requirement.requires_review:
            generated_review_cases = self._review_case_generation_service.generate(
                reconciliation_outcomes
            )
            self._review_integration_service.create_cases(
                run_id=run_id,
                review_cases=generated_review_cases,
                created_by="run_orchestration",
            )
            active_review_cases = self._review_integration_service.get_active_cases()

            return RunOrchestrationResult(
                run_status="review_required",
                review_cases=active_review_cases,
            )

        finalization = self._run_finalization_evaluator.evaluate(
            review_items=[],
            matching_completed=True,
        )

        if finalization.is_finalizable:
            return RunOrchestrationResult(
                run_status="completed",
                review_cases=[],
            )

        return RunOrchestrationResult(
            run_status="failed",
            review_cases=[],
        )

    def orchestrate_and_persist_post_matching(
        self,
        *,
        run_id: str,
        reconciliation_outcomes: List[Dict[str, Any]],
        run_store: RunStore,
        tenant_id: str | None = None,
        tenant_context: TenantContext | None = None,
    ) -> tuple[RunOrchestrationResult, ReconciliationRun]:
        effective_tenant_id = tenant_context.tenant_id if tenant_context is not None else tenant_id
        orchestration_result = self.orchestrate_post_matching(
            run_id=run_id,
            reconciliation_outcomes=reconciliation_outcomes,
            tenant_id=effective_tenant_id,
            tenant_context=tenant_context,
        )

        persisted_run = update_reconciliation_run(
            run_id,
            status=orchestration_result.run_status,
            run_store=run_store,
        )

        CompletedRunProjectionService(
            projection_store=self._projection_store,
            review_store=self._review_store,
        ).persist_if_completed(persisted_run)

        return orchestration_result, persisted_run

    def orchestrate_post_review_resolution(
        self,
        *,
        matching_completed: bool,
    ) -> RunOrchestrationResult:
        active_review_cases = self._review_integration_service.get_active_cases()

        finalization = self._run_finalization_evaluator.evaluate(
            review_items=active_review_cases,
            matching_completed=matching_completed,
        )

        if finalization.is_finalizable:
            return RunOrchestrationResult(
                run_status="completed",
                review_cases=[],
            )

        if matching_completed:
            return RunOrchestrationResult(
                run_status="review_required",
                review_cases=active_review_cases,
            )

        return RunOrchestrationResult(
            run_status="failed",
            review_cases=[],
        )

    def orchestrate_and_persist_post_review_resolution(
        self,
        *,
        run_id: str,
        matching_completed: bool,
        run_store: RunStore,
        tenant_id: str | None = None,
        tenant_context: TenantContext | None = None,
    ) -> tuple[RunOrchestrationResult, ReconciliationRun]:
        effective_tenant_id = tenant_context.tenant_id if tenant_context is not None else tenant_id
        current_run = run_store.get_run(run_id, tenant_id=effective_tenant_id)
        if current_run is None:
            raise KeyError(f"Reconciliation run not found: {run_id}")

        if current_run.status != "review_required":
            raise ValueError(
                f"Invalid state for review resolution: {current_run.status}"
            )

        orchestration_result = self.orchestrate_post_review_resolution(
            matching_completed=matching_completed,
        )

        if orchestration_result.run_status == "review_required":
            return orchestration_result, current_run

        persisted_run = update_reconciliation_run(
            run_id,
            status=orchestration_result.run_status,
            run_store=run_store,
        )

        CompletedRunProjectionService(
            projection_store=self._projection_store,
            review_store=self._review_store,
        ).persist_if_completed(persisted_run)

        return orchestration_result, persisted_run



