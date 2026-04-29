import pytest

from invomatch.services.export.errors import InconsistentProjectionStateError
from invomatch.services.orchestration.export_readiness_evaluator import ExportReadinessEvaluator


class FakeRun:
    def __init__(self, run_id, status, tenant_id="t1"):
        self.run_id = run_id
        self.status = status
        self.tenant_id = tenant_id


class FakeRunStore:
    def __init__(self, run):
        self._run = run

    def get_run(self, run_id):
        return self._run


class EmptyProjectionStore:
    def exists(self, tenant_id, run_id):
        return False


def test_completed_run_without_projection_is_invalid_state():
    run = FakeRun(run_id="r1", status="completed")

    evaluator = ExportReadinessEvaluator(
        run_store=FakeRunStore(run),
        projection_store=EmptyProjectionStore(),
    )

    with pytest.raises(InconsistentProjectionStateError):
        evaluator.evaluate("r1")