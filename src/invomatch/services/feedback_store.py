from __future__ import annotations

from typing import List, Protocol

from invomatch.domain.feedback import FeedbackRecord


class FeedbackStore(Protocol):
    """
    Contract for feedback persistence.
    """

    def create_feedback(self, record: FeedbackRecord) -> FeedbackRecord:
        """
        Persist a feedback record.
        """
        ...

    def list_by_run(self, run_id: str) -> List[FeedbackRecord]:
        """
        Return all feedback for a run.
        """
        ...

    def list_by_match(self, match_id: str) -> List[FeedbackRecord]:
        """
        Return feedback history for a specific match.
        """
        ...