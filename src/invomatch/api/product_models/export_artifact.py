from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ArtifactLifecycleState(str, Enum):
    AVAILABLE = "available"
    EXPIRED = "expired"
    DELETED = "deleted"
    FAILED = "failed"


class ExportArtifactResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    artifact_type: str = Field(min_length=1)
    format: str = Field(min_length=1)
    file_name: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    size_bytes: int = Field(ge=0)
    state: ArtifactLifecycleState
    created_at: datetime
    expires_at: datetime | None = None
    download_available: bool


class ExportArtifactListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    artifacts: list[ExportArtifactResource] = Field(default_factory=list)


class ExportArtifactMetadataResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact: ExportArtifactResource


class ArtifactErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)