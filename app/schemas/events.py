from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional

class EventIn(BaseModel):
    event_type: str = Field(min_length=1, max_length=100)
    event_time: datetime
    payload: Dict[str, Any]
    idempotency_key: Optional[str] = Field(default=None, max_length=128)
