from dataclasses import dataclass
from typing import Any, Dict, List

from invomatch.services.orchestration.review_case_generation_service import (
    ReviewCaseGenerationService,
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


class RunOrchestrationService:
    def __init__(self) -> None:
        self._review_requirement_evaluator = ReviewRequirementEvaluator()
        self._review_case_generation_service = ReviewCaseGenerationService()
        self._run_finalization_evaluator = RunFinalizationEvaluator()

    def orchestrate_post_matching(
        self,
        reconciliation_outcomes: List[Dict[str, Any]],
    ) -> RunOrchestrationResult:
        review_requirement = self._review_requirement_evaluator.evaluate(
            reconciliation_outcomes
        )

        if review_requirement.requires_review:
            review_cases = self._review_case_generation_service.generate(
                reconciliation_outcomes
            )
            return RunOrchestrationResult(
                run_status="review_required",
                review_cases=review_cases,
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
        review_items: List[Dict[str, Any]],
        matching_completed: bool,
    ) -> RunOrchestrationResult:
        finalization = self._run_finalization_evaluator.evaluate(
            review_items=review_items,
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
                review_cases=review_items,
            )

        return RunOrchestrationResult(
            run_status="failed",
            review_cases=[],
        )