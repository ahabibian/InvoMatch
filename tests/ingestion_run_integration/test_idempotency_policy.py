from invomatch.services.ingestion_run_integration.idempotency_policy import (
    RunCreationIdempotencyPolicy,
)
from invomatch.services.ingestion_run_integration.models import IdempotencyDecisionType


def test_create_new_when_no_existing_run():
    policy = RunCreationIdempotencyPolicy()

    result = policy.evaluate(
        existing_run_id=None,
        same_batch_identity=False,
        same_normalized_fingerprint=False,
    )

    assert result.decision == IdempotencyDecisionType.CREATE_NEW
    assert result.reason_code == "no_existing_run"


def test_reuse_when_same_batch_and_same_fingerprint():
    policy = RunCreationIdempotencyPolicy()

    result = policy.evaluate(
        existing_run_id="run-1",
        same_batch_identity=True,
        same_normalized_fingerprint=True,
    )

    assert result.decision == IdempotencyDecisionType.REUSE_EXISTING
    assert result.existing_run_id == "run-1"


def test_conflict_when_same_batch_but_different_fingerprint():
    policy = RunCreationIdempotencyPolicy()

    result = policy.evaluate(
        existing_run_id="run-1",
        same_batch_identity=True,
        same_normalized_fingerprint=False,
    )

    assert result.decision == IdempotencyDecisionType.CONFLICT
    assert result.reason_code == "batch_identity_conflict"