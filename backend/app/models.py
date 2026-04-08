"""SQLAlchemy models for the links table."""

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Index, String, Text, text, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TEXT

from .database import Base


def _now_utc():
    """Return timezone-aware UTC datetime without tzinfo (for TIMESTAMP WITHOUT TIME ZONE)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TagsList(TypeDecorator):
    """Cross-dialect tags column: stored as JSON TEXT in all databases."""

    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return "[]"
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []


class Link(Base):
    __tablename__ = "links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    tags = Column(TagsList, nullable=False, default=list)
    user_id = Column(Text, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=_now_utc)
