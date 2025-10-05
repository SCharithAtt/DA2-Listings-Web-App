import asyncio
from app.db.mongo import connect_to_mongo, get_db
from bson import ObjectId

async def check_batch_listing():
    await connect_to_mongo()
    db = get_db()
    
    # Get one listing from recent batch insert (Apple iPhone from batch)
    listing = await db.listings.find_one({"title": {"$regex": "Apple iPhone 14"}})
    
    if listing:
        print("Batch-inserted listing structure:")
        print(f"_id: {listing.get('_id')} (type: {type(listing.get('_id')).__name__})")
        print(f"title: {listing.get('title')}")
        
        userId = listing.get('userId')
        print(f"\nuserId: {userId}")
        print(f"userId type: {type(userId).__name__}")
        print(f"Is ObjectId?: {isinstance(userId, ObjectId)}")
        print(f"Is string?: {isinstance(userId, str)}")
        
        location = listing.get('location')
        print(f"\nlocation: {location}")
        print(f"location type: {type(location).__name__}")
        
        print("\n\nAll fields:")
        for key, value in listing.items():
            value_type = type(value).__name__
            value_str = str(value)[:80] if not isinstance(value, list) else f"[{len(value)} items]"
            print(f"  {key}: {value_type} = {value_str}")
    else:
        print("No batch listing found")
        
        # Show what we have
        count = await db.listings.count_documents({})
        print(f"\nTotal listings: {count}")
        
        # Show a sample
        sample = await db.listings.find_one({})
        if sample:
            print(f"\nSample listing title: {sample.get('title')}")

asyncio.run(check_batch_listing())
