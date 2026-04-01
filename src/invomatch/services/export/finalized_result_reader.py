from __future__ import annotations

from typing import Protocol

from invomatch.domain.export import FinalizedResult


class FinalizedResultReader(Protocol):
    """Read contract for finalized results used by the export layer."""

    def get_results_for_run(self, run_id: str) -> list[FinalizedResult]:
        """Return finalized export-ready results for a run."""