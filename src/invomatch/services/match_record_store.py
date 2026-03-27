from __future__ import annotations

from typing import Protocol

from invomatch.domain.match_record import MatchRecord


class MatchRecordStore(Protocol):
    def save_many(self, records: list[MatchRecord]) -> None:
        """Persist a batch of match records."""

    def list_by_run(self, run_id: str) -> list[MatchRecord]:
        """List persisted match records for a reconciliation run."""