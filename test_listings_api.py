import asyncio
from app.db.mongo import connect_to_mongo, get_db

async def test_listings():
    # Connect to MongoDB
    await connect_to_mongo()
    db = get_db()
    
    # Fetch latest listings
    cursor = db.listings.find({}).sort("posted_date", -1).limit(5)
    results = []
    async for doc in cursor:
        results.append({
            "_id": str(doc["_id"]),
            "title": doc.get("title"),
            "price": doc.get("price"),
            "city": doc.get("city"),
            "category": doc.get("category"),
            "images": doc.get("images", [])
        })
    
    print(f"Found {len(results)} listings:")
    for listing in results:
        print(f"  - {listing['title']} | Rs {listing['price']:,} | {listing['city']}")
        print(f"    Category: {listing['category']}")
        print(f"    Images: {len(listing.get('images', []))} image(s)")
    
    return results

if __name__ == "__main__":
    listings = asyncio.run(test_listings())
    print(f"\n✅ Successfully fetched {len(listings)} listings from database")
