from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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


@dataclass
class RunOrchestrationResult:
    run_status: str
    review_cases: List[Dict[str, Any]]


class _InMemoryReviewStore:
    def __init__(self) -> None:
        self.created: List[Dict[str, Any]] = []

    def create_review_case(self, case: Dict[str, Any]) -> None:
        self.created.append(case)

    def list_active(self) -> List[Dict[str, Any]]:
        return list(self.created)


class RunOrchestrationService:
    def __init__(self, review_store: Optional[Any] = None) -> None:
        self._review_requirement_evaluator = ReviewRequirementEvaluator()
        self._review_case_generation_service = ReviewCaseGenerationService()
        self._run_finalization_evaluator = RunFinalizationEvaluator()
        self._review_integration_service = ReviewIntegrationService(
            review_store=review_store or _InMemoryReviewStore()
        )

    def orchestrate_post_matching(
        self,
        reconciliation_outcomes: List[Dict[str, Any]],
    ) -> RunOrchestrationResult:
        review_requirement = self._review_requirement_evaluator.evaluate(
            reconciliation_outcomes
        )

        if review_requirement.requires_review:
            generated_review_cases = self._review_case_generation_service.generate(
                reconciliation_outcomes
            )
            self._review_integration_service.create_cases(generated_review_cases)
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

    def orchestrate_post_review_resolution(
        self,
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