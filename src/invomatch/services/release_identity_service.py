from __future__ import annotations

import os

from invomatch.domain.release_identity import (
    DEFAULT_APPLICATION_NAME,
    DEFAULT_APPLICATION_VERSION,
    DEFAULT_RELEASE_VALIDATION_STATUS,
    UNKNOWN_RELEASE_VALUE,
    ReleaseIdentity,
)


_SAFE_ENV_KEYS = {
    "application_name": "INVOMATCH_APPLICATION_NAME",
    "application_version": "INVOMATCH_APPLICATION_VERSION",
    "git_commit_sha": "INVOMATCH_RELEASE_COMMIT_SHA",
    "git_branch": "INVOMATCH_RELEASE_BRANCH",
    "build_timestamp_utc": "INVOMATCH_RELEASE_BUILD_TIMESTAMP_UTC",
    "validation_status": "INVOMATCH_RELEASE_VALIDATION_STATUS",
}


class ReleaseIdentityService:
    """Builds product-safe release identity metadata from explicit runtime settings.

    This service intentionally reads only a bounded allow-list of release metadata
    environment variables. It does not expose arbitrary environment variables,
    secrets, token configuration, persistence paths, or CI internals.
    """

    def __init__(
        self,
        *,
        environment: str,
        application_name: str | None = None,
        application_version: str | None = None,
        git_commit_sha: str | None = None,
        git_branch: str | None = None,
        build_timestamp_utc: str | None = None,
        validation_status: str | None = None,
    ) -> None:
        self._environment = _clean_required(environment, fallback=UNKNOWN_RELEASE_VALUE)
        self._application_name = _clean_required(
            application_name
            if application_name is not None
            else os.getenv(_SAFE_ENV_KEYS["application_name"]),
            fallback=DEFAULT_APPLICATION_NAME,
        )
        self._application_version = _clean_required(
            application_version
            if application_version is not None
            else os.getenv(_SAFE_ENV_KEYS["application_version"]),
            fallback=DEFAULT_APPLICATION_VERSION,
        )
        self._git_commit_sha = _clean_required(
            git_commit_sha
            if git_commit_sha is not None
            else os.getenv(_SAFE_ENV_KEYS["git_commit_sha"]),
            fallback=UNKNOWN_RELEASE_VALUE,
        )
        self._git_branch = _clean_required(
            git_branch
            if git_branch is not None
            else os.getenv(_SAFE_ENV_KEYS["git_branch"]),
            fallback=UNKNOWN_RELEASE_VALUE,
        )
        self._build_timestamp_utc = _clean_optional(
            build_timestamp_utc
            if build_timestamp_utc is not None
            else os.getenv(_SAFE_ENV_KEYS["build_timestamp_utc"])
        )
        self._validation_status = _clean_required(
            validation_status
            if validation_status is not None
            else os.getenv(_SAFE_ENV_KEYS["validation_status"]),
            fallback=DEFAULT_RELEASE_VALIDATION_STATUS,
        )

    def get_release_identity(self) -> ReleaseIdentity:
        metadata_available = (
            self._git_commit_sha != UNKNOWN_RELEASE_VALUE
            and self._git_branch != UNKNOWN_RELEASE_VALUE
        )

        return ReleaseIdentity(
            application_name=self._application_name,
            application_version=self._application_version,
            git_commit_sha=self._git_commit_sha,
            git_branch=self._git_branch,
            build_timestamp_utc=self._build_timestamp_utc,
            environment=self._environment,
            validation_status=self._validation_status,
            metadata_available=metadata_available,
        )


def _clean_required(value: str | None, *, fallback: str) -> str:
    cleaned = _clean_optional(value)
    if cleaned is None:
        return fallback
    return cleaned


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned:
        return None
    return cleaned
