import asyncio
from app.utils.settings import settings
from app.utils.embeddings import embed_text
from app.db.mongo import connect_to_mongo, get_db, close_mongo_connection


def corpus(doc: dict) -> str:
    """
    Enhanced corpus generation with category context and synonym expansion
    for better semantic embeddings - matches the logic in listings.py
    """
    parts = [
        doc.get("title") or "",
        doc.get("description") or "",
    ]
    
    # Add category context
    category = doc.get("category", "")
    if category:
        parts.append(f"Category: {category}")
    
    # Expand tags with synonyms
    tags = doc.get("tags") or []
    expanded_tags = list(tags)
    
    for tag in tags:
        tag_lower = tag.lower()
        
        # Brand/product expansions
        if "iphone" in tag_lower or "apple" in tag_lower:
            expanded_tags.extend(["Apple smartphone", "iOS phone", "Apple device"])
        elif "samsung" in tag_lower:
            expanded_tags.extend(["Samsung smartphone", "Android phone", "Galaxy device"])
        elif "oneplus" in tag_lower or "one plus" in tag_lower:
            expanded_tags.extend(["OnePlus smartphone", "Android phone", "One Plus device"])
        elif "lexus" in tag_lower:
            expanded_tags.extend(["Lexus vehicle", "luxury car", "Toyota premium brand"])
        elif "toyota" in tag_lower:
            expanded_tags.extend(["Toyota vehicle", "automobile", "car"])
        elif "honda" in tag_lower:
            expanded_tags.extend(["Honda vehicle", "automobile", "car", "motorcycle"])
        elif "retriever" in tag_lower or "dog" in tag_lower:
            expanded_tags.extend(["pet dog", "canine", "puppy", "animal companion"])
        elif "cat" in tag_lower:
            expanded_tags.extend(["pet cat", "feline", "kitten", "animal companion"])
        elif "boat" in tag_lower:
            expanded_tags.extend(["water vessel", "marine vehicle", "watercraft"])
        elif "laptop" in tag_lower or "notebook" in tag_lower:
            expanded_tags.extend(["portable computer", "laptop computer", "notebook computer"])
        elif "phone" in tag_lower and "iphone" not in tag_lower:
            expanded_tags.extend(["smartphone", "mobile phone", "cell phone"])
    
    if expanded_tags:
        parts.append(" ".join(expanded_tags))
    
    # Add city for location awareness
    city = doc.get("city") or ""
    if city:
        parts.append(f"Location: {city}")
    
    return " | ".join([p for p in parts if p])


async def run():
    if not settings.enable_semantic_search:
        print("⚠️  ENABLE_SEMANTIC_SEARCH is false; enable it in .env before backfilling.")
        return
    
    print("=" * 60)
    print("Enhanced Embeddings Backfill Script")
    print("=" * 60)
    
    await connect_to_mongo()
    db = get_db()
    
    # Get all listings (will regenerate all embeddings with enhanced corpus)
    print("\n🔍 Searching for listings to update...")
    cursor = db.listings.find({}, {"title": 1, "description": 1, "tags": 1, "city": 1, "category": 1})
    
    count = 0
    total = await db.listings.count_documents({})
    
    print(f"📊 Found {total} total listings in database")
    print("\n🚀 Starting embedding generation with enhanced corpus...\n")
    
    async for doc in cursor:
        title = doc.get("title", "Untitled")
        enhanced_corpus = corpus(doc)
        
        print(f"[{count + 1}/{total}] Processing: {title}")
        print(f"  📝 Enhanced corpus preview: {enhanced_corpus[:150]}...")
        
        vec = embed_text(enhanced_corpus)
        print(f"  ✅ Generated {len(vec)}-dimensional embedding")
        
        await db.listings.update_one({"_id": doc["_id"]}, {"$set": {"embedding": vec}})
        count += 1
        print()
    
    print("=" * 60)
    print(f"✅ Successfully backfilled embeddings for {count} listings!")
    print("=" * 60)
    print("\n💡 Your listings now have enhanced embeddings that understand:")
    print("   • Brand synonyms (Apple → iPhone)")
    print("   • Product categories")
    print("   • Common variations and related terms")
    print("\n🎯 Try searching with queries like:")
    print("   • 'Apple Phone' (will match iPhone)")
    print("   • 'luxury car' (will match Lexus)")
    print("   • 'dog' (will match retriever, puppy, etc.)")
    print()
    
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(run())
