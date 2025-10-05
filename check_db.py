import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_db():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['ListingsApp']
    
    # Check if there are any listings
    count = await db.listings.count_documents({})
    print(f"Total listings in database: {count}")
    
    # Get one listing to see its structure
    doc = await db.listings.find_one()
    if doc:
        print("\nFields in listing document:")
        for key, value in doc.items():
            value_type = type(value).__name__
            if isinstance(value, list):
                value_preview = f"[{len(value)} items]"
            elif isinstance(value, dict):
                value_preview = f"{{...}}"
            elif isinstance(value, str) and len(str(value)) > 50:
                value_preview = f"{str(value)[:50]}..."
            else:
                value_preview = str(value)
            print(f"  {key}: {value_type} = {value_preview}")
    else:
        print("\nNo listings found in database")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(check_db())
