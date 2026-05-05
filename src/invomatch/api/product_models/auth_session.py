from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProductAuthSessionUser(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1)
    username: str = Field(min_length=1)
    role: str = Field(min_length=1)
    status: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    auth_source: str = Field(min_length=1)


class ProductAuthSessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user: ProductAuthSessionUser
    permissions: list[str] = Field(default_factory=list)