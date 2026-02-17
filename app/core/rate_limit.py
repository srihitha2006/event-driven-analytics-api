import time
from fastapi import Header, HTTPException
import redis
import os
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def rate_limit(max_requests: int, window_seconds: int = 60):
    """
    Fixed-window rate limit per API key.
    Example: 60 req per 60 sec.
    """
    def dependency(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        if not x_api_key:
            raise HTTPException(status_code=401, detail="Missing X-API-Key header")

        now = int(time.time())
        window = now // window_seconds  # fixed window bucket
        key = f"rl:{x_api_key}:{window}"

        current = r.incr(key)
        if current == 1:
            r.expire(key, window_seconds + 2)

        if current > max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    return dependency
