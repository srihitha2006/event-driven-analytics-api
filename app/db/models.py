import uuid
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, BigInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    api_key_hash = Column(String(128), unique=True, nullable=False)
    rate_limit_per_min = Column(Integer, default=60)

class Event(Base):
    __tablename__ = "events"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_time = Column(DateTime(timezone=True), nullable=False, index=True)
    idempotency_key = Column(String(128), nullable=False)
    payload = Column(JSONB, nullable=False)
    status = Column(String(20), default="queued")
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processing_latency_ms = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("client_id", "idempotency_key", name="uq_client_event_idem"),
    )

class ApiAuditLog(Base):
    __tablename__ = "api_audit_logs"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    client_id = Column(UUID(as_uuid=True), nullable=True)
    method = Column(String(10), nullable=False)
    path = Column(Text, nullable=False)
    status_code = Column(Integer, nullable=False)
    duration_ms = Column(Integer, nullable=False)
    ip = Column(String(64), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
