import asyncio
from app.utils.settings import settings
from app.utils.embeddings import embed_text
from app.db.mongo import connect_to_mongo, get_db, close_mongo_connection


def corpus(doc: dict) -> str:
    parts = [
        doc.get("title") or "",
        doc.get("description") or "",
        " ".join(doc.get("tags") or []),
        doc.get("city") or "",
    ]
    return " | ".join([p for p in parts if p])


async def run():
    if not settings.enable_semantic_search:
        print("ENABLE_SEMANTIC_SEARCH is false; enable it in .env before backfilling.")
        return
    await connect_to_mongo()
    db = get_db()
    cursor = db.listings.find({"$or": [{"embedding": {"$exists": False}}, {"embedding": None}]},
                               {"title": 1, "description": 1, "tags": 1, "city": 1})
    count = 0
    async for doc in cursor:
        vec = embed_text(corpus(doc))
        await db.listings.update_one({"_id": doc["_id"]}, {"$set": {"embedding": vec}})
        count += 1
    print(f"Backfilled embeddings for {count} listings")
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(run())
