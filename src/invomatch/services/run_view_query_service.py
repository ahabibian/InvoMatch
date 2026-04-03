from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from invomatch.api.product_models.run_view import (
    ProductRunArtifactReference,
    ProductRunExportSummary,
    ProductRunMatchSummary,
    ProductRunReviewSummary,
    ProductRunView,
)
from invomatch.services.review_queries import ReviewQueryService


def _utc_min_datetime() -> datetime:
    return datetime.min.replace(tzinfo=timezone.utc)


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


class RunViewQueryService:
    def __init__(
        self,
        run_store,
        review_store=None,
        artifact_query_service=None,
    ) -> None:
        self._run_store = run_store
        self._review_store = review_store
        self._artifact_query_service = artifact_query_service

    def get_run_view(self, run_id: str) -> ProductRunView | None:
        run = self._run_store.get_run(run_id)
        if run is None:
            return None

        review_summary = self._build_review_summary(run_id)
        artifacts = self._build_artifacts(run_id)
        export_summary = self._build_export_summary(run, artifacts)
        match_summary = self._build_match_summary(run)

        return ProductRunView(
            run_id=str(run.run_id),
            status=str(run.status),
            created_at=run.created_at,
            updated_at=getattr(run, "updated_at", run.created_at),
            match_summary=match_summary,
            review_summary=review_summary,
            export_summary=export_summary,
            artifacts=artifacts,
        )

    def _build_match_summary(self, run) -> ProductRunMatchSummary:
        report = getattr(run, "report", None)
        if report is None:
            return ProductRunMatchSummary(
                total_items=0,
                matched_items=0,
                unmatched_items=0,
                ambiguous_items=0,
            )

        matched_items = _safe_int(getattr(report, "matched", 0))
        unmatched_items = _safe_int(getattr(report, "unmatched", 0))
        ambiguous_items = _safe_int(getattr(report, "ambiguous", 0))

        total_items = _safe_int(getattr(report, "total", 0))
        if total_items <= 0:
            total_items = matched_items + unmatched_items + ambiguous_items

        return ProductRunMatchSummary(
            total_items=total_items,
            matched_items=matched_items,
            unmatched_items=unmatched_items,
            ambiguous_items=ambiguous_items,
        )

    def _build_review_summary(self, run_id: str) -> ProductRunReviewSummary:
        if self._review_store is None:
            return ProductRunReviewSummary(
                status="not_started",
                total_items=0,
                open_items=0,
                resolved_items=0,
            )

        projection = ReviewQueryService(review_store=self._review_store).get_review_case_for_run(run_id)
        if projection is None:
            return ProductRunReviewSummary(
                status="not_started",
                total_items=0,
                open_items=0,
                resolved_items=0,
            )

        normalized_status = str(getattr(projection, "status", "open")).lower()
        if normalized_status == "open":
            status = "in_review"
            open_items = 1
            resolved_items = 0
        else:
            status = "completed"
            open_items = 0
            resolved_items = 1

        return ProductRunReviewSummary(
            status=status,
            total_items=1,
            open_items=open_items,
            resolved_items=resolved_items,
        )

    def _build_export_summary(
        self,
        run,
        artifacts: list[ProductRunArtifactReference],
    ) -> ProductRunExportSummary:
        run_status = str(getattr(run, "status", ""))
        status = "not_ready"

        if run_status == "completed" and artifacts:
            status = "exported"
        elif run_status == "completed":
            status = "ready"

        return ProductRunExportSummary(
            status=status,
            artifact_count=len(artifacts),
        )

    def _build_artifacts(self, run_id: str) -> list[ProductRunArtifactReference]:
        if self._artifact_query_service is None:
            return []

        raw_artifacts = list(self._artifact_query_service.list_artifacts_for_run(run_id))
        sorted_artifacts = sorted(
            raw_artifacts,
            key=lambda artifact: (
                getattr(artifact, "created_at", _utc_min_datetime()),
                str(getattr(artifact, "id", "")),
            ),
        )

        return [self._to_artifact_reference(artifact) for artifact in sorted_artifacts]

    def _to_artifact_reference(self, artifact) -> ProductRunArtifactReference:
        return ProductRunArtifactReference(
            artifact_id=str(getattr(artifact, "id")),
            kind=str(getattr(artifact, "artifact_type", "run_export")),
            file_name=str(getattr(artifact, "file_name", "artifact")),
            media_type=str(getattr(artifact, "content_type", "application/octet-stream")),
            size_bytes=_safe_int(getattr(artifact, "byte_size", getattr(artifact, "size_bytes", 0))),
            created_at=getattr(artifact, "created_at"),
            download_url=f"/api/reconciliation/exports/{getattr(artifact, 'id')}/download",
        )
