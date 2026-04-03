import pytest

from invomatch.services.lifecycle.errors import LifecycleOperationNotAllowedError
from invomatch.services.lifecycle.guards import RunLifecycleGuards


def test_export_allowed_only_for_completed():
    RunLifecycleGuards.require_export_allowed("completed")
    with pytest.raises(LifecycleOperationNotAllowedError):
        RunLifecycleGuards.require_export_allowed("processing")


def test_review_resolution_allowed_only_for_review_required():
    RunLifecycleGuards.require_review_resolution_allowed("review_required")
    with pytest.raises(LifecycleOperationNotAllowedError):
        RunLifecycleGuards.require_review_resolution_allowed("queued")


def test_processing_start_allowed_only_for_queued():
    RunLifecycleGuards.require_processing_start_allowed("queued")
    with pytest.raises(LifecycleOperationNotAllowedError):
        RunLifecycleGuards.require_processing_start_allowed("processing")