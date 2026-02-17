import asyncio
import json
import os
from datetime import datetime, timezone

import redis
from dotenv import load_dotenv
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models import Event

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

QUEUE_NAME = "events_queue"


async def process_one(event_id: int):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Event).where(Event.id == event_id))
        ev = result.scalar_one_or_none()
        if not ev:
            return

        # mark processed + latency
        now = datetime.now(timezone.utc)
        ev.status = "processed"
        ev.processed_at = now

        if ev.received_at:
            ev.processing_latency_ms = int((now - ev.received_at).total_seconds() * 1000)

        await db.commit()


async def main():
    print("👷 Worker started. Waiting for events...")

    while True:
        item = r.brpop(QUEUE_NAME, timeout=5)  # (queue, value)
        if not item:
            await asyncio.sleep(0.2)
            continue

        _, value = item
        try:
            data = json.loads(value)
            event_id = int(data["event_id"])
            await process_one(event_id)
            print(f"✅ Processed event_id={event_id}")
        except Exception as e:
            print("❌ Worker error:", str(e))


if __name__ == "__main__":
    asyncio.run(main())
