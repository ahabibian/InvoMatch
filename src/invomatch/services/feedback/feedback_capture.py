from __future__ import annotations

from invomatch.domain.feedback.models import CorrectionEvent
from invomatch.domain.feedback.repositories import FeedbackRepository


class FeedbackCaptureService:
    def __init__(self, repository: FeedbackRepository) -> None:
        self._repository = repository

    def capture(self, event: CorrectionEvent) -> CorrectionEvent:
        self._repository.save_correction_event(event)
        return event