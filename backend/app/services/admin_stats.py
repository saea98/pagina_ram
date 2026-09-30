from datetime import UTC, datetime, timedelta

from app.models.content import BioLinkClick, PortfolioItem
from app.models.enums import LeadStatus
from app.models.leads import Lead
from app.schemas.admin import CountPoint, PiecePlays, StatsOut
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def overview(session: AsyncSession) -> StatsOut:
    now = datetime.now(UTC)
    week_ago = now - timedelta(days=7)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    alive = Lead.deleted_at.is_(None)
    new_leads = await session.scalar(
        select(func.count()).select_from(Lead).where(alive, Lead.created_at >= week_ago)
    )
    won = await session.scalar(
        select(func.count()).select_from(Lead).where(alive, Lead.status == LeadStatus.WON)
    )
    lost = await session.scalar(
        select(func.count()).select_from(Lead).where(alive, Lead.status == LeadStatus.LOST)
    )
    closed = int(won or 0) + int(lost or 0)
    close_rate = None if closed == 0 else round(int(won or 0) / closed, 2)
    source_rows = (
        await session.execute(
            select(Lead.utm_source, func.count())
            .where(alive, Lead.created_at >= month_start)
            .group_by(Lead.utm_source)
            .order_by(func.count().desc())
        )
    ).all()
    top_source = None
    for source, _count in source_rows:
        if source:
            top_source = source
            break
    clicks = await session.scalar(
        select(func.count()).select_from(BioLinkClick).where(BioLinkClick.clicked_at >= week_ago)
    )
    status_rows = (
        await session.execute(select(Lead.status, func.count()).where(alive).group_by(Lead.status))
    ).all()
    source_30 = (
        await session.execute(
            select(Lead.utm_source, func.count())
            .where(alive, Lead.created_at >= now - timedelta(days=30))
            .group_by(Lead.utm_source)
            .order_by(func.count().desc())
        )
    ).all()
    pieces = (
        await session.execute(
            select(PortfolioItem.title, PortfolioItem.play_count)
            .where(PortfolioItem.deleted_at.is_(None))
            .order_by(PortfolioItem.play_count.desc())
            .limit(5)
        )
    ).all()
    weeks: list[CountPoint] = []
    for offset in range(7, -1, -1):
        start = (now - timedelta(days=offset * 7)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=7)
        count = await session.scalar(
            select(func.count())
            .select_from(Lead)
            .where(alive, Lead.created_at >= start, Lead.created_at < end)
        )
        weeks.append(CountPoint(label=start.date().isoformat(), count=int(count or 0)))
    return StatsOut(
        new_leads_7d=int(new_leads or 0),
        close_rate=close_rate,
        top_source_month=top_source,
        link_clicks_7d=int(clicks or 0),
        leads_by_status=[
            CountPoint(label=status.value, count=int(count)) for status, count in status_rows
        ],
        leads_by_source=[
            CountPoint(label=source or "directo", count=int(count)) for source, count in source_30
        ],
        leads_by_week=weeks,
        top_pieces=[PiecePlays(title=title, plays=int(plays)) for title, plays in pieces],
    )
