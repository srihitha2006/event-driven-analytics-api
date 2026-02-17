import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models import ApiAuditLog
from app.core.security import hash_api_key
from sqlalchemy import select
from app.db.models import Client


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()

        # Read API key (if present)
        api_key = request.headers.get("X-API-Key")
        client_id = None

        try:
            if api_key:
                key_hash = hash_api_key(api_key)
                async with AsyncSessionLocal() as db:
                    res = await db.execute(select(Client).where(Client.api_key_hash == key_hash))
                    client = res.scalar_one_or_none()
                    if client:
                        client_id = client.id
        except:
            # even if lookup fails, we still want audit log
            pass

        response = await call_next(request)

        duration_ms = int((time.time() - start) * 1000)

        # Save audit log
        try:
            async with AsyncSessionLocal() as db:
                log = ApiAuditLog(
                    client_id=client_id,
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    ip=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
                db.add(log)
                await db.commit()
        except:
            pass

        return response
