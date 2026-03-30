from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductExportModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(..., description="Associated product-facing run identifier.")
    export_status: Literal["not_ready", "ready", "generated", "failed"] = Field(
        ...,
        description="Product-facing export state.",
    )
    export_format: str = Field(..., description="Requested or generated export format.")
    download_url: Optional[str] = Field(
        default=None,
        description="Download URL if an export artifact is available.",
    )
    generated_at: Optional[str] = Field(
        default=None,
        description="Timestamp string for generated export artifact if available.",
    )