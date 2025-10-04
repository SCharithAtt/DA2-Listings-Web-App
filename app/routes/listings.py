from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.mongo import get_db
from app.models.listing import ListingCreate, ListingUpdate, ListingOut
from app.routes.auth import get_current_user_id
from app.utils.mongo_helpers import normalize_id


router = APIRouter()


def _to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")


@router.post("/", response_model=ListingOut)
async def create_listing(payload: ListingCreate, user_id: str = Depends(get_current_user_id), db=Depends(get_db)):
    doc = {
        "title": payload.title,
        "description": payload.description,
        "price": payload.price,
        "tags": payload.tags,
        "city": payload.city,
        "features": payload.features,
        "userId": user_id,
        "location": {"type": "Point", "coordinates": [payload.lng, payload.lat]},
    }
    res = await db.listings.insert_one(doc)
    created = await db.listings.find_one({"_id": res.inserted_id})
    return normalize_id(created)


@router.get("/{listing_id}", response_model=ListingOut)
async def get_listing(listing_id: str, db=Depends(get_db)):
    doc = await db.listings.find_one({"_id": _to_object_id(listing_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Listing not found")
    return normalize_id(doc)


@router.put("/{listing_id}", response_model=ListingOut)
async def update_listing(listing_id: str, payload: ListingUpdate, user_id: str = Depends(get_current_user_id), db=Depends(get_db)):
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
    if payload.lat is not None and payload.lng is not None:
        update["location"] = {"type": "Point", "coordinates": [payload.lng, payload.lat]}
    if not update:
        return normalize_id(doc)
    await db.listings.update_one({"_id": oid}, {"$set": update})
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
async def list_listings(skip: int = 0, limit: int = 20, db=Depends(get_db)):
    cursor = db.listings.find({}).skip(skip).limit(min(limit, 100))
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
    skip: int = 0,
    limit: int = 20,
    db=Depends(get_db),
):
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
    pipeline.append({"$limit": min(limit, 100)})

    cursor = db.listings.aggregate(pipeline)
    results = []
    async for doc in cursor:
        results.append(normalize_id(doc))
    return results


@router.get("/nearby", response_model=List[ListingOut])
async def listings_within_radius(lat: float, lng: float, radius: float = 5000, skip: int = 0, limit: int = 20, db=Depends(get_db)):
    query = {
        "location": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                "$maxDistance": radius,
            }
        }
    }
    cursor = db.listings.find(query).skip(skip).limit(min(limit, 100))
    results = []
    async for doc in cursor:
        results.append(normalize_id(doc))
    return results
