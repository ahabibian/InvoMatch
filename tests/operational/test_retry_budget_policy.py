import pytest

from invomatch.services.operational.retry_budget_policy import RetryBudgetPolicy


def test_retry_budget_remaining_is_bounded_at_zero() -> None:
    policy = RetryBudgetPolicy()

    assert policy.remaining(retry_count=0, retry_limit=3) == 3
    assert policy.remaining(retry_count=2, retry_limit=3) == 1
    assert policy.remaining(retry_count=3, retry_limit=3) == 0
    assert policy.remaining(retry_count=5, retry_limit=3) == 0


def test_retry_budget_exhaustion_and_can_retry_are_consistent() -> None:
    policy = RetryBudgetPolicy()

    assert policy.can_retry(retry_count=1, retry_limit=2) is True
    assert policy.is_exhausted(retry_count=1, retry_limit=2) is False

    assert policy.can_retry(retry_count=2, retry_limit=2) is False
    assert policy.is_exhausted(retry_count=2, retry_limit=2) is True


@pytest.mark.parametrize(
    ("retry_count", "retry_limit"),
    [(-1, 1), (0, -1)],
)
def test_retry_budget_policy_rejects_negative_values(
    retry_count: int,
    retry_limit: int,
) -> None:
    policy = RetryBudgetPolicy()

    with pytest.raises(ValueError):
        policy.remaining(retry_count=retry_count, retry_limit=retry_limit)