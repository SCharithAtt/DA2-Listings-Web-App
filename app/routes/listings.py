from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, UploadFile, File

from app.db.mongo import get_db
from app.models.listing import ListingCreate, ListingUpdate, ListingOut, Category
from app.routes.auth import get_current_user_id
from app.utils.mongo_helpers import normalize_id
from app.utils.settings import settings
from app.utils.embeddings import embed_text
from app.services.storage import save_image
import math


router = APIRouter()


def _to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")


def _listing_corpus(doc: dict) -> str:
    """
    Enhanced corpus generation with category context and synonym expansion
    for better semantic embeddings
    """
    parts = [
        doc.get("title") or "",
        doc.get("description") or "",
    ]
    
    # Add category context to help model understand domain
    category = doc.get("category", "")
    if category:
        parts.append(f"Category: {category}")
    
    # Expand tags with common synonyms/variations for better matching
    tags = doc.get("tags") or []
    expanded_tags = list(tags)  # Start with original tags
    
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


@router.post("/", response_model=ListingOut)
async def create_listing(payload: ListingCreate, user_id: str = Depends(get_current_user_id), db=Depends(get_db), background: BackgroundTasks = None):
    # mandatory fields enforced by model; compute posted/expiry
    allowed = {7, 14, 30, 90}
    expiry_days = payload.expiry_days if payload.expiry_days in allowed else 30
    from datetime import datetime, timedelta
    posted_date = payload.posted_date or datetime.utcnow()
    expires_at = posted_date + timedelta(days=expiry_days)
    doc = {
        "title": payload.title,
        "description": payload.description,
        "price": payload.price,
        "tags": payload.tags,
        "city": payload.city,
        "features": payload.features,
        "category": payload.category.value if isinstance(payload.category, Category) else str(payload.category),
        "userId": user_id,
        "location": {"type": "Point", "coordinates": [payload.lng, payload.lat]},
        "posted_date": posted_date,
        "expires_at": expires_at,
    }
    res = await db.listings.insert_one(doc)
    # Background embedding compute if enabled
    if settings.enable_semantic_search and background is not None:
        async def _compute_and_save(listing_id):
            fresh = await db.listings.find_one({"_id": listing_id})
            vec = embed_text(_listing_corpus(fresh or {}))
            await db.listings.update_one({"_id": listing_id}, {"$set": {"embedding": vec}})

        background.add_task(_compute_and_save, res.inserted_id)
    created = await db.listings.find_one({"_id": res.inserted_id})
    return normalize_id(created)


# IMPORTANT: Specific routes like /me, /latest, /categories MUST come before /{listing_id}
# Otherwise FastAPI will match /me to /{listing_id} and try to parse "me" as an ObjectId

@router.get("/latest", response_model=List[ListingOut])
async def latest_listings(limit: int = 12, db=Depends(get_db)):
    limit = max(1, min(limit, 50))
    cursor = db.listings.find({}).sort("posted_date", -1).limit(limit)
    results = []
    async for doc in cursor:
        normalized = normalize_id(doc)
        # Remove embedding field if present (it's huge and not needed for display)
        if 'embedding' in normalized:
            del normalized['embedding']
        results.append(normalized)
    return results


@router.get("/categories", response_model=List[str])
async def list_categories():
    try:
        return [c.value for c in Category]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")


@router.get("/me", response_model=List[ListingOut])
async def my_listings(user_id: str = Depends(get_current_user_id), db=Depends(get_db)):
    try:
        # active = not expired
        from datetime import datetime
        now = datetime.utcnow()
        print(f"Fetching listings for user: {user_id}")
        cursor = db.listings.find({"userId": user_id, "$or": [{"expires_at": {"$gt": now}}, {"expires_at": {"$exists": False}}]}).sort("posted_date", -1)
        results = []
        async for doc in cursor:
            results.append(normalize_id(doc))
        print(f"Found {len(results)} listings")
        return results
    except Exception as e:
        print(f"Error in my_listings: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching listings: {str(e)}")


