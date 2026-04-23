from __future__ import annotations

from collections.abc import Mapping, Set

from invomatch.domain.security import Permission, Role


ROLE_PERMISSIONS: Mapping[Role, frozenset[Permission]] = {
    Role.VIEWER: frozenset(
        {
            Permission.INPUT_VIEW,
            Permission.RUNS_LIST,
            Permission.RUNS_READ,
            Permission.RUNS_READ_VIEW,
            Permission.RUNS_READ_REVIEW,
            Permission.ARTIFACTS_LIST,
            Permission.ARTIFACTS_READ_METADATA,
        }
    ),
    Role.OPERATOR: frozenset(
        {
            Permission.INPUT_SUBMIT,
            Permission.INPUT_VIEW,
            Permission.RUNS_CREATE,
            Permission.RUNS_CREATE_FROM_INGESTION,
            Permission.RUNS_LIST,
            Permission.RUNS_READ,
            Permission.RUNS_READ_VIEW,
            Permission.RUNS_READ_REVIEW,
            Permission.ACTIONS_RESOLVE_REVIEW,
            Permission.ACTIONS_EXPORT_RUN,
            Permission.EXPORTS_DOWNLOAD_DIRECT,
            Permission.ARTIFACTS_LIST,
            Permission.ARTIFACTS_READ_METADATA,
            Permission.ARTIFACTS_DOWNLOAD,
        }
    ),
    Role.ADMIN: frozenset(
        {
            Permission.INPUT_SUBMIT,
            Permission.INPUT_VIEW,
            Permission.RUNS_CREATE,
            Permission.RUNS_CREATE_FROM_INGESTION,
            Permission.RUNS_LIST,
            Permission.RUNS_READ,
            Permission.RUNS_READ_VIEW,
            Permission.RUNS_READ_REVIEW,
            Permission.ACTIONS_RESOLVE_REVIEW,
            Permission.ACTIONS_EXPORT_RUN,
            Permission.EXPORTS_DOWNLOAD_DIRECT,
            Permission.ARTIFACTS_LIST,
            Permission.ARTIFACTS_READ_METADATA,
            Permission.ARTIFACTS_DOWNLOAD,
            Permission.OPERATIONS_VIEW_METRICS,
            Permission.OPERATIONS_EXECUTE_RECOVERY,
            Permission.OPERATIONS_EXECUTE_STARTUP_REPAIR,
            Permission.OPERATIONS_MANAGE_ADMIN_SURFACE,
        }
    ),
}


def get_permissions_for_role(role: Role) -> frozenset[Permission]:
    return ROLE_PERMISSIONS.get(role, frozenset())


def role_has_permission(role: Role, permission: Permission) -> bool:
    return permission in get_permissions_for_role(role)