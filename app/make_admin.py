import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.settings import settings

async def make_admin(email: str):
    """Make a user an admin by email"""
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db]
    
    user = await db.users.find_one({"email": email})
    if not user:
        print(f"❌ User not found: {email}")
        client.close()
        return
    
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"role": "admin"}}
    )
    
    if result.modified_count > 0:
        print(f"✅ User '{email}' is now an admin!")
    else:
        print(f"⚠️  User '{email}' was already an admin")
    
    # Verify
    updated_user = await db.users.find_one({"email": email})
    print(f"Current role: {updated_user.get('role')}")
    
    client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <email>")
        print("Example: python make_admin.py admin@example.com")
    else:
        asyncio.run(make_admin(sys.argv[1]))