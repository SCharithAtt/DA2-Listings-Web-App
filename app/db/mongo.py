from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.utils.settings import settings

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo():
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
        _db = _client[settings.mongodb_db]


async def close_mongo_connection():
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_db() -> AsyncIOMotorDatabase:
    assert _db is not None, "Database not initialized."
    return _db


async def ensure_indexes():
    db = get_db()

    # Users
    await db.users.create_index("email", unique=True)

    # Listings
    # Text index on title, description, tags
    await db.listings.create_index(
        [("title", "text"), ("description", "text"), ("tags", "text")],
        name="listings_text_index",
        default_language="english",
    )
    # 2dsphere index on coordinates
    await db.listings.create_index([("location", "2dsphere")], name="location_2dsphere")
    # userId index
    await db.listings.create_index("userId", name="userId_index")

    # Analytics summary timestamp index
    await db.analytics_summary.create_index("generatedAt", name="generatedAt_index")
