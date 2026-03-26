from __future__ import annotations

from collections.abc import Iterable

from invomatch.domain.feedback.enums import ReasonCode, SignalType
from invomatch.domain.feedback.models import CorrectionEvent, LearningSignal
from invomatch.domain.feedback.repositories import FeedbackRepository


_REASON_TO_SIGNAL_TYPE: dict[ReasonCode, SignalType] = {
    ReasonCode.VENDOR_ALIAS_DISCOVERED: SignalType.VENDOR_ALIAS_DISCOVERED,
    ReasonCode.OCR_INVOICE_NUMBER_ERROR: SignalType.INVOICE_NUMBER_OCR_CONFUSION,
    ReasonCode.AMOUNT_TOLERANCE_TOO_STRICT: SignalType.AMOUNT_TOLERANCE_TOO_STRICT,
    ReasonCode.AMOUNT_TOLERANCE_TOO_WIDE: SignalType.AMOUNT_TOLERANCE_TOO_WIDE,
    ReasonCode.DATE_WINDOW_TOO_STRICT: SignalType.DATE_WINDOW_TOO_STRICT,
    ReasonCode.DATE_WINDOW_TOO_WIDE: SignalType.DATE_WINDOW_TOO_WIDE,
    ReasonCode.PAYMENT_REFERENCE_MORE_RELIABLE: SignalType.PAYMENT_REFERENCE_MORE_RELIABLE,
}


class SignalExtractionService:
    def __init__(self, repository: FeedbackRepository, extraction_version: str) -> None:
        self._repository = repository
        self._extraction_version = extraction_version

    def extract_from_events(self, events: Iterable[CorrectionEvent]) -> list[LearningSignal]:
        grouped: dict[tuple[str, SignalType], list[CorrectionEvent]] = {}

        for event in events:
            signal_type = _REASON_TO_SIGNAL_TYPE.get(event.reason_code)
            if signal_type is None:
                continue

            key = (event.tenant_id, signal_type)
            grouped.setdefault(key, []).append(event)

        signals: list[LearningSignal] = []

        for (tenant_id, signal_type), grouped_events in grouped.items():
            signal = LearningSignal(
                signal_id=self._build_signal_id(tenant_id, signal_type, grouped_events),
                tenant_id=tenant_id,
                signal_type=signal_type,
                source_correction_ids=tuple(event.correction_id for event in grouped_events),
                source_match_ids=tuple(event.match_id for event in grouped_events),
                source_feature_snapshot_ids=tuple(
                    event.feature_snapshot_ref.snapshot_id for event in grouped_events
                ),
                evidence_count=len(grouped_events),
                consistency_score=1.0,
                reviewer_weight_score=1.0,
                extraction_version=self._extraction_version,
                candidate_rule_payload={
                    "signal_type": signal_type.value,
                    "reason_codes": sorted({event.reason_code.value for event in grouped_events}),
                },
            )
            self._repository.save_learning_signal(signal)
            signals.append(signal)

        return signals

    @staticmethod
    def _build_signal_id(
        tenant_id: str,
        signal_type: SignalType,
        events: list[CorrectionEvent],
    ) -> str:
        first_correction_id = events[0].correction_id
        return f"sig-{tenant_id}-{signal_type.value}-{first_correction_id}"