from dataclasses import dataclass

from .role import Role
from .user_status import UserStatus


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    user_id: str
    username: str
    role: Role
    status: UserStatus
    auth_source: str
    tenant_id: str

    @property
    def is_active(self) -> bool:
        return self.status is UserStatus.ACTIVE