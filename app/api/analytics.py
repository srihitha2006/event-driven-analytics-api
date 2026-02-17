from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
from sqlalchemy import join
from fastapi import Depends

from app.core.rate_limit import rate_limit
from app.db.models import Client
from app.db.session import get_db
from app.db.models import Event
from app.core.security import get_current_client

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/count-by-type", dependencies=[Depends(rate_limit(30))])
async def count_by_type(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    client=Depends(get_current_client),
):
    stmt = select(Event.event_type, func.count()).where(Event.client_id == client.id)

    if start:
        stmt = stmt.where(Event.event_time >= start)
    if end:
        stmt = stmt.where(Event.event_time <= end)

    stmt = stmt.group_by(Event.event_type)

    result = await db.execute(stmt)
    rows = result.all()

    return {event_type: count for event_type, count in rows}

@router.get("/group-by-client-and-type")
async def group_by_client_and_type(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Client.name, Event.event_type, func.count())
        .select_from(join(Event, Client, Event.client_id == Client.id))
    )

    if start:
        stmt = stmt.where(Event.event_time >= start)
    if end:
        stmt = stmt.where(Event.event_time <= end)

    stmt = stmt.group_by(Client.name, Event.event_type).order_by(Client.name)

    result = await db.execute(stmt)
    rows = result.all()

    # return list for easy reading
    return [
        {"client": name, "event_type": etype, "count": cnt}
        for name, etype, cnt in rows
    ]

@router.get("/processing-metrics")
async def processing_metrics(
    db: AsyncSession = Depends(get_db),
    client=Depends(get_current_client),
):
    total_q = select(func.count()).select_from(Event).where(Event.client_id == client.id)
    failed_q = select(func.count()).select_from(Event).where(
        Event.client_id == client.id, Event.status == "failed"
    )
    avg_q = select(func.avg(Event.processing_latency_ms)).select_from(Event).where(
        Event.client_id == client.id,
        Event.processing_latency_ms.isnot(None),
    )

    total = (await db.execute(total_q)).scalar() or 0
    failed = (await db.execute(failed_q)).scalar() or 0
    avg = (await db.execute(avg_q)).scalar()

    return {
        "total_events": int(total),
        "failed_events": int(failed),
        "avg_latency_ms": float(avg) if avg is not None else None,
    }
