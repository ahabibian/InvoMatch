from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional


class OperationalCondition(StrEnum):
    HEALTHY = "healthy"
    RETRY_PENDING = "retry_pending"
    RETRY_IN_PROGRESS = "retry_in_progress"
    REENTRY_PENDING = "reentry_pending"
    STUCK_DETECTED = "stuck_detected"
    RECOVERY_SKIPPED = "recovery_skipped"
    TERMINAL_CONFIRMED = "terminal_confirmed"
    RECOVERY_EXHAUSTED = "recovery_exhausted"


class OperationalDecision(StrEnum):
    RETRY_TRIGGERED = "retry_triggered"
    REENTRY_TRIGGERED = "reentry_triggered"
    RECOVERY_SKIPPED = "recovery_skipped"
    TERMINAL_CONFIRMED = "terminal_confirmed"
    CANDIDATE_REJECTED = "candidate_rejected"
    ALREADY_RECOVERED_NOOP = "already_recovered_noop"
    ELIGIBLE = "eligible"
    NOT_STUCK = "not_stuck"
    STUCK_DETECTED = "stuck_detected"


class OperationalActorType(StrEnum):
    SYSTEM = "system"


class OperationalReasonCode(StrEnum):
    NONE = "none"
    RECOVERABLE_FAILURE = "recoverable_failure"
    STUCK_PROCESSING = "stuck_processing"
    LEASE_EXPIRED = "lease_expired"
    NO_PROGRESS_TIMEOUT = "no_progress_timeout"
    RETRY_BUDGET_EXHAUSTED = "retry_budget_exhausted"
    FAILURE_NOT_RECOVERABLE = "failure_not_recoverable"
    TERMINAL_FAILURE_CONFIRMED = "terminal_failure_confirmed"
    ACTIVE_RECOVERY_IN_PROGRESS = "active_recovery_in_progress"
    VALID_LEASE_PRESENT = "valid_lease_present"
    ALREADY_RECOVERED_SAME_INCIDENT = "already_recovered_same_incident"
    MANUALLY_CANCELLED = "manually_cancelled"
    LIFECYCLE_BLOCKED = "lifecycle_blocked"
    CANDIDATE_STATE_CHANGED = "candidate_state_changed"
    TERMINAL_BUSINESS_STATE = "terminal_business_state"
    NO_FAILURE_OR_STUCK_SIGNAL = "no_failure_or_stuck_signal"
    ACTIVE_CLAIM_PRESENT = "active_claim_present"
    ALREADY_MARKED_SAME_INCIDENT = "already_marked_same_incident"


@dataclass(frozen=True, slots=True)
class RecoveryEvaluationResult:
    is_eligible: bool
    decision: OperationalDecision
    reason_code: OperationalReasonCode
    target_condition: OperationalCondition
    detail: Optional[str] = None


@dataclass(frozen=True, slots=True)
class RunOperationalMetadata:
    retry_count: int = 0
    retry_limit: int = 0
    retry_budget_remaining: int = 0
    recovery_attempt_count: int = 0
    last_failure_code: Optional[str] = None
    last_failure_at: Optional[datetime] = None
    last_recovery_attempt_at: Optional[datetime] = None
    last_recovery_decision: Optional[OperationalDecision] = None
    last_recovery_reason_code: Optional[OperationalReasonCode] = None
    stuck_detected_at: Optional[datetime] = None
    lease_expired_at: Optional[datetime] = None
    terminal_confirmed_at: Optional[datetime] = None
    last_operational_event_at: Optional[datetime] = None
    condition: OperationalCondition = OperationalCondition.HEALTHY


@dataclass(frozen=True, slots=True)
class OperationalAuditEvent:
    event_id: str
    tenant_id: str
    run_id: str
    event_type: str
    event_time: datetime
    actor_type: OperationalActorType
    decision: OperationalDecision
    reason_code: OperationalReasonCode
    reason_detail: Optional[str] = None
    previous_operational_state: Optional[OperationalCondition] = None
    new_operational_state: Optional[OperationalCondition] = None
    related_failure_code: Optional[str] = None
    attempt_number: Optional[int] = None
    correlation_id: Optional[str] = None
    metadata: dict[str, str] = field(default_factory=dict)