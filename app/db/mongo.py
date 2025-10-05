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
    if _db is None:
        raise RuntimeError("Database not initialized. Make sure connect_to_mongo() was called on startup.")
    return _db


async def ensure_indexes():
    try:
        db = get_db()

        # Users
        try:
            await db.users.create_index("email", unique=True)
        except Exception:
            pass  # Index might already exist

        # Listings
        try:
            # Text index on title, description, tags
            await db.listings.create_index(
                [("title", "text"), ("description", "text"), ("tags", "text")],
                name="listings_text_index",
                default_language="english",
            )
        except Exception:
            pass  # Index might already exist
        
        try:
            # 2dsphere index on coordinates
            await db.listings.create_index([("location", "2dsphere")], name="location_2dsphere")
        except Exception:
            pass
        
        try:
            # userId index
            await db.listings.create_index("userId", name="userId_index")
        except Exception:
            pass
        
        try:
            # category index
            await db.listings.create_index("category", name="category_index")
        except Exception:
            pass
        
        try:
            await db.listings.create_index("posted_date", name="posted_date_index")
        except Exception:
            pass

        # Analytics summary timestamp index
        try:
            await db.analytics_summary.create_index("generatedAt", name="generatedAt_index")
        except Exception:
            pass
    except Exception as e:
        print(f"Warning: Error ensuring indexes: {e}")
