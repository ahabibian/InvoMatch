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


def _utc_min_datetime() -> datetime:
    return datetime.min.replace(tzinfo=timezone.utc)


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _normalize_run_status(value: Any) -> str:
    return str(value or "").strip().lower()


def _normalize_review_item_status(value: Any) -> str:
    return str(value or "").strip().upper()


def _is_open_review_item_status(value: Any) -> bool:
    normalized = _normalize_review_item_status(value)
    return normalized in {"PENDING", "IN_REVIEW", "DEFERRED"}


def _is_resolved_review_item_status(value: Any) -> bool:
    normalized = _normalize_review_item_status(value)
    return normalized in {"APPROVED", "REJECTED", "MODIFIED", "CLOSED"}


def _is_ready_artifact_status(value: Any) -> bool:
    normalized = str(value or "").strip().upper()
    return normalized == "READY"


def _is_failed_artifact_status(value: Any) -> bool:
    normalized = str(value or "").strip().upper()
    return normalized == "FAILED"


class RunViewQueryService:
    def __init__(
        self,
        run_store,
        review_store=None,
        artifact_query_service=None,
        export_readiness_evaluator=None,
    ) -> None:
        self._run_store = run_store
        self._review_store = review_store
        self._artifact_query_service = artifact_query_service
        self._export_readiness_evaluator = export_readiness_evaluator

    def get_run_view(self, run_id: str) -> ProductRunView | None:
        run = self._run_store.get_run(run_id)
        if run is None:
            return None

        review_summary = self._build_review_summary(run_id)
        artifacts = self._build_artifacts(run_id)
        export_summary = self._build_export_summary(
            run=run,
            review_summary=review_summary,
            artifacts=artifacts,
        )
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
        computed_total = matched_items + unmatched_items + ambiguous_items

        if total_items <= 0:
            total_items = computed_total
        elif total_items < computed_total:
            total_items = computed_total

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

        list_review_items = getattr(self._review_store, "list_review_items", None)
        get_feedback = getattr(self._review_store, "get_feedback", None)

        if list_review_items is None or get_feedback is None:
            return ProductRunReviewSummary(
                status="not_started",
                total_items=0,
                open_items=0,
                resolved_items=0,
            )

        relevant_items = []
        for review_item in list_review_items():
            feedback_id = getattr(review_item, "feedback_id", None)
            if feedback_id is None:
                continue

            feedback = get_feedback(feedback_id)
            if feedback is None:
                continue

            if str(getattr(feedback, "run_id", "")) != str(run_id):
                continue

            relevant_items.append(review_item)

        total_items = len(relevant_items)
        if total_items == 0:
            return ProductRunReviewSummary(
                status="not_started",
                total_items=0,
                open_items=0,
                resolved_items=0,
            )

        open_items = 0
        resolved_items = 0

        for item in relevant_items:
            item_status = getattr(item, "item_status", None)

            if _is_resolved_review_item_status(item_status):
                resolved_items += 1
                continue

            if _is_open_review_item_status(item_status):
                open_items += 1
                continue

            # Conservative rule:
            # unknown / unexpected states are treated as open so projection
            # never claims completion while underlying reality is ambiguous.
            open_items += 1

        if open_items + resolved_items != total_items:
            open_items = max(total_items - resolved_items, 0)

        status = "in_review" if open_items > 0 else "completed"

        return ProductRunReviewSummary(
            status=status,
            total_items=total_items,
            open_items=open_items,
            resolved_items=resolved_items,
        )

    def _build_export_summary(
        self,
        run,
        review_summary: ProductRunReviewSummary,
        artifacts: list[ProductRunArtifactReference],
    ) -> ProductRunExportSummary:
        raw_artifacts = self._list_raw_artifacts(str(getattr(run, "run_id", "")))
        ready_artifact_count = sum(
            1 for artifact in raw_artifacts if _is_ready_artifact_status(getattr(artifact, "status", None))
        )
        failed_artifact_count = sum(
            1 for artifact in raw_artifacts if _is_failed_artifact_status(getattr(artifact, "status", None))
        )

        if ready_artifact_count > 0:
            return ProductRunExportSummary(
                status="exported",
                artifact_count=len(artifacts),
            )

        export_ready = self._evaluate_export_readiness(
            run=run,
            review_summary=review_summary,
        )

        if export_ready:
            return ProductRunExportSummary(
                status="ready",
                artifact_count=len(artifacts),
            )

        if failed_artifact_count > 0:
            return ProductRunExportSummary(
                status="failed",
                artifact_count=len(artifacts),
            )

        return ProductRunExportSummary(
            status="not_ready",
            artifact_count=len(artifacts),
        )

    def _evaluate_export_readiness(
        self,
        run,
        review_summary: ProductRunReviewSummary,
    ) -> bool:
        evaluator = self._export_readiness_evaluator
        run_id = str(getattr(run, "run_id", ""))

        if evaluator is not None:
            evaluate = getattr(evaluator, "evaluate", None)
            if callable(evaluate):
                result = evaluate(run_id)
                return bool(getattr(result, "is_export_ready", False))

        run_status = _normalize_run_status(getattr(run, "status", ""))
        return run_status == "completed" and review_summary.open_items == 0

    def _build_artifacts(self, run_id: str) -> list[ProductRunArtifactReference]:
        raw_artifacts = self._list_raw_artifacts(run_id)
        sorted_artifacts = sorted(
            raw_artifacts,
            key=lambda artifact: (
                getattr(artifact, "created_at", _utc_min_datetime()),
                str(getattr(artifact, "id", "")),
            ),
            reverse=True,
        )

        return [self._to_artifact_reference(artifact) for artifact in sorted_artifacts]

    def _list_raw_artifacts(self, run_id: str) -> list[Any]:
        if self._artifact_query_service is None:
            return []

        return list(self._artifact_query_service.list_artifacts_for_run(run_id))

    def _to_artifact_reference(self, artifact) -> ProductRunArtifactReference:
        artifact_id = str(getattr(artifact, "id"))
        artifact_status = getattr(artifact, "status", None)

        download_url = None
        if _is_ready_artifact_status(artifact_status):
            download_url = f"/api/reconciliation/exports/{artifact_id}/download"

        return ProductRunArtifactReference(
            artifact_id=artifact_id,
            kind=str(getattr(artifact, "artifact_type", "run_export")),
            file_name=str(getattr(artifact, "file_name", "artifact")),
            media_type=str(getattr(artifact, "content_type", "application/octet-stream")),
            size_bytes=_safe_int(getattr(artifact, "byte_size", getattr(artifact, "size_bytes", 0))),
            created_at=getattr(artifact, "created_at"),
            download_url=download_url,
        )