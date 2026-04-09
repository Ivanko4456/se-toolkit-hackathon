"""Pydantic v2 schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class LinkCreate(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    user_id: str


class LinkUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    title: Optional[str] = None
    tags: Optional[list[str]] = None


class LinkResponse(BaseModel):
    id: UUID
    url: str
    title: Optional[str] = None
    tags: list[str]
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LinkListResponse(BaseModel):
    links: list[LinkResponse]
    total: int


class TagStat(BaseModel):
    """Tag frequency statistic."""
    tag: str
    count: int


class StatsResponse(BaseModel):
    """Aggregated statistics for the dashboard."""
    total_links: int
    total_users: int
    links_last_7_days: int
    links_last_30_days: int
    top_tags: list[TagStat]
    oldest_links_count: int  # links older than 30 days


class StatsTimelineResponse(BaseModel):
    """Daily link creation timeline for charting."""
    dates: list[str]  # ISO date strings
    counts: list[int]
