import asyncio
import sys
sys.path.insert(0, '.')

from app.db.mongo import get_db_client
from app.utils.mongo_helpers import normalize_id

async def test_fetch():
    client = await get_db_client()
    db = client.listings_db
    
    print("Testing fetch latest listings...")
    try:
        cursor = db.listings.find({}).sort("posted_date", -1).limit(3)
        results = []
        async for doc in cursor:
            normalized = normalize_id(doc)
            print(f"Found listing: {normalized.get('title')}")
            results.append(normalized)
        
        print(f"\nTotal found: {len(results)}")
        
        if results:
            print(f"\nFirst listing details:")
            first = results[0]
            for key, value in first.items():
                if key != 'embedding':  # Skip embedding as it's too long
                    print(f"  {key}: {type(value).__name__} = {value}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_fetch())