@router.put("/{listing_id}", response_model=ListingOut)
async def update_listing(listing_id: str, payload: ListingUpdate, user_id: str = Depends(get_current_user_id), db=Depends(get_db), background: BackgroundTasks = None):
    oid = _to_object_id(listing_id)
    doc = await db.listings.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Listing not found")
    if doc.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update = {}
    for field in ["title", "description", "price", "tags", "city", "features"]:
        val = getattr(payload, field)
        if val is not None:
            update[field] = val
    if payload.category is not None:
        update["category"] = payload.category.value if isinstance(payload.category, Category) else str(payload.category)
    if payload.lat is not None and payload.lng is not None:
        update["location"] = {"type": "Point", "coordinates": [payload.lng, payload.lat]}
    # recalc expiry if requested
    if payload.expiry_days is not None:
        allowed = {7, 14, 30, 90}
        days = payload.expiry_days if payload.expiry_days in allowed else 30
        from datetime import datetime, timedelta
        # Use existing posted_date or now
        base = doc.get("posted_date") or datetime.utcnow()
        update["expires_at"] = base + timedelta(days=days)
    if not update:
        return normalize_id(doc)
    await db.listings.update_one({"_id": oid}, {"$set": update})
    if settings.enable_semantic_search and background is not None and update:
        async def _compute_and_save(listing_id):
            fresh = await db.listings.find_one({"_id": listing_id})
            vec = embed_text(_listing_corpus(fresh or {}))
            await db.listings.update_one({"_id": listing_id}, {"$set": {"embedding": vec}})

        background.add_task(_compute_and_save, oid)
    updated = await db.listings.find_one({"_id": oid})
    return normalize_id(updated)


@router.delete("/{listing_id}")
async def delete_listing(listing_id: str, user_id: str = Depends(get_current_user_id), db=Depends(get_db)):
    oid = _to_object_id(listing_id)
    doc = await db.listings.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Listing not found")
    if doc.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.listings.delete_one({"_id": oid})
    return {"deleted": True}


@router.get("/", response_model=List[ListingOut])
async def list_listings(skip: int = 0, limit: int = 20, category: Optional[Category] = None, db=Depends(get_db)):
    skip = max(0, skip)
    limit = max(1, min(limit, 100))
    query = {"category": (category.value if isinstance(category, Category) else str(category))} if category else {}
    cursor = db.listings.find(query).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        results.append(normalize_id(doc))
    return results


@router.get("/search/advanced", response_model=List[ListingOut])
async def search_listings(
    q: Optional[str] = Query(default=None, description="Text query"),
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius: Optional[float] = Query(default=5000, description="meters"),
    city: Optional[str] = None,
    tags: Optional[str] = Query(default=None, description="comma-separated"),
    category: Optional[Category] = None,
    skip: int = 0,
    limit: int = 20,
    db=Depends(get_db),
):
    skip = max(0, skip)
    limit = max(1, min(limit, 100))
    pipeline = []

    # Text search must be first if provided (MongoDB requirement)
    match = {}
    if q:
        match["$text"] = {"$search": q}
    
    if city:
        match["city"] = city
    if tags:
        match["tags"] = {"$in": [t.strip() for t in tags.split(",") if t.strip()]}
    if category:
        match["category"] = category.value if isinstance(category, Category) else str(category)
    
    # Add initial match stage
    if match:
        pipeline.append({"$match": match})
    
    # Add text score if text search was used
    if q:
        pipeline.append({"$addFields": {"textScore": {"$meta": "textScore"}}})
    else:
        pipeline.append({"$addFields": {"textScore": 0}})
    
    # Add geoNear after text search if lat/lng provided
    if lat is not None and lng is not None:
        pipeline.append({
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [lng, lat]},
                "distanceField": "distance",
                "spherical": True,
                "maxDistance": radius,
            }
        })
    else:
        pipeline.append({"$addFields": {"distance": None}})

    # Composite score: weight text relevance and proximity (if distance exists)
    pipeline.append(
        {
            "$addFields": {
                "proximityScore": {
                    "$cond": [
                        {"$ifNull": ["$distance", False]},
                        {"$max": [0, {"$subtract": [1, {"$divide": ["$distance", radius or 1]}]}]},
                        0,
                    ]
                },
            }
        }
    )

    pipeline.append(
        {
            "$addFields": {
                "score": {"$add": [{"$multiply": ["$textScore", 2]}, {"$multiply": ["$proximityScore", 1.5]}]},
            }
        }
    )

    pipeline.append({"$sort": {"score": -1}})
    pipeline.append({"$skip": skip})
    pipeline.append({"$limit": limit})

    cursor = db.listings.aggregate(pipeline)
    results = []
    async for doc in cursor:
        results.append(normalize_id(doc))
    return results


