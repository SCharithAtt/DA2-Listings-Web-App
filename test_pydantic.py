import asyncio
from app.db.mongo import connect_to_mongo, get_db
from app.models.listing import ListingOut
from app.utils.mongo_helpers import normalize_id

async def test_pydantic_validation():
    await connect_to_mongo()
    db = get_db()
    
    cursor = db.listings.find({}).sort("posted_date", -1).limit(3)
    
    async for doc in cursor:
        normalized = normalize_id(doc)
        if 'embedding' in normalized:
            del normalized['embedding']
        
        print(f"\n===== Testing: {normalized.get('title')} =====")
        print(f"Fields present: {list(normalized.keys())}")
        
        try:
            listing_out = ListingOut(**normalized)
            print(f"✅ Pydantic validation passed!")
            print(f"   ID: {listing_out.id}")
            print(f"   Title: {listing_out.title}")
            print(f"   Price: Rs {listing_out.price:,}")
        except Exception as e:
            print(f"❌ Pydantic validation FAILED: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            # Show which field is problematic
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pydantic_validation())
