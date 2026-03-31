from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class ActionExecutionStatus(str, Enum):
    SUCCESS = "success"
    NO_OP = "no_op"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass
class ActionExecutionResult:
    action_type: str
    target_type: str
    target_id: str
    status: ActionExecutionStatus
    state_changes: List[Dict[str, Any]] = field(default_factory=list)
    side_effects: List[Dict[str, Any]] = field(default_factory=list)
    audit_event_ids: List[str] = field(default_factory=list)
    response_payload: Dict[str, Any] = field(default_factory=dict)