from __future__ import annotations


class RetryBudgetPolicy:
    def remaining(self, retry_count: int, retry_limit: int) -> int:
        self._validate(retry_count=retry_count, retry_limit=retry_limit)
        remaining = retry_limit - retry_count
        return remaining if remaining > 0 else 0

    def is_exhausted(self, retry_count: int, retry_limit: int) -> bool:
        return self.remaining(retry_count=retry_count, retry_limit=retry_limit) == 0

    def can_retry(self, retry_count: int, retry_limit: int) -> bool:
        return not self.is_exhausted(retry_count=retry_count, retry_limit=retry_limit)

    def _validate(self, retry_count: int, retry_limit: int) -> None:
        if retry_count < 0:
            raise ValueError("retry_count must be >= 0")
        if retry_limit < 0:
            raise ValueError("retry_limit must be >= 0")