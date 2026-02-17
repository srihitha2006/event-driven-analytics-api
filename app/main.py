from fastapi import FastAPI
from app.core.security import get_current_client
from fastapi import Depends
from app.api.events import router as events_router
from app.api.analytics import router as analytics_router
from app.core.audit_middleware import AuditMiddleware

app = FastAPI(title="Event Analytics API")
app.include_router(events_router)
app.include_router(analytics_router)
app.add_middleware(AuditMiddleware)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/protected")
async def protected_route(client=Depends(get_current_client)):
    return {
        "message": "Authenticated successfully",
        "client_id": str(client.id),
        "client_name": client.name
    }