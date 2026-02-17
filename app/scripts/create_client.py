import asyncio
import secrets

from sqlalchemy import select

from app.core.security import hash_api_key
from app.db.session import AsyncSessionLocal
from app.db.models import Client


async def main():
    # 1) Create a random API key
    raw_api_key = secrets.token_urlsafe(32)
    key_hash = hash_api_key(raw_api_key)

    client_name = input("Enter client name (example: client1): ").strip() or "client1"

    async with AsyncSessionLocal() as db:
        # 2) Check if same hash already exists (very rare, but safe)
        existing = await db.execute(select(Client).where(Client.api_key_hash == key_hash))
        if existing.scalar_one_or_none():
            print("Generated key already exists. Run again.")
            return

        # 3) Insert client
        client = Client(
            name=client_name,
            api_key_hash=key_hash,
            rate_limit_per_min=60,
        )
        db.add(client)
        await db.commit()
        await db.refresh(client)

    print("\n✅ Client created!")
    print("Client ID:", client.id)
    print("\n🔑 API KEY (copy this, you won't see it again):")
    print(raw_api_key)


if __name__ == "__main__":
    asyncio.run(main())
