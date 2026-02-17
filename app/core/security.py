import hashlib
from fastapi import Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import Client


def hash_api_key(raw_key: str) -> str:
    # store only the hash in DB (never store raw key)
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


async def get_current_client(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> Client:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")

    key_hash = hash_api_key(x_api_key)

    result = await db.execute(select(Client).where(Client.api_key_hash == key_hash))
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return client
