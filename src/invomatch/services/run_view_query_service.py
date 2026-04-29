from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from invomatch.api.product_models.run_view import (
    ProductRunArtifactReference,
    ProductRunError,
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
    if value is None:
        return ""
    raw = getattr(value, "value", value)
    return str(raw).strip().upper()


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
        projection_store=None,
    ) -> None:
        self._run_store = run_store
        self._review_store = review_store
        self._artifact_query_service = artifact_query_service
        self._export_readiness_evaluator = export_readiness_evaluator
        self._projection_store = projection_store

    def get_run_view(self, run_id: str) -> ProductRunView | None:
        run = self._run_store.get_run(run_id)
        if run is None:
            return None

        review_summary = self._build_review_summary(run_id)
        raw_artifacts = self._safe_list_raw_artifacts(run_id)
        artifacts = self._build_artifacts_from_raw(raw_artifacts)
        export_summary = self._build_export_summary(
            run=run,
            review_summary=review_summary,
            artifacts=artifacts,
            raw_artifacts=raw_artifacts,
        )
        match_summary = self._build_match_summary(run)
        run_error = self._build_run_error(run)

        return ProductRunView(
            run_id=str(run.run_id),
            status=str(run.status),
            created_at=run.created_at,
            updated_at=getattr(run, "updated_at", run.created_at),
            error=run_error,
            match_summary=match_summary,
            review_summary=review_summary,
            export_summary=export_summary,
            artifacts=artifacts,
        )

    def _build_run_error(self, run) -> ProductRunError | None:
        error = getattr(run, "error", None)
        if error is not None:
            return ProductRunError(
                code=str(getattr(error, "code", "runtime_error")),
                message=str(getattr(error, "message", "Runtime failure")),
                retryable=bool(getattr(error, "retryable", False)),
                terminal=bool(
                    getattr(
                        error,
                        "terminal",
                        _normalize_run_status(getattr(run, "status", "")) == "failed",
                    )
                ),
            )

        error_message = getattr(run, "error_message", None)
        if error_message:
            return ProductRunError(
                code="runtime_error",
                message=str(error_message),
                retryable=False,
                terminal=_normalize_run_status(getattr(run, "status", "")) == "failed",
            )

        return None

    def _build_match_summary(self, run) -> ProductRunMatchSummary:
        projection_summary = self._build_match_summary_from_projection(run)
        if projection_summary is not None:
            return projection_summary

        return self._build_match_summary_from_report(run)

    def _build_match_summary_from_projection(self, run) -> ProductRunMatchSummary | None:
        projection_store = getattr(self, "_projection_store", None)
        if projection_store is None:
            return None

        run_status = _normalize_run_status(getattr(run, "status", ""))
        if run_status != "completed":
            return None

        tenant_id = getattr(run, "tenant_id", None)
        run_id = getattr(run, "run_id", None)
        if not tenant_id or not run_id:
            return None

        try:
            results = projection_store.get_results(
                tenant_id=str(tenant_id),
                run_id=str(run_id),
            )
        except Exception:
            return None

        if results is None:
            return None

        matched_items = 0
        unmatched_items = 0
        ambiguous_items = 0

        for result in results:
            decision_type = str(getattr(getattr(result, "decision_type", None), "value", getattr(result, "decision_type", ""))).upper()

            if decision_type == "MATCH":
                matched_items += 1
                continue

            if decision_type == "UNMATCHED":
                unmatched_items += 1
                continue

            if decision_type == "PARTIAL":
                ambiguous_items += 1
                continue

            ambiguous_items += 1

        total_items = matched_items + unmatched_items + ambiguous_items

        return ProductRunMatchSummary(
            total_items=total_items,
            matched_items=matched_items,
            unmatched_items=unmatched_items,
            ambiguous_items=ambiguous_items,
        )

    def _build_match_summary_from_report(self, run) -> ProductRunMatchSummary:
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

        try:
            review_items = list(list_review_items())
        except Exception:
            return ProductRunReviewSummary(
                status="not_started",
                total_items=0,
                open_items=0,
                resolved_items=0,
            )

        relevant_items = []
        for review_item in review_items:
            feedback_id = getattr(review_item, "feedback_id", None)
            if feedback_id is None:
                continue

            try:
                feedback = get_feedback(feedback_id)
            except Exception:
                return ProductRunReviewSummary(
                    status="not_started",
                    total_items=0,
                    open_items=0,
                    resolved_items=0,
                )

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
        raw_artifacts: list[Any],
    ) -> ProductRunExportSummary:
        ready_artifact_count = sum(
            1
            for artifact in raw_artifacts
            if _is_ready_artifact_status(getattr(artifact, "status", None))
        )
        failed_artifact_count = sum(
            1
            for artifact in raw_artifacts
            if _is_failed_artifact_status(getattr(artifact, "status", None))
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

        run_status = _normalize_run_status(getattr(run, "status", ""))
        export_eligible = run_status == "completed" and review_summary.open_items == 0

        if export_eligible and failed_artifact_count > 0:
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
                try:
                    result = evaluate(run_id)
                    return bool(getattr(result, "is_export_ready", False))
                except Exception:
                    return False

        run_status = _normalize_run_status(getattr(run, "status", ""))
        return run_status == "completed" and review_summary.open_items == 0

    def _build_artifacts_from_raw(
        self,
        raw_artifacts: list[Any],
    ) -> list[ProductRunArtifactReference]:
        sorted_artifacts = sorted(
            raw_artifacts,
            key=lambda artifact: (
                getattr(artifact, "created_at", _utc_min_datetime()),
                str(getattr(artifact, "id", "")),
            ),
            reverse=True,
        )

        return [self._to_artifact_reference(artifact) for artifact in sorted_artifacts]

    def _safe_list_raw_artifacts(self, run_id: str) -> list[Any]:
        if self._artifact_query_service is None:
            return []

        try:
            return list(self._artifact_query_service.list_artifacts_for_run(run_id))
        except Exception:
            return []

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
            size_bytes=_safe_int(
                getattr(artifact, "byte_size", getattr(artifact, "size_bytes", 0))
            ),
            created_at=getattr(artifact, "created_at"),
            download_url=download_url,
        )