"""Link CRUD API endpoints."""

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, Text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Link
from ..schemas import LinkCreate, LinkListResponse, LinkResponse

router = APIRouter(prefix="/api/links", tags=["links"])


@router.post("", response_model=LinkResponse, status_code=201)
async def create_link(data: LinkCreate, db: AsyncSession = Depends(get_db)):
    """Save a new link."""
    link = Link(
        url=str(data.url),
        title=data.title,
        tags=data.tags,
        user_id=data.user_id,
    )
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return link


def _tag_filter_expr(tag: str, dialect_name: str):
    """Build a tag filter that works when tags are stored as JSON TEXT in any DB."""
    # tags stored as JSON text: '["tag1", "tag2"]'
    # Match tag as exact JSON array element in all possible positions
    from sqlalchemy import cast
    return (
        # Single element array: ["tag"]
        (cast(Link.tags, Text) == f'["{tag}"]') |
        # First element: ["tag", ...]
        (cast(Link.tags, Text).like(f'["{tag}", %')) |
        # Last element: [..., "tag"]
        (cast(Link.tags, Text).like(f'[%, "{tag}"]')) |
        # Middle element: [..., "tag", ...]
        (cast(Link.tags, Text).like(f'%, "{tag}", %'))
    )


@router.get("", response_model=LinkListResponse)
async def list_links(
    tag: str | None = Query(None, description="Filter by tag"),
    user_id: str | None = Query(None, description="Filter by user_id"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List links with optional tag filter."""
    query = select(Link)
    count_query = select(func.count(Link.id))

    # Determine dialect for tag filtering
    dialect_name = db.get_bind().dialect.name

    if tag:
        tag_expr = _tag_filter_expr(tag, dialect_name)
        query = query.where(tag_expr)
        count_query = count_query.where(tag_expr)
    if user_id:
        query = query.where(Link.user_id == user_id)
        count_query = count_query.where(Link.user_id == user_id)

    # Count total
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Fetch paginated results
    query = query.order_by(Link.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    links = result.scalars().all()

    return LinkListResponse(links=links, total=total)


@router.get("/{link_id}", response_model=LinkResponse)
async def get_link(link_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single link by ID."""
    result = await db.execute(select(Link).where(Link.id == link_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@router.delete("/{link_id}", status_code=204)
async def delete_link(
    link_id: UUID,
    user_id: str = Query(..., description="User ID for authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Delete a link (protected by user_id)."""
    result = await db.execute(select(Link).where(Link.id == link_id, Link.user_id == user_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found or access denied")
    await db.delete(link)
    return None