@router.get("/nearby", response_model=List[ListingOut])
async def listings_within_radius(lat: float, lng: float, radius: float = 5000, skip: int = 0, limit: int = 20, db=Depends(get_db)):
    skip = max(0, skip)
    limit = max(1, min(limit, 100))
    query = {
        "location": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                "$maxDistance": radius,
            }
        }
    }
    cursor = db.listings.find(query).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        results.append(normalize_id(doc))
    return results


def _cosine(a, b):
    dot = sum((x or 0.0) * (y or 0.0) for x, y in zip(a, b))
    na = math.sqrt(sum((x or 0.0) ** 2 for x in a))
    nb = math.sqrt(sum((y or 0.0) ** 2 for y in b))
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)


@router.get("/search/semantic", response_model=List[ListingOut])
async def semantic_search(
    q: str = Query(..., min_length=2),
    city: Optional[str] = None,
    tags: Optional[str] = None,
    category: Optional[Category] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius: Optional[float] = None,
    limit: int = 20,
    min_score: float = Query(default=0.3, description="Minimum similarity score (0-1)"),
    db=Depends(get_db),
):
    """
    Semantic search using ML embeddings for intelligent similarity matching.
    Understands synonyms and related terms (e.g., 'Apple Phone' matches 'iPhone').
    """
    if not settings.enable_semantic_search:
        raise HTTPException(status_code=400, detail="Semantic search disabled")

    limit = max(1, min(limit, 100))
    min_score = max(0.0, min(min_score, 1.0))  # Clamp between 0 and 1
    
    # Preprocess and expand query with synonyms
    from app.utils.query_processor import preprocess_query
    expanded_query = preprocess_query(q)
    print(f"🔍 Original query: '{q}' → Expanded: '{expanded_query[:100]}...'")
    
    query_vec = embed_text(expanded_query)
    
    # Base filter: only docs that have embeddings
    base_filter: dict = {"embedding": {"$type": "array"}}
    if city:
        base_filter["city"] = city
    if tags:
        base_filter["tags"] = {"$in": [t.strip() for t in tags.split(",") if t.strip()]}
    if category:
        base_filter["category"] = category.value if isinstance(category, Category) else str(category)
    if lat is not None and lng is not None and radius:
        base_filter["location"] = {
            "$geoWithin": {"$centerSphere": [[lng, lat], (radius / 1000) / 6378.1]}
        }

    candidates = []
    async for d in db.listings.find(base_filter).limit(500):
        score = _cosine(query_vec, d.get("embedding") or [])
        
        # Filter by minimum similarity threshold
        if score >= min_score:
            d["_score"] = score
            candidates.append(d)
    
    print(f"✅ Found {len(candidates)} results above threshold {min_score}")
    
    # Sort by score and limit results
    ranked = sorted(candidates, key=lambda x: x.get("_score", 0), reverse=True)[:limit]
    
    for d in ranked:
        d.pop("embedding", None)  # reduce payload
    
    return [normalize_id(d) for d in ranked]


