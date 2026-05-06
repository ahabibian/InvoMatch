from __future__ import annotations

from dataclasses import dataclass


UNKNOWN_RELEASE_VALUE = "unknown"
DEFAULT_APPLICATION_NAME = "invomatch"
DEFAULT_APPLICATION_VERSION = "0.1.0"
DEFAULT_RELEASE_VALIDATION_STATUS = "not_declared"


@dataclass(frozen=True)
class ReleaseIdentity:
    application_name: str
    application_version: str
    git_commit_sha: str
    git_branch: str
    build_timestamp_utc: str | None
    environment: str
    validation_status: str
    metadata_available: bool
