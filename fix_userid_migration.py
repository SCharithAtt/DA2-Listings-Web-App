"""
Migration script to fix userId field from ObjectId to string
This fixes the batch-inserted listings that have ObjectId userId
"""
import asyncio
from app.db.mongo import connect_to_mongo, get_db
from bson import ObjectId

async def fix_userid_types():
    await connect_to_mongo()
    db = get_db()
    
    print("=" * 70)
    print("FIXING userId FIELD TYPES")
    print("=" * 70)
    
    # Find all listings where userId is ObjectId
    cursor = db.listings.find({"userId": {"$type": "objectId"}})
    
    count = 0
    async for listing in cursor:
        old_user_id = listing["userId"]
        new_user_id = str(old_user_id)
        
        # Update the listing
        await db.listings.update_one(
            {"_id": listing["_id"]},
            {"$set": {"userId": new_user_id}}
        )
        
        count += 1
        print(f"✅ Fixed listing: {listing.get('title', 'Unknown')[:50]}")
        print(f"   Old userId: {old_user_id} (ObjectId)")
        print(f"   New userId: {new_user_id} (string)")
    
    print("\n" + "=" * 70)
    print(f"✅ Fixed {count} listings")
    print("=" * 70)
    
    # Verify
    remaining = await db.listings.count_documents({"userId": {"$type": "objectId"}})
    if remaining == 0:
        print("✅ All userId fields are now strings!")
    else:
        print(f"⚠️  Warning: {remaining} listings still have ObjectId userId")

if __name__ == "__main__":
    asyncio.run(fix_userid_types())