@router.get("/search/hybrid", response_model=List[ListingOut])
async def hybrid_search(
    q: str = Query(..., min_length=2),
    city: Optional[str] = None,
    tags: Optional[str] = None,
    category: Optional[Category] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius: Optional[float] = None,
    limit: int = 20,
    text_weight: float = Query(default=0.4, description="Weight for keyword search (0-1)"),
    semantic_weight: float = Query(default=0.6, description="Weight for semantic search (0-1)"),
    min_score: float = Query(default=0.2, description="Minimum combined score"),
    db=Depends(get_db),
):
    """
    Hybrid search combining keyword matching and semantic similarity.
    Best of both worlds: exact matches get high scores, but semantic matches also included.
    """
    if not settings.enable_semantic_search:
        raise HTTPException(status_code=400, detail="Semantic search disabled")
    
    limit = max(1, min(limit, 100))
    
    # Normalize weights
    total_weight = text_weight + semantic_weight
    if total_weight > 0:
        text_weight = text_weight / total_weight
        semantic_weight = semantic_weight / total_weight
    else:
        text_weight = 0.5
        semantic_weight = 0.5
    
    print(f"🔍 Hybrid search: '{q}' (text: {text_weight:.2f}, semantic: {semantic_weight:.2f})")
    
    # Preprocess query for semantic search
    from app.utils.query_processor import preprocess_query
    expanded_query = preprocess_query(q)
    
    # 1. Get semantic search candidates
    query_vec = embed_text(expanded_query)
    
    base_filter: dict = {"embedding": {"$type": "array"}}
    if city:
        base_filter["city"] = city
    if tags:
        base_filter["tags"] = {"$in": [t.strip() for t in tags.split(",") if t.strip()]}
    if category:
        base_filter["category"] = category.value if isinstance(category, Category) else str(category)
    if lat is not None and lng is not None and radius:
        base_filter["location"] = {
            "$geoWithin": {"$centerSphere": [[lng, lat], (radius / 1000) / 6378.1]}
        }
    
    # Get semantic scores
    semantic_scores = {}
    async for d in db.listings.find(base_filter).limit(500):
        doc_id = str(d["_id"])
        semantic_scores[doc_id] = _cosine(query_vec, d.get("embedding") or [])
    
    # 2. Get text search candidates
    text_match = {"$text": {"$search": q}}
    if city:
        text_match["city"] = city
    if tags:
        text_match["tags"] = {"$in": [t.strip() for t in tags.split(",") if t.strip()]}
    if category:
        text_match["category"] = category.value if isinstance(category, Category) else str(category)
    if lat is not None and lng is not None and radius:
        text_match["location"] = {
            "$geoWithin": {"$centerSphere": [[lng, lat], (radius / 1000) / 6378.1]}
        }
    
    text_pipeline = [
        {"$match": text_match},
        {"$addFields": {"textScore": {"$meta": "textScore"}}},
        {"$limit": 500}
    ]
    
    text_scores = {}
    max_text_score = 0.0
    try:
        async for d in db.listings.aggregate(text_pipeline):
            doc_id = str(d["_id"])
            score = d.get("textScore", 0)
            text_scores[doc_id] = score
            max_text_score = max(max_text_score, score)
    except Exception as e:
        # If text search fails (no index), continue with semantic only
        print(f"⚠️  Text search failed: {e}")
        text_scores = {}
    
    # Normalize text scores to 0-1 range
    if max_text_score > 0:
        text_scores = {k: v / max_text_score for k, v in text_scores.items()}
    
    # 3. Combine scores
    all_doc_ids = set(semantic_scores.keys()) | set(text_scores.keys())
    combined_scores = {}
    
    for doc_id in all_doc_ids:
        text_score = text_scores.get(doc_id, 0.0)
        semantic_score = semantic_scores.get(doc_id, 0.0)
        combined = (text_weight * text_score) + (semantic_weight * semantic_score)
        
        if combined >= min_score:
            combined_scores[doc_id] = {
                "combined": combined,
                "text": text_score,
                "semantic": semantic_score
            }
    
    print(f"✅ Found {len(combined_scores)} results above threshold {min_score}")
    
    # 4. Fetch and rank results
    from bson import ObjectId
    top_ids = sorted(combined_scores.items(), key=lambda x: x[1]["combined"], reverse=True)[:limit]
    
    results = []
    for doc_id, scores in top_ids:
        doc = await db.listings.find_one({"_id": ObjectId(doc_id)})
        if doc:
            doc["_score"] = scores["combined"]
            doc["_text_score"] = scores["text"]
            doc["_semantic_score"] = scores["semantic"]
            doc.pop("embedding", None)
            results.append(normalize_id(doc))
    
    return results


# IMPORTANT: This route MUST be last among GET routes to avoid catching specific routes like /latest
@router.get("/{listing_id}", response_model=ListingOut)
async def get_listing(listing_id: str, db=Depends(get_db)):
    doc = await db.listings.find_one({"_id": _to_object_id(listing_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Listing not found")
    return normalize_id(doc)


@router.post("/{listing_id}/images/upload")
async def upload_listing_image(
    listing_id: str,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    """Upload an image file for a listing"""
    oid = _to_object_id(listing_id)
    doc = await db.listings.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Listing not found")
    if doc.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")

    url = await save_image(file, listing_id)
    await db.listings.update_one({"_id": oid}, {"$push": {"images": url}})
    return {"url": url}


@router.post("/{listing_id}/images/url")
async def add_image_by_url(
    listing_id: str,
    image_url: str = Query(..., description="URL of the image to add"),
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    """Add an image to a listing via URL"""
    oid = _to_object_id(listing_id)
    doc = await db.listings.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Listing not found")
    if doc.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Validate URL format
    if not image_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Add the URL to the images array
    await db.listings.update_one({"_id": oid}, {"$push": {"images": image_url}})
    return {"url": image_url, "message": "Image URL added successfully"}
