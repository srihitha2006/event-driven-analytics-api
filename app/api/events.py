import json
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import Depends

from app.core.rate_limit import rate_limit
from app.db.session import get_db
from app.db.models import Event
from app.core.security import get_current_client
from app.schemas.events import EventIn

import redis
import os
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

router = APIRouter(prefix="/events", tags=["Events"])

def make_idempotency_key(client_id: str, e: EventIn) -> str:
    if e.idempotency_key:
        return e.idempotency_key
    raw = f"{client_id}:{e.event_type}:{e.event_time.isoformat()}:{json.dumps(e.payload, sort_keys=True)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

@router.post("/ingest", status_code=202, dependencies=[Depends(rate_limit(5))])
async def ingest_event(
    event: EventIn,
    db: AsyncSession = Depends(get_db),
    client = Depends(get_current_client),
):
    idem = make_idempotency_key(str(client.id), event)

    new_event = Event(
        client_id=client.id,
        event_type=event.event_type,
        event_time=event.event_time,
        idempotency_key=idem,
        payload=event.payload,
        status="queued",
    )

    db.add(new_event)
    try:
        await db.commit()
        await db.refresh(new_event)
    except IntegrityError:
        await db.rollback()
        # Duplicate (same client_id + idempotency_key)
        return {"status": "duplicate_ignored", "idempotency_key": idem}

    # Push to Redis queue
    r.lpush("events_queue", json.dumps({"event_id": new_event.id}))

    return {"status": "queued", "event_id": new_event.id, "idempotency_key": idem}
