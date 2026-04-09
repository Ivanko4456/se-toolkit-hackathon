"""Statistics and analytics API endpoints."""

from datetime import datetime, timedelta, timezone
from collections import Counter

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, Text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Link
from ..schemas import StatsResponse, StatsTimelineResponse, TagStat

router = APIRouter(prefix="/api/stats", tags=["stats"])


def _now_utc():
    """Return current UTC time as naive datetime (matches DB storage)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get aggregated statistics for the dashboard."""
    now = _now_utc()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    # Total links
    total_result = await db.execute(select(func.count(Link.id)))
    total_links = total_result.scalar() or 0

    # Total unique users
    users_result = await db.execute(select(func.count(func.distinct(Link.user_id))))
    total_users = users_result.scalar() or 0

    # Links in last 7 days
    last_7_result = await db.execute(
        select(func.count(Link.id)).where(Link.created_at >= seven_days_ago)
    )
    links_last_7_days = last_7_result.scalar() or 0

    # Links in last 30 days
    last_30_result = await db.execute(
        select(func.count(Link.id)).where(Link.created_at >= thirty_days_ago)
    )
    links_last_30_days = last_30_result.scalar() or 0

    # Links older than 30 days (potentially forgotten)
    oldest_result = await db.execute(
        select(func.count(Link.id)).where(Link.created_at < thirty_days_ago)
    )
    oldest_links_count = oldest_result.scalar() or 0

    # Top tags: fetch all tags and count occurrences
    all_links = await db.execute(select(Link.tags))
    all_tags_list = all_links.scalars().all()
    
    tag_counter = Counter()
    for tags in all_tags_list:
        if tags:
            tag_counter.update(tags)
    
    top_tags = [
        TagStat(tag=tag, count=count)
        for tag, count in tag_counter.most_common(10)
    ]

    return StatsResponse(
        total_links=total_links,
        total_users=total_users,
        links_last_7_days=links_last_7_days,
        links_last_30_days=links_last_30_days,
        top_tags=top_tags,
        oldest_links_count=oldest_links_count,
    )


@router.get("/timeline", response_model=StatsTimelineResponse)
async def get_timeline(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to include"),
    db: AsyncSession = Depends(get_db),
):
    """Get daily link creation counts for charting."""
    cutoff_date = _now_utc() - timedelta(days=days)
    
    # Query: group by date, count links
    # Works for both PostgreSQL and SQLite
    date_trunc = func.date(Link.created_at)
    
    result = await db.execute(
        select(date_trunc, func.count(Link.id))
        .where(Link.created_at >= cutoff_date)
        .group_by(date_trunc)
        .order_by(date_trunc)
    )
    
    rows = result.all()
    
    # Build a dict of date -> count
    # func.date returns date object on PostgreSQL, string on SQLite
    counts_by_date = {}
    for row in rows:
        date_val = row[0]
        if isinstance(date_val, str):
            date_key = date_val
        else:
            date_key = date_val.isoformat()
        counts_by_date[date_key] = row[1]
    
    # Fill in missing dates with 0
    dates = []
    counts = []
    for i in range(days):
        day = (_now_utc() - timedelta(days=days - 1 - i)).date()
        day_str = day.isoformat()
        dates.append(day_str)
        counts.append(counts_by_date.get(day_str, 0))
    
    return StatsTimelineResponse(dates=dates, counts=counts)
