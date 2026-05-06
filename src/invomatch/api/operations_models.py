from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


OperationalVisibilityStatus = Literal["healthy", "degraded", "attention_required"]
OperationalAlertStatus = Literal["clear", "active"]
OperationalAlertSeverity = Literal["info", "warning", "critical"]
OperationalRecommendedAction = Literal[
    "none",
    "inspect_startup_repair",
    "inspect_terminal_failures",
    "inspect_recovery_activity",
]


class OperationalMetricsResponse(BaseModel):
    status: OperationalVisibilityStatus = Field(
        description="Overall operational condition derived from normalized signals."
    )
    generated_at: str = Field(
        description="ISO-8601 timestamp indicating when the condition was generated."
    )
    signals: dict[str, int] = Field(
        description="Normalized operational signal counters consumed by UI and alert policy."
    )
    counters: dict[str, int] = Field(
        description="Raw operational counters captured by the metrics service."
    )
    decision_counts: dict[str, int] = Field(
        description="Counts grouped by operational recovery decision."
    )
    reason_counts: dict[str, int] = Field(
        description="Counts grouped by operational recovery reason code."
    )


class OperationalHealthSummaryResponse(BaseModel):
    status: OperationalVisibilityStatus = Field(
        description="Overall operational condition derived from normalized signals."
    )
    generated_at: str = Field(
        description="ISO-8601 timestamp indicating when the condition was generated."
    )
    summary: dict[str, str] = Field(
        description="Human-readable operational summary grouped by operational area."
    )
    signals: dict[str, int] = Field(
        description="Normalized operational signal counters used to build the health summary."
    )
    recommended_action: OperationalRecommendedAction = Field(
        description="Machine-readable recommended operator action."
    )


class OperationalAlertResponse(BaseModel):
    code: str = Field(
        description="Stable machine-readable alert code."
    )
    severity: OperationalAlertSeverity = Field(
        description="Alert severity intended for operator-facing UI prioritization."
    )
    message: str = Field(
        description="Human-readable alert message."
    )
    recommended_action: OperationalRecommendedAction = Field(
        description="Machine-readable recommended operator action."
    )
    signal: str = Field(
        description="Operational signal that triggered the alert."
    )
    value: int = Field(
        description="Signal value observed when the alert was generated."
    )


class OperationalAlertsResponse(BaseModel):
    status: OperationalAlertStatus = Field(
        description="Whether active operational alerts exist."
    )
    generated_at: str = Field(
        description="ISO-8601 timestamp indicating when alerts were evaluated."
    )
    alerts: list[OperationalAlertResponse] = Field(
        description="Stable ordered list of machine-readable operational alerts."
    )

class OperationalReleaseIdentityResponse(BaseModel):
    application_name: str = Field(
        description="Stable application identifier."
    )
    application_version: str = Field(
        description="Application version or internal release version."
    )
    git_commit_sha: str = Field(
        description="Git commit SHA associated with this runtime, or unknown when not provided."
    )
    git_branch: str = Field(
        description="Git branch or ref associated with this runtime, or unknown when not provided."
    )
    build_timestamp_utc: str | None = Field(
        description="UTC build timestamp when explicitly provided by release tooling."
    )
    environment: str = Field(
        description="Configured InvoMatch runtime environment name."
    )
    validation_status: str = Field(
        description="Release validation status explicitly provided by release tooling, or not_declared."
    )
    metadata_available: bool = Field(
        description="Whether concrete commit and branch metadata were explicitly provided."
    )
