Event-Driven Analytics & Audit API
🚀 Overview

This project is a production-style Event-Driven Analytics & Audit API built using FastAPI, PostgreSQL, and Redis.

It supports high-throughput event ingestion, background processing, per-client API authentication, rate limiting, analytics queries, and full audit logging.

🏗 Architecture

- FastAPI – API layer (async)

- PostgreSQL – Event storage (time-series friendly schema)

- Redis – Queue + rate limiting

- Alembic – Database migrations

- Background Worker – Event processing engine

- API Key Authentication – Per-client access control

- Middleware – Audit logging

🔐 Features
✅ API Key Authentication

- Clients authenticate using X-API-Key header

- Keys are hashed and stored securely

- Unauthorized requests return 401

✅ Rate Limiting (Per API Key)

- Redis-based fixed window rate limiting

- Returns 429 Too Many Requests

✅ Async Event Ingestion

- POST /events/ingest

- Returns 202 Accepted

- Supports high-throughput ingestion

✅ Idempotency

- Prevents duplicate event processing

- Uses (client_id + idempotency_key) unique constraint

✅ Redis Queue

- Events pushed to events_queue

- Decouples ingestion from processing

✅ Background Worker

- Processes queued events

- Updates status from queued → processed

- Tracks processing latency

✅ PostgreSQL Storage

Tables:

- clients

- events

- api_audit_logs

Optimized with:

- Indexes on event_type, client_id, event_time

- Unique constraints for idempotency

✅ Analytics APIs

- GET /analytics/count-by-type

- GET /analytics/group-by-client-and-type

- GET /analytics/processing-metrics

- Filter by time range

✅ Audit Logging

Every API request is logged:

- method

- path

- status code

- duration

- client_id

- timestamp

✅ Health Check

- GET /health

- Returns system status

📦 Installation
1️⃣ Clone the repository
git clone <repo-url>
cd event_analytics_api

2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate   (Windows)

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Configure environment

Create .env file:

DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost:5432/eventdb
REDIS_URL=redis://localhost:6379/0

5️⃣ Run migrations
alembic upgrade head

6️⃣ Start Redis (Docker)
docker run -d --name redis-events -p 6379:6379 redis

7️⃣ Start API
uvicorn app.main:app --reload


API Docs:

http://127.0.0.1:8000/docs

👷 Running the Worker

Open a new terminal:

python -m app.queue.worker


Worker listens to Redis queue and processes events.

🔎 Example Event Payload
{
  "event_type": "login",
  "event_time": "2026-02-17T15:23:14.119Z",
  "payload": {
    "user_id": 123
  }
}


Header:

X-API-Key: <your_api_key>

📊 HTTP Status Codes

- 200 – Success

- 202 – Event accepted and queued

- 401 – Unauthorized (invalid/missing API key)

- 429 – Rate limit exceeded

- 500 – Internal error

🎯 Design Highlights

- Fully async architecture

- Event-driven processing

- Decoupled ingestion & processing

- Observability via audit logs

- Production-style rate limiting

- Scalable queue-based design