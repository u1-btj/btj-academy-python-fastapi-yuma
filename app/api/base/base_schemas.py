from __future__ import annotations

from pydantic import Field, BaseModel


class PaginationParams(BaseModel):
    """Request query params for paginated API."""

    page: int = Field(ge=1, default=1)
    item_per_page: int = Field(ge=1, le=100, default=10)


class PaginationMetaResponse(BaseModel):
    total_item: int = Field(default=0)
    item_per_page: int = Field(default=10)
    page: int = Field(default=1)
    total_page: int = Field(default=1)


class BaseResponse(BaseModel):
    status: str = Field(default="success")
    message: str = Field(default="")
