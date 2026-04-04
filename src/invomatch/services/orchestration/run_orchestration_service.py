from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from invomatch.domain.models import ReconciliationRun
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
from invomatch.services.reconciliation_runs import update_reconciliation_run
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import InMemoryRunStore, RunStore


@dataclass
class RunOrchestrationResult:
    run_status: str
    review_cases: List[Dict[str, Any]]


class RunOrchestrationService:
    def __init__(
        self,
        review_store: Optional[InMemoryReviewStore] = None,
        review_service: Optional[ReviewService] = None,
    ) -> None:
        self._review_requirement_evaluator = ReviewRequirementEvaluator()
        self._review_case_generation_service = ReviewCaseGenerationService()
        self._run_finalization_evaluator = RunFinalizationEvaluator()
        self._review_integration_service = ReviewIntegrationService(
            review_service=review_service or ReviewService(),
            review_store=review_store or InMemoryReviewStore(),
        )

    def orchestrate_post_matching(
        self,
        *,
        run_id: str,
        reconciliation_outcomes: List[Dict[str, Any]],
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
    ) -> tuple[RunOrchestrationResult, ReconciliationRun]:
        orchestration_result = self.orchestrate_post_matching(
            run_id=run_id,
            reconciliation_outcomes=reconciliation_outcomes,
        )

        persisted_run = update_reconciliation_run(
            run_id,
            status=orchestration_result.run_status,
            run_store=run_store,
        )

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