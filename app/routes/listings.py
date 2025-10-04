from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, UploadFile, File

from app.db.mongo import get_db
from app.models.listing import ListingCreate, ListingUpdate, ListingOut
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
    parts = [
        doc.get("title") or "",
        doc.get("description") or "",
        " ".join(doc.get("tags") or []),
        doc.get("city") or "",
    ]
    return " | ".join([p for p in parts if p])


@router.post("/", response_model=ListingOut)
async def create_listing(payload: ListingCreate, user_id: str = Depends(get_current_user_id), db=Depends(get_db), background: BackgroundTasks = None):
    doc = {
        "title": payload.title,
        "description": payload.description,
        "price": payload.price,
        "tags": payload.tags,
        "city": payload.city,
    "features": payload.features,
    "category": payload.category,
        "userId": user_id,
        "location": {"type": "Point", "coordinates": [payload.lng, payload.lat]},
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


@router.get("/{listing_id}", response_model=ListingOut)
async def get_listing(listing_id: str, db=Depends(get_db)):
    doc = await db.listings.find_one({"_id": _to_object_id(listing_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Listing not found")
    return normalize_id(doc)


@router.put("/{listing_id}", response_model=ListingOut)
async def update_listing(listing_id: str, payload: ListingUpdate, user_id: str = Depends(get_current_user_id), db=Depends(get_db), background: BackgroundTasks = None):
    oid = _to_object_id(listing_id)
    doc = await db.listings.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Listing not found")
    if doc.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update = {}
    for field in ["title", "description", "price", "tags", "city", "category", "features"]:
        val = getattr(payload, field)
        if val is not None:
            update[field] = val
    if payload.lat is not None and payload.lng is not None:
        update["location"] = {"type": "Point", "coordinates": [payload.lng, payload.lat]}
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
async def list_listings(skip: int = 0, limit: int = 20, category: Optional[str] = None, db=Depends(get_db)):
    skip = max(0, skip)
    limit = max(1, min(limit, 100))
    query = {"category": category} if category else {}
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
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db=Depends(get_db),
):
    skip = max(0, skip)
    limit = max(1, min(limit, 100))
    pipeline = []

    # Start with geoNear if lat/lng provided to get distance and proximity score.
    if lat is not None and lng is not None:
        near_stage = {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [lng, lat]},
                "distanceField": "distance",
                "spherical": True,
                "maxDistance": radius,
            }
        }
        pipeline.append(near_stage)
    else:
        pipeline.append({"$match": {}})

    match = {}
    if city:
        match["city"] = city
    if tags:
        match["tags"] = {"$in": [t.strip() for t in tags.split(",") if t.strip()]}
    if category:
        match["category"] = category
    if match:
        pipeline.append({"$match": match})

    # Text search scoring
    if q:
        pipeline.append({"$match": {"$text": {"$search": q}}})
        pipeline.append({"$addFields": {"textScore": {"$meta": "textScore"}}})
    else:
        pipeline.append({"$addFields": {"textScore": 0}})

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
    category: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius: Optional[float] = None,
    limit: int = 20,
    db=Depends(get_db),
):
    if not settings.enable_semantic_search:
        raise HTTPException(status_code=400, detail="Semantic search disabled")

    limit = max(1, min(limit, 100))
    query_vec = embed_text(q)
    # Base filter: only docs that have embeddings
    base_filter: dict = {"embedding": {"$type": "array"}}
    if city:
        base_filter["city"] = city
    if tags:
        base_filter["tags"] = {"$in": [t.strip() for t in tags.split(",") if t.strip()]}
    if category:
        base_filter["category"] = category
    if lat is not None and lng is not None and radius:
        base_filter["location"] = {
            "$geoWithin": {"$centerSphere": [[lng, lat], (radius / 1000) / 6378.1]}
        }

    candidates = []
    async for d in db.listings.find(base_filter).limit(500):
        d["_score"] = _cosine(query_vec, d.get("embedding") or [])
        candidates.append(d)
    ranked = sorted(candidates, key=lambda x: x.get("_score", 0), reverse=True)[: limit]
    for d in ranked:
        d.pop("embedding", None)  # reduce payload
    return [normalize_id(d) for d in ranked]


@router.post("/{listing_id}/images")
async def upload_listing_image(
    listing_id: str,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
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
