import asyncio
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.settings import settings


async def run():
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db]

    # Aggregation: listings per city
    per_city = [
        {"$group": {"_id": "$city", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    per_city_res = [x async for x in db.listings.aggregate(per_city)]

    # Aggregation: listings per category
    per_category = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    per_category_res = [x async for x in db.listings.aggregate(per_category)]

    # Most common tags (top 20)
    common_tags = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
    ]
    common_tags_res = [x async for x in db.listings.aggregate(common_tags)]

    # Daily new listings (last 30 days) by day based on _id timestamp
    daily_new = [
        {"$addFields": {"createdAt": {"$toDate": "$_id"}}},
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$createdAt"}}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    daily_new_res = [x async for x in db.listings.aggregate(daily_new)]

    summary = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "perCity": per_city_res,
    "perCategory": per_category_res,
        "commonTags": common_tags_res,
        "dailyNew": daily_new_res,
    }

    await db.analytics_summary.insert_one(summary)
    client.close()


if __name__ == "__main__":
    asyncio.run(run())
