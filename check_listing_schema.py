import asyncio
from app.db.mongo import connect_to_mongo, get_db

async def check_listing_fields():
    await connect_to_mongo()
    db = get_db()
    
    # Get one listing to inspect
    listing = await db.listings.find_one({})
    
    if listing:
        print("Sample listing fields:")
        for key, value in listing.items():
            value_str = str(value)[:50] if not isinstance(value, (int, float, bool)) else value
            print(f"  {key}: {type(value).__name__} = {value_str}")
    else:
        print("No listings found!")

if __name__ == "__main__":
    asyncio.run(check_listing_fields())
