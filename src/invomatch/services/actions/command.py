from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from invomatch.domain.tenant import TenantContext


@dataclass(slots=True)
class ActionCommand:
    action_type: str
    run_id: str
    tenant_id: Optional[str] = None
    tenant_context: Optional[TenantContext] = None
    target_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    note: Optional[str] = None