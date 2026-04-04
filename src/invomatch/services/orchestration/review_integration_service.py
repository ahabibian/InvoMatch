from typing import Any, Dict, List


class ReviewIntegrationService:
    def __init__(self, review_store):
        self._review_store = review_store

    def create_cases(self, review_cases: List[Dict[str, Any]]) -> None:
        for case in review_cases:
            self._review_store.create_review_case(case)

    def get_active_cases(self) -> List[Dict[str, Any]]:
        return self._review_store.list_active()